"""Focused v2 contract and release-tooling regressions."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from runtime.errors import ValidationError
from runtime.layout import (
    LUNA_WORKFLOW_SKILL,
    LUNA_WORKFLOW_SKILL_OWNER,
    LEGACY_SKILL_MARKERS,
    SOL_WORKFLOW_SKILL,
    SOL_WORKFLOW_SKILL_OWNER,
    WORKFLOW_SKILLS,
    WATCH_REPAIR_SKILL,
    WATCH_REPAIR_SKILL_OWNER,
    PackageLayout,
    ProjectPaths,
    RuntimePaths,
)
from runtime.lifecycle import plan_bootstrap, plan_remove, plan_update
from runtime.markers import PROJECT_PERSONALIZATION, remove_region
from runtime.personalization import materialize_personalization
from runtime.project_ops import plan_project_install, plan_project_update
from runtime.release import RELEASES_URL, _checksum_for
from runtime.runtime_ops import plan_platform_and_workers, plan_runtime_remove
from runtime.plan import OperationPlan
from runtime.transaction import apply as apply_mutations
from scripts.package import build


class V2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = PackageLayout.resolve(PACKAGE_ROOT)

    def test_package_validation_requires_expected_workers_and_v2_metadata(self):
        self.assertEqual(self.package.version, "2.2.0")
        self.assertEqual(
            self.package.worker_names,
            {
                "auditor",
                "default_executor",
                "investigator",
                "researcher",
                "luna_executor",
                "tester",
            },
        )
        self.package.validate()

    def test_worker_models_reasoning_and_permissions_are_parsed_contracts(self):
        from runtime._toml import tomllib

        expected = {
            "default_executor": ("gpt-6.1-sol", "medium", "workspace-write"),
            "auditor": ("gpt-6.1-sol", "medium", "read-only"),
            "tester": ("gpt-6.1-sol", "medium", "workspace-write"),
            "luna_executor": ("gpt-6-luna", "high", "workspace-write"),
            "investigator": ("gpt-6-luna", "high", "read-only"),
            "researcher": ("gpt-6-luna", "xhigh", "read-only"),
        }
        self.assertEqual(self.package.worker_names, set(expected))
        for worker, contract in expected.items():
            with self.subTest(worker=worker):
                config = tomllib.loads(
                    (self.package.agent_templates / f"{worker}.toml").read_text(encoding="utf-8")
                )
                self.assertEqual(config["name"], worker)
                self.assertEqual(
                    (config["model"], config["model_reasoning_effort"], config["sandbox_mode"]),
                    contract,
                )
                self.assertEqual(config["service_tier"], "fast")
                self.assertTrue(config["developer_instructions"].strip())

    def test_three_skills_with_resolvable_references_and_invocation_policies(self):
        self.assertEqual(WORKFLOW_SKILLS, {"codex-workflow-sol", "codex-workflow-luna", "codex-workflow-watch-repair"})
        self.assertEqual({path.name for path in (PACKAGE_ROOT / "skills").iterdir()}, WORKFLOW_SKILLS)
        for name in WORKFLOW_SKILLS:
            folder = PACKAGE_ROOT / "skills" / name
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            self.assertEqual(
                next(line.split(":", 1)[1].strip() for line in frontmatter.splitlines() if line.startswith("name:")),
                name,
            )
            # Dependency-free parser for this fixed scalar metadata contract.
            metadata = (folder / "agents" / "openai.yaml").read_text(encoding="utf-8")
            fields = dict(line.strip().split(":", 1) for line in metadata.splitlines() if ":" in line)
            self.assertEqual(
                fields["allow_implicit_invocation"].strip(),
                "true" if name == WATCH_REPAIR_SKILL else "false",
            )
            self.assertIn("$" + name, fields["default_prompt"])
            import re
            for relative in re.findall(r"\]\((references/[^)]+)\)", text):
                self.assertTrue((folder / relative).is_file(), relative)

    def test_watch_repair_requires_its_referenced_policy_resources(self):
        for resource in ("intake-and-authority.md", "repair-and-pr.md", "tether-policy.md"):
            with self.subTest(resource=resource), tempfile.TemporaryDirectory() as directory:
                incoming = Path(directory) / "incoming"
                shutil.copytree(PACKAGE_ROOT, incoming, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
                (incoming / "skills" / WATCH_REPAIR_SKILL / "references" / resource).unlink()
                with self.assertRaisesRegex(ValidationError, "references are incomplete"):
                    PackageLayout.resolve(incoming)

    def test_watch_repair_migrates_two_skill_install_and_replaces_owned_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = RuntimePaths(root / "home")
            project = ProjectPaths(root / "project")
            plan_bootstrap(self.package, runtime, project).apply()
            # Model an existing same-version two-skill runtime, including its manifest.
            shutil.rmtree(runtime.skills / WATCH_REPAIR_SKILL)
            shutil.rmtree(runtime.runtime / "skills" / WATCH_REPAIR_SKILL)
            state_path = runtime.runtime / "install_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["owned_skills"].remove(WATCH_REPAIR_SKILL)
            state["owned_runtime_files"] = [
                relative for relative in state["owned_runtime_files"]
                if not relative.startswith("skills/" + WATCH_REPAIR_SKILL + "/")
            ]
            state_path.write_text(json.dumps(state), encoding="utf-8")
            plan_update(self.package, runtime, project).apply()
            target = runtime.skills / WATCH_REPAIR_SKILL
            source = PACKAGE_ROOT / "skills" / WATCH_REPAIR_SKILL
            self.assertIn(WATCH_REPAIR_SKILL_OWNER, (target / "SKILL.md").read_text(encoding="utf-8"))
            for file in source.rglob("*"):
                if file.is_file():
                    self.assertEqual(file.read_bytes(), (target / file.relative_to(source)).read_bytes())
            updated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(set(updated["owned_skills"]), WORKFLOW_SKILLS)
            self.assertFalse(project.active.exists())
            self.assertFalse(project.workflow_dir.exists())
            stale = target / "references" / "retired.md"
            stale.write_text("retired", encoding="utf-8")
            (target / "SKILL.md").write_text(WATCH_REPAIR_SKILL_OWNER + "\nold content\n", encoding="utf-8")
            plan_update(self.package, runtime, project).apply()
            self.assertEqual((target / "SKILL.md").read_bytes(), (source / "SKILL.md").read_bytes())
            self.assertFalse(stale.exists())

    def test_release_acquisition_uses_public_repository(self):
        self.assertEqual(
            RELEASES_URL,
            "https://api.github.com/repos/evan-larsen/codex-workflow/releases?per_page=100",
        )

    def test_project_install_is_additive_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            project.root.joinpath("AGENTS.md").write_text("# Existing rules\n", encoding="utf-8")
            project.gitignore.write_text(".env\n", encoding="utf-8")
            plan_project_install(self.package, project).apply()
            first = project.active.read_text(encoding="utf-8")
            plan_project_install(self.package, project).apply()
            self.assertEqual(project.active.read_text(encoding="utf-8"), first)
            self.assertIn("# Existing rules", project.active.read_text(encoding="utf-8"))
            self.assertIn(".env", project.gitignore.read_text(encoding="utf-8"))
            self.assertEqual(project.gitignore.read_text(encoding="utf-8").count("codex-workflow-managed-start"), 1)

    def test_old_project_marker_migrates_to_canonical_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            plan_project_install(self.package, project).apply()
            old = "<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->"
            project.active.write_text(
                project.active.read_text(encoding="utf-8").replace(
                    "<!-- codex-workflow-id: codex_workflow -->", old
                ),
                encoding="utf-8",
            )
            mutations, _ = plan_project_update(self.package, self.package, project, legacy_local_instructions=None)
            for mutation in mutations:
                if mutation.content is not None:
                    mutation.path.parent.mkdir(parents=True, exist_ok=True)
                    mutation.path.write_bytes(mutation.content)
            result = project.active.read_text(encoding="utf-8")
            self.assertIn("<!-- codex-workflow-id: codex_workflow -->", result)
            self.assertNotIn(old, result)

    def test_legacy_merged_entry_requires_reviewed_local_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            project = ProjectPaths(Path(directory))
            template = self.package.project_template.read_text(encoding="utf-8")
            old = "<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->"
            merged = remove_region(template, PROJECT_PERSONALIZATION).replace(
                "<!-- codex-workflow-id: codex_workflow -->", old
            )
            merged += "\n# merged legacy content\n"
            project.active.write_text(merged, encoding="utf-8")
            reviewed = "Keep the local build command documented."
            mutations, _ = plan_project_update(
                self.package, self.package, project,
                legacy_local_instructions=reviewed,
            )
            apply_mutations(mutations)
            result = project.active.read_text(encoding="utf-8")
            self.assertIn(reviewed, result)
            self.assertNotIn("merged legacy content", result)

            project.active.write_text(merged, encoding="utf-8")
            with self.assertRaises(ValidationError):
                plan_project_update(self.package, self.package, project, legacy_local_instructions=None)

    def test_bootstrap_removes_only_legacy_global_agents_region(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = RuntimePaths(root / "codex-home")
            runtime.codex_home.mkdir(parents=True)
            runtime.user_agents.write_text(
                "# Keep before\n\n"
                "<!-- codex-workflow-user-managed-start -->\n"
                "old workflow router\n"
                "<!-- codex-workflow-user-managed-end -->\n\n"
                "# Keep after\n",
                encoding="utf-8",
            )
            plan_bootstrap(self.package, runtime, ProjectPaths(root / "project")).apply()
            result = runtime.user_agents.read_text(encoding="utf-8")
            self.assertIn("# Keep before", result)
            self.assertIn("# Keep after", result)
            self.assertNotIn("old workflow router", result)
            self.assertNotIn("codex-workflow-user-managed", result)

    def test_three_section_personalization_remains_compatible(self):
        resource = """# Project Workflow Personalization

## Frontend Project Profile
Status: customized
Decision: Prefer accessible forms.

## Design Principles
Status: default
Decision: Keep defaults.

## Additional Workflow Decisions
Status: skipped
Decision: No additional decisions.
"""
        self.assertEqual(materialize_personalization(resource), "Prefer accessible forms.")

    def test_unowned_auditor_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            runtime = RuntimePaths(home)
            runtime.runtime.mkdir(parents=True)
            runtime.agents.mkdir(parents=True)
            (runtime.runtime / "install_state.json").write_text("{}\n", encoding="utf-8")
            target = runtime.agents / "auditor.toml"
            target.write_text('name = "someone_else"\n', encoding="utf-8")
            with self.assertRaises(ValidationError):
                plan_platform_and_workers(runtime, package=self.package)
            self.assertEqual(target.read_text(encoding="utf-8"), 'name = "someone_else"\n')

    def test_release_archive_and_checksum_are_reproducible_and_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, sums = build(PACKAGE_ROOT, Path(directory))
            second, _ = build(PACKAGE_ROOT, Path(directory) / "second")
            line = sums.read_text(encoding="ascii")
            self.assertEqual(_checksum_for(line, archive.name), hashlib.sha256(archive.read_bytes()).hexdigest())
            self.assertEqual(archive.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(archive) as bundle:
                self.assertTrue(bundle.namelist())
                self.assertTrue(all(name == "codex_workflow" or name.startswith("codex_workflow/") for name in bundle.namelist()))
                bundle.extractall(Path(directory) / "extracted")
            extracted = PackageLayout.resolve(Path(directory) / "extracted" / "codex_workflow")
            self.assertEqual(extracted.version, "2.2.0")
            for source in sorted(self.package.agent_templates.glob("*.toml")):
                archived = (
                    Path(directory)
                    / "extracted"
                    / "codex_workflow"
                    / "templates"
                    / "agents"
                    / source.name
                )
                self.assertEqual(archived.read_bytes(), source.read_bytes(), source.name)
            for skill_name in WORKFLOW_SKILLS:
                skill_root = PACKAGE_ROOT / "skills" / skill_name
                for source in sorted(
                    path for path in skill_root.rglob("*") if path.is_file()
                ):
                    archived = (
                        Path(directory)
                        / "extracted"
                        / "codex_workflow"
                        / "skills"
                        / skill_name
                        / source.relative_to(skill_root)
                    )
                    self.assertEqual(
                        archived.read_bytes(), source.read_bytes(), str(source)
                    )

    def test_bootstrap_installs_exact_packaged_worker_templates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            project.root.mkdir()
            project.active.write_text("# Existing project rules\n", encoding="utf-8")
            plan_bootstrap(self.package, RuntimePaths(home), project).apply()
            self.assertEqual(
                project.active.read_text(encoding="utf-8"),
                "# Existing project rules\n",
            )
            self.assertFalse((home / "codex_workflow" / ".git").exists())
            state = json.loads(
                (home / "codex_workflow" / "install_state.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertFalse(
                any(path.startswith(".git/") for path in state["owned_runtime_files"])
            )
            self.assertFalse((home / "AGENTS.md").exists())
            config = (home / "config.toml").read_text(encoding="utf-8")
            self.assertIn("max_concurrent_threads_per_session = 10", config)
            for source in sorted(self.package.agent_templates.glob("*.toml")):
                installed = home / "agents" / source.name
                self.assertEqual(
                    installed.read_text(encoding="utf-8"),
                    source.read_text(encoding="utf-8"),
                    source.name,
                )

    def test_bootstrap_scripts_expose_checksum_and_project_inputs(self):
        powershell = (PACKAGE_ROOT / "scripts" / "bootstrap.ps1").read_text(encoding="utf-8")
        bash = (PACKAGE_ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")
        for text in (powershell, bash):
            self.assertIn("SHA256", text)
            self.assertIn("project", text.lower())
            self.assertIn("check-compatibility", text)
            self.assertIn("validate", text)

    def test_powershell_bootstrap_runs_with_mocked_codex(self):
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_output = root / "dist"
            package_result = subprocess.run(
                [
                    powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(PACKAGE_ROOT / "scripts" / "package.ps1"), "-Root", str(PACKAGE_ROOT),
                    "-Output", str(package_output),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(package_result.returncode, 0, package_result.stdout + package_result.stderr)
            archive = package_output / "codex_workflow-2.2.0.zip"
            self.assertTrue(archive.is_file())
            self.assertTrue((package_output / "SHA256SUMS").is_file())
            fake_bin = root / "bin"
            fake_bin.mkdir()
            (fake_bin / "codex.cmd").write_text("@echo codex 0.147.0\n", encoding="ascii")
            if os.name != "nt":
                codex = fake_bin / "codex"
                codex.write_text("#!/bin/sh\necho codex 0.147.0\n", encoding="ascii")
                codex.chmod(0o755)
            project = root / "project"
            home = root / "codex-home"
            environment = os.environ.copy()
            environment["PATH"] = str(fake_bin) + os.pathsep + environment["PATH"]
            result = subprocess.run(
                [
                    powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PACKAGE_ROOT / "scripts" / "bootstrap.ps1"),
                    "-Archive", str(archive), "-Project", str(project), "-CodexHome", str(home),
                ],
                capture_output=True, text=True, env=environment, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((project / "AGENTS.md").exists())
            self.assertTrue((home / "codex_workflow" / "install_state.json").is_file())

    def test_update_does_not_modify_project_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            project.root.mkdir()
            project.active.write_text("# Preserve exactly\n", encoding="utf-8")
            runtime = RuntimePaths(home)
            plan_bootstrap(self.package, runtime, project).apply()
            before = project.active.read_bytes()
            stale_git_file = home / "codex_workflow" / ".git" / "stale"
            stale_git_file.parent.mkdir()
            stale_git_file.write_text("obsolete\n", encoding="utf-8")
            state_path = home / "codex_workflow" / "install_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["owned_runtime_files"].append(".git/stale")
            state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")
            plan_update(self.package, runtime, project).apply()
            self.assertEqual(project.active.read_bytes(), before)
            self.assertFalse(project.workflow_dir.exists())
            self.assertFalse(stale_git_file.exists())
            self.assertFalse(stale_git_file.parent.exists())

    def test_bootstrap_installs_owned_global_workflow_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            project = ProjectPaths(Path(directory) / "project")
            plan_bootstrap(self.package, RuntimePaths(home), project).apply()
            skill = home / "skills" / SOL_WORKFLOW_SKILL / "SKILL.md"
            self.assertTrue(skill.is_file())
            self.assertIn(SOL_WORKFLOW_SKILL_OWNER, skill.read_text(encoding="utf-8"))
            self.assertTrue(
                (home / "skills" / SOL_WORKFLOW_SKILL / "references" / "maintenance.md").is_file()
            )
            heavy_skill = home / "skills" / LUNA_WORKFLOW_SKILL / "SKILL.md"
            self.assertTrue(heavy_skill.is_file())
            self.assertIn(
                LUNA_WORKFLOW_SKILL_OWNER,
                heavy_skill.read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (
                    home
                    / "skills"
                    / LUNA_WORKFLOW_SKILL
                    / "references"
                    / "maintenance.md"
                ).is_file()
            )
            state = json.loads((home / "codex_workflow" / "install_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["owned_skills"], sorted(WORKFLOW_SKILLS))

    def test_unowned_global_skill_collision_is_rejected_without_mutation(self):
        for skill_name in WORKFLOW_SKILLS:
            with self.subTest(skill_name=skill_name), tempfile.TemporaryDirectory() as directory:
                home = Path(directory) / "codex-home"
                project = ProjectPaths(Path(directory) / "project")
                skill = home / "skills" / skill_name
                skill.mkdir(parents=True)
                marker = skill / "SKILL.md"
                marker.write_text("---\nname: unrelated\n---\n", encoding="utf-8")
                with self.assertRaises(ValidationError):
                    plan_bootstrap(self.package, RuntimePaths(home), project)
                self.assertEqual(
                    marker.read_text(encoding="utf-8"),
                    "---\nname: unrelated\n---\n",
                )
                self.assertFalse((home / "codex_workflow").exists())

    def test_update_replaces_owned_global_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            runtime = RuntimePaths(home)
            plan_bootstrap(self.package, runtime, project).apply()
            incoming_root = root / "incoming"
            shutil.copytree(PACKAGE_ROOT, incoming_root)
            incoming_skill = incoming_root / "skills" / LUNA_WORKFLOW_SKILL / "SKILL.md"
            incoming_skill.write_text(
                incoming_skill.read_text(encoding="utf-8") + "\nUpdated test content.\n",
                encoding="utf-8",
            )
            stale = home / "skills" / LUNA_WORKFLOW_SKILL / "references" / "obsolete.md"
            stale.write_text("obsolete\n", encoding="utf-8")
            incoming = PackageLayout.resolve(incoming_root)
            plan_update(incoming, runtime, project).apply()
            self.assertIn("Updated test content.", (home / "skills" / LUNA_WORKFLOW_SKILL / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(stale.exists())

    def test_update_repairs_missing_luna_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            runtime = RuntimePaths(home)
            plan_bootstrap(self.package, runtime, project).apply()
            shutil.rmtree(home / "skills" / LUNA_WORKFLOW_SKILL)
            state_path = home / "codex_workflow" / "install_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["owned_skills"] = [SOL_WORKFLOW_SKILL]
            state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

            plan_update(self.package, runtime, project).apply()

            heavy_skill = home / "skills" / LUNA_WORKFLOW_SKILL / "SKILL.md"
            self.assertTrue(heavy_skill.is_file())
            self.assertIn(
                LUNA_WORKFLOW_SKILL_OWNER,
                heavy_skill.read_text(encoding="utf-8"),
            )
            updated_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_state["owned_skills"], sorted(WORKFLOW_SKILLS))

    def test_update_migrates_owned_legacy_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            runtime = RuntimePaths(home)
            plan_bootstrap(self.package, runtime, project).apply()
            legacy_name, legacy_marker = next(iter(LEGACY_SKILL_MARKERS.items()))
            legacy = home / "skills" / legacy_name
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text(legacy_marker + "\n", encoding="utf-8")
            state_path = home / "codex_workflow" / "install_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["owned_skills"] = [legacy_name]
            obsolete_worker = home / "agents" / "companion.toml"
            obsolete_worker.write_text(
                '# codex-workflow-worker: companion\nname = "companion"\n',
                encoding="utf-8",
            )
            state["owned_workers"].append("companion")
            state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")
            plan_update(self.package, runtime, project).apply()
            self.assertFalse(legacy.exists())
            self.assertFalse(obsolete_worker.exists())
            self.assertTrue((home / "skills" / SOL_WORKFLOW_SKILL / "SKILL.md").is_file())
            self.assertTrue((home / "skills" / LUNA_WORKFLOW_SKILL / "SKILL.md").is_file())

    def _legacy_runtime(self, root, *, marked=True):
        """Schema-1 layout deliberately lacking either new skill or worker set."""
        runtime = RuntimePaths(root / "codex-home")
        runtime.runtime.mkdir(parents=True)
        shutil.copytree(PACKAGE_ROOT / "templates", runtime.runtime / "templates")
        for name in ("default_executor", "luna_executor"):
            (runtime.runtime / "templates" / "agents" / f"{name}.toml").unlink()
        runtime.agents.mkdir()
        for worker in ("default_executor", "heavy_coordinator", "senior_executor"):
            content = f'name = "{worker}"\n'
            if marked or worker == "default_executor":
                content = f"# codex-workflow-worker: {worker}\n" + content
            (runtime.agents / f"{worker}.toml").write_text(content, encoding="utf-8")
            (runtime.runtime / "templates" / "agents" / f"{worker}.toml").write_text(content, encoding="utf-8")
        owned_runtime = ["templates/agents/heavy_coordinator.toml", "templates/agents/senior_executor.toml"]
        for name, marker in LEGACY_SKILL_MARKERS.items():
            folder = runtime.skills / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text((marker if marked else "user-owned") + "\n", encoding="utf-8")
            stale = runtime.runtime / "skills" / name / "SKILL.md"
            stale.parent.mkdir(parents=True)
            stale.write_text(marker + "\n", encoding="utf-8")
            owned_runtime.append(stale.relative_to(runtime.runtime).as_posix())
        (runtime.runtime / "VERSION").write_text("2.0.10\n", encoding="utf-8")
        (runtime.runtime / "install_state.json").write_text(json.dumps({
            "schema_version": 1, "version": "2.0.10",
            "owned_workers": ["default_executor", "heavy_coordinator", "senior_executor"],
            "owned_skills": list(LEGACY_SKILL_MARKERS),
            "owned_runtime_files": owned_runtime,
        }), encoding="utf-8")
        runtime.config_toml.write_text(
            'model = "user-parent"\nmodel_reasoning_effort = "high"\n[unrelated]\nkeep = true\n',
            encoding="utf-8",
        )
        (runtime.agents / "custom.toml").write_text('name = "custom"\n', encoding="utf-8")
        runtime.user_agents.write_text("# Personal instructions\n", encoding="utf-8")
        project = ProjectPaths(root / "project")
        project.root.mkdir()
        project.active.write_text("# Project instructions\n", encoding="utf-8")
        project.docs.mkdir()
        (project.docs / "existing.md").write_text("Keep memory untouched\n", encoding="utf-8")
        return runtime, project

    def test_schema_one_legacy_migration_preserves_unowned_content(self):
        from runtime._toml import tomllib
        for marked in (True, False):
            with self.subTest(marked=marked), tempfile.TemporaryDirectory() as directory:
                runtime, project = self._legacy_runtime(Path(directory), marked=marked)
                preserved = {
                    path: path.read_bytes() for path in (
                        project.active, project.docs / "existing.md",
                        runtime.user_agents, runtime.agents / "custom.toml",
                    )
                }
                with self.assertRaises(ValidationError):
                    PackageLayout.resolve(runtime.runtime)
                PackageLayout.resolve(runtime.runtime, allow_legacy=True)
                plan = plan_update(self.package, runtime, project)
                plan.apply()
                state = json.loads((runtime.runtime / "install_state.json").read_text(encoding="utf-8"))
                self.assertEqual(state["schema_version"], 2)
                self.assertEqual(state["version"], "2.2.0")
                self.assertEqual(set(state["owned_skills"]), WORKFLOW_SKILLS)
                self.assertEqual(set(state["owned_workers"]), self.package.worker_names)
                for name in LEGACY_SKILL_MARKERS:
                    self.assertEqual((runtime.skills / name).exists(), not marked)
                    self.assertFalse((runtime.runtime / "skills" / name).exists())
                    if not marked:
                        self.assertEqual((runtime.skills / name / "SKILL.md").read_text(encoding="utf-8"), "user-owned\n")
                for name in ("heavy_coordinator", "senior_executor"):
                    self.assertEqual((runtime.agents / f"{name}.toml").exists(), not marked)
                    self.assertFalse((runtime.runtime / "templates" / "agents" / f"{name}.toml").exists())
                for path, original in preserved.items():
                    self.assertEqual(path.read_bytes(), original)
                config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
                self.assertEqual(config["model"], "user-parent")
                self.assertEqual(config["model_reasoning_effort"], "high")
                self.assertEqual(config["unrelated"], {"keep": True})
                self.assertTrue(Path(plan.details["backup"]).is_dir())
                self.assertFalse(project.workflow_dir.exists())

    def test_update_new_target_collision_leaves_legacy_install_untouched(self):
        for name in WORKFLOW_SKILLS:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                runtime, project = self._legacy_runtime(Path(directory))
                target = runtime.skills / name
                target.mkdir()
                (target / "SKILL.md").write_text("user-owned\n", encoding="utf-8")
                before = {path: path.read_bytes() for path in runtime.codex_home.rglob("*") if path.is_file()}
                with self.assertRaises(ValidationError):
                    plan_update(self.package, runtime, project)
                after = {path: path.read_bytes() for path in runtime.codex_home.rglob("*") if path.is_file()}
                self.assertEqual(after, before)

    def test_bootstrap_retires_marked_legacy_without_creating_project_files(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime, project = self._legacy_runtime(Path(directory))
            plan_bootstrap(self.package, runtime, project).apply()
            self.assertEqual({path.name for path in runtime.skills.iterdir()}, WORKFLOW_SKILLS)
            for worker in ("heavy_coordinator", "senior_executor"):
                self.assertFalse((runtime.agents / f"{worker}.toml").exists())
            self.assertEqual(project.active.read_text(encoding="utf-8"), "# Project instructions\n")
            self.assertFalse(project.workflow_dir.exists())

    def test_remove_recognizes_legacy_markers_and_preserves_unmarked_names(self):
        for marked in (True, False):
            with self.subTest(marked=marked), tempfile.TemporaryDirectory() as directory:
                runtime, project = self._legacy_runtime(Path(directory), marked=marked)
                mutations, dirs, warnings = plan_runtime_remove(runtime)
                OperationPlan("remove", mutations, warnings, [], cleanup_dirs=dirs).apply()
                for name in LEGACY_SKILL_MARKERS:
                    self.assertEqual((runtime.skills / name).exists(), not marked)
                for worker in ("heavy_coordinator", "senior_executor"):
                    self.assertEqual((runtime.agents / f"{worker}.toml").exists(), not marked)
                self.assertTrue((runtime.agents / "custom.toml").is_file())
                self.assertEqual(project.active.read_text(encoding="utf-8"), "# Project instructions\n")
                self.assertTrue((project.docs / "existing.md").is_file())

    def test_remove_deletes_owned_skill_but_preserves_unowned_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            project = ProjectPaths(root / "project")
            runtime = RuntimePaths(home)
            plan_bootstrap(self.package, runtime, project).apply()
            unowned = home / "skills" / "unrelated"
            unowned.mkdir(parents=True)
            (unowned / "SKILL.md").write_text("---\nname: unrelated\n---\n", encoding="utf-8")
            plan_remove(runtime, project).apply()
            for skill_name in WORKFLOW_SKILLS:
                self.assertFalse((home / "skills" / skill_name).exists())
            self.assertTrue((unowned / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

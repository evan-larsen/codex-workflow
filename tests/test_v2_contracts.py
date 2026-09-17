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
    LEGACY_SKILL_MARKERS,
    WORKFLOW_SKILL,
    WORKFLOW_SKILL_OWNER,
    PackageLayout,
    ProjectPaths,
    RuntimePaths,
)
from runtime.lifecycle import plan_bootstrap, plan_remove, plan_update
from runtime.markers import PROJECT_PERSONALIZATION, remove_region
from runtime.personalization import materialize_personalization
from runtime.project_ops import plan_project_install, plan_project_update
from runtime.release import RELEASES_URL, _checksum_for
from runtime.runtime_ops import plan_platform_and_workers
from runtime.transaction import apply as apply_mutations
from scripts.package import build


class V2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = PackageLayout.resolve(PACKAGE_ROOT)

    def test_package_validation_requires_expected_workers_and_v2_metadata(self):
        self.assertEqual(self.package.version, "2.0.4")
        self.assertEqual(
            self.package.worker_names,
            {"auditor", "default_executor", "investigator", "senior_executor", "tester"},
        )
        self.package.validate()

    def test_single_skill_and_worker_guardrails_are_source_contracts(self):
        skill = (PACKAGE_ROOT / "skills" / WORKFLOW_SKILL / "SKILL.md").read_text(
            encoding="utf-8"
        )
        coordination = (
            PACKAGE_ROOT / "skills" / WORKFLOW_SKILL / "references" / "coordination.md"
        ).read_text(encoding="utf-8")
        metadata = (
            PACKAGE_ROOT / "skills" / WORKFLOW_SKILL / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        project = (PACKAGE_ROOT / "templates" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        skill_compact = " ".join(skill.split())
        coordination_compact = " ".join(coordination.split())
        project_compact = " ".join(project.split())
        for requirement in (
            "There are no Light, Medium, or Heavy modes",
            "obvious reversible micro-edits",
            "Use one `default_executor`",
            "Reuse the current worker",
            "Run a justified broad suite once at the end",
        ):
            self.assertIn(requirement, skill_compact)
        self.assertIn("Do not create Companion", coordination_compact)
        self.assertIn("one prioritized, deduplicated defect packet", coordination_compact)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("# Project instructions", project_compact)
        self.assertNotIn("$codex-workflow", project)
        self.assertNotIn("Route Selection", project)
        for obsolete in (
            "heavy_route.md",
            "medium_route.md",
            "companion.md",
            "investigation_team.md",
            "closure_steward.md",
            "user_AGENTS.md",
            "enable_auto_check_update.md",
            "disable_auto_check_update.md",
            "resources/auto_check_update.md",
            "install.md",
            "personalization_guide.md",
            "enable.md",
            "disable.md",
        ):
            self.assertFalse((PACKAGE_ROOT / obsolete).exists(), obsolete)

        required_worker_contracts = {
            "default_executor": (
                'service_tier = "fast"',
                "no more than 12 outer tool calls",
                "Do not create a one-defect-per-turn loop",
            ),
            "investigator": (
                'service_tier = "fast"',
                "at most 6 outer tool calls",
                "Stop as soon as the coordinator can make the named decision",
            ),
            "senior_executor": (
                'model_reasoning_effort = "xhigh"',
                "at most 16 outer tool calls",
                "Do not coordinate or spawn agents",
            ),
            "tester": (
                'service_tier = "fast"',
                "at most 8 outer tool calls",
                "one prioritized packet",
            ),
            "auditor": (
                'service_tier = "fast"',
                "at most 8 outer tool calls",
                "Do not run tests, lint, formatting, builds, or environment checks",
            ),
        }
        for worker, requirements in required_worker_contracts.items():
            text = (
                PACKAGE_ROOT / "templates" / "agents" / f"{worker}.toml"
            ).read_text(encoding="utf-8")
            text_compact = " ".join(text.split())
            for requirement in requirements:
                self.assertIn(requirement, text_compact, f"{worker}: {requirement}")

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
            self.assertEqual(extracted.version, "2.0.4")
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
            skill_root = PACKAGE_ROOT / "skills" / WORKFLOW_SKILL
            for source in sorted(path for path in skill_root.rglob("*") if path.is_file()):
                archived = (
                    Path(directory)
                    / "extracted"
                    / "codex_workflow"
                    / "skills"
                    / WORKFLOW_SKILL
                    / source.relative_to(skill_root)
                )
                self.assertEqual(archived.read_bytes(), source.read_bytes(), str(source))

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
            archive = package_output / "codex_workflow-2.0.4.zip"
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

    def test_bootstrap_installs_owned_global_workflow_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            project = ProjectPaths(Path(directory) / "project")
            plan_bootstrap(self.package, RuntimePaths(home), project).apply()
            skill = home / "skills" / WORKFLOW_SKILL / "SKILL.md"
            self.assertTrue(skill.is_file())
            self.assertIn(WORKFLOW_SKILL_OWNER, skill.read_text(encoding="utf-8"))
            self.assertTrue(
                (home / "skills" / WORKFLOW_SKILL / "references" / "coordination.md").is_file()
            )
            state = json.loads((home / "codex_workflow" / "install_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["owned_skills"], [WORKFLOW_SKILL])

    def test_unowned_global_skill_collision_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            project = ProjectPaths(Path(directory) / "project")
            skill = home / "skills" / WORKFLOW_SKILL
            skill.mkdir(parents=True)
            marker = skill / "SKILL.md"
            marker.write_text("---\nname: unrelated\n---\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                plan_bootstrap(self.package, RuntimePaths(home), project)
            self.assertEqual(marker.read_text(encoding="utf-8"), "---\nname: unrelated\n---\n")
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
            incoming_skill = incoming_root / "skills" / WORKFLOW_SKILL / "SKILL.md"
            incoming_skill.write_text(
                incoming_skill.read_text(encoding="utf-8") + "\nUpdated test content.\n",
                encoding="utf-8",
            )
            stale = home / "skills" / WORKFLOW_SKILL / "references" / "obsolete.md"
            stale.write_text("obsolete\n", encoding="utf-8")
            incoming = PackageLayout.resolve(incoming_root)
            plan_update(incoming, runtime, project).apply()
            self.assertIn("Updated test content.", (home / "skills" / WORKFLOW_SKILL / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(stale.exists())

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
            self.assertTrue((home / "skills" / WORKFLOW_SKILL / "SKILL.md").is_file())

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
            self.assertFalse((home / "skills" / WORKFLOW_SKILL).exists())
            self.assertTrue((unowned / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

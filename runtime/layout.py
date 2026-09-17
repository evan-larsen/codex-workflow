"""Package, user-runtime, and project path contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ._toml import tomllib
from .errors import ValidationError
from .markers import (
    validate_project_template,
)
from .personalization import materialize_personalization


PROJECT_ID = "<!-- codex-workflow-id: codex_workflow -->"
# v1 installations used the original repository-qualified marker. Keep it
# recognizable for one explicit update migration, but never emit it again.
LEGACY_PROJECT_IDS = frozenset(
    {"<!-- codex-workflow-id: viettran-edgeAI/codex_workflow -->"}
)


def is_project_owned(text: str) -> bool:
    """Return whether a project entry belongs to this workflow or its legacy."""

    return PROJECT_ID in text or any(marker in text for marker in LEGACY_PROJECT_IDS)


WORKER_MARKER = re.compile(r"^# codex-workflow-worker: ([A-Za-z0-9_-]+)$", re.MULTILINE)
PROJECT_STATE = "state.json"
USER_STATE = "install_state.json"
WORKFLOW_SKILL = "codex-workflow"
WORKFLOW_SKILL_OWNER = "<!-- codex-workflow-skill-owner: codex_workflow -->"
LEGACY_SKILL_MARKERS = {
    "codex-workflow-maintainer": (
        "<!-- codex-workflow-maintainer-owner: codex_workflow -->"
    ),
}
OWNED_SKILL_MARKERS = {WORKFLOW_SKILL: WORKFLOW_SKILL_OWNER, **LEGACY_SKILL_MARKERS}
BUILTIN_WORKERS = frozenset(
    {
        "default_executor",
        "senior_executor",
        "tester",
        "investigator",
        "auditor",
    }
)


@dataclass(frozen=True)
class PackageLayout:
    root: Path
    project_template: Path
    agent_templates: Path
    project_docs: Path

    @classmethod
    def resolve(cls, root: Path, *, allow_legacy: bool = False) -> "PackageLayout":
        root = root.resolve()
        if not (root / "VERSION").is_file():
            nested = root / "codex_workflow"
            if nested.is_dir() and (nested / "VERSION").is_file():
                root = nested
            else:
                raise ValidationError(f"package root does not contain VERSION: {root}")
        if (root / "templates" / "AGENTS.md").is_file():
            layout = cls(
                root,
                root / "templates" / "AGENTS.md",
                root / "templates" / "agents",
                root / "templates" / "project_docs",
            )
        else:
            layout = cls(root, root / "AGENTS.md", root / "agents", root / "project_docs")
        layout.validate(allow_legacy=allow_legacy)
        return layout

    def validate(self, *, allow_legacy: bool = False) -> None:
        symlinks = [
            path
            for path in self.root.rglob("*")
            if path.is_symlink()
            and ".backups" not in path.parts
            and ".source_backup" not in path.parts
        ]
        if symlinks:
            raise ValidationError(f"package contains symlinks: {symlinks[:3]}")
        version = self.version
        if not re.fullmatch(
            r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
            r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?",
            version,
        ):
            raise ValidationError(f"invalid package VERSION: {version!r}")
        if not allow_legacy:
            skill_dir = self.root / "skills" / WORKFLOW_SKILL
            skill = skill_dir / "SKILL.md"
            if not skill.is_file():
                raise ValidationError("package workflow skill is missing")
            if WORKFLOW_SKILL_OWNER not in skill.read_text(encoding="utf-8"):
                raise ValidationError("package workflow skill ownership marker is missing")
            if not (skill_dir / "agents" / "openai.yaml").is_file():
                raise ValidationError("package workflow skill metadata is missing")
            required_skill_references = {
                "coordination.md",
                "maintenance.md",
                "verification.md",
            }
            present_skill_references = {
                path.name
                for path in (skill_dir / "references").glob("*.md")
                if path.is_file()
            }
            if not required_skill_references.issubset(present_skill_references):
                raise ValidationError("package workflow skill references are incomplete")
            required = [
                "workflow.py",
                "bootstrap.md",
                "update.md",
                "check_update.md",
                "remove.md",
                "runtime/__init__.py",
                "runtime/_toml.py",
                "runtime/backup.py",
                "runtime/layout.py",
                "runtime/lifecycle.py",
                "runtime/markers.py",
                "runtime/platform_settings.py",
                "runtime/personalization.py",
                "runtime/plan.py",
                "runtime/project_ops.py",
                "runtime/release.py",
                "runtime/runtime_ops.py",
                "runtime/transaction.py",
                "resources/personalization.md",
            ]
            missing = [relative for relative in required if not (self.root / relative).is_file()]
            if missing:
                raise ValidationError(f"package runtime files missing: {missing}")
            validate_project_template(self.project_template.read_text(encoding="utf-8"))
        required_docs = {
            "project_overview.md",
            "project_core_tech.md",
            "project_structure.md",
            "project_progress.md",
            "project_diary.md",
            "latest_session_work.md",
        }
        present_docs = {path.name for path in self.project_docs.glob("*.md")}
        if not required_docs.issubset(present_docs):
            raise ValidationError(
                f"package project document templates missing: {sorted(required_docs - present_docs)}"
            )
        templates = self.worker_names
        if not templates:
            raise ValidationError("package has no worker templates")
        if not allow_legacy and templates != BUILTIN_WORKERS:
            raise ValidationError(
                "package worker set is incomplete or unsupported; "
                f"missing={sorted(BUILTIN_WORKERS - templates)}, "
                f"unexpected={sorted(templates - BUILTIN_WORKERS)}"
            )
        for worker in templates:
            text = (self.agent_templates / f"{worker}.toml").read_text(encoding="utf-8")
            match = WORKER_MARKER.search(text)
            if not allow_legacy and (match is None or match.group(1) != worker):
                raise ValidationError(f"worker ownership marker missing or wrong: {worker}")
            try:
                tomllib.loads(text)
            except tomllib.TOMLDecodeError as error:
                raise ValidationError(f"invalid worker TOML {worker}: {error}") from error
        if not allow_legacy:
            materialize_personalization(
                (self.root / "resources" / "personalization.md").read_text(
                    encoding="utf-8"
                )
            )

    @property
    def version(self) -> str:
        lines = (self.root / "VERSION").read_text(encoding="utf-8").splitlines()
        if len(lines) != 1 or not lines[0]:
            raise ValidationError("VERSION must contain exactly one non-empty line")
        return lines[0]

    @property
    def worker_names(self) -> set[str]:
        return {path.stem for path in self.agent_templates.glob("*.toml") if path.is_file()}

    @property
    def default_personalization(self) -> Path:
        return self.root / "resources" / "personalization.md"


@dataclass(frozen=True)
class RuntimePaths:
    codex_home: Path

    @property
    def runtime(self) -> Path:
        return self.codex_home / "codex_workflow"

    @property
    def agents(self) -> Path:
        return self.codex_home / "agents"

    @property
    def skills(self) -> Path:
        return self.codex_home / "skills"

    @property
    def config_toml(self) -> Path:
        return self.codex_home / "config.toml"

    @property
    def user_agents(self) -> Path:
        return self.codex_home / "AGENTS.md"


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def active(self) -> Path:
        return self.root / "AGENTS.md"

    @property
    def hidden_dir(self) -> Path:
        return self.root / ".codex_workflow_hidden_resources"

    @property
    def legacy_hidden_dir(self) -> Path:
        """Previous singular resource name retained for existing projects."""
        return self.root / ".codex_workflow_hidden_resource"

    @property
    def workflow_dir(self) -> Path:
        """Select the canonical resource directory, or an existing legacy one."""
        if self.hidden_dir.exists() or not self.legacy_hidden_dir.exists():
            return self.hidden_dir
        return self.legacy_hidden_dir

    @property
    def source_dir(self) -> Path:
        """Project-local package staging directory removed after installation."""
        return self.root / "Codex_Workflow"

    @property
    def gitignore(self) -> Path:
        return self.root / ".gitignore"

    @property
    def disabled(self) -> Path:
        return self.workflow_dir / ".AGENTS.md"

    @property
    def personalization(self) -> Path:
        return self.workflow_dir / "personalization.md"

    @property
    def state(self) -> Path:
        return self.workflow_dir / PROJECT_STATE

    @property
    def docs(self) -> Path:
        return self.root / "agent_docs"

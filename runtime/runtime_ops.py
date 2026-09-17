"""User-level runtime and fixed platform-setting operations."""

from __future__ import annotations

from pathlib import Path

from .platform_settings import (
    patch_codex_settings,
    remove_workflow_owned_settings,
)
from .errors import ValidationError
from .layout import (
    OWNED_SKILL_MARKERS,
    USER_STATE,
    WORKFLOW_SKILL,
    WORKFLOW_SKILL_OWNER,
    WORKER_MARKER,
    PackageLayout,
    RuntimePaths,
)
from .markers import (
    USER_MANAGED,
    remove_region,
)
from .plan import read_json, read_string_list, text_mutation
from .transaction import Mutation


def plan_runtime_files(
    package: PackageLayout,
    runtime: RuntimePaths,
) -> tuple[list[Mutation], set[str]]:
    mutations: list[Mutation] = []
    owned: set[str] = set()
    excluded = {
        ".git",
        ".pytest_cache",
        "AGENTS.md",
        "agents",
        "dist",
        "project_docs",
        "templates",
        "tmp",
        ".source_backup",
        ".backups",
        USER_STATE,
    }
    for source in sorted(package.root.rglob("*")):
        relative = source.relative_to(package.root)
        if (
            relative.parts[0] in excluded
            or any(
                part in {".git", ".pytest_cache", "dist", "tmp", "__pycache__"}
                for part in relative.parts
            )
            or source.suffix == ".pyc"
            or not source.is_file()
        ):
            continue
        target = runtime.runtime / relative
        mutations.append(Mutation(target, source.read_bytes()))
        owned.add(relative.as_posix())
    template_targets = [(package.project_template, runtime.runtime / "templates" / "AGENTS.md")]
    template_targets.extend(
        (source, runtime.runtime / "templates" / "agents" / source.name)
        for source in sorted(package.agent_templates.glob("*.toml"))
    )
    template_targets.extend(
        (source, runtime.runtime / "templates" / "project_docs" / source.name)
        for source in package.project_docs.glob("*.md")
    )
    for source, target in template_targets:
        mutations.append(Mutation(target, source.read_bytes()))
        owned.add(target.relative_to(runtime.runtime).as_posix())
    mutations.extend(plan_legacy_user_agents_cleanup(runtime))
    mutations.extend(plan_platform_and_workers(runtime, package=package))
    mutations.extend(plan_workflow_skill(package, runtime))
    backup = runtime.runtime / ".source_backup" / package.version
    for source in sorted(package.root.rglob("*")):
        relative = source.relative_to(package.root)
        if (
            source.is_file()
            and not any(
                part in {".git", ".pytest_cache", "dist", "tmp", "__pycache__"}
                for part in relative.parts
            )
            and source.suffix != ".pyc"
            and ".source_backup" not in source.parts
            and ".backups" not in source.parts
        ):
            mutations.append(
                Mutation(backup / relative, source.read_bytes())
            )
    return mutations, owned


def plan_workflow_skill(package: PackageLayout, runtime: RuntimePaths) -> list[Mutation]:
    """Install the workflow-owned coordination skill in Codex's global skill root.

    An existing unmarked directory is unrelated user content and is never
    overwritten. A matching ownership marker is the only proof accepted for
    replacement during an update.
    """

    source_dir = package.root / "skills" / WORKFLOW_SKILL
    target_dir = runtime.skills / WORKFLOW_SKILL
    if runtime.skills.is_symlink() or (
        runtime.skills.exists() and not runtime.skills.is_dir()
    ):
        raise ValidationError(f"Codex skills path is not a directory: {runtime.skills}")
    if target_dir.is_symlink() or (
        target_dir.exists() and not target_dir.is_dir()
    ):
        raise ValidationError(
            f"refusing to replace non-directory workflow skill: {target_dir}"
        )
    if target_dir.is_dir():
        marker = target_dir / "SKILL.md"
        if not marker.is_file() or WORKFLOW_SKILL_OWNER not in marker.read_text(
            encoding="utf-8"
        ):
            raise ValidationError(
                f"refusing to replace unowned global skill: {target_dir}"
            )

    mutations: list[Mutation] = []
    source_files: set[Path] = set()
    for source in sorted(source_dir.rglob("*")):
        if source.is_symlink() or not source.is_file():
            continue
        relative = source.relative_to(source_dir)
        source_files.add(relative)
        mutations.append(
            Mutation(target_dir / relative, source.read_bytes())
        )
    if not mutations:
        raise ValidationError("package workflow skill has no files")
    if target_dir.is_dir():
        for target in sorted(target_dir.rglob("*")):
            if target.is_symlink():
                raise ValidationError(
                    f"refusing to replace symlink in global skill: {target}"
                )
            if target.is_file() and target.relative_to(target_dir) not in source_files:
                mutations.append(Mutation(target, None))
    return mutations


def plan_obsolete_owned_skills(
    runtime: RuntimePaths, previous_owned: set[str]
) -> tuple[list[Mutation], list[Path], list[str]]:
    """Remove obsolete workflow skills only when their ownership is proven."""

    mutations: list[Mutation] = []
    cleanup_dirs: list[Path] = []
    warnings: list[str] = []
    candidates = (previous_owned | set(OWNED_SKILL_MARKERS)) - {WORKFLOW_SKILL}
    for name in sorted(candidates):
        marker_text = OWNED_SKILL_MARKERS.get(name)
        if marker_text is None:
            warnings.append(f"unrecognized global skill will be preserved: {name}")
            continue
        skill_dir = runtime.skills / name
        if skill_dir.is_symlink() or (skill_dir.exists() and not skill_dir.is_dir()):
            warnings.append(f"unowned global skill path will be preserved: {skill_dir}")
            continue
        if not skill_dir.is_dir():
            continue
        marker = skill_dir / "SKILL.md"
        if not marker.is_file() or marker_text not in marker.read_text(encoding="utf-8"):
            warnings.append(f"unowned global skill will be preserved: {skill_dir}")
            continue
        for path in sorted(skill_dir.rglob("*")):
            if path.is_symlink():
                raise ValidationError(f"refusing to remove symlink in global skill: {path}")
            if path.is_dir():
                cleanup_dirs.append(path)
            elif path.is_file():
                mutations.append(Mutation(path, None))
        cleanup_dirs.append(skill_dir)
    return mutations, cleanup_dirs, warnings


def plan_legacy_user_agents_cleanup(runtime: RuntimePaths) -> list[Mutation]:
    """Remove only the obsolete workflow-owned global AGENTS.md region."""

    if runtime.user_agents.is_symlink() or (
        runtime.user_agents.exists() and not runtime.user_agents.is_file()
    ):
        raise ValidationError(f"user AGENTS path is not a regular file: {runtime.user_agents}")
    if not runtime.user_agents.is_file():
        return []
    current = runtime.user_agents.read_text(encoding="utf-8")
    if USER_MANAGED.start not in current and USER_MANAGED.end not in current:
        return []
    rendered = remove_region(current, USER_MANAGED)
    return [
        Mutation(
            runtime.user_agents,
            rendered.encode("utf-8") if rendered else None,
        )
    ]


def plan_platform_and_workers(
    runtime: RuntimePaths,
    *,
    package: PackageLayout | None = None,
) -> list[Mutation]:
    templates = package.agent_templates if package else runtime.runtime / "templates" / "agents"
    mutations: list[Mutation] = []
    current_state = read_json(runtime.runtime / USER_STATE, default={})
    previous_owned = set(read_string_list(current_state, "owned_workers"))
    workers = {
        path.stem for path in templates.glob("*.toml") if path.is_file()
    }
    for worker in sorted(workers):
        source = templates / f"{worker}.toml"
        target = runtime.agents / f"{worker}.toml"
        if target.exists():
            if target.is_symlink() or not target.is_file():
                raise ValidationError(f"worker path is not a regular file: {target}")
            validate_worker_owner(target, worker)
        mutations.append(
            text_mutation(
                target,
                source.read_text(encoding="utf-8"),
            )
        )
    for worker in sorted(previous_owned - workers):
        target = runtime.agents / f"{worker}.toml"
        if target.exists():
            validate_worker_owner(target, worker)
            mutations.append(Mutation(target, None))
    config_text = (
        runtime.config_toml.read_text(encoding="utf-8")
        if runtime.config_toml.is_file()
        else ""
    )
    mutations.append(
        text_mutation(runtime.config_toml, patch_codex_settings(config_text))
    )
    return mutations


def validate_worker_owner(path: Path, worker: str) -> None:
    text = path.read_text(encoding="utf-8")
    match = WORKER_MARKER.search(text)
    if match is None or match.group(1) != worker:
        raise ValidationError(f"refusing to remove non-owned worker file: {path}")


def plan_runtime_remove(
    runtime: RuntimePaths,
) -> tuple[list[Mutation], list[Path], list[str]]:
    """Plan removal of workflow-owned user-level runtime files."""

    mutations: list[Mutation] = []
    cleanup_dirs: list[Path] = []
    warnings = [
        "unrelated content in the user AGENTS.md and config.toml will be preserved",
        "unrelated worker TOMLs will be preserved",
        "unrelated global skills will be preserved",
    ]

    if runtime.skills.is_symlink() or (
        runtime.skills.exists() and not runtime.skills.is_dir()
    ):
        raise ValidationError(f"Codex skills path is not a directory: {runtime.skills}")
    for skill_name, owner_marker in OWNED_SKILL_MARKERS.items():
        skill_dir = runtime.skills / skill_name
        if skill_dir.is_dir() and not skill_dir.is_symlink():
            marker = skill_dir / "SKILL.md"
            if marker.is_file() and owner_marker in marker.read_text(encoding="utf-8"):
                for path in sorted(skill_dir.rglob("*")):
                    if path.is_symlink():
                        raise ValidationError(
                            f"refusing to remove symlink in global skill: {path}"
                        )
                    if path.is_dir():
                        cleanup_dirs.append(path)
                    elif path.is_file():
                        mutations.append(Mutation(path, None))
                cleanup_dirs.append(skill_dir)
            else:
                warnings.append(f"unowned global skill will be preserved: {skill_dir}")
        elif skill_dir.exists():
            warnings.append(f"unowned global skill path will be preserved: {skill_dir}")

    if runtime.user_agents.is_symlink() or (
        runtime.user_agents.exists() and not runtime.user_agents.is_file()
    ):
        raise ValidationError(f"user AGENTS path is not a regular file: {runtime.user_agents}")
    if runtime.user_agents.is_file():
        current = runtime.user_agents.read_text(encoding="utf-8")
        if USER_MANAGED.start in current or USER_MANAGED.end in current:
            rendered = remove_region(current, USER_MANAGED)
            mutations.append(
                Mutation(
                    runtime.user_agents,
                    rendered.encode("utf-8") if rendered else None,
                )
            )

    if runtime.config_toml.is_symlink() or (
        runtime.config_toml.exists() and not runtime.config_toml.is_file()
    ):
        raise ValidationError(f"Codex config path is not a regular file: {runtime.config_toml}")
    if runtime.config_toml.is_file():
        current = runtime.config_toml.read_text(encoding="utf-8")
        rendered = remove_workflow_owned_settings(current)
        if rendered != current:
            mutations.append(
                Mutation(
                    runtime.config_toml,
                    rendered.encode("utf-8") if rendered else None,
                )
            )

    if runtime.agents.is_symlink() or (
        runtime.agents.exists() and not runtime.agents.is_dir()
    ):
        raise ValidationError(f"worker directory is not a directory: {runtime.agents}")
    if runtime.agents.is_dir():
        for target in sorted(runtime.agents.glob("*.toml")):
            if target.is_symlink() or not target.is_file():
                raise ValidationError(f"worker path is not a regular file: {target}")
            match = WORKER_MARKER.search(target.read_text(encoding="utf-8"))
            if match is None:
                continue
            if match.group(1) != target.stem:
                raise ValidationError(
                    f"worker ownership marker does not match file name: {target}"
                )
            mutations.append(Mutation(target, None))
        cleanup_dirs.append(runtime.agents)

    if runtime.runtime.is_symlink() or (
        runtime.runtime.exists() and not runtime.runtime.is_dir()
    ):
        raise ValidationError(f"workflow runtime path is not a directory: {runtime.runtime}")
    if runtime.runtime.is_dir():
        for path in sorted(runtime.runtime.rglob("*")):
            if path.is_symlink():
                raise ValidationError(f"refusing to remove symlink in workflow runtime: {path}")
            if path.is_dir():
                cleanup_dirs.append(path)
            elif path.is_file():
                mutations.append(Mutation(path, None))
            elif path.exists():
                raise ValidationError(f"workflow runtime contains a non-file entry: {path}")
        cleanup_dirs.append(runtime.runtime)
        warnings.append(
            f"all files under {runtime.runtime} (including source and update backups) will be permanently deleted"
        )

    return mutations, cleanup_dirs, warnings

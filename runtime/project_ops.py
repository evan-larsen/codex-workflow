"""Project entry-point, personalization, and documentation operations."""

from __future__ import annotations

from pathlib import Path

from . import ENTRY_FORMAT_VERSION, RUNTIME_SCHEMA_VERSION
from .errors import ValidationError
from .layout import (
    LEGACY_PROJECT_IDS,
    PROJECT_ID,
    PackageLayout,
    ProjectPaths,
    is_project_owned,
)
from .markers import (
    PROJECT_LOCAL,
    PROJECT_PERSONALIZATION,
    WORKFLOW_MANAGED,
    extract,
    render_project_entry,
    replace,
)
from .personalization import materialize_personalization
from .plan import OperationPlan, json_mutation, read_json, text_mutation
from .transaction import Mutation


GITIGNORE_ENTRIES = (
    "agent_docs/",
    ".codex_workflow_hidden_resources/",
    "AGENTS.md",
)
GITIGNORE_MANAGED_START = "# codex-workflow-managed-start"
GITIGNORE_MANAGED_END = "# codex-workflow-managed-end"


def _gitignore_block(entries: tuple[str, ...] = GITIGNORE_ENTRIES) -> str:
    return "\n".join((GITIGNORE_MANAGED_START, *entries, GITIGNORE_MANAGED_END))


def _gitignore_managed_range(lines: list[str]) -> tuple[int, int] | None:
    starts = [index for index, line in enumerate(lines) if line == GITIGNORE_MANAGED_START]
    ends = [index for index, line in enumerate(lines) if line == GITIGNORE_MANAGED_END]
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValidationError("project .gitignore has malformed workflow-managed markers")
    return starts[0], ends[0]


def _append_gitignore_block(current: str, entries: tuple[str, ...]) -> str:
    prefix = current.rstrip("\r\n")
    if prefix:
        prefix += "\n\n"
    return prefix + _gitignore_block(entries) + "\n"


def _remove_unmarked_gitignore_entries(current: str) -> str:
    retained = [
        line
        for line in current.splitlines()
        if not (line.strip() in GITIGNORE_ENTRIES and not line.lstrip().startswith("#"))
    ]
    rendered = "\n".join(retained).rstrip()
    return f"{rendered}\n" if rendered else ""


def _plan_gitignore(project: ProjectPaths) -> Mutation | None:
    """Add a removable, workflow-owned block to ``.gitignore``."""

    path = project.gitignore
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValidationError(
            f"project .gitignore path is not a regular file: {path}"
        )

    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = current.splitlines()
    managed_range = _gitignore_managed_range(lines)
    if managed_range is not None:
        start, end = managed_range
        managed_entries = lines[start + 1 : end]
        if (
            any(entry not in GITIGNORE_ENTRIES for entry in managed_entries)
            or len(managed_entries) != len(set(managed_entries))
        ):
            raise ValidationError("project .gitignore has invalid workflow-managed rules")
        existing = {
            line.strip()
            for line in lines
            if line.strip() and not line.lstrip().startswith("#")
        }
        missing = [entry for entry in GITIGNORE_ENTRIES if entry not in existing]
        if not missing:
            return None
        rendered_lines = lines[:end] + missing + lines[end:]
        rendered = "\n".join(rendered_lines).rstrip() + "\n"
        return text_mutation(path, rendered)

    existing = {
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }
    # Legacy releases wrote all three entries without markers. A recognized
    # workflow project containing that complete set can safely adopt it into a
    # removable block during its next install/update operation.
    if set(GITIGNORE_ENTRIES).issubset(existing):
        return text_mutation(
            path,
            _append_gitignore_block(
                _remove_unmarked_gitignore_entries(current), GITIGNORE_ENTRIES
            ),
        )
    missing = [entry for entry in GITIGNORE_ENTRIES if entry not in existing]
    if not missing:
        return None
    return text_mutation(path, _append_gitignore_block(current, tuple(missing)))


def _plan_gitignore_remove(project: ProjectPaths) -> Mutation | None:
    """Remove only the ignore rules that this workflow can prove it owns."""

    path = project.gitignore
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValidationError(f"project .gitignore path is not a regular file: {path}")
    if not path.is_file():
        return None
    current = path.read_text(encoding="utf-8")
    lines = current.splitlines()
    managed_range = _gitignore_managed_range(lines)
    if managed_range is not None:
        start, end = managed_range
        retained = lines[:start] + lines[end + 1 :]
        rendered = "\n".join(retained).rstrip()
        rendered = f"{rendered}\n" if rendered else ""
        return text_mutation(path, rendered)
    existing = {
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }
    if set(GITIGNORE_ENTRIES).issubset(existing):
        return text_mutation(path, _remove_unmarked_gitignore_entries(current))
    return None


def _plan_source_cleanup(project: ProjectPaths) -> tuple[list[Mutation], list[Path]]:
    """Delete the extracted project-level ``Codex_Workflow`` staging tree."""

    source = project.source_dir
    if source.is_symlink():
        raise ValidationError(
            f"refusing to remove symlinked package staging directory: {source}"
        )
    if not source.exists():
        return [], []
    if not source.is_dir():
        raise ValidationError(f"project package staging path is not a directory: {source}")

    mutations: list[Mutation] = []
    cleanup_dirs: list[Path] = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValidationError(
                f"refusing to remove symlink in package staging directory: {path}"
            )
        if path.is_dir():
            cleanup_dirs.append(path)
        elif path.is_file():
            mutations.append(Mutation(path, None))
        elif path.exists():
            raise ValidationError(
                f"package staging directory contains a non-file entry: {path}"
            )
    cleanup_dirs.append(source)
    return mutations, cleanup_dirs


def plan_project_install(package: PackageLayout, project: ProjectPaths) -> OperationPlan:
    active_exists = project.active.exists()
    disabled_exists = project.disabled.exists()
    if active_exists and disabled_exists:
        raise ValidationError("both active and disabled project entry points exist")
    template = package.project_template.read_text(encoding="utf-8")
    personalization = (
        project.personalization.read_text(encoding="utf-8")
        if project.personalization.is_file()
        else package.default_personalization.read_text(encoding="utf-8")
    )
    direct_personalization = materialize_personalization(personalization)
    mutations: list[Mutation] = []
    warnings: list[str] = []
    entry_path = project.disabled if disabled_exists else project.active
    enabled = not disabled_exists
    if active_exists or disabled_exists:
        current = entry_path.read_text(encoding="utf-8")
        if is_project_owned(current):
            if WORKFLOW_MANAGED.start not in current or PROJECT_LOCAL.start not in current:
                raise ValidationError(
                    "legacy workflow entry point requires update migration before installation"
                )
            extract(current, WORKFLOW_MANAGED)
            current_personalization = extract(current, PROJECT_PERSONALIZATION)
            extract(current, PROJECT_LOCAL)
            if not project.personalization.is_file() and current_personalization:
                raise ValidationError(
                    "personalization resource is missing but the generated region is not empty"
                )
            if current_personalization != direct_personalization:
                raise ValidationError(
                    "project personalization resource and generated entry point disagree; "
                    "invoke $codex-workflow personalize or $codex-workflow update"
                )
            if extract(current, WORKFLOW_MANAGED) != extract(template, WORKFLOW_MANAGED):
                raise ValidationError(
                    "recognized project entry point uses an older or modified workflow template; "
                    "invoke $codex-workflow update"
                )
        else:
            if disabled_exists:
                raise ValidationError("unrecognized disabled entry point cannot be imported")
            reject_reserved_markers(current)
            rendered = render_project_entry(
                template,
                personalization=direct_personalization,
                local_instructions=current,
            )
            mutations.append(text_mutation(entry_path, rendered))
            warnings.append("existing AGENTS.md will be preserved in the project-local region")
    else:
        rendered = render_project_entry(template, personalization=direct_personalization)
        mutations.append(text_mutation(project.active, rendered))
    if not project.personalization.is_file():
        mutations.append(text_mutation(project.personalization, personalization))
    # Installation does not opt the user into session memory. Preserve existing
    # documents and leave missing/template documents untouched. Agents create
    # only the requested memory files after explicit conversational opt-in.
    project_state = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "entry_format_version": ENTRY_FORMAT_VERSION,
        "workflow_version": package.version,
        "enabled": enabled,
    }
    mutations.append(json_mutation(project.state, project_state))
    gitignore_mutation = _plan_gitignore(project)
    if gitignore_mutation is not None:
        mutations.append(gitignore_mutation)
    cleanup_mutations, cleanup_dirs = _plan_source_cleanup(project)
    mutations.extend(cleanup_mutations)
    if cleanup_mutations:
        warnings.append(f"{project.source_dir} will be deleted after installation")
    return OperationPlan(
        "project-install",
        mutations,
        warnings,
        [],
        cleanup_dirs=cleanup_dirs,
    )


def plan_personalize(project: ProjectPaths, resource_text: str) -> OperationPlan:
    entry = recognized_entry(project)
    current = entry.read_text(encoding="utf-8")
    if WORKFLOW_MANAGED.start not in current or PROJECT_LOCAL.start not in current:
        raise ValidationError("project entry point uses the legacy marker format")
    rendered = replace(
        current,
        PROJECT_PERSONALIZATION,
        materialize_personalization(resource_text),
    )
    return OperationPlan(
        "personalize",
        [
            text_mutation(project.personalization, resource_text),
            text_mutation(entry, rendered),
        ],
        [],
        [],
    )


def plan_enable(project: ProjectPaths, *, enable: bool) -> OperationPlan:
    source = project.disabled if enable else project.active
    target = project.active if enable else project.disabled
    operation = "enable" if enable else "disable"
    if target.is_file() and not source.exists():
        text = target.read_text(encoding="utf-8")
        if not is_project_owned(text):
            raise ValidationError(f"existing {target} is not workflow-owned")
        return OperationPlan(operation, [], [f"project is already {operation}d"], [])
    if not source.is_file() or target.exists():
        raise ValidationError("project entry-point state is missing or conflicted")
    content = source.read_bytes()
    if not is_project_owned(content.decode("utf-8")):
        raise ValidationError("source project entry point is not workflow-owned")
    state = read_json(project.state, default={})
    state.setdefault("schema_version", RUNTIME_SCHEMA_VERSION)
    state.setdefault("entry_format_version", ENTRY_FORMAT_VERSION)
    state["enabled"] = enable
    return OperationPlan(
        operation,
        [Mutation(target, content), Mutation(source, None), json_mutation(project.state, state)],
        [],
        [],
    )


def plan_project_update(
    installed: PackageLayout,
    incoming: PackageLayout,
    project: ProjectPaths,
    *,
    legacy_local_instructions: str | None,
) -> tuple[list[Mutation], list[str]]:
    warnings: list[str] = []
    active_exists = project.active.exists()
    disabled_exists = project.disabled.exists()
    if active_exists and disabled_exists:
        raise ValidationError("both active and disabled project entry points exist")
    if not active_exists and not disabled_exists:
        return [], ["current project has no workflow entry point; user-level update only"]
    entry = project.disabled if disabled_exists else project.active
    current = entry.read_text(encoding="utf-8")
    if not is_project_owned(current):
        raise ValidationError("current project AGENTS.md is not workflow-owned")
    personalization_resource = (
        project.personalization.read_text(encoding="utf-8")
        if project.personalization.is_file()
        else incoming.default_personalization.read_text(encoding="utf-8")
    )
    direct = materialize_personalization(personalization_resource)
    if (
        WORKFLOW_MANAGED.start in current
        and PROJECT_PERSONALIZATION.start in current
        and PROJECT_LOCAL.start in current
    ):
        installed_template = installed.project_template.read_text(encoding="utf-8")
        if extract(current, WORKFLOW_MANAGED) != extract(
            installed_template, WORKFLOW_MANAGED
        ):
            raise ValidationError(
                "workflow-managed project region has local drift; move project rules to the local region"
            )
        if not project.personalization.is_file() and extract(
            current, PROJECT_PERSONALIZATION
        ):
            raise ValidationError(
                "personalization resource is missing but the generated region is not empty"
            )
        local = extract(current, PROJECT_LOCAL)
        trailing = current.split(PROJECT_LOCAL.end, 1)[1].strip()
        if trailing:
            reject_reserved_markers(trailing)
            local = "\n\n".join(part for part in (local.rstrip(), trailing) if part)
            warnings.append(
                "content after the project-local marker was migrated into the "
                "protected project-local region"
            )
    else:
        old_template = installed.project_template.read_text(encoding="utf-8")
        current_without_personalization = _without_optional_personalization(current)
        old_without_personalization = _without_optional_personalization(old_template)
        if current_without_personalization != old_without_personalization:
            if legacy_local_instructions is None:
                raise ValidationError(
                    "legacy project entry contains local edits; pass reviewed local instructions explicitly"
                )
            reject_reserved_markers(legacy_local_instructions)
            local = legacy_local_instructions
        else:
            local = legacy_local_instructions or ""
    rendered = render_project_entry(
        incoming.project_template.read_text(encoding="utf-8"),
        personalization=direct,
        local_instructions=local,
    )
    mutations = [text_mutation(entry, rendered)]
    if not project.personalization.is_file():
        mutations.append(text_mutation(project.personalization, personalization_resource))
    state = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "entry_format_version": ENTRY_FORMAT_VERSION,
        "workflow_version": incoming.version,
        "enabled": not disabled_exists,
    }
    mutations.append(json_mutation(project.state, state))
    gitignore_mutation = _plan_gitignore(project)
    if gitignore_mutation is not None:
        mutations.append(gitignore_mutation)
    return mutations, warnings


def plan_project_remove(
    project: ProjectPaths,
) -> tuple[list[Mutation], list[Path], list[str]]:
    """Plan removal of the workflow-owned project surface."""

    if project.active.is_symlink() or project.disabled.is_symlink():
        raise ValidationError("refusing to remove a symlinked project entry point")
    active_exists = project.active.exists()
    disabled_exists = project.disabled.exists()
    if active_exists and disabled_exists:
        raise ValidationError("both active and disabled project entry points exist")
    for entry in (project.active, project.disabled):
        if entry.exists() and not entry.is_file():
            raise ValidationError(f"project entry point is not a regular file: {entry}")

    mutations: list[Mutation] = []
    warnings = [
        "project agent_docs/ files are project documentation and will be preserved",
    ]
    entry = project.active if active_exists else project.disabled if disabled_exists else None
    if entry is not None:
        current = entry.read_text(encoding="utf-8")
        if not is_project_owned(current):
            raise ValidationError(f"refusing to remove unrecognized project entry point: {entry}")
        if PROJECT_LOCAL.start not in current or PROJECT_LOCAL.end not in current:
            raise ValidationError(
                "refusing to remove workflow entry without recoverable project-local instructions"
            )
        local_instructions = extract(current, PROJECT_LOCAL)
        if local_instructions:
            mutations.append(text_mutation(project.active, local_instructions.rstrip() + "\n"))
            warnings.append(
                f"workflow wrapper will be removed and project-local instructions restored to {project.active}"
            )
        else:
            mutations.append(Mutation(entry, None))
            warnings.append(f"{entry} will be permanently deleted because it has no project-local instructions")

    gitignore_mutation = _plan_gitignore_remove(project)
    if gitignore_mutation is not None:
        mutations.append(gitignore_mutation)
        warnings.append("workflow-owned .gitignore rules will be removed")

    hidden_dir = project.workflow_dir
    if hidden_dir.is_symlink() or (
        hidden_dir.exists() and not hidden_dir.is_dir()
    ):
        raise ValidationError(f"project hidden resource is not a directory: {hidden_dir}")

    for path in (project.personalization, project.state):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValidationError(f"project workflow resource is not a regular file: {path}")
        if path.is_file():
            mutations.append(Mutation(path, None))

    cleanup_dirs: list[Path] = []
    if hidden_dir.is_dir():
        for path in sorted(hidden_dir.rglob("*")):
            if path.is_symlink():
                raise ValidationError(f"refusing to remove symlink in project resource: {path}")
            if path.is_dir():
                cleanup_dirs.append(path)
            elif path.exists() and not path.is_file():
                raise ValidationError(f"project resource contains a non-file entry: {path}")
        cleanup_dirs.append(hidden_dir)

    return mutations, cleanup_dirs, warnings


def recognized_entry(project: ProjectPaths) -> Path:
    if project.active.exists() and project.disabled.exists():
        raise ValidationError("both active and disabled project entry points exist")
    path = project.active if project.active.is_file() else project.disabled
    if not path.is_file() or not is_project_owned(path.read_text(encoding="utf-8")):
        raise ValidationError("no recognized workflow project entry point")
    return path


def reject_reserved_markers(text: str) -> None:
    reserved = [
        WORKFLOW_MANAGED.start,
        WORKFLOW_MANAGED.end,
        PROJECT_PERSONALIZATION.start,
        PROJECT_PERSONALIZATION.end,
        PROJECT_LOCAL.start,
        PROJECT_LOCAL.end,
    ]
    collisions = [marker for marker in reserved if marker in text]
    if collisions:
        raise ValidationError(f"existing AGENTS.md contains reserved markers: {collisions}")


def _without_optional_personalization(text: str) -> str:
    """Remove a complete legacy personalization region, allowing old entries without it."""

    has_start = PROJECT_PERSONALIZATION.start in text
    has_end = PROJECT_PERSONALIZATION.end in text
    if has_start != has_end:
        raise ValidationError("legacy project entry has incomplete personalization markers")
    normalized = text if not has_start else replace(text, PROJECT_PERSONALIZATION, "")
    for legacy_id in LEGACY_PROJECT_IDS:
        normalized = normalized.replace(legacy_id, PROJECT_ID)
    return normalized

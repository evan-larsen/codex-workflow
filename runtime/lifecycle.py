"""Composition layer for user-level and project lifecycle plans."""

from __future__ import annotations

from datetime import datetime, timezone
from . import RUNTIME_SCHEMA_VERSION
from .backup import append_backup_mutations
from .layout import WORKFLOW_SKILLS, USER_STATE, PackageLayout, ProjectPaths, RuntimePaths
from .plan import (
    OperationPlan,
    deduplicate,
    json_mutation,
    read_json,
    read_string_list,
    resolve_owned_runtime_path,
)
from .project_ops import plan_project_remove
from .runtime_ops import (
    plan_obsolete_owned_skills,
    plan_runtime_files,
    plan_runtime_remove,
)
from .transaction import Mutation


def plan_bootstrap(
    package: PackageLayout, runtime: RuntimePaths, project: ProjectPaths
) -> OperationPlan:
    mutations, owned_runtime = plan_runtime_files(package, runtime)
    state = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "version": package.version,
        "owned_runtime_files": sorted(owned_runtime),
        "owned_workers": sorted(package.worker_names),
        "owned_skills": sorted(WORKFLOW_SKILLS),
    }
    mutations.append(json_mutation(runtime.runtime / USER_STATE, state))
    return OperationPlan(
        "bootstrap",
        deduplicate(mutations),
        [],
        [],
        {"version": package.version},
    )


def plan_remove(
    runtime: RuntimePaths,
    project: ProjectPaths,
) -> OperationPlan:
    runtime_mutations, runtime_dirs, runtime_warnings = plan_runtime_remove(runtime)
    project_mutations, project_dirs, project_warnings = plan_project_remove(project)
    return OperationPlan(
        "remove",
        deduplicate(runtime_mutations + project_mutations),
        runtime_warnings + project_warnings,
        [],
        {
            "confirmation_required": True,
            "preserves": [
                "project agent_docs/ files",
                "unrelated user AGENTS.md content",
                "unrelated Codex config.toml keys",
                "unrelated worker TOMLs",
                "unrelated global skills",
            ],
        },
        cleanup_dirs=runtime_dirs + project_dirs,
    )


def plan_update(
    incoming: PackageLayout,
    runtime: RuntimePaths,
    project: ProjectPaths | None = None,
    *,
    legacy_local_instructions: str | None = None,
) -> OperationPlan:
    installed = PackageLayout.resolve(runtime.runtime, allow_legacy=True)
    previous_state = read_json(runtime.runtime / USER_STATE, default={})
    backup_root = (
        runtime.runtime
        / ".backups"
        / f"{installed.version}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    )
    mutations: list[Mutation] = []
    append_backup_mutations(mutations, backup_root, runtime, project)
    runtime_mutations, owned_runtime = plan_runtime_files(incoming, runtime)
    mutations.extend(runtime_mutations)
    obsolete_skill_mutations, obsolete_skill_dirs, skill_warnings = (
        plan_obsolete_owned_skills(
            runtime, set(read_string_list(previous_state, "owned_skills"))
        )
    )
    mutations.extend(obsolete_skill_mutations)
    warnings: list[str] = []
    warnings.extend(skill_warnings)
    incoming_targets = {
        mutation.path.resolve(strict=False) for mutation in runtime_mutations
    }
    obsolete_runtime_dirs = []
    for relative in read_string_list(previous_state, "owned_runtime_files"):
        obsolete = resolve_owned_runtime_path(runtime.runtime, relative)
        if obsolete not in incoming_targets and obsolete.exists():
            mutations.append(Mutation(obsolete, None))
            parent = obsolete.parent
            runtime_root = runtime.runtime.resolve()
            while parent != runtime_root:
                obsolete_runtime_dirs.append(parent)
                parent = parent.parent
    # The legacy configuration was workflow-owned, even for installations
    # whose older ownership manifest predates its entry.  Retire it after the
    # preference has been migrated so it cannot become a second source of
    # truth.
    legacy_config = runtime.runtime / "workflow_config.json"
    if (
        legacy_config.is_file()
        and legacy_config.resolve(strict=False) not in incoming_targets
    ):
        mutations.append(Mutation(legacy_config, None))
    state = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "version": incoming.version,
        "owned_runtime_files": sorted(owned_runtime),
        "owned_workers": sorted(incoming.worker_names),
        "owned_skills": sorted(WORKFLOW_SKILLS),
    }
    mutations.append(json_mutation(runtime.runtime / USER_STATE, state))
    return OperationPlan(
        "update",
        deduplicate(mutations),
        warnings,
        [],
        {
            "from_version": installed.version,
            "to_version": incoming.version,
            "backup": str(backup_root),
        },
        cleanup_dirs=obsolete_skill_dirs + obsolete_runtime_dirs,
    )

---
name: codex-workflow-maintainer
description: Maintain, release, install, update, or diagnose the codex_workflow package and its published runtime; do not use for ordinary project workflow tasks.
metadata:
  short-description: Maintain the codex_workflow release and runtime
---

<!-- codex-workflow-maintainer-owner: codex_workflow -->

# codex_workflow maintainer

Use this skill only when the request explicitly concerns maintaining, releasing,
installing, updating, or diagnosing codex_workflow itself. It does not govern
ordinary use of codex_workflow in a project.

## Source and installed runtime

- The canonical source is the public repository
  `evan-larsen/codex-workflow`; inspect and change that repository when fixing
  the workflow.
- The installed runtime is `~/.codex/codex_workflow` (or `CODEX_HOME`); it is a
  release-derived copy, not canonical source. The installed maintainer skill is
  `~/.codex/skills/codex-workflow-maintainer/SKILL.md`.
- A source edit is not authorization to commit, push, publish a release, update
  the shared runtime, migrate a project, or change unrelated Codex settings.
  Obtain explicit authorization for each external or shared-state mutation.

## Maintenance contract

- Preserve project-local `AGENTS.md`, personalization, state, documents, and
  unrelated user settings. Do not use this skill to silently migrate projects.
- Validate the package and run focused tests for the changed lifecycle seam.
  For install/update/remove work, include isolated temporary-runtime tests for
  fresh installation, replacement, collision refusal, and removal semantics as
  applicable. Keep source and runtime tests separate.
- Treat an unmarked existing global skill directory as unrelated: refuse to
  overwrite or remove it. Only the workflow-owned maintainer skill may be
  replaced during an authorized workflow update and removed during an explicit
  confirmed workflow removal.
- After a global runtime update, tell the user to refresh or restart Codex so
  skill discovery loads the new installed instructions.

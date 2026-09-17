# Workflow Update

Supported skill invocation:

    $codex-workflow update

Codex 0.147.0 or newer and Python 3.11 or newer are required. Before downloading
or mutating anything, run:

```text
python3 ~/.codex/codex_workflow/workflow.py check-compatibility --json
```

Stop unless it reports `"compatible": true`. The lifecycle CLI then applies a
validated update directly.

## Source

The script queries GitHub Releases, selects the highest
non-draft SemVer release containing both the universal ZIP and `SHA256SUMS`,
verifies the checksum, and extracts it safely. It includes prereleases and
never clones the repository. The installed launcher delegates planning and
application to the incoming CLI, which owns validation for its package schema.

## Update

Run:

```text
python3 ~/.codex/codex_workflow/workflow.py update --project <project>
```

For migration from a pre-script installation, run the incoming package's
`workflow.py` instead of an older installed launcher.

The script replaces the installed workflow skill and worker TOMLs with the
incoming release's fixed definitions. It preserves unrelated Codex settings,
source backups, and every project file. The retained `--project` and
`--legacy-local-instructions` arguments are compatibility inputs only; update
does not create, wrap, rewrite, enable, disable, or personalize project
`AGENTS.md`. It removes obsolete workflow-owned runtime files, creates a
verified timestamped runtime backup, and applies user-level state as one
compensating transaction. A downgrade additionally requires
`--allow-downgrade`.

Report the installed version, preserved preferences, backup location, and any failure.
Do not describe a partial or rolled-back update as successful.

An update replaces the workflow-owned global skill at
`~/.codex/skills/codex-workflow/`. An unmarked skill at that path is unrelated
and blocks the update. An owned legacy `codex-workflow-maintainer` skill is
removed during migration; an unmarked legacy directory is preserved. Refresh
or restart Codex after the update so the new skill is discovered.

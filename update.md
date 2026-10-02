# Workflow Update

Supported skill invocation:

    $codex-workflow-sol update

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

The script replaces the installed workflow skills and worker TOMLs with the
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

An update installs exactly three workflow-owned global skills:
`~/.codex/skills/codex-workflow-sol/`,
`~/.codex/skills/codex-workflow-luna/`, and
`~/.codex/skills/codex-workflow-watch-repair/`. An unmarked skill at any target blocks
the update before mutation. Marked legacy `codex-workflow`,
`codex-workflow-heavy`, and `codex-workflow-maintainer` skills are removed;
unmarked legacy directories are preserved. Marked obsolete `heavy_coordinator`
and `senior_executor` workers are retired, preserving unowned role names.
Old package layouts and schema-1 installation manifests remain migration inputs.
Refresh or restart Codex after updating so skill and role discovery reloads.

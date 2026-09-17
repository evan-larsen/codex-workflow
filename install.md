# Workflow Installation

Use this procedure only to install the already-bootstrapped workflow into the
current project. Do not manually copy or merge workflow files, and do not
modify or reinstall anything under `~/.codex/`.

Codex 0.147.0 or newer and Python 3.11 or newer are required. On Windows, use
the equivalent `py -3.11` invocation and native paths. Before any mutation,
run and require `"compatible": true`:

```text
python3 ~/.codex/codex_workflow/workflow.py check-compatibility --json
```

## Existing project installation

The CLI validates the current project's active `AGENTS.md` and disabled
`.codex_workflow_hidden_resources/.AGENTS.md` entry points before reporting an
existing installation. Missing or template-marked session-memory documents do
not trigger recovery, workers, or installation failure. A valid active entry is
reported as `already enabled` and needs no action. A valid hidden entry is
reported as `already disabled`; then tell the user to run:

```text
codex_workflow --enable
```

If both entry points exist, or a recognized entry is stale, malformed, or
disagrees with its personalization resource, stop and report the CLI's recovery
instruction. Do not misreport those states as an ordinary disabled installation.

## Install the current project

Use the installed CLI:

```text
python3 ~/.codex/codex_workflow/workflow.py install \
  --project <project>
```

The command reads templates from the existing user-level bootstrap but changes
only the current project. It creates the project `AGENTS.md`, the hidden
personalization and state files, and other project-level assets. It imports an existing unrecognized
project `AGENTS.md` verbatim into the project-local marker region and adds a
marked workflow-owned block to `.gitignore` without changing unrelated rules.

It does not rewrite the shared user-level runtime, fixed definitions, user
instructions, source backup, or worker TOMLs under `~/.codex/`. Stop and report
the error if the initial user-level bootstrap is missing.

## Session memory is opt-in

Installation does not create or populate `agent_docs/`, recover template files,
or launch a documentation worker. Existing documents are preserved. Missing
session-memory documents do not make installation incomplete. After successful
installation, report completion directly.

If the user explicitly asks to enable session memory, agree on a small document
scope and initialize only those files from verified facts. Do not initialize a
whole framework by default. Necessary product documentation is separate.

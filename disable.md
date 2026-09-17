# Disable the Project Workflow

Run the installed lifecycle CLI from the project directory:

```text
python3 ~/.codex/codex_workflow/workflow.py disable --project <project> --json
```

It atomically moves the recognized `AGENTS.md` to the hidden entry point,
updates project state, and preserves its exact contents. An already disabled
project is a safe no-op; conflicted or unrecognized entry points are a hard
error.

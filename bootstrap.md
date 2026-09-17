# Initial Workflow Bootstrap

Use this guide only for the first installation from a universal GitHub Release
ZIP. Codex 0.147.0 or newer and Python 3.11 or newer are required. On Windows,
use the equivalent `py -3.11` invocation and native paths.

Verify `codex_workflow-<version>.zip` against `SHA256SUMS`, extract it into a
temporary directory, and require exactly one top-level `codex_workflow/`
directory. Verify Codex compatibility before any mutation:

```text
python3 codex_workflow/workflow.py check-compatibility --json
```

Stop if that command does not report `"compatible": true`; Codex 0.147.0 is
the tested minimum release for this workflow's role-specific subagents. Then
validate the package:

```text
python3 codex_workflow/workflow.py validate --package-root codex_workflow --json
```

Stop on any validation error. Run:

```text
python3 <extracted>/codex_workflow/workflow.py bootstrap \
  --package-root <extracted>/codex_workflow \
  --project <project>
```

The bootstrap installs the shared runtime, global `$codex-workflow` skill,
source backup, installation state, distributed worker TOMLs, and workflow-owned
Codex settings in one compensating transaction. The retained `--project`
argument is compatibility metadata only; bootstrap does not create or modify a
project `AGENTS.md`, personalization, project state, or project documentation.

## Session memory is opt-in

Installation does not create or populate `agent_docs/` or recover template
files. Existing project files are preserved. After successful installation,
report completion directly and restart Codex.

If the user explicitly asks to enable session memory, agree on a small document
scope and initialize only those files from verified facts. Do not initialize a
whole framework by default. Necessary product documentation is separate.

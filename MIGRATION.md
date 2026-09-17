# v1 to v2 migration

The v2 runtime accepts the v1 project marker (`viettran-edgeAI/codex_workflow`)
only to make an explicit one-time update safe. It never emits that marker.

1. Build or obtain a verified v2 package and run `check-compatibility` and
   `validate` before changing a project.
2. If the old project entry contains only the recognized managed template,
   run `workflow.py update --source <package> --project <project>`.
3. If it contains local instructions merged into the old entry, extract and
   review only those instructions into a temporary text file, then pass
   `--legacy-local-instructions <file>` to the same update command.

The reviewed text is rejected if it contains reserved workflow markers. The
result uses the canonical v2 marker and protected project-local region. A
failed validation makes no live mutation.

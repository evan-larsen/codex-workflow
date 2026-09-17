# codex_workflow

Portable, deterministic lifecycle tooling for installing a generic Codex
workflow into a user runtime. The CLI slug is `codex_workflow` and
the canonical package version is `2.0.6`.

The package owns only its runtime directory, marked worker files, global skill,
and workflow settings. Existing unowned role files and project files are never
overwritten. Legacy project-wrapper support remains only so removal can restore
previously captured project instructions safely.

This public repository is maintained at
[`evan-larsen/codex-workflow`](https://github.com/evan-larsen/codex-workflow).

## Support status and prerequisites

The initial public release has been verified in an isolated Windows
PowerShell setup. macOS and Linux packaging and bootstrap paths are present,
but have not yet been independently verified; treat those platforms as
experimental until tested.

For the supported Windows path, install Codex 0.147.0 or newer and Python
3.11 or newer. PowerShell 5.1+ (or PowerShell 7+) and permission to write the
selected Codex home and project are also required. The bootstrap checks the
Codex version and validates the package before making any changes.

## Download, review, and bootstrap on Windows

Download the release archive and its checksum as separate files, inspect the
checksum and archive contents, verify the SHA-256 value, and only then run the
bootstrap script. This deliberately avoids executing a blind network pipe.

Run the following from the project you want to configure, changing `$Version`
if you are installing another published release:

```powershell
$Version = '2.0.6'
$BaseUrl = "https://github.com/evan-larsen/codex-workflow/releases/download/v$Version"
$Download = Join-Path $env:TEMP "codex-workflow-$Version"
New-Item -ItemType Directory -Force -Path $Download | Out-Null

Invoke-WebRequest "$BaseUrl/codex_workflow-$Version.zip" -OutFile (Join-Path $Download "codex_workflow-$Version.zip")
Invoke-WebRequest "$BaseUrl/SHA256SUMS" -OutFile (Join-Path $Download 'SHA256SUMS')

# Review the downloaded checksum and archive listing before continuing.
Get-Content (Join-Path $Download 'SHA256SUMS')
Expand-Archive -LiteralPath (Join-Path $Download "codex_workflow-$Version.zip") `
  -DestinationPath (Join-Path $Download 'review') -Force
Get-ChildItem (Join-Path $Download 'review/codex_workflow') -Recurse -File |
  Select-Object -ExpandProperty FullName

$Archive = Join-Path $Download "codex_workflow-$Version.zip"
$Expected = ((Get-Content (Join-Path $Download 'SHA256SUMS') |
  Where-Object { $_ -match [regex]::Escape((Split-Path $Archive -Leaf)) } |
  Select-Object -First 1) -split '\s+')[0].ToLowerInvariant()
$Actual = (Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Expected -ne $Actual) { throw 'SHA-256 checksum mismatch; do not run the bootstrap.' }

$Bootstrap = Join-Path $Download 'review/codex_workflow/scripts/bootstrap.ps1'
& $Bootstrap -Archive $Archive -Project (Get-Location).Path
```

The bootstrap script repeats checksum and package validation immediately before
installation. It writes workflow-owned files only under the selected Codex
home; the bootstrap's project argument is retained for command compatibility
but does not modify the project. Keep the downloaded files until installation
has completed successfully.

After the initial bootstrap, invoke the global skill for lifecycle operations
documented in
[`update.md`](update.md),
[`check_update.md`](check_update.md), and [`remove.md`](remove.md):

```text
$codex-workflow check for updates
$codex-workflow update
$codex-workflow remove
```

Removal is destructive and requires its separate confirmation phase. Read
[`remove.md`](remove.md) before using it.

## One explicit adaptive workflow

Normal chats keep normal single-agent behavior. Invoke `$codex-workflow` when
you want coordinated execution; there are no Light, Medium, or Heavy modes to
choose between. The coordinator selects the smallest useful shape for the
outcome: direct work for known micro-seams, one Luna High Fast executor for a
bounded implementation, parallel executors for disjoint ownership, or one Luna
xhigh Fast senior executor for a genuinely hard reasoning slice.
One read-only Luna xhigh Fast researcher is available for an explicitly
requested research assignment or an unusually large external-evidence package;
ordinary documentation and API lookups stay with the current agent.
The installer caps concurrent Codex agent threads at 10 to prevent accidental
fan-out; normal packages should use far fewer and add workers only when they
shorten the critical path.

Workers start from compact task capsules rather than full parent-chat forks, so
their packaged Luna model settings remain authoritative and long coordinator
history is not copied into every worker.

The workflow optimizes the critical path. It reuses workers for related
follow-ups, skips investigators unless uncertainty blocks implementation,
groups tester findings into one repair packet, waits on lifecycle events rather
than polling, avoids routine worker-to-coordinator status traffic, and runs
proportionate verification once the coherent change is stable. Obvious micro
follow-ups use the direct fast path when the seam is already known. It does not
create a companion or closure worker.

The packaged skill and worker templates are canonical release artifacts.
Lifecycle tests verify that archives and installed runtimes preserve them and
that owned legacy workflow components are removed safely during an update.

## Build and bootstrap

```text
python3 scripts/package.py
python3 workflow.py validate --package-root . --json
```

The build creates `dist/codex_workflow-<version>.zip` and `dist/SHA256SUMS`.
Use `scripts/bootstrap.sh` or `scripts/bootstrap.ps1` to verify a release,
validate it, check Codex compatibility, and perform the initial bootstrap.

## Legacy marker migration

v1 project entries carrying the repository-qualified marker are recognized only
as a migration source. Run the v2 `workflow.py update` with a reviewed
`--legacy-local-instructions <file>` when the old entry contains local edits.
The update writes the canonical marker and dedicated local region in one
transaction. Never copy merged instructions automatically; review them first.

## Development

```text
python3 -m unittest discover -s tests -v
```

The release workflow in [`.github/workflows/release.yml`](.github/workflows/release.yml)
runs tests and validation, creates the universal archive and `SHA256SUMS`, and
publishes both assets for every `v*` tag.

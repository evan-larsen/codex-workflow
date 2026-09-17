# codex_workflow

Portable, deterministic lifecycle tooling for installing a generic Codex
workflow into a user runtime and project. The CLI slug is `codex_workflow` and
the canonical package version is `2.0.0`.

The package owns only its marked user/project regions, marked worker files, and
workflow settings. Existing unowned role files are never overwritten. The
three-section personalization resource remains compatible with v1 projects;
customized sections are materialized into the project entry point without
creating selectable profiles.

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
$Version = '2.0.0'
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
installation. It writes workflow-owned files under the selected Codex home
and project; keep the downloaded files until installation has completed
successfully.

After the initial bootstrap, use the lifecycle forms documented in
[`install.md`](install.md), [`update.md`](update.md),
[`check_update.md`](check_update.md), and [`remove.md`](remove.md):

```text
codex_workflow --install
codex_workflow --check-update
codex_workflow --update
codex_workflow --remove
```

`--remove` is destructive and requires its separate confirmation phase. Read
[`remove.md`](remove.md) before using it. To turn the notification-only update
check on or off, see [`enable_auto_check_update.md`](enable_auto_check_update.md)
and [`disable_auto_check_update.md`](disable_auto_check_update.md).

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

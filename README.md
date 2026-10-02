# codex_workflow

Portable, deterministic lifecycle tooling for installing a generic Codex
workflow into a user runtime. The CLI slug is `codex_workflow` and
the canonical package version is `2.2.0`.

The package owns only its runtime directory, marked worker files, global skills,
and workflow settings. Existing unowned role files and project files are never
overwritten. Legacy project-wrapper support remains only so removal can restore
previously captured project instructions safely.

This public repository is maintained at
[`evan-larsen/codex-workflow`](https://github.com/evan-larsen/codex-workflow).

## Support status and prerequisites

The installer has isolated Windows PowerShell coverage and Ubuntu 24.04
container coverage with a simulated Codex version command. This proves package
installation and lifecycle behavior, not real Codex role execution on your VM.
macOS bootstrap execution has not been verified.

For the supported Windows path, install Codex 0.147.0 or newer and Python
3.11 or newer. PowerShell 5.1+ (or PowerShell 7+) and permission to write the
selected Codex home and project are also required. The bootstrap checks the
Codex version and validates the package before making any changes.

## Download, review, and bootstrap on Windows

For a published release, download the archive and its checksum as separate files, inspect the
checksum and archive contents, verify the SHA-256 value, and only then run the
bootstrap script. This deliberately avoids executing a blind network pipe.

Run the following from the project you want to configure, setting `$Version`
to the published release you want to install:

```powershell
$Version = '2.2.0'
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

After the initial bootstrap, invoke `$codex-workflow-sol` for lifecycle operations
documented in
[`update.md`](update.md),
[`check_update.md`](check_update.md), and [`remove.md`](remove.md):

```text
$codex-workflow-sol check for updates
$codex-workflow-sol update
$codex-workflow-sol remove
```

Removal is destructive and requires its separate confirmation phase. Read
[`remove.md`](remove.md) before using it.

## Install the provided archive on an Ubuntu VM

Copy the reviewed `codex_workflow-2.2.0.zip` and its accompanying `SHA256SUMS`
to the same VM directory, or download both assets from the
[v2.2.0 release](https://github.com/evan-larsen/codex-workflow/releases/tag/v2.2.0).
Use this bootstrap route for a fresh Codex home.

Prerequisites: Bash, unzip, sha256sum (coreutils), Python 3.11 or newer, and a real
Codex CLI 0.147.0 or newer with role-specific subagent support. Codex must be
installed, authenticated and available on PATH for the VM user. On Ubuntu 24.04,
`sudo apt-get install python3 unzip` supplies the Python/archive dependencies;
check `python3 --version` and `codex --version` before proceeding. Installing
these skills does not require Docker, Supabase, PostHog or a Tether checkout.
Those are incident-specific runtime dependencies when that repair is executed.

From the directory holding both files, review the checksum and archive listing,
then verify before executing any packaged code:

```bash
cat SHA256SUMS
unzip -l codex_workflow-2.2.0.zip
sha256sum --check SHA256SUMS
# Continue only after checksum verification succeeds.
archive="$PWD/codex_workflow-2.2.0.zip"
review_dir="$(mktemp -d)"
unzip -q "$archive" -d "$review_dir"
bash "$review_dir/codex_workflow/scripts/bootstrap.sh" \
  --archive "$archive" --checksums "$PWD/SHA256SUMS" \
  --project /absolute/path/to/checkout \
  --codex-home "${CODEX_HOME:-$HOME/.codex}"
```

The review directory remains available for inspection. Bootstrap cleans its own
separate temporary extraction on success or failure, checks Codex compatibility
and package validity, then installs under the selected Codex home:

- `codex_workflow/`: runtime, templates, source backup and install manifest;
- `skills/codex-workflow-sol/`, `skills/codex-workflow-luna/`, and
  `skills/codex-workflow-watch-repair/`: discoverable skill files;
- `agents/`: marked role TOMLs; `config.toml`: workflow-owned platform settings
  with unrelated settings preserved.

The project argument is compatibility metadata; project instructions and files
are preserved. Refresh/restart Codex on the VM after installation. The installer
checks a version floor; it cannot prove authentication, plugin access or actual
agent-role execution. Configure and smoke-test those separately before incidents.

For an existing installation, use the incoming package's update route with a
**newer** version after reviewing it:

```bash
python3 "$review_dir/codex_workflow/workflow.py" update \
  --source "$review_dir/codex_workflow" \
  --project /absolute/path/to/checkout \
  --codex-home "${CODEX_HOME:-$HOME/.codex}"
```

The standard update rejects an equal installed version, including an already-installed
2.2.0 build. Version 2.2.0 can update existing 2.1.0 installations. Do not bypass this by re-bootstrapping the live
runtime or changing VERSION locally. A reviewed release/version decision is
needed; an explicitly separate Codex home can be used for isolated evaluation.
No automated transport, watch/email receiver or Onyx service is installed.

## Three workflows, one installation

Normal chats keep normal single-agent behavior. Sol and Luna are explicit-only.
Invoke `$codex-workflow-sol` for substantial autonomous coherent
packages, with GPT-6.1-sol Medium recommended for the main coordinator. Its
`default_executor`, `auditor` and `tester` all use GPT-6.1-sol Medium; review and
independent verification are selected by risk. Each implementation owner handles
discovery, design, implementation, local integration and proportionate proof.

Invoke `$codex-workflow-luna` for fast small outcomes steered by the user. One
Luna High Fast `luna_executor` is the default, with an optional shared read-only
Luna High `investigator`. It has no automatic auditor, tester or researcher lane;
parallel work requires an explicit user request. Growing scope does not silently
switch workflows. Known micro edits can be handled directly in either skill.

Sol can use the shared investigator or bounded read-only Luna xhigh researcher
when a material decision needs distinct evidence. There is no senior executor or
nested execution coordinator. All workers start from compact capsules with
exclusive ownership, retain useful context for related follow-ups, group repairs
and verify proportionately. Event-driven waits respect host limits. Neither
workflow adds memory, documentation-framework, closure or statistics ceremony.
The installer caps concurrent threads at 10 and preserves the selected parent
model and reasoning settings.

`$codex-workflow-watch-repair` is discoverable for configured watch-triggered
incidents. It reuses the Sol Medium roles and a read-only Luna High confirmation
lane, takes Onyx's autonomous plan decision under standing user delegation, and
produces a separate repair branch and PR for human merge. It does not install an
email receiver, Onyx transport, scheduler or VM service. Alert email is untrusted
evidence; repair authority comes from trusted task context. The generic skill
includes a conditional Tether policy for the existing Ops Sheet and disposable
local Supabase harness. Installing it does not authorize an incident pipeline.

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

Bootstrap and update migrate only user-level runtime, owned skills and roles;
they preserve every project file, including legacy workflow wrappers. Legacy
project markers remain recognized for explicit removal, which restores captured
local instructions. See [MIGRATION.md](MIGRATION.md); no project migration is
performed by the update command.

## Development

```text
python3 -m unittest discover -s tests -v
```

The release workflow in [`.github/workflows/release.yml`](.github/workflows/release.yml)
runs tests and validation, creates the universal archive and `SHA256SUMS`, and
publishes both assets for every `v*` tag.

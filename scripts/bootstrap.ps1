param(
  [Parameter(Mandatory=$true)][string]$Archive,
  [Parameter(Mandatory=$true)][string]$Project,
  [string]$CodexHome,
  [string]$Checksums
)
$ErrorActionPreference = 'Stop'
$archivePath = (Resolve-Path -LiteralPath $Archive).Path
$checksumPath = if ($Checksums) { (Resolve-Path -LiteralPath $Checksums).Path } else { Join-Path (Split-Path $archivePath) 'SHA256SUMS' }
if (-not (Test-Path -LiteralPath $checksumPath -PathType Leaf)) { throw "SHA256SUMS not found: $checksumPath" }
$name = Split-Path $archivePath -Leaf
$line = Select-String -LiteralPath $checksumPath -Pattern ([regex]::Escape($name)) | Select-Object -First 1
if (-not $line) { throw "SHA256SUMS has no entry for $name" }
$expected = ($line.Line -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($expected -ne $actual) { throw 'release ZIP checksum mismatch' }
$temp = Join-Path ([IO.Path]::GetTempPath()) ('codex-workflow-bootstrap-' + [guid]::NewGuid())
try {
  New-Item -ItemType Directory -Path $temp | Out-Null
  Expand-Archive -LiteralPath $archivePath -DestinationPath $temp
  $package = Join-Path $temp 'codex_workflow'
  if (-not (Test-Path -LiteralPath $package -PathType Container) -or ((Get-ChildItem -LiteralPath $temp -Force).Count -ne 1)) { throw 'archive must contain exactly one top-level codex_workflow directory' }
  $script = Join-Path $package 'workflow.py'
  if ($env:CODEX_WORKFLOW_PYTHON) {
    & $env:CODEX_WORKFLOW_PYTHON $script 'check-compatibility' '--json'; if ($LASTEXITCODE) { exit $LASTEXITCODE }
    & $env:CODEX_WORKFLOW_PYTHON $script 'validate' '--package-root' $package '--json'; if ($LASTEXITCODE) { exit $LASTEXITCODE }
    if ($CodexHome) { & $env:CODEX_WORKFLOW_PYTHON $script 'bootstrap' '--package-root' $package '--project' $Project '--codex-home' $CodexHome }
    else { & $env:CODEX_WORKFLOW_PYTHON $script 'bootstrap' '--package-root' $package '--project' $Project }
  } else {
    & py -3.11 $script 'check-compatibility' '--json'; if ($LASTEXITCODE) { exit $LASTEXITCODE }
    & py -3.11 $script 'validate' '--package-root' $package '--json'; if ($LASTEXITCODE) { exit $LASTEXITCODE }
    if ($CodexHome) { & py -3.11 $script 'bootstrap' '--package-root' $package '--project' $Project '--codex-home' $CodexHome }
    else { & py -3.11 $script 'bootstrap' '--package-root' $package '--project' $Project }
  }
  if ($LASTEXITCODE) { exit $LASTEXITCODE }
} finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force } }

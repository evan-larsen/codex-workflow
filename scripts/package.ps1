param(
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$Output
)
$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'package.py'
if ($env:CODEX_WORKFLOW_PYTHON) {
  if ($Output) { & $env:CODEX_WORKFLOW_PYTHON $script '--root' $Root '--output' $Output }
  else { & $env:CODEX_WORKFLOW_PYTHON $script '--root' $Root }
} elseif ($Output) {
  & py -3.11 $script '--root' $Root '--output' $Output
} else {
  & py -3.11 $script '--root' $Root
}
if ($LASTEXITCODE) { exit $LASTEXITCODE }

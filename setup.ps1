# Idempotent setup (Windows PowerShell): installs what is missing and reports what is left to do by hand.
# Pass --check to only verify.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py -3 -m outbound setup @args; exit $LASTEXITCODE }
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) { & python -m outbound setup @args; exit $LASTEXITCODE }
Write-Error 'Python não encontrado. Instale com: winget install Python.Python.3.12'
exit 1

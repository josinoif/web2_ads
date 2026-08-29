# Encaminha para sistemas-distribuidos/lab.ps1. Igual em todos os labs — não edite.
$ErrorActionPreference = "Stop"
$dir = $PSScriptRoot
while ($dir) {
    $tools = Join-Path $dir "ferramentas\lab-tools\Dockerfile"
    $runner = Join-Path $dir "lab.ps1"
    if ((Test-Path $tools) -and (Test-Path $runner)) {
        & $runner @args
        exit $LASTEXITCODE
    }
    $parent = Split-Path $dir
    if (-not $parent -or $parent -eq $dir) { break }
    $dir = $parent
}
Write-Error "nao achei sistemas-distribuidos/lab.ps1 (pasta com ferramentas/lab-tools)."

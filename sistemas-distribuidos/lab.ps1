# Executor de scripts .sh dos labs no Windows PowerShell.
#
# Na pasta do lab (onde está o docker-compose.yml e o atalho lab.ps1):
#   .\lab.ps1 enviar-lote 10
#   .\lab.ps1 cliente sincrono
#
# Tutoriais RabbitMQ / Kafka pedido-pago: use
#   docker compose exec -T api python lab.py …
# (não precisa deste runner).

param(
    [Parameter(Position = 0)]
    [string]$Script,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"

if (-not $Script) {
    Write-Host "uso: .\lab.ps1 NOME-DO-SCRIPT [args...]"
    Write-Host "  exemplo: .\lab.ps1 enviar-lote 10"
    Write-Host "  exemplo: .\lab.ps1 cliente sincrono"
    Write-Host "  exemplo: .\lab.ps1 scripts/cliente.sh sincrono"
    exit 2
}

$lab = (Get-Location).Path
if (-not (Test-Path (Join-Path $lab "docker-compose.yml"))) {
    Write-Error "rode na pasta do lab (precisa existir docker-compose.yml). cwd=$lab"
}

$root = $PSScriptRoot
$dockerfile = Join-Path $root "ferramentas\lab-tools\Dockerfile"
if (-not (Test-Path $dockerfile)) {
    Write-Error "nao achei ferramentas/lab-tools (o lab.ps1 raiz deve ficar em sistemas-distribuidos). root=$root"
}

if ($Script -like "*.sh" -or $Script -like "scripts/*" -or $Script -like "scripts\*") {
    $rel = ($Script -replace "\\", "/")
} else {
    $rel = "scripts/$Script.sh"
}

$hostScript = Join-Path $lab ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)
if (-not (Test-Path $hostScript)) {
    Write-Error "nao achei $hostScript"
}

$image = "aulas-ads-lab-tools"
docker image inspect $image *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "construindo imagem $image (primeira vez)..."
    docker build -t $image (Join-Path $root "ferramentas\lab-tools")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$deny = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
@(
    "ALLUSERSPROFILE", "APPDATA", "COMMONPROGRAMFILES", "COMMONPROGRAMFILES(X86)",
    "COMPOSE_PROJECT_NAME", "COMPUTERNAME", "COMSPEC", "DRIVERDATA", "HOME",
    "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA", "LOGONSERVER", "NUMBER_OF_PROCESSORS",
    "ONEDRIVE", "ONEDRIVECONSUMER", "OS", "PATH", "PATHEXT", "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER", "PROCESSOR_LEVEL", "PROCESSOR_REVISION", "PROGRAMDATA",
    "PROGRAMFILES", "PROGRAMFILES(X86)", "PROMPT", "PSMODULEPATH", "PUBLIC",
    "SESSIONNAME", "SYSTEMROOT", "TEMP", "TMP", "USERDOMAIN", "USERDOMAIN_ROAMINGPROFILE",
    "USERPROFILE", "USERNAME", "WINDIR", "PATHEXT", "PYTHONPATH", "VIRTUAL_ENV"
) | ForEach-Object { [void]$deny.Add($_) }

$project = Split-Path -Leaf $lab
$workScript = "/work/$rel"

$dockerArgs = @(
    "run", "--rm",
    "-v", "${lab}:/work",
    "-v", "/var/run/docker.sock:/var/run/docker.sock",
    "-w", "/work",
    "-e", "COMPOSE_PROJECT_NAME=$project",
    "--add-host=host.docker.internal:host-gateway"
)

foreach ($e in Get-ChildItem Env:) {
    if ($deny.Contains($e.Name)) { continue }
    if ($e.Name -match '^(CURSOR_|VSCODE_|TERM_|POWERSHELL_|GIT_|Chocolatey)') { continue }
    if ($e.Name -notmatch '^[A-Z][A-Z0-9_]*$') { continue }
    $dockerArgs += "-e"
    $dockerArgs += $e.Name
}

$dockerArgs += $image
$dockerArgs += $workScript
if ($ScriptArgs) {
    $dockerArgs += $ScriptArgs
}
& docker @dockerArgs
exit $LASTEXITCODE

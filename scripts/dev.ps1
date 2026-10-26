param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$runArguments = @('run', '--locked')
$environmentFile = Join-Path (Split-Path $PSScriptRoot -Parent) '.env'
if (Test-Path -LiteralPath $environmentFile) {
    $runArguments += @('--env-file', $environmentFile)
}
$runArguments += @('uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', "$Port", '--reload-dir', 'app')
& "$PSScriptRoot\uv.ps1" @runArguments
exit $LASTEXITCODE

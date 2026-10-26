param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\uv.ps1" run --locked uvicorn app.main:app --reload --host 127.0.0.1 --port $Port --reload-dir app
exit $LASTEXITCODE

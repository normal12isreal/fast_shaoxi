# Forward all arguments unchanged; do not require activation or a global uv/Python.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$uvExecutable = Join-Path $projectRoot '.tools\uv\uv.exe'
if (-not (Test-Path -LiteralPath $uvExecutable)) {
    throw 'Project uv is missing. Run .\scripts\bootstrap.ps1 first.'
}

$localEnvironment = @{
    UV_CACHE_DIR = Join-Path $projectRoot '.uv-cache'
    UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot '.runtime\python'
    UV_PYTHON_BIN_DIR = Join-Path $projectRoot '.runtime\bin'
    UV_PYTHON_CACHE_DIR = Join-Path $projectRoot '.uv-cache\python'
    UV_TOOL_DIR = Join-Path $projectRoot '.tools\environments'
    UV_TOOL_BIN_DIR = Join-Path $projectRoot '.tools\bin'
    UV_PROJECT_ENVIRONMENT = Join-Path $projectRoot '.venv'
    UV_PYTHON_PREFERENCE = 'only-managed'
    UV_PYTHON_INSTALL_REGISTRY = 'false'
    UV_PYTHON_INSTALL_BIN = 'false'
    UV_PYTHON_NO_REGISTRY = 'true'
    PYTHONNOUSERSITE = '1'
    PYTHONPATH = ''
    TEMP = Join-Path $projectRoot '.tools\tmp'
    TMP = Join-Path $projectRoot '.tools\tmp'
}
New-Item -ItemType Directory -Path $localEnvironment.TEMP -Force | Out-Null
$previousEnvironment = @{}
foreach ($name in $localEnvironment.Keys) {
    $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

Push-Location $projectRoot
try {
    foreach ($name in $localEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $localEnvironment[$name], 'Process')
    }
    & $uvExecutable @args
    $commandExitCode = $LASTEXITCODE
}
finally {
    foreach ($name in $previousEnvironment.Keys) {
        if ($null -eq $previousEnvironment[$name]) {
            Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue
        }
        else {
            [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], 'Process')
        }
    }
    Pop-Location
}
exit $commandExitCode

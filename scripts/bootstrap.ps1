$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolchain = Get-Content (Join-Path $PSScriptRoot 'toolchain.json') -Raw | ConvertFrom-Json
$uvDirectory = Join-Path $projectRoot '.tools\uv'
$uvExecutable = Join-Path $uvDirectory 'uv.exe'

if (-not [Environment]::Is64BitProcess -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
    throw 'This bootstrap currently supports Windows x64 PowerShell.'
}

if (-not (Test-Path -LiteralPath $uvExecutable)) {
    New-Item -ItemType Directory -Path $uvDirectory -Force | Out-Null
    $archivePath = Join-Path $uvDirectory 'uv.zip'
    $downloadUrl = "https://github.com/astral-sh/uv/releases/download/$($toolchain.uv_version)/uv-x86_64-pc-windows-msvc.zip"
    & curl.exe --fail --location --silent --show-error --retry 3 --connect-timeout 20 --max-time 180 --output $archivePath $downloadUrl
    if ($LASTEXITCODE -ne 0) { throw 'uv download failed; rerun bootstrap to retry.' }
    $actualHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash
    if ($actualHash -ne $toolchain.windows_x64_sha256) {
        throw 'uv archive checksum does not match the pinned official release.'
    }
    Expand-Archive -LiteralPath $archivePath -DestinationPath $uvDirectory -Force
    Remove-Item -LiteralPath $archivePath
}

$installedVersion = & $uvExecutable --version
if ($LASTEXITCODE -ne 0 -or $installedVersion -notmatch "^uv $([regex]::Escape($toolchain.uv_version))(\s|$)") {
    throw 'Local uv version differs from scripts/toolchain.json; review the toolchain before reinstalling.'
}

$pythonVersion = (Get-Content (Join-Path $projectRoot '.python-version') -Raw).Trim()
& "$PSScriptRoot\uv.ps1" python install $pythonVersion
if ($LASTEXITCODE -ne 0) { throw 'Project Python installation failed.' }
if (Test-Path -LiteralPath (Join-Path $projectRoot 'uv.lock')) {
    & "$PSScriptRoot\uv.ps1" sync --locked
}
else {
    & "$PSScriptRoot\uv.ps1" sync
}
if ($LASTEXITCODE -ne 0) { throw 'Dependency synchronization failed.' }
Write-Output 'Ready. Start the development server with .\scripts\dev.ps1'

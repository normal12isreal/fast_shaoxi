# Keep AWS credentials, runtime, and MCP registration inside this project.
param([switch] $Mcp)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$stateDirectory = Join-Path $projectRoot '.tools/aws-state'
New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
$awsEnvironment = @{
    AWS_CONFIG_FILE = Join-Path $stateDirectory 'config'
    AWS_SHARED_CREDENTIALS_FILE = Join-Path $stateDirectory 'credentials'
    AWS_LOGIN_CACHE_DIRECTORY = Join-Path $stateDirectory 'login-cache'
    AWS_PROFILE = 'fastapi-aws'
    AWS_MCP_PROXY_PROFILES = 'fastapi-aws'
    AWS_REGION = 'us-east-2'
    AWS_DEFAULT_REGION = 'us-east-2'
    AWS_PAGER = ''
    HTTP_PROXY = 'http://127.0.0.1:7890'
    HTTPS_PROXY = 'http://127.0.0.1:7890'
    NO_PROXY = 'localhost,127.0.0.1,::1'
}
$previousEnvironment = @{}
try {
    foreach ($name in $awsEnvironment.Keys) {
        $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, $awsEnvironment[$name], 'Process')
    }
    if ($Mcp) {
        & (Join-Path $PSScriptRoot 'uv.ps1') tool run --from mcp-proxy-for-aws-cli==1.7.0 mcp-proxy-for-aws-cli https://aws-mcp.us-east-1.api.aws/mcp --region us-east-1 --metadata AWS_REGION=us-east-2
    }
    else {
        $awsExecutable = Join-Path $projectRoot '.tools/aws-cli/aws.exe'
        if (-not (Test-Path -LiteralPath $awsExecutable)) {
            throw 'Project AWS CLI is missing. See docs/setup.md.'
        }
        & $awsExecutable @args
    }
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
}
exit $commandExitCode

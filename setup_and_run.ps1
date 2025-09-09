param(
  [switch]$Rebuild
)

Write-Host "=== Dexter Docker Launcher ===" -ForegroundColor Cyan

# 1) Check Docker Desktop
try {
  docker version | Out-Null
} catch {
  Write-Error "Docker Desktop not found or not running. Install & start Docker, then re-run."; exit 1
}

# 2) Compose up
$composeFile = "infra/docker-compose.yml"
Push-Location (Split-Path $PSCommandPath)
if ($Rebuild) { docker compose -f $composeFile build }
docker compose -f $composeFile up -d
Pop-Location

# 3) Info
$api = $env:API_PORT; if (-not $api) { $api = 8000 }
$web = $env:WEB_PORT; if (-not $web) { $web = 5173 }
Write-Host "API:    http://localhost:$api/docs" -ForegroundColor Green
Write-Host "Web:    http://localhost:$web" -ForegroundColor Green
Write-Host "Logs:   docker compose -f $composeFile logs -f" -ForegroundColor DarkGray

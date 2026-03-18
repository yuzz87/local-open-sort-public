python .\scripts\init_env.py

docker compose -f .\docker-compose.yml -f .\docker-compose.local.yml down -v 2>$null
docker compose -f .\docker-compose.yml -f .\docker-compose.local.yml up -d --build db app nginx

Write-Host "waiting for local stack..."

for ($i = 0; $i -lt 40; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8080/health" -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "Web app is running:"
            Write-Host "http://127.0.0.1:8080"
            exit 0
        }
    } catch {
    }

    Start-Sleep -Seconds 3
}

Write-Host "local stack failed to start"
docker compose -f .\docker-compose.yml -f .\docker-compose.local.yml ps
docker compose -f .\docker-compose.yml -f .\docker-compose.local.yml logs --tail=100
exit 1
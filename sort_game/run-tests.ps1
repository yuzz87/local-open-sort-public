python .\scripts\init_env.py

docker compose -f .\docker-compose.test.yml down -v 2>$null
docker compose -f .\docker-compose.test.yml up -d db-test

Write-Host "waiting for test mysql..."

for ($i = 0; $i -lt 40; $i++) {
    docker exec sort_db_test mysqladmin ping -h localhost -uroot -proot --silent 2>$null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 2
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "test mysql failed to start"
    docker compose -f .\docker-compose.test.yml ps
    docker compose -f .\docker-compose.test.yml logs --tail=100
    exit 1
}

Get-Content .\docker\mysql\initdb\01_schema.sql | docker exec -i sort_db_test mysql -u root -proot sort_portfolio_test
if ($LASTEXITCODE -ne 0) {
    Write-Host "failed to apply schema"
    docker compose -f .\docker-compose.test.yml logs --tail=100
    docker compose -f .\docker-compose.test.yml down -v
    exit 1
}

Get-Content .\docker\mysql\initdb\02_seed.sql | docker exec -i sort_db_test mysql -u root -proot sort_portfolio_test
if ($LASTEXITCODE -ne 0) {
    Write-Host "failed to apply seed"
    docker compose -f .\docker-compose.test.yml logs --tail=100
    docker compose -f .\docker-compose.test.yml down -v
    exit 1
}

python -m pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-report=xml
$pytestExitCode = $LASTEXITCODE

docker compose -f .\docker-compose.test.yml down -v

exit $pytestExitCode
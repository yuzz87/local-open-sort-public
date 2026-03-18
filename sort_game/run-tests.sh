#!/usr/bin/env bash
set -e

python scripts/init_env.py

docker compose -f docker-compose.yml -f docker-compose.local.yml down -v || true
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d db

echo "waiting for mysql..."
for i in {1..30}; do
  if docker exec sort_db_local mysqladmin ping -h localhost -uroot -proot --silent; then
    break
  fi
  sleep 2
done

docker exec -i sort_db_local mysql -u root -proot sort_portfolio_test < docker/mysql/initdb/01_schema.sql
docker exec -i sort_db_local mysql -u root -proot sort_portfolio_test < docker/mysql/initdb/02_seed.sql

python -m pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-report=xml
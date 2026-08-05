#!/bin/bash
set -e

echo "=== PT-Docs bootstrap ==="

if [ ! -f .env ]; then
  echo "Creando .env desde .env.example..."
  cp .env.example .env
fi

echo "Construyendo contenedores..."
docker compose -f docker/docker-compose.yml build

echo "Aplicando migraciones..."
docker compose -f docker/docker-compose.yml run --rm web python manage.py migrate

echo "Sembrando roles..."
docker compose -f docker/docker-compose.yml run --rm web python manage.py seed_roles

echo "Sembrando catálogos DIAN..."
docker compose -f docker/docker-compose.yml run --rm web python manage.py seed_catalogos

echo ""
echo "=== Bootstrap completo ==="
echo "Ahora crea un superuser:"
echo "  docker compose -f docker/docker-compose.yml run --rm web python manage.py createsuperuser"
echo ""
echo "Y levanta el stack:"
echo "  docker compose -f docker/docker-compose.yml up"
echo ""
echo "Abre http://localhost:8000"

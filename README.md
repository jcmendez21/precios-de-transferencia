# PT-Docs

Sistema web para automatizar la generación del Informe Local de precios de transferencia ante DIAN (Colombia).

## Requisitos
- Docker Desktop 24+
- Docker Compose v2

## Setup rápido
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Web app en http://localhost:8000

## Estado actual
Sprint 0 en curso: fundaciones (Django, Postgres, auth, catálogos DIAN).

## Documentación
- Spec de diseño: `docs/superpowers/specs/2026-08-03-pt-docs-diseno.md`
- Plan Sprint 0: `docs/superpowers/plans/2026-08-03-sprint-0-setup.md`

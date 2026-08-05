# PT-Docs

Sistema web para automatizar la generación del Informe Local de precios de transferencia ante DIAN (Colombia).

## Requisitos
- Docker Desktop 24+
- Docker Compose v2
- Git

## Setup rápido

```bash
# Clonar el repo
git clone <repo-url>
cd precios-de-tranferencia

# Bootstrap (crea .env, arranca contenedores, migra, semilla)
bash scripts/bootstrap.sh

# Crear superuser
docker compose -f docker/docker-compose.yml run --rm web python manage.py createsuperuser

# Levantar stack completo
docker compose -f docker/docker-compose.yml up
```

Web app en http://localhost:8000
Admin Django en http://localhost:8000/admin/

## Roles del sistema
- `admin_firma` — administra usuarios y catálogos.
- `senior` — puede crear/editar comparables globales y aprobar estudios.
- `junior` — trabaja estudios; no toca catálogo compartido.
- `revisor` — revisa estudios (rol de supervisión).

Los grupos se crean con `python manage.py seed_roles`.

## Comandos útiles

```bash
# Tests
docker compose -f docker/docker-compose.yml run --rm web pytest ../tests -v

# Lint
docker compose -f docker/docker-compose.yml run --rm web ruff check src tests

# Type check
docker compose -f docker/docker-compose.yml run --rm web mypy src

# Re-sembrar catálogos (idempotente)
docker compose -f docker/docker-compose.yml run --rm web python manage.py seed_catalogos
```

## Estructura del proyecto
```
src/config/          # Django project (settings, urls, wsgi)
src/apps/core/       # Firma, Usuario, roles, auditoría
src/apps/catalogos/  # Catálogos DIAN (países, paraísos, tipos operación, sectores)
tests/               # Suite pytest
docker/              # Dockerfile + docker-compose
scripts/             # Utilitarios (bootstrap)
docs/                # Spec, planes, memoria del proyecto
```

## Sprints
- ✅ **Sprint 0** — Setup, apps core y catalogos, auth, CI.
- ⬜ **Sprint 1** — Clientes, estudios, importador xlsx DIAN.
- ⬜ **Sprint 2** — Comparables, análisis, cuartiles.
- ⬜ **Sprint 3** — Plantillas docx, generación Informe Local.
- ⬜ **Sprint 4** — Endurecimiento, auditoría full, backups.

## Documentación
- Spec de diseño: `docs/superpowers/specs/2026-08-03-pt-docs-diseno.md`
- Plan Sprint 0: `docs/superpowers/plans/2026-08-03-sprint-0-setup.md`

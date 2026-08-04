# PT-Docs — Sprint 0 (Setup) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establecer las fundaciones del sistema PT-Docs: repositorio, contenedores, proyecto Django con apps `core` y `catalogos`, autenticación con roles, testing/CI, y catálogos DIAN iniciales cargados. Al final de Sprint 0, un desarrollador nuevo corre `docker compose up`, se loguea, y ve los catálogos oficiales en el admin.

**Architecture:** Django 5 monolito modular. Postgres para datos, Redis para tasks async, Django-Q2 para workers. Auth con django-allauth (login local). Auditoría con django-simple-history. Todo en Docker Compose. Estructura de apps: `src/apps/<nombre>/`.

**Tech Stack:** Python 3.12, Django 5.x, Postgres 16, Redis 7, django-allauth, django-simple-history, django-q2, pytest-django, factory-boy, hypothesis, ruff, mypy, pre-commit, Docker Compose.

## Global Constraints

- Python 3.12+ (pin en `pyproject.toml` y `Dockerfile`).
- Django 5.x LTS-compatible.
- Postgres 16.
- Estructura fuente: `src/apps/<nombre_app>/`. Django project: `config`.
- Nombres de modelos y campos en español (dominio); mixins/helpers técnicos en inglés.
- Timezone: `America/Bogota`.
- Locale: `es-co`.
- Encoding: UTF-8.
- Formato moneda: `$ 5.000.000` (punto miles).
- Formato porcentaje: `12,34%` (coma decimal).
- Cobertura test target Sprint 0: **70% baseline global**.
- Todos los commits usan Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `docs:`).
- No commitear `.env` real; solo `.env.example`.
- No commitear `_materiales/` (dataset de prueba local).

---

## File Structure

```
precios-de-tranferencia/
├── .github/workflows/ci.yml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── admin.py
│   │   │   ├── mixins.py
│   │   │   ├── migrations/
│   │   │   └── management/commands/seed_roles.py
│   │   └── catalogos/
│   │       ├── __init__.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── admin.py
│   │       ├── migrations/
│   │       ├── data/
│   │       │   ├── paises_dian.csv
│   │       │   ├── paraisos_fiscales.csv
│   │       │   └── tipos_operacion.csv
│   │       └── management/commands/seed_catalogos.py
│   └── templates/
│       ├── base.html
│       ├── home.html
│       └── account/
│           └── login.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── factories.py
│   ├── test_smoke.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_seed_roles.py
│   └── catalogos/
│       ├── __init__.py
│       ├── test_models.py
│       └── test_seed_catalogos.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── pytest.ini
├── ruff.toml
├── mypy.ini
└── README.md
```

---

### Task 1: Bootstrap del repo — git init, gitignore, pyproject, README

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `pyproject.toml`
- Create: `README.md`

**Interfaces:**
- Produces: repositorio git inicializado con dependencias declaradas.

- [ ] **Step 1: Inicializar git y verificar working directory**

Run: `git init && git status`
Expected: repo inicializado, working tree limpio (excepto `_materiales/` y `docs/`).

- [ ] **Step 2: Crear `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.venv/
venv/
env/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
/src/media/
/src/staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Materiales de prueba (dataset local, no commitear)
_materiales/

# Docker
docker/postgres_data/
docker/redis_data/
```

- [ ] **Step 3: Crear `.env.example`**

```dotenv
# Django
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=ptdocs
POSTGRES_USER=ptdocs
POSTGRES_PASSWORD=ptdocs_dev
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Timezone / Locale
TIME_ZONE=America/Bogota
LANGUAGE_CODE=es-co
```

- [ ] **Step 4: Crear `pyproject.toml`**

```toml
[project]
name = "pt-docs"
version = "0.1.0"
description = "Sistema de generación de documentación de precios de transferencia (DIAN Colombia)"
requires-python = ">=3.12"
dependencies = [
    "Django>=5.0,<5.2",
    "psycopg2-binary>=2.9",
    "python-dotenv>=1.0",
    "django-allauth>=0.61",
    "django-simple-history>=3.5",
    "django-q2>=1.6",
    "redis>=5.0",
    "gunicorn>=21.2",
    "whitenoise>=6.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "pytest-cov>=5.0",
    "factory-boy>=3.3",
    "hypothesis>=6.100",
    "ruff>=0.4",
    "mypy>=1.10",
    "django-stubs>=5.0",
    "pre-commit>=3.7",
]

[tool.setuptools]
packages = ["config", "apps"]
package-dir = {"" = "src"}
```

- [ ] **Step 5: Crear `README.md` mínimo**

```markdown
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
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore .env.example pyproject.toml README.md
git commit -m "chore: bootstrap repo with pyproject and gitignore"
```

---

### Task 2: Django project skeleton — settings split

**Files:**
- Create: `src/manage.py`
- Create: `src/config/__init__.py`
- Create: `src/config/settings/__init__.py`
- Create: `src/config/settings/base.py`
- Create: `src/config/settings/dev.py`
- Create: `src/config/settings/prod.py`
- Create: `src/config/urls.py`
- Create: `src/config/wsgi.py`
- Create: `src/config/asgi.py`

**Interfaces:**
- Produces: `DJANGO_SETTINGS_MODULE=config.settings.{dev|prod}` cargable.
- Consumes: variables de entorno de `.env`.

- [ ] **Step 1: Crear entorno virtual local para probar**

Run: `python -m venv .venv && .venv\Scripts\activate && pip install -e .[dev]`
Expected: instalación exitosa (usar cmd.exe o powershell según entorno).

- [ ] **Step 2: Crear `src/manage.py`**

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Did you install requirements?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Crear `src/config/settings/base.py`**

```python
"""Django settings compartidos entre dev y prod."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party (se agregarán en tareas posteriores)
    # Apps propias (se agregarán en tareas posteriores)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "ptdocs"),
        "USER": os.environ.get("POSTGRES_USER", "ptdocs"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "es-co")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Bogota")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1
```

- [ ] **Step 4: Crear `src/config/settings/dev.py`**

```python
"""Settings de desarrollo."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "web"]

# Emails a consola en dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

- [ ] **Step 5: Crear `src/config/settings/prod.py`**

```python
"""Settings de producción."""
from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

- [ ] **Step 6: Crear `src/config/settings/__init__.py`**

Archivo vacío. Solo hace que `settings/` sea un package.

- [ ] **Step 7: Crear `src/config/__init__.py`**

Archivo vacío.

- [ ] **Step 8: Crear `src/config/urls.py`**

```python
"""URL configuration del proyecto."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def home(request):
    return HttpResponse("PT-Docs — Sprint 0 activo", content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]
```

- [ ] **Step 9: Crear `src/config/wsgi.py`**

```python
"""WSGI config."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
```

- [ ] **Step 10: Crear `src/config/asgi.py`**

```python
"""ASGI config."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()
```

- [ ] **Step 11: Verificar imports funcionan**

Run: `cd src && python -c "import django; django.setup()" `
Prerequisito: `DJANGO_SETTINGS_MODULE=config.settings.dev` en env; puede fallar por Postgres inexistente aún — está bien, aún no lo levantamos.

- [ ] **Step 12: Commit**

```bash
git add src/
git commit -m "feat: add Django project skeleton with settings split"
```

---

### Task 3: Docker Compose — Postgres + Redis + Django

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/docker-compose.yml`
- Create: `docker/entrypoint.sh`

**Interfaces:**
- Consumes: `.env`, `pyproject.toml`.
- Produces: `docker compose up` levanta stack completo, http://localhost:8000/ responde "PT-Docs — Sprint 0 activo".

- [ ] **Step 1: Crear `docker/Dockerfile`**

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install -e .[dev]

COPY src/ ./src/
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd --create-home --shell /bin/bash ptdocs \
    && chown -R ptdocs:ptdocs /app
USER ptdocs

WORKDIR /app/src

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

- [ ] **Step 2: Crear `docker/entrypoint.sh`**

```bash
#!/bin/bash
set -e

echo "Waiting for postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
until curl -f "http://$POSTGRES_HOST:$POSTGRES_PORT" -o /dev/null 2>&1 || nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" 2>/dev/null; do
  sleep 1
done
echo "Postgres reachable."

python manage.py migrate --noinput

exec "$@"
```

- [ ] **Step 3: Crear `docker/docker-compose.yml`**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    env_file:
      - ../.env
    environment:
      POSTGRES_HOST: db
    ports:
      - "8000:8000"
    volumes:
      - ../src:/app/src
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: python manage.py runserver 0.0.0.0:8000

volumes:
  postgres_data:
  redis_data:
```

- [ ] **Step 4: Crear archivo `.env` local (no se commitea)**

```bash
cp .env.example .env
```

- [ ] **Step 5: Levantar el stack y verificar**

Run: `docker compose -f docker/docker-compose.yml up --build`
Espera a que arranque. En otra terminal:

Run: `curl http://localhost:8000/`
Expected: `PT-Docs — Sprint 0 activo`

- [ ] **Step 6: Detener y commit**

```bash
docker compose -f docker/docker-compose.yml down
git add docker/
git commit -m "feat: add docker-compose with Postgres, Redis, and Django dev server"
```

---

### Task 4: Testing tooling — pytest, factory-boy, ruff, mypy, pre-commit

**Files:**
- Create: `pytest.ini`
- Create: `ruff.toml`
- Create: `mypy.ini`
- Create: `.pre-commit-config.yaml`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

**Interfaces:**
- Produces: `pytest` corre verde con 1 smoke test; `ruff check` y `mypy` clean.

- [ ] **Step 1: Crear `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = src
addopts = --strict-markers --tb=short --reuse-db
markers =
    slow: marca tests lentos (no correr en dev loop)
    integration: tests de integración con DB
    e2e: tests end-to-end con Playwright
```

- [ ] **Step 2: Crear `ruff.toml`**

```toml
line-length = 100
target-version = "py312"

[lint]
select = [
    "E", "W",  # pycodestyle
    "F",       # pyflakes
    "I",       # isort
    "N",       # pep8-naming
    "UP",      # pyupgrade
    "B",       # bugbear
    "DJ",      # flake8-django
    "SIM",     # simplify
    "RUF",     # ruff-specific
]
ignore = ["E501"]  # line length handled by formatter

[lint.per-file-ignores]
"tests/*" = ["N802", "N803"]  # tests pueden usar nombres largos
"**/migrations/*" = ["ALL"]
```

- [ ] **Step 3: Crear `mypy.ini`**

```ini
[mypy]
python_version = 3.12
plugins = mypy_django_plugin.main
strict_optional = True
warn_unused_ignores = True
warn_redundant_casts = True
show_error_codes = True
ignore_missing_imports = True

[mypy.plugins.django-stubs]
django_settings_module = config.settings.dev

[mypy-tests.*]
ignore_errors = True

[mypy-*.migrations.*]
ignore_errors = True
```

- [ ] **Step 4: Crear `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 5: Crear `tests/__init__.py`**

Archivo vacío.

- [ ] **Step 6: Crear `tests/conftest.py`**

```python
"""Fixtures compartidas de pytest."""
import pytest


@pytest.fixture
def anonymous_client(client):
    """Cliente HTTP sin login."""
    return client
```

- [ ] **Step 7: Escribir smoke test en `tests/test_smoke.py`**

```python
"""Smoke tests — el sistema arranca."""
import pytest


def test_home_returns_200(anonymous_client):
    response = anonymous_client.get("/")
    assert response.status_code == 200
    assert b"PT-Docs" in response.content


@pytest.mark.django_db
def test_migrations_apply_cleanly():
    """El sólo hecho de que este test corra implica que migrate corrió."""
    from django.contrib.contenttypes.models import ContentType
    assert ContentType.objects.exists()
```

- [ ] **Step 8: Correr tests para verificar que FALLAN inicialmente por falta de auth setup**

Run: `cd src && pytest ../tests/test_smoke.py -v`
Expected: PASS (Django default sin login funciona con la view `home` que devuelve texto simple).

Si falla por conexión a DB local, correr dentro del container:
Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/test_smoke.py -v`

- [ ] **Step 9: Correr ruff y mypy**

Run: `ruff check src tests`
Expected: no issues.

Run: `mypy src`
Expected: no issues (o solo warnings menores que se ignoran).

- [ ] **Step 10: Instalar pre-commit hooks**

Run: `pre-commit install`
Expected: `pre-commit installed at .git/hooks/pre-commit`.

- [ ] **Step 11: Commit**

```bash
git add pytest.ini ruff.toml mypy.ini .pre-commit-config.yaml tests/
git commit -m "test: add pytest, ruff, mypy, pre-commit with smoke test"
```

---

### Task 5: GitHub Actions CI — lint + typecheck + tests

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: pipeline verde en cada push/PR corriendo lint, mypy, pytest.

- [ ] **Step 1: Crear `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: ptdocs_test
          POSTGRES_USER: ptdocs
          POSTGRES_PASSWORD: ptdocs_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DJANGO_SETTINGS_MODULE: config.settings.dev
      DJANGO_SECRET_KEY: ci-secret-key-not-for-prod
      DJANGO_DEBUG: "True"
      DJANGO_ALLOWED_HOSTS: localhost,127.0.0.1
      POSTGRES_DB: ptdocs_test
      POSTGRES_USER: ptdocs
      POSTGRES_PASSWORD: ptdocs_test
      POSTGRES_HOST: localhost
      POSTGRES_PORT: 5432
      REDIS_URL: redis://localhost:6379/0

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]

      - name: Ruff lint
        run: ruff check src tests

      - name: Ruff format check
        run: ruff format --check src tests

      - name: MyPy
        run: mypy src

      - name: Django check
        working-directory: src
        run: python manage.py check

      - name: Pytest
        working-directory: src
        run: pytest ../tests --cov=apps --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: src/coverage.xml
```

- [ ] **Step 2: Verificar sintaxis YAML localmente**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: sin errores.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for lint, mypy, and tests"
```

---

### Task 6: App `core` — modelos base y mixins

**Files:**
- Create: `src/apps/__init__.py`
- Create: `src/apps/core/__init__.py`
- Create: `src/apps/core/apps.py`
- Create: `src/apps/core/mixins.py`
- Create: `src/apps/core/models.py`
- Create: `src/apps/core/admin.py`
- Create: `src/apps/core/migrations/__init__.py`
- Create: `tests/core/__init__.py`
- Create: `tests/core/test_models.py`
- Create: `tests/factories.py`
- Modify: `src/config/settings/base.py` (agregar apps a INSTALLED_APPS)

**Interfaces:**
- Produces:
  - `apps.core.mixins.TimestampedModel` — abstract model con `created_at`, `updated_at`, `created_by`, `updated_by`.
  - `apps.core.models.Firma` — modelo con `nombre`, `nit`, `activa`.
  - `apps.core.models.Usuario` — extiende `AbstractUser`, tiene FK a `Firma`.
  - `apps.core.models.PerfilUsuario` — OneToOne a Usuario, campo `rol` (choices).

- [ ] **Step 1: Escribir tests fallando en `tests/core/test_models.py`**

```python
"""Tests de modelos de la app core."""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_firma_str_returns_nombre():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR Consultores", nit="900123456")
    assert str(firma) == "CR Consultores"


@pytest.mark.django_db
def test_usuario_belongs_to_firma():
    from apps.core.models import Firma
    User = get_user_model()
    firma = Firma.objects.create(nombre="CR Consultores", nit="900123456")
    user = User.objects.create_user(
        username="jyaya",
        email="j@cr.co",
        password="test123",
        firma=firma,
    )
    assert user.firma == firma


@pytest.mark.django_db
def test_perfil_default_rol_is_junior():
    from apps.core.models import Firma, PerfilUsuario, RolUsuario
    User = get_user_model()
    firma = Firma.objects.create(nombre="CR", nit="900")
    user = User.objects.create_user(username="junior", firma=firma)
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    assert perfil.rol == RolUsuario.JUNIOR


@pytest.mark.django_db
def test_timestamped_model_sets_created_at():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="Test", nit="1")
    assert firma.created_at is not None
    assert firma.updated_at is not None
```

- [ ] **Step 2: Correr tests para verificar que FALLAN**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/ -v`
Expected: FAIL con "cannot import apps.core.models".

- [ ] **Step 3: Crear `src/apps/__init__.py`**

Archivo vacío.

- [ ] **Step 4: Crear `src/apps/core/__init__.py`**

Archivo vacío.

- [ ] **Step 5: Crear `src/apps/core/apps.py`**

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
```

- [ ] **Step 6: Crear `src/apps/core/mixins.py`**

```python
"""Mixins reutilizables."""
from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    """Añade timestamps y trazabilidad de usuario."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Creado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Actualizado por",
    )

    class Meta:
        abstract = True
```

- [ ] **Step 7: Crear `src/apps/core/models.py`**

```python
"""Modelos base: Firma, Usuario, PerfilUsuario."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.mixins import TimestampedModel


class Firma(TimestampedModel):
    """Tenant lógico. Por ahora solo hay una instancia (CR Consultores)."""

    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmas"

    def __str__(self) -> str:
        return self.nombre


class Usuario(AbstractUser):
    """Usuario del sistema. Pertenece a una Firma."""

    firma = models.ForeignKey(
        Firma,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
        verbose_name="Firma",
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class RolUsuario(models.TextChoices):
    ADMIN_FIRMA = "admin_firma", "Administrador de firma"
    SENIOR = "senior", "Senior"
    JUNIOR = "junior", "Junior"
    REVISOR = "revisor", "Revisor"


class PerfilUsuario(TimestampedModel):
    """Perfil extendido del usuario con rol."""

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.JUNIOR,
        verbose_name="Rol",
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self) -> str:
        return f"{self.usuario.username} ({self.get_rol_display()})"
```

- [ ] **Step 8: Crear `src/apps/core/admin.py`**

```python
"""Admin de la app core."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.core.models import Firma, PerfilUsuario, Usuario


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "activa", "created_at")
    search_fields = ("nombre", "nit")
    list_filter = ("activa",)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "firma", "is_staff", "is_active")
    list_filter = ("firma", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Firma", {"fields": ("firma",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Firma", {"fields": ("firma",)}),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
```

- [ ] **Step 9: Crear `src/apps/core/migrations/__init__.py`**

Archivo vacío.

- [ ] **Step 10: Actualizar `src/config/settings/base.py` — agregar apps y AUTH_USER_MODEL**

Modificar `INSTALLED_APPS` (agregar `"apps.core",` en la sección de apps propias) y añadir al final:

```python
AUTH_USER_MODEL = "core.Usuario"
```

- [ ] **Step 11: Crear `tests/core/__init__.py`**

Archivo vacío.

- [ ] **Step 12: Crear `tests/factories.py`**

```python
"""Factories globales para tests."""
import factory
from django.contrib.auth import get_user_model

from apps.core.models import Firma, PerfilUsuario, RolUsuario


class FirmaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Firma

    nombre = factory.Sequence(lambda n: f"Firma {n}")
    nit = factory.Sequence(lambda n: f"9001234{n:03d}")
    activa = True


class UsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.co")
    firma = factory.SubFactory(FirmaFactory)


class PerfilUsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PerfilUsuario

    usuario = factory.SubFactory(UsuarioFactory)
    rol = RolUsuario.JUNIOR
```

- [ ] **Step 13: Generar migraciones**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py makemigrations core`
Expected: crea `0001_initial.py`.

- [ ] **Step 14: Correr tests — deben PASAR ahora**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/ -v`
Expected: 4 tests pasan.

- [ ] **Step 15: Commit**

```bash
git add src/apps/core/ src/config/settings/base.py tests/core/ tests/factories.py
git commit -m "feat(core): add Firma, Usuario, PerfilUsuario models with TimestampedModel mixin"
```

---

### Task 7: Roles y grupos — management command `seed_roles`

**Files:**
- Create: `src/apps/core/management/__init__.py`
- Create: `src/apps/core/management/commands/__init__.py`
- Create: `src/apps/core/management/commands/seed_roles.py`
- Create: `tests/core/test_seed_roles.py`

**Interfaces:**
- Consumes: `apps.core.models.RolUsuario`.
- Produces: `python manage.py seed_roles` crea 4 grupos Django: `admin_firma`, `senior`, `junior`, `revisor` (idempotente).

- [ ] **Step 1: Escribir test fallando en `tests/core/test_seed_roles.py`**

```python
"""Tests del management command seed_roles."""
import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.mark.django_db
def test_seed_roles_creates_four_groups():
    call_command("seed_roles")
    names = set(Group.objects.values_list("name", flat=True))
    assert names == {"admin_firma", "senior", "junior", "revisor"}


@pytest.mark.django_db
def test_seed_roles_is_idempotent():
    call_command("seed_roles")
    call_command("seed_roles")  # segundo run no debe fallar ni duplicar
    assert Group.objects.count() == 4
```

- [ ] **Step 2: Correr tests para verificar que FALLAN**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_seed_roles.py -v`
Expected: FAIL con "Unknown command: seed_roles".

- [ ] **Step 3: Crear directorios management**

```bash
mkdir -p src/apps/core/management/commands
```

- [ ] **Step 4: Crear `src/apps/core/management/__init__.py` y `src/apps/core/management/commands/__init__.py`**

Archivos vacíos.

- [ ] **Step 5: Crear `src/apps/core/management/commands/seed_roles.py`**

```python
"""Crea los grupos Django que corresponden a los roles del sistema."""
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.core.models import RolUsuario


class Command(BaseCommand):
    help = "Crea los grupos Django para cada rol de usuario (idempotente)."

    def handle(self, *args, **options) -> None:
        for value, label in RolUsuario.choices:
            group, created = Group.objects.get_or_create(name=value)
            verb = "creado" if created else "existente"
            self.stdout.write(f"  · Grupo '{value}' ({label}) — {verb}")
        self.stdout.write(self.style.SUCCESS("Roles sembrados correctamente."))
```

- [ ] **Step 6: Correr tests — deben PASAR**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_seed_roles.py -v`
Expected: 2 tests pasan.

- [ ] **Step 7: Correr el comando manualmente para validar output**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py seed_roles`
Expected: 4 líneas "Grupo ... creado", y "Roles sembrados correctamente."

- [ ] **Step 8: Commit**

```bash
git add src/apps/core/management/ tests/core/test_seed_roles.py
git commit -m "feat(core): add seed_roles management command"
```

---

### Task 8: Auth con django-allauth + templates base con Tailwind + HTMX

**Files:**
- Create: `src/templates/base.html`
- Create: `src/templates/home.html`
- Create: `src/templates/account/login.html`
- Modify: `src/config/settings/base.py` (allauth setup)
- Modify: `src/config/urls.py` (agregar allauth URLs)
- Create: `tests/test_auth.py`

**Interfaces:**
- Produces: `/accounts/login/`, `/accounts/logout/` funcionales. `home` requiere login.

- [ ] **Step 1: Escribir test fallando en `tests/test_auth.py`**

```python
"""Tests de autenticación."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_redirects_anonymous_to_login(anonymous_client):
    response = anonymous_client.get("/")
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_see_home(client):
    from tests.factories import UsuarioFactory
    user = UsuarioFactory()
    user.set_password("test1234")
    user.save()
    client.login(username=user.username, password="test1234")
    response = client.get("/")
    assert response.status_code == 200
    assert b"PT-Docs" in response.content
```

- [ ] **Step 2: Correr test para verificar que FALLA**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/test_auth.py -v`
Expected: FAIL (home aún no exige login).

- [ ] **Step 3: Modificar `src/config/settings/base.py`**

Agregar a `INSTALLED_APPS`:
```python
"allauth",
"allauth.account",
```

Agregar bloque después de `AUTH_USER_MODEL`:
```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"  # MVP: login local sin verify email
ACCOUNT_SESSION_REMEMBER = True
```

Agregar `"allauth.account.middleware.AccountMiddleware",` al final de `MIDDLEWARE`.

- [ ] **Step 4: Modificar `src/config/urls.py`**

```python
"""URL configuration del proyecto."""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import include, path


@login_required
def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", home, name="home"),
]
```

- [ ] **Step 5: Crear `src/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="es-co">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PT-Docs{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@2.0.0"></script>
    <script defer src="https://unpkg.com/alpinejs@3.14.0/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
    <nav class="bg-white border-b border-gray-200 px-6 py-3">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-semibold">PT-Docs</a>
            {% if user.is_authenticated %}
                <div class="text-sm">
                    <span class="mr-3">{{ user.username }}</span>
                    <a href="{% url 'account_logout' %}" class="text-blue-600 hover:underline">Salir</a>
                </div>
            {% endif %}
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-6 py-8">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 6: Crear `src/templates/home.html`**

```html
{% extends "base.html" %}
{% block content %}
<div class="bg-white shadow rounded-lg p-8">
    <h1 class="text-3xl font-bold mb-2">PT-Docs</h1>
    <p class="text-gray-600">Sprint 0 activo — Bienvenido {{ user.get_full_name|default:user.username }}.</p>
    <p class="mt-4 text-sm text-gray-500">
        Rol: {% if user.perfil %}{{ user.perfil.get_rol_display }}{% else %}sin perfil{% endif %}
    </p>
</div>
{% endblock %}
```

- [ ] **Step 7: Crear `src/templates/account/login.html`**

```html
{% extends "base.html" %}
{% load allauth %}
{% block title %}Iniciar sesión — PT-Docs{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white shadow rounded-lg p-8">
    <h1 class="text-2xl font-bold mb-6">Iniciar sesión</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Entrar
        </button>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 8: Correr migraciones (allauth necesita las suyas)**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py migrate`
Expected: aplica migraciones de allauth y account.

- [ ] **Step 9: Correr tests — deben PASAR**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/test_auth.py -v`
Expected: 2 tests pasan.

- [ ] **Step 10: Verificar visualmente**

Run: `docker compose -f docker/docker-compose.yml up`
Navegador → http://localhost:8000/ → redirige a /accounts/login/.
Crear superuser: `docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser`
Login → ver la página home con nombre de usuario.

- [ ] **Step 11: Commit**

```bash
git add src/config/ src/templates/ tests/test_auth.py
git commit -m "feat(core): add django-allauth auth with base templates (Tailwind + HTMX)"
```

---

### Task 9: App `catalogos` — modelos DIAN

**Files:**
- Create: `src/apps/catalogos/__init__.py`
- Create: `src/apps/catalogos/apps.py`
- Create: `src/apps/catalogos/models.py`
- Create: `src/apps/catalogos/admin.py`
- Create: `src/apps/catalogos/migrations/__init__.py`
- Create: `tests/catalogos/__init__.py`
- Create: `tests/catalogos/test_models.py`
- Modify: `src/config/settings/base.py` (agregar apps.catalogos)

**Interfaces:**
- Produces:
  - `apps.catalogos.models.PaisDIAN` — con `codigo_dian`, `nombre`, `codigo_iso`.
  - `apps.catalogos.models.ParaisoFiscal` — con `pais` (FK PaisDIAN), `fecha_inclusion`, `activo`.
  - `apps.catalogos.models.TipoOperacionDIAN` — con `codigo`, `nombre`, `seccion` (choices), `activa`.
  - `apps.catalogos.models.SectorEconomico` — con `codigo_ciiu`, `nombre`, `division`.
  - `apps.catalogos.models.ParametroFiscal` — con `anio`, `uvt`, `tasa_referencia`.

- [ ] **Step 1: Escribir tests fallando en `tests/catalogos/test_models.py`**

```python
"""Tests de modelos de catalogos DIAN."""
import pytest


@pytest.mark.django_db
def test_pais_dian_str():
    from apps.catalogos.models import PaisDIAN
    pais = PaisDIAN.objects.create(codigo_dian="249", nombre="Estados Unidos", codigo_iso="US")
    assert str(pais) == "Estados Unidos"


@pytest.mark.django_db
def test_tipo_operacion_has_seccion():
    from apps.catalogos.models import SeccionOperacion, TipoOperacionDIAN
    op = TipoOperacionDIAN.objects.create(
        codigo="21",
        nombre="Venta servicios",
        seccion=SeccionOperacion.INGRESO,
    )
    assert op.seccion == SeccionOperacion.INGRESO


@pytest.mark.django_db
def test_paraiso_fiscal_references_pais():
    from apps.catalogos.models import ParaisoFiscal, PaisDIAN
    pais = PaisDIAN.objects.create(codigo_dian="446", nombre="Islas Caimán", codigo_iso="KY")
    pf = ParaisoFiscal.objects.create(pais=pais)
    assert pf.pais.nombre == "Islas Caimán"


@pytest.mark.django_db
def test_parametro_fiscal_unique_per_anio():
    from apps.catalogos.models import ParametroFiscal
    ParametroFiscal.objects.create(anio=2025, uvt=49799)
    with pytest.raises(Exception):
        ParametroFiscal.objects.create(anio=2025, uvt=50000)
```

- [ ] **Step 2: Correr tests para verificar que FALLAN**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/catalogos/ -v`
Expected: FAIL con "cannot import apps.catalogos.models".

- [ ] **Step 3: Crear `src/apps/catalogos/__init__.py`**

Archivo vacío.

- [ ] **Step 4: Crear `src/apps/catalogos/apps.py`**

```python
from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalogos"
    verbose_name = "Catálogos DIAN"
```

- [ ] **Step 5: Crear `src/apps/catalogos/models.py`**

```python
"""Catálogos oficiales DIAN."""
from django.db import models

from apps.core.mixins import TimestampedModel


class PaisDIAN(models.Model):
    """Códigos oficiales de país usados por DIAN."""

    codigo_dian = models.CharField(max_length=5, unique=True, verbose_name="Código DIAN")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_iso = models.CharField(max_length=3, blank=True, verbose_name="Código ISO")

    class Meta:
        verbose_name = "País DIAN"
        verbose_name_plural = "Países DIAN"
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class ParaisoFiscal(TimestampedModel):
    """Países/jurisdicciones catalogados como paraísos fiscales (Decreto 1966/2014)."""

    pais = models.OneToOneField(
        PaisDIAN,
        on_delete=models.PROTECT,
        related_name="paraiso_fiscal",
        verbose_name="País",
    )
    fecha_inclusion = models.DateField(null=True, blank=True, verbose_name="Fecha inclusión")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Paraíso fiscal"
        verbose_name_plural = "Paraísos fiscales"

    def __str__(self) -> str:
        return f"{self.pais.nombre} (paraíso fiscal)"


class SeccionOperacion(models.TextChoices):
    INGRESO = "ingreso", "Operación de ingreso"
    EGRESO = "egreso", "Operación de egreso"
    ACTIVO = "activo", "Operación con activos"
    PASIVO = "pasivo", "Operación con pasivos"


class TipoOperacionDIAN(models.Model):
    """Catálogo oficial de tipos de operación con vinculados."""

    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código DIAN")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    seccion = models.CharField(
        max_length=10,
        choices=SeccionOperacion.choices,
        verbose_name="Sección",
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Tipo de operación DIAN"
        verbose_name_plural = "Tipos de operación DIAN"
        ordering = ("codigo",)

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre}"


class SectorEconomico(models.Model):
    """Sectores CIIU rev. 4 A.C. (DANE)."""

    codigo_ciiu = models.CharField(max_length=6, unique=True, verbose_name="Código CIIU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    division = models.CharField(max_length=100, blank=True, verbose_name="División")

    class Meta:
        verbose_name = "Sector económico (CIIU)"
        verbose_name_plural = "Sectores económicos (CIIU)"
        ordering = ("codigo_ciiu",)

    def __str__(self) -> str:
        return f"{self.codigo_ciiu} — {self.nombre}"


class ParametroFiscal(models.Model):
    """Parámetros anuales: UVT, tasas de referencia, umbrales."""

    anio = models.PositiveIntegerField(unique=True, verbose_name="Año gravable")
    uvt = models.PositiveIntegerField(verbose_name="Valor UVT (COP)")
    tasa_referencia = models.DecimalField(
        max_digits=6, decimal_places=4, null=True, blank=True,
        verbose_name="Tasa de referencia (%)",
    )

    class Meta:
        verbose_name = "Parámetro fiscal"
        verbose_name_plural = "Parámetros fiscales"
        ordering = ("-anio",)

    def __str__(self) -> str:
        return f"Parámetros {self.anio}"
```

- [ ] **Step 6: Crear `src/apps/catalogos/admin.py`**

```python
"""Admin de catalogos DIAN."""
from django.contrib import admin

from apps.catalogos.models import (
    ParaisoFiscal,
    PaisDIAN,
    ParametroFiscal,
    SectorEconomico,
    TipoOperacionDIAN,
)


@admin.register(PaisDIAN)
class PaisDIANAdmin(admin.ModelAdmin):
    list_display = ("codigo_dian", "nombre", "codigo_iso")
    search_fields = ("nombre", "codigo_dian", "codigo_iso")


@admin.register(ParaisoFiscal)
class ParaisoFiscalAdmin(admin.ModelAdmin):
    list_display = ("pais", "fecha_inclusion", "activo")
    list_filter = ("activo",)


@admin.register(TipoOperacionDIAN)
class TipoOperacionDIANAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "seccion", "activa")
    list_filter = ("seccion", "activa")
    search_fields = ("codigo", "nombre")


@admin.register(SectorEconomico)
class SectorEconomicoAdmin(admin.ModelAdmin):
    list_display = ("codigo_ciiu", "nombre", "division")
    search_fields = ("codigo_ciiu", "nombre", "division")


@admin.register(ParametroFiscal)
class ParametroFiscalAdmin(admin.ModelAdmin):
    list_display = ("anio", "uvt", "tasa_referencia")
```

- [ ] **Step 7: Crear `src/apps/catalogos/migrations/__init__.py`**

Archivo vacío.

- [ ] **Step 8: Actualizar `src/config/settings/base.py`**

Agregar `"apps.catalogos",` a INSTALLED_APPS después de `"apps.core",`.

- [ ] **Step 9: Crear `tests/catalogos/__init__.py`**

Archivo vacío.

- [ ] **Step 10: Generar migraciones**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py makemigrations catalogos`
Expected: crea `0001_initial.py` con los 5 modelos.

- [ ] **Step 11: Correr tests — deben PASAR**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/catalogos/ -v`
Expected: 4 tests pasan.

- [ ] **Step 12: Commit**

```bash
git add src/apps/catalogos/ src/config/settings/base.py tests/catalogos/
git commit -m "feat(catalogos): add DIAN reference models (paises, paraisos, tipos operacion, sectores)"
```

---

### Task 10: Seed data de catálogos DIAN (management command)

**Files:**
- Create: `src/apps/catalogos/data/paises_dian.csv`
- Create: `src/apps/catalogos/data/paraisos_fiscales.csv`
- Create: `src/apps/catalogos/data/tipos_operacion.csv`
- Create: `src/apps/catalogos/data/sectores_ciiu.csv`
- Create: `src/apps/catalogos/data/parametros_fiscales.csv`
- Create: `src/apps/catalogos/management/__init__.py`
- Create: `src/apps/catalogos/management/commands/__init__.py`
- Create: `src/apps/catalogos/management/commands/seed_catalogos.py`
- Create: `tests/catalogos/test_seed_catalogos.py`

**Interfaces:**
- Consumes: modelos de `apps.catalogos.models`.
- Produces: `python manage.py seed_catalogos` carga los 5 CSVs (idempotente).

**Nota:** los CSVs se pueden derivar de los manuales DIAN oficiales en `_materiales/precios de tranferencia/` durante la implementación. Para el MVP arrancamos con un subconjunto mínimo suficiente para el caso END GAME.

- [ ] **Step 1: Escribir test fallando en `tests/catalogos/test_seed_catalogos.py`**

```python
"""Tests de seed_catalogos."""
import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_seed_catalogos_loads_paises():
    from apps.catalogos.models import PaisDIAN
    call_command("seed_catalogos")
    assert PaisDIAN.objects.count() >= 20  # arranque con al menos 20 países comunes
    assert PaisDIAN.objects.filter(codigo_dian="249").exists()  # Estados Unidos


@pytest.mark.django_db
def test_seed_catalogos_loads_tipos_operacion():
    from apps.catalogos.models import TipoOperacionDIAN
    call_command("seed_catalogos")
    assert TipoOperacionDIAN.objects.count() >= 10


@pytest.mark.django_db
def test_seed_catalogos_loads_parametros_fiscales_2025():
    from apps.catalogos.models import ParametroFiscal
    call_command("seed_catalogos")
    assert ParametroFiscal.objects.filter(anio=2025).exists()


@pytest.mark.django_db
def test_seed_catalogos_is_idempotent():
    from apps.catalogos.models import PaisDIAN
    call_command("seed_catalogos")
    count = PaisDIAN.objects.count()
    call_command("seed_catalogos")
    assert PaisDIAN.objects.count() == count  # no duplica
```

- [ ] **Step 2: Correr tests para verificar que FALLAN**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/catalogos/test_seed_catalogos.py -v`
Expected: FAIL con "Unknown command: seed_catalogos".

- [ ] **Step 3: Crear `src/apps/catalogos/data/paises_dian.csv`**

Contenido mínimo (subset de países comunes; ampliar según manual DIAN 4-Manual-presentacion-documentacion-comprobatoria.pdf). Encoding UTF-8, delimitador `,`:

```csv
codigo_dian,nombre,codigo_iso
169,Colombia,CO
249,Estados Unidos,US
138,España,ES
211,Reino Unido,GB
239,Alemania,DE
276,Francia,FR
586,Panamá,PA
575,México,MX
024,Argentina,AR
105,Brasil,BR
124,Chile,CL
446,Islas Caimán,KY
447,Bermudas,BM
473,Barbados,BB
239,Alemania,DE
392,Japón,JP
410,Corea del Sur,KR
344,Hong Kong,HK
702,Singapur,SG
158,China,CN
```

**Nota**: durante la implementación real, el desarrollador debe validar la lista completa contra el manual oficial DIAN y ampliar el CSV.

- [ ] **Step 4: Crear `src/apps/catalogos/data/paraisos_fiscales.csv`**

```csv
codigo_pais_dian,fecha_inclusion,notas
446,2014-10-07,Decreto 1966/2014
447,2014-10-07,Decreto 1966/2014
473,2014-10-07,Decreto 1966/2014
```

**Nota**: lista real derivable del Decreto 1966/2014 y actualizaciones.

- [ ] **Step 5: Crear `src/apps/catalogos/data/tipos_operacion.csv`**

Subset mínimo (ampliar contra manuales DIAN):

```csv
codigo,nombre,seccion
21,Venta de servicios,ingreso
22,Comisiones,ingreso
23,Intereses recibidos,ingreso
24,Regalías recibidas,ingreso
31,Compra de servicios,egreso
32,Pago de comisiones,egreso
33,Intereses pagados,egreso
34,Regalías pagadas,egreso
41,Compra de activos fijos,activo
42,Adquisición de intangibles,activo
51,Préstamos recibidos,pasivo
52,Préstamos otorgados,activo
```

- [ ] **Step 6: Crear `src/apps/catalogos/data/sectores_ciiu.csv`**

Subset mínimo relevante (gaming, tech, servicios). Real: sección J y M del CIIU rev. 4 A.C.:

```csv
codigo_ciiu,nombre,division
5820,"Edición de programas de informática (software)",Información
6201,"Actividades de desarrollo de sistemas informáticos",Información
6202,"Actividades de consultoría informática",Información
6209,"Otras actividades de tecnologías de información",Información
6311,"Procesamiento de datos, alojamiento y actividades conexas",Información
7020,"Actividades de consultoría de gestión",Servicios profesionales
7220,"Investigación en ciencias sociales y humanidades",Servicios profesionales
```

- [ ] **Step 7: Crear `src/apps/catalogos/data/parametros_fiscales.csv`**

```csv
anio,uvt,tasa_referencia
2023,42412,0.1300
2024,47065,0.1275
2025,49799,0.0975
```

**Nota**: valores oficiales DIAN. UVT 2025 debe confirmarse antes de deploy.

- [ ] **Step 8: Crear `src/apps/catalogos/management/__init__.py` y `commands/__init__.py`**

Archivos vacíos.

- [ ] **Step 9: Crear `src/apps/catalogos/management/commands/seed_catalogos.py`**

```python
"""Carga los catálogos DIAN desde archivos CSV embebidos."""
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.catalogos.models import (
    ParaisoFiscal,
    PaisDIAN,
    ParametroFiscal,
    SectorEconomico,
    TipoOperacionDIAN,
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class Command(BaseCommand):
    help = "Carga catálogos DIAN (idempotente)."

    def handle(self, *args, **options) -> None:
        self._load_paises()
        self._load_paraisos()
        self._load_tipos_operacion()
        self._load_sectores()
        self._load_parametros()
        self.stdout.write(self.style.SUCCESS("Catálogos cargados."))

    def _load_paises(self) -> None:
        path = DATA_DIR / "paises_dian.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                PaisDIAN.objects.update_or_create(
                    codigo_dian=row["codigo_dian"],
                    defaults={
                        "nombre": row["nombre"],
                        "codigo_iso": row["codigo_iso"],
                    },
                )
        self.stdout.write(f"  · Países: {PaisDIAN.objects.count()}")

    def _load_paraisos(self) -> None:
        path = DATA_DIR / "paraisos_fiscales.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    pais = PaisDIAN.objects.get(codigo_dian=row["codigo_pais_dian"])
                except PaisDIAN.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"  · País {row['codigo_pais_dian']} no encontrado, saltando paraíso."
                    ))
                    continue
                ParaisoFiscal.objects.update_or_create(
                    pais=pais,
                    defaults={
                        "fecha_inclusion": date.fromisoformat(row["fecha_inclusion"])
                            if row["fecha_inclusion"] else None,
                        "notas": row.get("notas", ""),
                        "activo": True,
                    },
                )
        self.stdout.write(f"  · Paraísos fiscales: {ParaisoFiscal.objects.count()}")

    def _load_tipos_operacion(self) -> None:
        path = DATA_DIR / "tipos_operacion.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                TipoOperacionDIAN.objects.update_or_create(
                    codigo=row["codigo"],
                    defaults={
                        "nombre": row["nombre"],
                        "seccion": row["seccion"],
                        "activa": True,
                    },
                )
        self.stdout.write(f"  · Tipos de operación: {TipoOperacionDIAN.objects.count()}")

    def _load_sectores(self) -> None:
        path = DATA_DIR / "sectores_ciiu.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                SectorEconomico.objects.update_or_create(
                    codigo_ciiu=row["codigo_ciiu"],
                    defaults={
                        "nombre": row["nombre"],
                        "division": row.get("division", ""),
                    },
                )
        self.stdout.write(f"  · Sectores CIIU: {SectorEconomico.objects.count()}")

    def _load_parametros(self) -> None:
        path = DATA_DIR / "parametros_fiscales.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ParametroFiscal.objects.update_or_create(
                    anio=int(row["anio"]),
                    defaults={
                        "uvt": int(row["uvt"]),
                        "tasa_referencia": Decimal(row["tasa_referencia"])
                            if row["tasa_referencia"] else None,
                    },
                )
        self.stdout.write(f"  · Parámetros fiscales: {ParametroFiscal.objects.count()}")
```

- [ ] **Step 10: Correr tests — deben PASAR**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/catalogos/test_seed_catalogos.py -v`
Expected: 4 tests pasan.

- [ ] **Step 11: Ejecutar seed manualmente y verificar en admin**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py seed_catalogos`
Expected: output con conteos.

Verificar en http://localhost:8000/admin/ que las tablas tienen datos.

- [ ] **Step 12: Commit**

```bash
git add src/apps/catalogos/data/ src/apps/catalogos/management/ tests/catalogos/test_seed_catalogos.py
git commit -m "feat(catalogos): add seed_catalogos command with initial DIAN data"
```

---

### Task 11: Auditoría con django-simple-history

**Files:**
- Modify: `src/config/settings/base.py` (agregar `simple_history` + middleware)
- Modify: `src/apps/core/models.py` (agregar HistoricalRecords a modelos sensibles)
- Create: `tests/core/test_audit.py`

**Interfaces:**
- Produces: cambios en `Firma`, `Usuario`, `PerfilUsuario` quedan en tablas históricas de django-simple-history, con `history_user` = usuario logueado.

- [ ] **Step 1: Escribir test fallando en `tests/core/test_audit.py`**

```python
"""Tests de auditoría con django-simple-history."""
import pytest


@pytest.mark.django_db
def test_firma_creates_history_on_save():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR Test", nit="900")
    assert firma.history.count() == 1
    assert firma.history.first().history_type == "+"


@pytest.mark.django_db
def test_firma_history_on_update():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR", nit="900")
    firma.nombre = "CR Consultores"
    firma.save()
    assert firma.history.count() == 2
    latest = firma.history.first()
    assert latest.history_type == "~"
    assert latest.nombre == "CR Consultores"
```

- [ ] **Step 2: Correr test para verificar que FALLA**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_audit.py -v`
Expected: FAIL con `AttributeError: 'Firma' object has no attribute 'history'`.

- [ ] **Step 3: Modificar `src/config/settings/base.py`**

Agregar a `INSTALLED_APPS`:
```python
"simple_history",
```

Agregar a `MIDDLEWARE` (después de AuthenticationMiddleware):
```python
"simple_history.middleware.HistoryRequestMiddleware",
```

- [ ] **Step 4: Modificar `src/apps/core/models.py` — agregar HistoricalRecords**

Al inicio del archivo, después de imports Django existentes:
```python
from simple_history.models import HistoricalRecords
```

Dentro de cada modelo (`Firma`, `Usuario`, `PerfilUsuario`), añadir como último atributo antes de `Meta`:
```python
    history = HistoricalRecords()
```

- [ ] **Step 5: Generar migraciones**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py makemigrations`
Expected: nuevas migraciones creando tablas `HistoricalFirma`, `HistoricalUsuario`, `HistoricalPerfilUsuario`.

- [ ] **Step 6: Aplicar migraciones**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py migrate`

- [ ] **Step 7: Correr tests — deben PASAR**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_audit.py -v`
Expected: 2 tests pasan.

- [ ] **Step 8: Correr TODA la suite para verificar no rompe nada más**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests -v`
Expected: todos los tests previos siguen pasando.

- [ ] **Step 9: Commit**

```bash
git add src/config/settings/base.py src/apps/core/models.py src/apps/core/migrations/ tests/core/test_audit.py
git commit -m "feat(core): add audit trail with django-simple-history"
```

---

### Task 12: Django-Q + Redis — task async minimal

**Files:**
- Modify: `src/config/settings/base.py` (Django-Q config)
- Modify: `docker/docker-compose.yml` (worker service)
- Create: `src/apps/core/tasks.py`
- Create: `tests/core/test_tasks.py`

**Interfaces:**
- Produces:
  - Función `apps.core.tasks.ping()` que retorna `"pong"`, encolable vía `django_q.tasks.async_task`.
  - Worker Django-Q corriendo en contenedor separado.

- [ ] **Step 1: Escribir test fallando en `tests/core/test_tasks.py`**

```python
"""Tests de tasks async."""


def test_ping_returns_pong():
    """Función pura testeable sin async."""
    from apps.core.tasks import ping
    assert ping() == "pong"
```

- [ ] **Step 2: Correr test — FALLA**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_tasks.py -v`
Expected: FAIL con "cannot import apps.core.tasks".

- [ ] **Step 3: Crear `src/apps/core/tasks.py`**

```python
"""Tasks async del core."""


def ping() -> str:
    """Task de prueba para validar el pipeline Django-Q."""
    return "pong"
```

- [ ] **Step 4: Modificar `src/config/settings/base.py`**

Agregar a `INSTALLED_APPS`:
```python
"django_q",
```

Al final del archivo:
```python
import os as _os

Q_CLUSTER = {
    "name": "ptdocs",
    "workers": 2,
    "recycle": 500,
    "timeout": 300,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "label": "Django Q",
    "redis": _os.environ.get("REDIS_URL", "redis://redis:6379/0"),
}
```

- [ ] **Step 5: Modificar `docker/docker-compose.yml` — agregar servicio `worker`**

Añadir al bloque `services:`:

```yaml
  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    env_file:
      - ../.env
    environment:
      POSTGRES_HOST: db
    volumes:
      - ../src:/app/src
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: python manage.py qcluster
```

- [ ] **Step 6: Generar y aplicar migraciones (django-q crea tablas)**

Run: `docker compose -f docker/docker-compose.yml run --rm web python manage.py migrate`

- [ ] **Step 7: Correr tests — PASAN**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests/core/test_tasks.py -v`
Expected: 1 test pasa.

- [ ] **Step 8: Levantar stack completo y verificar worker arranca**

Run: `docker compose -f docker/docker-compose.yml up`
Expected: logs muestran `worker` conectado a Redis, listo para tasks.

En otra terminal:
Run: `docker compose -f docker/docker-compose.yml exec web python manage.py shell -c "from django_q.tasks import async_task; async_task('apps.core.tasks.ping')"`
Expected: worker log muestra ejecución exitosa.

- [ ] **Step 9: Commit**

```bash
git add src/config/settings/base.py src/apps/core/tasks.py docker/docker-compose.yml src/apps/core/migrations/ tests/core/test_tasks.py
git commit -m "feat(core): add django-q worker with ping task"
```

---

### Task 13: Bootstrap script + docs finales de Sprint 0

**Files:**
- Create: `scripts/bootstrap.sh`
- Modify: `README.md` (documentación completa Sprint 0)

**Interfaces:**
- Produces: comando `./scripts/bootstrap.sh` levanta stack + migra + seed + crea superuser interactivo.

- [ ] **Step 1: Crear `scripts/bootstrap.sh`**

```bash
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
```

- [ ] **Step 2: Hacer ejecutable (en shell Unix; en Windows se ejecuta con bash)**

Run: `chmod +x scripts/bootstrap.sh` (skip en Windows).

- [ ] **Step 3: Actualizar `README.md`**

```markdown
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
```

- [ ] **Step 4: Correr bootstrap desde cero para validar**

Run: `bash scripts/bootstrap.sh`
Expected: completa sin errores, catálogos cargados.

- [ ] **Step 5: Correr la suite completa una vez más**

Run: `docker compose -f docker/docker-compose.yml run --rm web pytest ../tests -v --cov=apps --cov-report=term`
Expected: todos verdes, cobertura ≥ 70%.

- [ ] **Step 6: Verificar CI localmente antes de push**

Run: `ruff check src tests && ruff format --check src tests && mypy src`
Expected: sin errores.

- [ ] **Step 7: Commit**

```bash
git add scripts/ README.md
git commit -m "docs: add bootstrap script and complete Sprint 0 documentation"
```

---

## Definition of Done — Sprint 0

Sprint 0 se considera completo cuando:

1. ✅ `bash scripts/bootstrap.sh` desde repo recién clonado deja el sistema listo.
2. ✅ `docker compose up` arranca Postgres, Redis, Django, Django-Q worker.
3. ✅ http://localhost:8000/ redirige a login si anónimo; muestra home tras login.
4. ✅ Admin Django tiene poblados: 4 grupos, ≥20 países DIAN, ≥3 paraísos fiscales, ≥10 tipos operación, ≥5 sectores CIIU, parámetros fiscales 2023-2025.
5. ✅ Modificar una `Firma` desde admin genera registro en `HistoricalFirma`.
6. ✅ `docker compose exec web python manage.py shell -c "from django_q.tasks import async_task; async_task('apps.core.tasks.ping')"` ejecuta en worker.
7. ✅ `pytest` corre verde con cobertura global ≥ 70%.
8. ✅ `ruff check`, `ruff format --check`, `mypy` corren sin errores.
9. ✅ Pipeline CI de GitHub Actions pasa en verde en el primer push.
10. ✅ README explica setup en ≤ 5 comandos.

## Handoff a Sprint 1

Sprint 1 arrancará con estas fundaciones ya sólidas:
- Modelos `Firma`, `Usuario`, `PerfilUsuario` disponibles como FKs para `Cliente`.
- `TimestampedModel` mixin reusable.
- Auditoría configurada — solo agregar `HistoricalRecords` a nuevos modelos.
- Catálogos DIAN referenciables desde `Cliente` (sector), `Operacion` (tipo operación, país).
- Tests, lint, mypy, CI ya listos — Sprint 1 solo agrega tests, no re-setup.
- Django-Q worker listo — Sprint 3 lo consumirá para renderizado docx.

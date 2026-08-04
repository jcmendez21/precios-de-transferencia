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

COPY pyproject.toml README.md pytest.ini ruff.toml mypy.ini ./
# Create stub package directories so pip editable install can resolve package-dir = {"": "src"}
RUN mkdir -p src/config src/apps \
    && touch src/config/__init__.py src/apps/__init__.py
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

# Build Stage
FROM python:3.12-slim AS builder

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/opt/poetry_cache

RUN pip install --no-cache-dir poetry==1.8.3

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root --no-directory --compile

COPY app/ ./app/
# (If we needed to build any local wheel we'd do it here, but no root needed for this small app)

# Release Stage
FROM python:3.12-slim AS key-server-image

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

RUN groupadd -r maskd_user && useradd -r -g maskd_user maskd_user

COPY --chown=maskd_user:maskd_user --from=builder /app /app

USER maskd_user
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.main:app"]

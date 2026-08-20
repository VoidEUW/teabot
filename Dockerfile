# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd -r -g 10001 teabot \
 && useradd -r -u 10001 -g teabot -d /app -s /sbin/nologin teabot

COPY --from=builder /app /app

RUN mkdir -p /app/data \
 && chown -R teabot:teabot /app/data \
 && chmod +x docker-entrypoint.sh

USER teabot
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]

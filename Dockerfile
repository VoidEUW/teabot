# syntax = docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime

WORKDIR /app

RUN groupadd -r teabot && useradd -r -g teabot -d /app -s /sbin/nologin teabot

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

RUN mkdir -p /app/data && chown -R teabot:teabot /app/data

RUN chmod +x docker-entrypoint.sh

USER teabot

VOLUME ["/app/data"]

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
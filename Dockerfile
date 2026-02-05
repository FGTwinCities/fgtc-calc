# syntax=docker.io/docker/dockerfile:1.7-labs

# ===============================================
# Stage 0: Base Image
# ===============================================
FROM astral/uv:python3.13-alpine3.23 as base

RUN apk add --no-cache tzdata npm


# ===============================================
# Stage 1: Builder
# ===============================================
FROM base as builder

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --parents pyproject.toml uv.lock package.json package-lock.json /app/

RUN npm install

RUN uv sync --frozen --no-editable --no-install-project

COPY --parents app/ src/ assets/ templates/ vite.config.ts README.md /app/

RUN uv run app assets build && \
    uv build


# ===============================================
# Stage 2: Runtime
# ===============================================
FROM base as runtime

ENV LITESTAR_APP="app.asgi:create_app" \
    DEV_MODE=0

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY --from=builder /app/dist/*.whl /tmp/

WORKDIR /app

COPY --parents alembic/ alembic.ini /app/

RUN uv venv && \
    uv pip install --quiet --disable-pip-version-check --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*

COPY --from=builder /app/public /app/public

STOPSIGNAL SIGTERM
EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "app", "run", "--host", "0.0.0.0", "--port", "8585"]
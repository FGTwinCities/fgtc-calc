# syntax=docker.io/docker/dockerfile:1.7-labs
FROM astral/uv:python3.13-alpine3.23

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --parents app/ assets/ templates/ pyproject.toml uv.lock /app/

RUN uv sync --locked

EXPOSE 8000

ENTRYPOINT ["uv", "run", "litestar", "run", "--host", "0.0.0.0", "--port", "8000"]
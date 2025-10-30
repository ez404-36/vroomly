FROM python:3.13-slim as backend-base

ARG python_version=3.13
ARG backend_dir=/app

ARG UID
ARG GID

WORKDIR $backend_dir


RUN apt-get update --quiet && \
    apt-get install -y git


# Cоздание пользователя
RUN groupadd -g "${GID}" vroomly && \
    useradd --uid "${UID}" --gid vroomly --shell /bin/bash -d /app vroomly && \
    chown -R vroomly:vroomly /app


RUN mkdir -p /.venv && chown -R vroomly:vroomly /.venv

COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv
ENV PATH="/root/.cargo/bin:${PATH}"

COPY --chown=vroomly:vroomly pyproject.toml uv.lock $backend_dir
COPY .pre-commit-config.yaml $backend_dir

USER vroomly
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen


FROM backend-base as codegen

USER root

# Обновляем пакеты и ставим Node.js + npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g json-schema-to-typescript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


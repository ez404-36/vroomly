FROM python:3.13-slim as backend-base

ARG python_version=3.13
ARG backend_dir=/app

ARG UID
ARG GID

WORKDIR $backend_dir

ENV PYTHONUNBEFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=False \
    LC_CTYPE=ru_RU.UTF-8 \
    LANG=ru_RU.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    ACCEPT_EULA=Y


ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"


RUN apt-get update --quiet && \
    apt-get install -y git


# Cоздание пользователя
RUN groupadd -g "${GID}" vroomly && \
    useradd --uid "${UID}" --gid vroomly --shell /bin/bash -d /app vroomly && \
    chown -R vroomly:vroomly /app


COPY --link --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv
ENV PATH="/root/.cargo/bin:${PATH}"

RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
      --locked \
      --no-editable \
      --no-install-project

USER vroomly


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


USER vroomly

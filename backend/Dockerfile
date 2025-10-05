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


COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

ENV UV_PYTHON="python$python_version" \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/.venv \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PYTHONOPTIMIZE=1

COPY pyproject.toml uv.lock .pre-commit-config.yaml $backend_dir

RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
uv sync \
  --no-dev \
  --no-install-project \
  --frozen
EOF

ENV UV_PYTHON=$UV_PROJECT_ENVIRONMENT

COPY .python-version $backend_dir

RUN --mount=type=cache,destination=/root/.cache/uv
RUN <<EOF
# cd /app
sed -Ei "s/^(version = \")0\.0\.0(\")$/\1$(cat .python-version)\2/" pyproject.toml
uv sync \
  --no-dev \
  --no-editable \
  --frozen
EOF

RUN chmod 777 /.venv/

FROM backend-base as backend-with-hooks

RUN pip install pre-commit


FROM backend-base as codegen

# Обновляем пакеты и ставим Node.js + npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g json-schema-to-typescript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


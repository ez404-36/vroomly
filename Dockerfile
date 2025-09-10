FROM python:3.13-slim as build

ARG python_version=3.13

WORKDIR /app

SHELL ["/bin/sh", "-exc"]


RUN apt-get update --quiet


COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

ENV UV_PYTHON="python$python_version" \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/.venv \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PYTHONOPTIMIZE=1

COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
uv sync \
  --no-dev \
  --no-install-project \
  --frozen
EOF

ENV UV_PYTHON=$UV_PROJECT_ENVIRONMENT

COPY .python-version /app/
COPY . /app

RUN --mount=type=cache,destination=/root/.cache/uv
RUN <<EOF
# cd /app
sed -Ei "s/^(version = \")0\.0\.0(\")$/\1$(cat .python-version)\2/" pyproject.toml
uv sync \
  --no-dev \
  --no-editable \
  --frozen
EOF

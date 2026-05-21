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


# Переменные окружения для пакетного менеджера UV
# отключить локальное кеширование пакетов
ENV UV_NO_CACHE=1
# не скачивать python с помощью UV
ENV UV_PYTHON_DOWNLOADS=never
# не использовать управляемый python
ENV UV_NO_MANAGED_PYTHON=1
# устанавливаемая версия
ENV UV_VERSION=0.11

# Cоздание пользователя
RUN groupadd -g "${GID}" vroomly && \
    useradd --uid "${UID}" --gid vroomly --shell /bin/bash -d /app vroomly && \
    chown -R vroomly:vroomly /app


RUN apt-get update --quiet

RUN pip install "uv==${UV_VERSION}" && \
    uv --version

RUN uv venv /app/.venv

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
      --locked \
      --no-editable \
      --no-install-project

COPY --chown=vroomly:vroomly entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER vroomly

ENTRYPOINT ["/entrypoint.sh"]

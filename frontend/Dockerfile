ARG node_version=24

FROM node:${node_version}-bullseye AS builder

ARG frontend_dir=/app

ARG UID
ARG GID

WORKDIR $frontend_dir

RUN apt update -qq && apt install -y --no-install-recommends net-tools
RUN usermod -u "${UID}" node
RUN groupmod -g "${GID}" node

EXPOSE 5173

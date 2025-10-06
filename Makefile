base-setup: network-prepare volumes-prepare env-prepare
docker-setup: up-project

setup-for-backend: base-setup docker-setup install-git-hooks
setup-for-frontend: base-setup set-profile-frontend docker-setup

network-prepare:
	docker network create vroomly || true

volumes-prepare:
	docker volume create vroomly-postgres-data || true

env-prepare:
	cp .env.example .env

set-profile-frontend:
	sed -i 's/COMPOSE_PROFILES=vr-backend/COMPOSE_PROFILES=vr-frontend/' .env

up-project:
	docker compose up -d

install-git-hooks:
	docker compose run --rm backend-build bash -c "pre-commit install --install-hooks --overwrite"
	./backend/scripts/setup_docker_precommit.sh vroomly-backend-build-1
	docker compose stop backend-build

seeds:
	docker compose up -d seed

tests:
	docker compose up -d tests

codegen:
	docker compose up -d codegen

recreate-db:
	docker exec -it vroomly-db-1 bash -c "psql -U postgres -f /app/scripts/recreate_db.sql"


.PHONY: base-setup docker-setup setup-for-backend setup-for-frontend network-prepare volumes-prepare env-prepare set-profile-frontend up-project seeds tests codegen

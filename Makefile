base-setup: network-prepare volumes-prepare env-prepare
docker-setup: up-project

setup-for-backend: base-setup docker-setup
setup-for-frontend: base-setup set-profile-frontend docker-setup

network-prepare:
	@echo "Проверка и создание сети vroomly (подсеть 10.245.0.0/16 для избежания конфликтов с VPN)..."
	@if docker network inspect vroomly >/dev/null 2>&1; then \
		echo "Сеть vroomly уже существует. Если есть конфликт с VPN, удалите: docker network rm vroomly"; \
	else \
		docker network create --subnet=10.245.0.0/16 vroomly; \
	fi

volumes-prepare:
	docker volume create vroomly-postgres-data || true

env-prepare:
	cp .env.example .env

set-profile-frontend:
	sed -i 's/COMPOSE_PROFILES=vr-backend/COMPOSE_PROFILES=vr-frontend/' .env

up-project:
	docker compose up -d

seeds:
	docker compose up -d seed

tests:
	docker compose up -d tests

codegen:
	docker compose run --rm codegen

recreate-db:
	docker exec -it vroomly-db-1 bash -c "psql -U postgres -f /app/scripts/recreate_db.sql"

lint:
	docker compose up -d linters

typecheck:
	docker compose run --rm linters ty check .


.PHONY: base-setup docker-setup setup-for-backend setup-for-frontend network-prepare volumes-prepare env-prepare set-profile-frontend up-project seeds tests codegen lint typecheck

setup-for-backend: network-prepare volumes-prepare env-prepare up-project seeds
setup-for-frontend: network-prepare volumes-prepare env-prepare set-profile-frontend up-project seeds

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

seeds:
	docker compose up -d seed


.PHONY: setup-for-backend setup-for-frontend network-prepare volumes-prepare env-prepare set-profile-frontend up-project seeds

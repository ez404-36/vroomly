# Vroomly

### Локальное развёртывание проекта

1. Создать docker сеть и docker volumes
```bash
docker network create vroomly
docker volume create vroomly-postgres-data
```

2. Скопировать содержимое .env.example в .env
```bash
cp .env.example .env
```

3. Указать профиль запуска
В проекте есть несколько определенных профилей для запуска приложения в docker:
- vr-backend - запускает БД и фронтенд
- vr-frontend - запускает БД, бекенд и применяет миграции
В файле `.env` задать нужный профиль в COMPOSE_PROFILES. Профили можно комбинировать между собой, указав их через запятую

4. Запустить проект

```bash
docker compose up -d
```

5. Наполнение БД первичными данными
```bash
docker compose up -d seed
```

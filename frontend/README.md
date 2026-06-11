# Проект Vroomly

Веб-приложение для автовладельцев

## Технологии:

- HTML
- CSS
- React
- TypeScript
- Redux Toolkit
- React Router
- Vite
- Radix UI

## Основные Команды

### Запуск сервера для разработки

```shell
npm run dev
```

### Сборка проекта

```shell
npm run build
```

### Форматирование, унификация кода

```shell
npm run lint
```

### Проверка приложения перед деплоем

```shell
npm run preview
```

## Запуск через Docker (рекомендуется)

Все команды должны выполняться внутри контейнера `frontend`, а не локально:

```shell
# Линтинг JS/TS
docker compose run --rm frontend npm run lint:js

# Линтинг CSS
docker compose run --rm frontend npm run lint:css

# Полный линтинг
docker compose run --rm frontend npm run lint

# Автоисправление
docker compose run --rm frontend npm run lint:fix-all

# Тесты
docker compose run --rm frontend npm test

# Генерация TypeScript типов из OpenAPI-схемы бекенда
make codegen
```

### Настройка интерпретатора для IDE
1. Контейнер - backend-build
2. Путь - /.venv/bin/python


### Локальный запуск бекенда
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
или
```bash
python3 main.py
```

### Установка новых python-пакетов
Внутри контейнера выполнить команду
TODO: тупая команда это, надо сделать чтобы было `uv add $package_name`
```bash
uv pip install --system $package_name
```
После чего пересобрать Docker-образ бекенд
```bash
docker compose build backend
```

### Работа с БД

Создание миграций
```bash
alembic revision --autogenerate -m "%some_comment"
```

Применение миграций
```bash
alembic upgrade head
```

Откат миграций
```bash
alembic downgrade -1 # откат на 1 миграцию назад
```
или
```bash
alembic downgrade d97a9824423b # откат к определенной миграции
```

### Возможные проблемы
1. Я зарегистрировал роутер, но fastapi не добавляет мои эндпоинты.
**Решение:** Убедиться, что ваш роутер лежит в `apps/<your_app>/api/routers.py` и добавлен в список `list_routers`

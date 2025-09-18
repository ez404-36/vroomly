### Настройка интерпретатора для IDE
1. Контейнер - backend-build
2. Путь - /.venv/bin/python

### Установка новых python-пакетов
Внутри контейнера выполнить команду
```bash
uv add $package_name
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
# TODO: настроить автоимпорт всех роутеров, чтобы не приходилось заниматься этими неявными импортами
1. Я зарегистрировал роутер, но fastapi не добавляет мои эндпоинты.
**Решение:**
- Убедиться, что ваш роутер лежит в `apps/<your_app>/api/routers.py` и добавлен в список `list_routers`
- в `$module/api/__init__.py` добавить `from .endpoints import *` и в `$module/api/endpoints/__init__.py` тоже импортировать все эндпоинты 

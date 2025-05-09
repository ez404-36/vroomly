### Приложение для отслеживания привычек
Позволяет нам становиться чуточку лучше

[Документация](https://app.archbee.com/docs/X9aAXSXIiyx5OaC1iHJF0/2MVKtp0b8-8XX0sZhL2rp)

### Запуск бекенда
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
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
**Решение:** Убедиться, что роутер лежит в `apps/<your_app>/api/router.py` и называется `router`

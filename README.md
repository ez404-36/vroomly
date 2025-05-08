### Приложение для отслеживания привычек
Позволяет нам становиться чуточку лучше в увлекательной форме

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

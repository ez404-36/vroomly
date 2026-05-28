---
id: 0cb0d348-1386-499b-836c-91b903bfd9d6
title: Напоминания для автомобиля (UserVehicle Reminders)
tags:
  - feature
  - backend
  - frontend
  - vehicles
  - reminders
status: draft
priority: medium
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-28T21:41:39.997Z"
updatedAt: "2026-05-28T22:32:40.706Z"
linkedIdeaIds: []
linkedReviewIds: []
---

## Goal

Добавить полнофункциональные напоминания, привязанные к `UserVehicle`: создание/редактирование/удаление, дата-время выполнения (с флагом «весь день»), отметка о выполнении и история. Сейчас на фронте напоминания работают только на моках (`garageMocks`), бэкенда нет вовсе.

**Правило удаления:** удаление выполненного напоминания — без подтверждения; удаление невыполненного — с подтверждением (реализуется в UI).

## Архитектурные решения (подтверждены)

- **История** = единый статус-флаг `is_completed` + `completed_at` в той же таблице (без отдельной history-таблицы).
- **Связь**: FK `user_vehicle_id` → `vehicles.user_vehicle.id` `ON DELETE CASCADE` + денормализованный `user_id` (для быстрой проверки доступа/выборок).
- **Дата/время**: `due_at: datetime` (nullable) + `is_all_day: bool`.
- Таблица в схеме `vehicles`, имя `vehicle_reminder` (модель `VehicleReminder`).

## Контекст кодовой базы (исследовано)

- Модель `UserVehicle`: `backend/apps/vehicles/models/vehicle/user_vehicle.py` (наследует `AutoSchemaBase` + user/vehicle link mixins).
- Паттерн link-mixin: `get_vehicle_link_mixin` / `get_user_link_mixin` через `common/models/mixins/relations.get_foreign_key_mixin`.
- Таймстемпы: `common/models/mixins/timestamped_model.TimestampedModelMixin`.
- Автозагрузка моделей: `core/models/loader.py` (имя класса должно быть уникально — `VehicleReminder` свободно).
- API-паттерн: `backend/apps/vehicles/api/user_vehicle/endpoints.py` (`@cbv`, `BaseAPI`, `self.user`, `database.get_async_session()` / `database.fetch_one|fetch_all`).
- Роутеры: `backend/apps/vehicles/api/routers.py`.
- Текущий head миграций: `b2c3d4e5f6a7`.
- Фронт-типы генерятся из OpenAPI через `openapi-typescript` (`frontend/src/types/schemas.ts` + алиасы `schema-types.ts`), запускается `make codegen`. **Эти файлы руками не править.**
- Фронт уже содержит UI-заготовки на моках: `frontend/src/components/GaragePage/AddReminderModal.tsx`, `ReminderItem.tsx`, `pages/GaragePage.tsx`, `mocks/garageMocks.ts`.
- RTK API: `frontend/src/api/vehiclesApi.ts` (сейчас без `tagTypes`).

## Прогресс

- [x] **Этап A** — модель `VehicleReminder` + `get_user_vehicle_link_mixin`. Файлы: `backend/apps/vehicles/models/vehicle/reminder.py` (new), `user_vehicle.py` (edited). Проверено: ruff + ty + loader/configure_mappers.
- [x] **Этап B** — миграция `e057f8de8cb7_add_vehicle_reminder-2026_05_28_2148.py`, `down_revision='b2c3d4e5f6a7'`. Проверено up/down/up. **Девиации:** `created_at`/`updated_at` = `DateTime` без `timezone=True` (так в `TimestampedModelMixin`); у boolean-полей нет `server_default` (модель использует Python-side `default=False`, чтобы не было ORM/DB drift).
- [x] **Этап C** — схемы в `backend/apps/vehicles/api/reminder/schemas.py` (`CreateReminderSchema`, `UpdateReminderSchema`, `ReminderDetailSchema` + ORM-конвертер). Partial-update через `model_dump(exclude_unset=True)` (precedent: `accounts/api/endpoints/readers.py`). Проверено: ruff + ty + smoke.
- [x] **Этап D** — `reminder_router` в `routers.py` + `ReminderAPI` (`backend/apps/vehicles/api/reminder/endpoints.py`). 7 роутов: POST/GET list, GET/PATCH/DELETE(204) by id, POST complete + uncomplete (toggle). Ownership по денормализованному `user_id` → 404 без утечки. Проверено: ruff + ty + app-boot.
  - **Найдено (вне scope):** фронтовый `deleteUserVehicle` зовёт DELETE `/user-vehicles/{id}/`, которого НЕТ в бэке — предсуществующий баг, зафиксировать отдельно.
- [x] **Этап E** — backend unit-тесты `backend/tests/unit/apps/vehicles/api/test_reminder.py` (33 теста). Покрыто: валидация схем (happy/edge/invalid), ORM-конвертер + guard, все 7 эндпоинтов — create (+404 на чужое ТС), list (+фильтр is_completed, +404), get/patch (exclude_unset, explicit-null clear, +404), complete (идемпотентность), uncomplete (toggle), delete (204, +404). Мок-стиль как в `test_user_vehicle` (`_run`/`asyncio.run`, `unittest.mock`, без pytest-asyncio). Проверено: pytest 33 passed, соседи зелёные, ruff + ty passed.
- [x] **Этап F** — `make codegen` обновил `schemas.ts` (3 схемы + 7 путей, camelCase). Алиасы `CreateReminderSchema`/`UpdateReminderSchema`/`ReminderDetailSchema` добавлены ВРУЧНУЮ в `schema-types.ts` (этот файл hand-maintained, codegen генерит только `schemas.ts`). Проверено: `tsc --noEmit` EXIT=0. Примечание: codegen фетчит OpenAPI с живого backend — нужен запущенный и готовый backend (первый прогон упал ECONNREFUSED при рестарте контейнера).
- [x] **Этап G** — RTK Query в `vehiclesApi.ts`: `tagTypes: ['Reminder','UserVehicle']`, 6 эндпоинтов (`getReminders` с фильтром `isCompleted`, `createReminder`, `updateReminder` PATCH, `completeReminder`, `uncompleteReminder`, `deleteReminder`) + providesTags/invalidatesTags; теги добавлены и на user-vehicle эндпоинты. Хуки + типы экспортированы. Проверено: `tsc --noEmit` EXIT=0, `eslint src/api/vehiclesApi.ts` EXIT=0 (полный eslint по проекту слишком долгий в контейнере — линтили изменённый файл точечно).
- [ ] Этап H — frontend UI
- [ ] Этап I — frontend тесты

## Шаги

### Этап A — Backend модель

**Шаг 1. Создать модель `VehicleReminder`**
- Файл: `backend/apps/vehicles/models/vehicle/reminder.py`
- Наследует `AutoSchemaBase`, `TimestampedModelMixin`, миксины связей:
  - `get_user_link_mixin('reminders', False)`
  - FK на `UserVehicle` через новый helper `get_user_vehicle_link_mixin(...)` (добавить в `user_vehicle.py` по образцу `get_vehicle_link_mixin`, чтобы избежать циклического импорта): `back_populates='reminders'`, `nullable=False`, `on_delete='CASCADE'`.
- Поля (все типизированы, с `doc=`):
  - `title: Mapped[str]` (`String(100)`, NOT NULL)
  - `description: Mapped[str | None]` (`String(500)`)
  - `due_at: Mapped[datetime | None]` (`DateTime(timezone=True)`)
  - `is_all_day: Mapped[bool]` (`Boolean`, default `False`)
  - `is_completed: Mapped[bool]` (`Boolean`, default `False`)
  - `completed_at: Mapped[datetime | None]` (`DateTime(timezone=True)`)
- В `UserVehicle` добавить обратную связь `reminders: Mapped[list[VehicleReminder]]`.
- **Зависит от:** ничего. **Success:** `ty check` + `ruff check` зелёные, импорт модели не падает.

### Этап B — Миграция

**Шаг 2. Alembic-миграция создания таблицы `vehicle_reminder`**
- Файл: `backend/migrations/versions/<rev>_add_vehicle_reminder-<date>.py`, `down_revision = 'b2c3d4e5f6a7'`.
- `op.create_table('vehicle_reminder', ..., schema='vehicles')` с колонками выше; FK `user_vehicle_id` → `vehicles.user_vehicle.id` `ondelete='CASCADE'`, FK `user_id` → `accounts.user.id`.
- Индексы: `user_vehicle_id`, `is_completed`.
- `downgrade()`: `op.drop_table('vehicle_reminder', schema='vehicles')`.
- **Зависит от:** Шаг 1. **Риск:** auto-generate может не подхватить кастомные миксины → проверить DDL вручную, прогнать up/down. **Success:** `docker compose run --rm migrations` ок.

### Этап C — Backend схемы

**Шаг 3. Pydantic-схемы** (`backend/apps/vehicles/api/reminder/schemas.py`, новый подпакет с `__init__.py`)
- `CreateReminderSchema`: `title` (min_length 1), `description?`, `due_at?: datetime`, `is_all_day: bool = False`.
- `UpdateReminderSchema`: все поля опциональны (partial update).
- `ReminderDetailSchema`: `id`, `user_vehicle_id`, `title`, `description`, `due_at`, `is_all_day`, `is_completed`, `completed_at`, `created_at`, `updated_at`.
- Конвертер ORM→схема (по образцу `_user_vehicle_to_detail`).
- **Зависит от:** Шаг 1. **Success:** схемы в OpenAPI.

### Этап D — Backend эндпоинты

**Шаг 4. Роутер** — в `routers.py` добавить `reminder_router` и включить в `list_routers`.

**Шаг 5. CBV `ReminderAPI`** (`backend/apps/vehicles/api/reminder/endpoints.py`, `@cbv`, `BaseAPI`). Все эндпоинты проверяют `user_id == self.user.id` (иначе 404):
- `POST /user-vehicles/{user_vehicle_id}/reminders/` — создать (проверить владение ТС).
- `GET /user-vehicles/{user_vehicle_id}/reminders/` — список, query `is_completed: bool | None` (активные / история).
- `GET /reminders/{reminder_id}/` — деталь.
- `PATCH /reminders/{reminder_id}/` — partial update.
- `POST /reminders/{reminder_id}/complete/` — `is_completed=True`, `completed_at=now()` (идемпотентно).
- `DELETE /reminders/{reminder_id}/` — физическое удаление (бэкенд всегда удаляет; подтверждение — на фронте).
- **Зависит от:** 1, 3, 4. **Success:** эндпоинты в Swagger, ручной CRUD ок.

### Этап E — Backend тесты

**Шаг 6.** `backend/tests/unit/apps/vehicles/api/test_reminder.py` — валидация схем (happy/edge/invalid), конвертер ORM→Detail, логика `complete`, проверка доступа (чужой user → 404), удаление, фильтр `is_completed`. Запуск `make tests`.
- **Зависит от:** 3, 5. **Success:** `make tests` зелёный + покрытие нового кода.

### Этап F — Codegen / типы фронта

**Шаг 7.** `make codegen` → обновляет `schemas.ts` + `schema-types.ts`. При необходимости добавить алиасы `ReminderDetailSchema`, `CreateReminderSchema`, `UpdateReminderSchema`. **Не править сгенерированные файлы вручную.**
- **Зависит от:** 3, 5. **Success:** типы доступны во фронте.

### Этап G — Frontend API

**Шаг 8.** RTK Query в `vehiclesApi.ts`: `getReminders` (опц. `?is_completed=`), `createReminder`, `updateReminder` (PATCH), `completeReminder`, `deleteReminder`. Добавить `tagTypes: ['Reminder', 'UserVehicle']` + `providesTags`/`invalidatesTags`, экспортировать хуки.
- **Зависит от:** 7. **Риск:** добавление тегов не должно ломать существующие эндпоинты.

### Этап H — Frontend UI

**Шаг 9.** В `GaragePage.tsx` заменить mock-state на `useGetRemindersQuery(currentVehicle.id)`; `handleAddReminder` → `useCreateReminderMutation`; checked-change → `useCompleteReminderMutation`. Убрать генерацию моков напоминаний (рекомендации оставить вне scope).

**Шаг 10. Логика подтверждения удаления (ключевое требование).** В `ReminderItem` пробросить `isCompleted`. В `handleReminderDelete`: выполнено → сразу `deleteReminder` без диалога; не выполнено → открыть подтверждающий `Dialog` (паттерн модалки удаления ТС), затем `deleteReminder`.

**Шаг 11. Редактирование.** Расширить `AddReminderModal` до create/edit (`initialValue` + `mode`) либо отдельный `EditReminderModal`; кнопка «Редактировать» в `ReminderItem`.

**Шаг 12. История.** Вкладка/секция «История» (через `Tabs`) или отдельный список: `useGetRemindersQuery({id, is_completed: true})`; выполненные — `line-through`.
- **Зависит от:** 8, 7. **Success:** на `http://localhost:5173` CRUD + complete + история работают; правило подтверждения соблюдено; консоль/логи `frontend` без ошибок.

### Этап I — Frontend тесты

**Шаг 13.** Vitest + RTL: логика подтверждения удаления (выполненное — без диалога, невыполненное — с диалогом), `ReminderItem`, маппинг API.
- **Зависит от:** 9–12. **Success:** `npm run lint` + тесты ок.

## Карта зависимостей

```
1(model) → 2(migration)
1 → 3(schemas) → 4(router) → 5(endpoints) → 6(tests)
3,5 → 7(codegen) → 8(api) → 9,10,11,12(UI) → 13(fe tests)
```

Параллельно после Шага 1: 2 и 3. Параллельно после Шага 7: 8 → затем UI-шаги.

## Риски и митигации

1. **Циклический импорт** model ↔ user_vehicle → link-mixin helper в `user_vehicle.py` (паттерн как у `Vehicle`).
2. **Alembic auto-generate** может не увидеть кастомные миксины → DDL писать/проверять вручную; up+down прогон.
3. **RTK кэш**: без `tagTypes` списки не обновятся → добавить теги и инвалидацию.
4. **openapi vs tschema**: фронт-типы из openapi-typescript; `schemas.ts` руками не трогать — только `make codegen`.
5. **Демо/моки**: `garageMocks` генерит напоминания → решить, оставлять ли за `MockService` флагом.
6. **Toggle complete**: нужно ли снимать отметку (`/uncomplete/`)?

## Открытые уточнения

- Снятие отметки «выполнено» (un-complete) — поддерживать?
- «История» — отдельная вкладка или фильтр в текущем списке?
- Сохранять ли мок-режим напоминаний при `MockService.isEnabled()`.

## Success Criteria (общие)

- `make lint`, `make typecheck`, `make tests` — зелёные.
- Миграция применяется и откатывается.
- CRUD + complete + история работают end-to-end.
- Правило подтверждения удаления соблюдено (выполненное — без, невыполненное — с подтверждением).
- Фронт без ошибок в консоли/логах.

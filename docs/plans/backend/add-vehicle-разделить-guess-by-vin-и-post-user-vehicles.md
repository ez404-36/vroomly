---
id: 10a737ff-fe50-4729-a4cf-74b794f2c183
title: "Add Vehicle: разделить guess_by_vin и POST /user-vehicles/"
tags:
  - backend
  - frontend
  - api
  - vehicles
  - refactor
status: done
priority: high
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-28T16:19:58.106Z"
updatedAt: "2026-05-28T16:52:36.739Z"
linkedIdeaIds: []
linkedReviewIds: []
---

# Add Vehicle: разделить guess_by_vin и POST /user-vehicles/

## 1. Цель

Перестроить сценарий «Добавить ТС в гараж»:

1. `create_by_vin` переименовать в `guess_by_vin`. Эндпоинт становится **read-only** — ничего не пишет в БД, только подбирает варианты по VIN и возвращает данные для предзаполнения формы на фронте.
2. POST `/vehicles/user-vehicles/` принимает **только** `UserVehicleDetailSchema` (без id/user_id — см. ниже про CreateUserVehicleSchema). `UserVehicleWithChoicesSchema`, `CreateUserVehicleByChoiceSchema`, `CreateUserVehicleManualSchema`, `CreateUserVehicleByVinSchema` — удаляются.
3. Параллельно закрыть существующий технический долг в `_create_user_vehicle`: создать `Vehicle` + `CarSpec` + `UserVehicle` в одной транзакции и корректно проставить FK.

## 2. Архитектурные решения

| # | Решение | Обоснование |
|---|---------|-------------|
| 1 | `GET /vehicles/guess_by_vin?vin=...` | Read-only ⇒ GET. Гармонирует с существующим `GET /vehicles/by_vin`. |
| 2 | Единый `GuessByVinResponseSchema {brand, model, generations[], trims[], vin, year, color}` | Плоская структура без обёртки list-из-одного-элемента; всегда один тип ответа. |
| 3 | Один `POST /vehicles/user-vehicles/`, принимает `CreateUserVehicleSchema` (тот же набор полей, что в `UserVehicleDetailSchema`, без id/user_id/vehicle_id) | Соответствует требованию пользователя. `by-choice` и `manual` эндпоинты удаляются. |
| 4 | POST полностью «глупый»: создаёт строго по присланным `generation_id`/`trim_id`/`production_year`/`color`/`mileage`. VIN внутри POST не используется. | Чистая ответственность: guess предлагает, фронт подтверждает, POST создаёт. |
| 5 | Внутри POST создаётся: `Vehicle` (production_year, color, mileage, is_mileage_in_miles, vehicle_type=CAR) + `CarSpec` (vin?, trim_id, vehicle_id) + `UserVehicle` (user_id, vehicle_id, avg_fuel_consumption) — в одной транзакции. | `trim_id` живёт на `CarSpec`, `production_year/color/mileage` — на `Vehicle`. Без этого новый POST end-to-end не заработает. |
| 6 | На входе POST `vin` остаётся опциональным полем (если фронт пришёл из guess-сценария) — пишется в `CarSpec.vin`. | Не теряем VIN, который пользователь уже сообщил. |

## 3. Затронутые файлы

### Backend
- `backend/apps/vehicles/api/user_vehicle/endpoints.py` — основная переработка
- `backend/apps/vehicles/api/user_vehicle/schemas.py` — удалить лишние схемы, добавить `CreateUserVehicleSchema`
- `backend/apps/vehicles/api/car_info/endpoints.py` — добавить `guess_by_vin` (или новый модуль `guess_by_vin/endpoints.py`)
- `backend/apps/vehicles/services/guess_common_car_info.py` — без изменений (используется как есть)
- `backend/tests/unit/apps/vehicles/api/test_user_vehicle.py` — переписать тесты схем
- `backend/tests/unit/apps/vehicles/api/` — добавить тесты для guess_by_vin endpoint и нового create endpoint (с моками БД)

### Frontend
- `frontend/src/api/vehiclesApi.ts` — заменить мутации на новый контракт
- `frontend/src/components/Vehicle/VinLookupForm.tsx` — переработать: теперь только лукап, без создания
- `frontend/src/components/Vehicle/VehicleForm.tsx` — теперь это единая форма создания; принимает опциональное предзаполнение из guess
- `frontend/src/pages/AddVehiclePage.tsx` — пересобрать flow: VIN-шаг → форма с предзаполнением → POST
- `frontend/src/types/schema-types.ts` — пересоберётся через `make codegen`
- `frontend/src/types/schemas.ts` — пересоберётся через `make codegen`
- `frontend/src/mocks/factories.ts`, `frontend/src/mocks/autoRegister.ts` — обновить моки под новые эндпоинты

## 4. Шаги (порядок исполнения)

### Фаза A. Backend — схемы и эндпоинты

**Шаг A1. Переработка схем (`schemas.py`)**
- Удалить: `CreateUserVehicleByVinSchema`, `CreateUserVehicleByChoiceSchema`, `CreateUserVehicleManualSchema`, `UserVehicleChoiceSchema`, `UserVehicleWithChoicesSchema`.
- Добавить:
  - `CreateUserVehicleSchema(APIModel)` — поля: `generation_id: str`, `trim_id: str | None`, `production_year: int | None (1900..2100)`, `color: str | None`, `mileage: int | None (>=0)`, `is_mileage_in_miles: bool = False`, `avg_fuel_consumption: float | None (>=0)`, `vin: str | None (len=17)`.
  - `GuessByVinResponseSchema(APIModel)` — поля: `brand: ChoiceFieldSchema`, `model: ChoiceFieldSchema`, `generations: list[ChoiceFieldSchema]`, `trims: list[ChoiceFieldWithParentSchema]`, `vin: str`, `year: int`, `color: str | None`.
- Сохранить: `UserVehicleDetailSchema`, `UserVehicleListSchema`.

**Шаг A2. Новый endpoint `guess_by_vin`**
- В `backend/apps/vehicles/api/car_info/endpoints.py` (либо новый под-роут `guess_by_vin/`) добавить:
  ```python
  @router.get('/guess_by_vin', response_model=GuessByVinResponseSchema, summary='Подобрать данные ТС по VIN')
  async def guess_by_vin(self, vin: str) -> GuessByVinResponseSchema: ...
  ```
- Логика: `CarInfoByVinProvider().get_info(vin)` → `GuessCommonCarInfo().get_from_vin01(info)` → собрать `GuessByVinResponseSchema`, прокинув `vin`, `year`, `color` из `CarInfoByVinDataSchema`.
- Валидация VIN: `Query(..., min_length=17, max_length=17)`.

**Шаг A3. Переработка POST `/user-vehicles/`**
- Удалить методы `create_by_vin`, `create_by_choice`, `create_manual` и старый приватный `_create_user_vehicle`.
- Добавить единственный POST:
  ```python
  @user_vehicle_router.post('/user-vehicles/', response_model=UserVehicleDetailSchema, summary='Добавить ТС в гараж')
  async def create_user_vehicle(self, data: CreateUserVehicleSchema) -> UserVehicleDetailSchema: ...
  ```
- Полная реализация `_create_user_vehicle` в одной транзакции:
  1. Создать `Vehicle(vehicle_type=CAR, production_year, color, mileage, is_mileage_in_miles, country_id=None)`.
  2. Если `trim_id` задан → создать `CarSpec(vehicle_id=vehicle.id, trim_id=UUID(trim_id), vin=data.vin)`.
  3. Создать `UserVehicle(user_id=self.user.id, vehicle_id=vehicle.id, avg_fuel_consumption=data.avg_fuel_consumption)`.
  4. `session.commit()`, `session.refresh()` всех трёх.
- Response: собрать `UserVehicleDetailSchema` с brand/series/generation/trim — резолвить через `CarSpec.trim.generation.series.brand` (если есть spec) с `selectinload`.

**Шаг A4. Обновление списка/детали ТС**
- В `list_user_vehicles` и `get_user_vehicle` поправить selectinload-цепочку: `UserVehicle.vehicle → CarSpec → CarTrim → VehicleGeneration → VehicleSeries → VehicleBrand`. Текущие selectinload через `__mapper__.relationships['generation']` — это анти-паттерн и в новой модели у `UserVehicle` нет `generation` напрямую.
- Удалить хелперы `_uv_mileage` / `_uv_is_mileage_in_miles` если они дублируются: значения теперь читаются с `user_vehicle.vehicle`.

**Шаг A5. Backend-тесты**
- Удалить тесты `TestCreateUserVehicleByVinSchema`, `TestUserVehicleWithChoicesSchema`, `TestCreateUserVehicleByChoiceSchema`, `TestCreateUserVehicleManualSchema`.
- Добавить:
  - `TestCreateUserVehicleSchema` — валидация полей (year range, mileage >= 0, vin length).
  - `TestGuessByVinResponseSchema` — корректное конструирование.
  - Integration-тест на POST `/user-vehicles/` (создание Vehicle+CarSpec+UserVehicle, FK не NULL, корректная связка).
  - Integration-тест на `GET /vehicles/guess_by_vin?vin=...` (мокаем `CarInfoByVinProvider.get_info`, проверяем форму ответа).

### Фаза B. Кодогенерация типов
**Шаг B1.** `make codegen` — пересобрать `frontend/src/types/schemas.ts` и `frontend/src/types/schema-types.ts`. `UserVehicleWithChoicesSchema`, `CreateUserVehicleByVinSchema` и т.д. уйдут автоматически.

### Фаза C. Frontend

**Шаг C1. `vehiclesApi.ts`**
- Удалить: `useCreateUserVehicleByVinMutation`, `useCreateUserVehicleByChoiceMutation`, `useCreateUserVehicleManualMutation`, типы `CreateUserVehicleByVinDTO`/`ByChoiceDTO`/`ManualDTO`, локальный `UserVehicleChoiceSchema`, реэкспорт `UserVehicleWithChoicesSchema`.
- Добавить:
  - `guessByVin: builder.query<GuessByVinResponseSchema, string>({ query: (vin) => `guess_by_vin/?vin=${vin}` })` → `useGuessByVinQuery` / `useLazyGuessByVinQuery`.
  - `createUserVehicle: builder.mutation<UserVehicleDetailSchema, CreateUserVehicleSchema>({ query: (body) => ({ url: 'user-vehicles/', method: 'POST', body }) })`.
- `lookupByVin` (`by_vin/`) — оставить как есть (это другой эндпоинт, raw VIN data).

**Шаг C2. `VinLookupForm.tsx` → preview-режим**
- Убрать прямое создание ТС. Компонент возвращает `GuessByVinResponseSchema | null` через колбэк `onGuess(data)` и переключает родителя на форму.
- Удалить `UserVehicleDetailSchema | UserVehicleWithChoicesSchema` из state.

**Шаг C3. `VehicleForm.tsx` — единая форма создания**
- Принимает опциональный prop `prefill?: GuessByVinResponseSchema` для предзаполнения brand/model/generations/trims + vin + production_year + color.
- При наличии prefill:
  - Подставить значения в селекты brand/series без обращения к `getVehicleSeriesQuery`, либо подмешать `prefill.brand`/`prefill.model` в опции.
  - Если `generations.length === 1` — авто-выбрать; иначе показать опции из `prefill.generations`.
  - Аналогично с `trims`.
- Submit вызывает `createUserVehicle` (новая мутация).
- Удалить `useCreateUserVehicleManualMutation` — везде один и тот же mutation.

**Шаг C4. `AddVehiclePage.tsx`**
- Перестроить state-машину: `step: 'vin' | 'form'`.
  - На `vin`: `VinLookupForm` с `onGuess(prefill) → setPrefill(prefill); setStep('form')`. Кнопка «Заполнить вручную» → `setStep('form'); setPrefill(undefined)`.
  - На `form`: `VehicleForm prefill={prefill} onSuccess={() => navigate('/garage')} onBack={() => setStep('vin')}`.
- Удалить Tabs «Через VIN / Вручную» (или сохранить как два входа в одну форму).

**Шаг C5. Моки**
- `frontend/src/mocks/factories.ts` — добавить `guessByVinResponse()`-фабрику, удалить упоминания `UserVehicleWithChoicesSchema`.
- `frontend/src/mocks/autoRegister.ts` — зарегистрировать мок `GET:vehicles/guess_by_vin`.
- Поправить `userVehicleDetail()` если поля в Detail-схеме сменились.

**Шаг C6. Frontend-проверка**
- Запустить `make codegen` → запустить frontend → `docker compose logs -f frontend` на ошибки → открыть `http://localhost:5173/add-vehicle` (или соответствующий путь) → проверить консоль браузера: VIN → guess → форма → submit → редирект в гараж.

### Фаза D. Lint / typecheck
- `make lint` (ruff + ty).
- Frontend: `npm run lint` в контейнере frontend.

## 5. Зависимости между шагами

```
A1 → A2 ─┐
A1 → A3 ─┼→ A4 → A5 → B1 → C1 ─┬→ C2 ─┐
                                  ├→ C3 ─┼→ C4 → C5 → C6 → D
                                  └─────┘
```

- A1 (схемы) — фундамент для A2, A3.
- B1 (codegen) обязателен ДО любого C-шага: без него фронт не увидит новых типов.
- C2/C3 независимы друг от друга, но оба нужны для C4.

## 6. Риски и митигации

| Риск | Митигация |
|------|-----------|
| **Существующий тех. долг (vehicle_id=None при NOT NULL FK)** — текущий код вообще не создаёт UserVehicle корректно. | Шаг A3 закрывает долг: создаём Vehicle+CarSpec+UserVehicle в одной транзакции. Без этого новый POST упадёт на FK-constraint в БД. |
| **`vehicle_type` Vehicle** — нужно явно проставить `VehicleType.CAR` (мотоциклы пока не поддержаны UI). | В шаге A3 захардкодить `vehicle_type=VehicleType.CAR`. Зафиксировать TODO на расширение для мотоциклов. |
| **`trim_id` обязателен на `CarSpec`** (NOT NULL). Если пользователь не выбрал комплектацию → нельзя создать CarSpec. | Бизнес-решение: если `trim_id is None` → создавать только Vehicle+UserVehicle без CarSpec. Это значит, что Vehicle без spec временно допустим. **Уточнение требуется** — но пока идём через «без trim_id → без CarSpec». |
| **`Vehicle.production_year` NOT NULL**, а на форме это `int \| None`. | На входе в POST требовать `production_year: int` обязательно (не nullable). Frontend: сделать поле обязательным. |
| **`avg_fuel_consumption` тип** — на бэке `Decimal`, на схеме `float`. | В POST конвертировать `float → Decimal` через `Decimal(str(value))`. |
| **Тесты с моками БД не ловят SQL-семантику** (см. failures.md про pg_trgm). | Для шага A5 — минимум 1 integration-тест на реальной БД для POST и для guess_by_vin. |
| **Старый код во фронте использует `'choices' in response`** для типизации. | После C1 эта проверка перестанет компилироваться → TypeScript подскажет все места, требующие правки. |
| **`brand_id` / `series_id`** во фронте сейчас в форме обязательны, но новая `CreateUserVehicleSchema` их не использует (только `generation_id` + `trim_id`). | На бэк уходят только `generation_id` и `trim_id`. Brand/Series на фронте остаются для UX-выбора каскада. |
| **Pre-existing `is_mileage_in_miles` boolean field default** — на Vehicle `default=False`, ok. | OK, без действий. |

## 7. Открытые вопросы (по ходу могут понадобиться уточнения)

- **`trim_id is None` сценарий**: создаём ли Vehicle без CarSpec? Предложение — да. Альтернатива — делать `trim_id` обязательным во вводе.
- **`country_id` на Vehicle** — оставляем `None` (nullable=True). Возможно, фронту понадобится поле в форме — пока нет.
- **`UserVehicle.groups`** — никак не затрагиваем; новый POST не назначает группы.

## 8. Success Criteria

- [ ] `GET /vehicles/guess_by_vin?vin=<17-char>` возвращает `GuessByVinResponseSchema`, не пишет в БД.
- [ ] В БД после вызова guess_by_vin нет новых записей в `user_vehicle` / `vehicle` / `car_spec`.
- [ ] `POST /vehicles/user-vehicles/` с телом `CreateUserVehicleSchema` создаёт `Vehicle` + (опционально) `CarSpec` + `UserVehicle`, FK `vehicle_id` корректно проставлен.
- [ ] `GET /vehicles/user-vehicles/` и `GET /vehicles/user-vehicles/{id}/` корректно отдают brand/series/generation/trim через resolved связи.
- [ ] Схемы `UserVehicleWithChoicesSchema`, `CreateUserVehicleByVinSchema`, `CreateUserVehicleByChoiceSchema`, `CreateUserVehicleManualSchema` удалены из кода и не появляются в `schemas.ts`.
- [ ] Frontend flow «Добавить ТС»: VIN → guess → форма с предзаполнением → submit → редирект в гараж. Ручной flow: пропустить VIN → форма пустая → submit.
- [ ] `make lint` и `make typecheck` зелёные.
- [ ] Все существующие тесты схем переписаны и зелёные, добавлены integration-тесты на POST + guess.
- [ ] Browser console без ошибок при прохождении flow.

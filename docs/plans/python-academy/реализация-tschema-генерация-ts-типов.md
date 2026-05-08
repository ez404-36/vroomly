---
id: ac232be3-48ee-44b2-af2b-20e66c57bed1
title: Реализация tschema — генерация TS типов
tags:
  - codegen
  - typescript
  - python
  - academy
  - implementation
status: draft
priority: medium
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-07T21:15:57.731Z"
updatedAt: "2026-05-07T22:29:31.926Z"
linkedIdeaIds:
  - 6d96e85f-0166-4a64-8dd1-ef222b967dfc
linkedReviewIds: []
---

## Контекст

Python-пакет `tschema` для генерации TypeScript элементов типизации из Python моделей. Расширяет существующий codegen (`scripts/collect_models.py`).

## Название

**tschema** — TypeScript Schema Generator

## Этапы реализации

### 1. Package Structure
- [ ] Создать структуру пакета `tschema/`
- [ ] `tschema/backends/` - поддержка разных фреймворков
- [ ] `tschema/generators/` - генераторы для разных типов TS
- [ ] `tschema/formatters/` - форматирование вывода

### 2. Backend Support (Parsers)
- [ ] Парсинг Pydantic моделей
- [ ] Парсинг Django models
- [ ] Парсинг DRF serializers
- [ ] Парсинг SQLAlchemy models
- [ ] Обработка ForeignKey, ManyToMany
- [ ] Обработка SerializerMethodField

### 3. Model Discovery + Type Resolution
- [ ] Извлечение полей, типов, constraints
- [ ] Обработка вложенных моделей
- [ ] Обработка Optional/nullable полей
- [ ] Обработка ForeignKey, ManyToMany
- [ ] Обработка SerializerMethodField

### 4. Auxiliary Types Support
- [ ] Python `Enum` → TypeScript enum
- [ ] Python `StrEnum` / `Literal` → TypeScript literal
- [ ] `typing.Literal` → union of literals
- [ ] `typing.Annotated` → doc comments, validation
- [ ] `typing.NewType` → type aliases
- [ ] Forward references (строки/циклы)
- [ ] Generic types (TypeVar, Generic)

### 5. Type Mapping (Python → TS)
- [ ] Обработка стандартных типов (str, int, bool, float)
- [ ] Обработка Optional/Union
- [ ] Обработка List/Dict/Set
- [ ] Обработка Enum
- [ ] Обработка Datetime/UUID

### 6. TS Generators
- [ ] `generate_interface()` - TypeScript interfaces
- [ ] `generate_type_alias()` - type aliases
- [ ] `generate_union()` - union types
- [ ] `generate_enum()` - enum definitions
- [ ] `generate_generic()` - generic types
- [ ] `generate_utility()` - Partial, Required, Pick, Omit
- [ ] `generate_literal()` - literal types

### 7. Специализированные генераторы
- [ ] Redux Toolkit types (State, Action, Thunk)
- [ ] React Query types (QueryFnData, Mutation)
- [ ] API response/request types

### 6. CLI + Configuration
- [ ] Командная строка для генерации
- [ ] Флаги: `--output`, `--format`, `--target`
- [ ] Конфигурация (pyproject.toml, yaml/json)

### 9. pyproject.toml Configuration
- [ ] Секция `[tool.tschema]`
- [ ] Настройки вывода: `output_dir`, `file_pattern`
- [ ] Настройки типов: `target`, `strict`, `optional_as_union`
- [ ] Наименование: `naming_convention` (camelCase, snake_case)
- [ ] Исключения: `exclude_models`, `exclude_fields`

Пример конфигурации:
```toml
[tool.tschema]
output_dir = "frontend/src/types"
target = "react-query"
strict = true

[tool.tschema.naming]
models = "PascalCase"
fields = "camelCase"

[tool.tschema.exclude]
models = ["BaseModel", "AuditMixin"]
fields = ["created_at", "updated_at"]
```

### 10. Frontend TS Configuration
- [ ] Чтение `tsconfig.json` / `tsconfig.node.json`
- [ ] Парсинг compilerOptions
- [ ] Учёт: `strict`, `esModuleInterop`, `jsx`
- [ ] Валидация сгенерированного кода против tsconfig
- [ ] Генерация с учётом настроекstrictness

```toml
[tool.tschema.typescript]
tsconfig_path = "tsconfig.json"  # относительно frontend/
strict_mode = "inherit"          # inherit | strict | relaxed
module_resolution = "node16"     # node | node16 | bundler
```

### 11. Integration + Tests
- [ ] Интеграция с существующим codegen
- [ ] Обновление `scripts/collect_models.py`
- [ ] **Основа кода:** `/home/egor/PycharmProjects/vroomly/backend/scripts/collect_models.py`
- [ ] **Основа тестов:** `/home/egor/PycharmProjects/vroomly/backend/tests/unit/scripts/test_collect_models.py`
- [ ] Тесты

## Референсы

- Код: `/home/egor/PycharmProjects/vroomly/backend/scripts/collect_models.py`
- Тесты: `/home/egor/PycharmProjects/vroomly/backend/tests/unit/scripts/test_collect_models.py`

## Файловая структура

```
tschema/
├── __init__.py
├── backends/
│   ├── __init__.py
│   ├── base.py          # Base parser interface
│   ├── pydantic.py      # Pydantic parser
│   ├── django.py        # Django model parser
│   ├── drf.py           # DRF serializer parser
│   └── sqlalchemy.py    # SQLAlchemy parser
├── generators/
│   ├── __init__.py
│   ├── interface.py
│   ├── type_alias.py
│   ├── union.py
│   ├── enum.py
│   └── utility.py
├── formatters/
│   ├── __init__.py
│   └── typescript.py
├── config.py
└── cli.py
```

## Приоритет

1. Package structure
2. Model discovery (Pydantic)
3. Type mapping
4. Interface generator
5. CLI
6. Интеграция с Vroomly
7. Расширение генераторов
8. Тесты

---
id: 6d96e85f-0166-4a64-8dd1-ef222b967dfc
title: tschema — генерация TypeScript типов из Python моделей
tags:
  - codegen
  - typescript
  - python
  - academy
  - typization
status: draft
priority: medium
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-07T21:07:37.786Z"
updatedAt: "2026-05-07T21:26:05.043Z"
---

## Контекст

В проекте Vroomly уже есть codegen (`scripts/collect_models.py`), который генерирует TypeScript типы из Python моделей.

## Суть идеи

Создать Python пакет (Academy) — скрипт генерации TypeScript элементов типизации из Python моделей.

## Генерирует

- TypeScript interfaces
- Type aliases
- Union types
- Enum definitions
- Generic types
- Utility types (Partial, Required, Pick, Omit)

## Входные данные

- Python модели (Pydantic, SQLAlchemy)
- Django models
- DRF serializers
- Настройки генерации (output format, naming conventions)

## Выходные данные

- TypeScript definition files (.d.ts)
- Типы для Redux Toolkit
- Типы для React Query
- Типы для API response/response

## Цель

Унифицировать типизацию между backend и frontend на уровне Python моделей.

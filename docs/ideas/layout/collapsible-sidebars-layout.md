---
id: 914fe8d3-638c-4e96-b26c-0ed32cf9849a
title: Collapsible Sidebars Layout
tags:
  - layout
  - react
  - sidebar
  - ui
  - frontend
status: draft
priority: medium
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-07T21:09:11.194Z"
updatedAt: "2026-05-18T13:40:48.627Z"
---

## Суть

Layout-паттерн для React-приложения с двумя collapsible сайдбарами и фиксированным header.

## Структура

```
┌──────┬──────────────────────────────────────────┐
│      │ Header (на всю ширину, кроме левого)    │
│ Left ├──────────────────────────────────────────┤
│Side  │                                          │
│      │   Main Content    │   Right Sidebar     │
│      │                   │   (height = main)    │
│      │   (прокрутка)     │   (прокрутка)        │
│      │                   │                      │
└──────┴───────────────────┴─────────────────────┘
```

### Left Sidebar

- На всю высоту экрана (включая header)
- Collapsible (скрывается/раскрывается)
- Перекрывает header по вертикали

### Header

- Фиксированный, не прокручивается
- Ширина = 100% - левый сайдбар (когда открыт)

### Right Sidebar

- Высота = высота main контента
- Не перекрывает header
- Collapsible

### Main Content

- Прокручиваемая область
- Высота = header + контент

## Состояния

- Оба сайдбара открыты
- Левый открыт, правый закрыт
- Левый закрыт, правый открыт
- Оба закрыты

## Технический подход

- CSS Grid для layout
- React state для toggle
- CSS transitions для анимации
- CSS custom properties для ширин



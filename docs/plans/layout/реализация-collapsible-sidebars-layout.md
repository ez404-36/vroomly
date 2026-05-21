---
id: e832bf07-290c-44b0-8f70-e18b569630d3
title: Реализация Collapsible Sidebars Layout
tags:
  - layout
  - react
  - sidebar
  - implementation
status: draft
priority: medium
linkedDialogIds: []
createdBy: dev-user
createdAt: "2026-05-07T21:13:45.938Z"
updatedAt: "2026-05-07T21:13:45.938Z"
linkedIdeaIds:
  - 914fe8d3-638c-4e96-b26c-0ed32cf9849a
linkedReviewIds: []
---

## Этапы реализации

### 1. Layout-компонент
- [ ] Создать компонент `AppLayout`
- [ ] Добавить CSS Grid layout
- [ ] Определить CSS-переменные для ширин сайдбаров

### 2. Left Sidebar
- [ ] Компонент `LeftSidebar`
- [ ] Sticky positioning (на всю высоту)
- [ ] Z-index выше header
- [ ] Toggle состояние (open/closed)
- [ ] CSS transitions для анимации

### 3. Header
- [ ] Компонент `AppHeader`
- [ ] Sticky positioning
- [ ] Адаптация ширины под левый сайдбар
- [ ] Кнопка toggle для левого сайдбара

### 4. Right Sidebar
- [ ] Компонент `RightSidebar`
- [ ] Высота = высота main контента
- [ ] Toggle состояние
- [ ] Кнопка toggle

### 5. Main Content
- [ ] Компонент `MainContent`
- [ ] Прокрутка контента
- [ ] Адаптация ширины под оба сайдбара

### 6. State Management
- [ ] Zustand store для layout state
- [ ] Persist preference (localStorage)
- [ ] Actions: toggleLeft, toggleRight

### 7. Стили
- [ ] CSS modules или Tailwind
- [ ] Transitions/animations
- [ ] Responsive (мобильные breakpoints)

## Файловая структура

```
src/
├── components/
│   └── layout/
│       ├── AppLayout.tsx
│       ├── AppHeader.tsx
│       ├── LeftSidebar.tsx
│       ├── RightSidebar.tsx
│       ├── MainContent.tsx
│       └── index.ts
├── store/
│   └── layoutStore.ts
└── styles/
    └── layout.css
```

## Приоритет

1. Layout + CSS Grid
2. State management (Zustand)
3. Left Sidebar (базовая функциональность)
4. Header + toggle кнопка
5. Right Sidebar
6. Main Content
7. Animations
8. Responsive
9. Persist

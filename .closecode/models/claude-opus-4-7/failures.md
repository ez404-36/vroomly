# Project Model Knowledge — failures and corrections

### Tailwind v4 dropped `[--var]` shorthand for CSS variables
- **Date:** Tue May 19 2026
- **Context:** Frontend uses Tailwind v4 (`tailwindcss@^4.3.0`). Many components used `bg-[--color-primary]`, `text-[--color-text]`, `border-[--color-border]`, `ring-[--ring]`, `rounded-[--radius]` etc. These compile to literal `background-color: --color-primary` (invalid CSS) because v4 removed the implicit `var()` wrapping for the bracket shorthand.
- **Wrong approach:** Assuming `bg-[--color-primary]` works like in Tailwind v3.
- **Correct approach:** Use the v4 parenthesis shorthand `bg-(--color-primary)`, or explicit `bg-[var(--color-primary)]`. Same for every utility (`text-`, `border-`, `ring-`, `rounded-`, `from-`, `to-`, etc.).
- **Rule:** In this project's Tailwind v4 setup, ALL CSS-variable arbitrary values must use `utility-(--var)` parenthesis syntax, never `utility-[--var]`.

### Two competing Tailwind background utilities don't override each other reliably
- **Date:** Tue May 19 2026
- **Context:** Switch had `bg-(--color-text)` in the base class and `bg-(--color-primary)` appended conditionally for checked state via `clsx(base, isChecked && checked)`. The checked colour never won — both utilities have identical specificity, and class order in the `class` attribute does NOT affect CSS cascade; the winner depends on Tailwind's generated source order.
- **Wrong approach:** Stacking two same-property utilities and relying on class-attribute order to override.
- **Correct approach:** Make the property mutually exclusive — `clsx(base, isChecked ? checkedClass : uncheckedClass)`. Base class must NOT set that property.
- **Rule:** When toggling a CSS property between two states with Tailwind, never include the property in the base class. Use a ternary so only one utility for that property is ever applied.

### Switch peer-checked selectors don't reach nested children
- **Date:** Tue May 19 2026
- **Context:** `ui/components/Switch` used `<input class="peer sr-only" />` then a track `<span class="peer-checked:...">` with a nested thumb `<span class="peer-checked:translate-x-4">`. The thumb is NOT a sibling of the peer input, so the `peer-checked:` class never applied — switch appeared stuck.
- **Wrong approach:** Relying on `peer-checked:` for elements nested inside the peer's sibling.
- **Correct approach:** Drive visual state from the controlled `checked` prop with conditional classes (`clsx(base, isChecked && checkedClass)`).
- **Rule:** `peer-*` Tailwind variants only target direct siblings of the `peer` element. For deeply nested children, derive state in JS and toggle classes conditionally.

### pg_trgm similarity регистрозависима и требует калибровки на реальных данных
- **Date:** Thu May 28 2026
- **Context:** В `GuessCommonCarInfo._fuzzy_lookup` использовали `func.similarity(name, query)` без `lower()` и с порогом 0.6, угаданным из плана без проверки. В проде similarity(`'Tucson'`, `'TUXON'`) = 0.3 (а не ~0.6-0.7 как предполагалось), и регистр критичен — триграммы извлекаются из исходной строки. Тесты с моками этого не ловили, потому что подсовывали готовые score.
- **Wrong approach:** Выбор порога fuzzy-поиска по интуиции; индексы и сравнение без `lower()`; покрытие только моками без проверки на реальной БД.
- **Correct approach:** Перед выбором порога — запустить `SELECT similarity(lower(name), lower(:q))` на реальных данных для нескольких представительных кейсов. Использовать `func.lower(...)` с обеих сторон. Создавать функциональный GIN-индекс `gin (lower(name) gin_trgm_ops)` — без него запрос с `lower()` уходит в seq scan. Добавлять хотя бы один integration-тест с реальной БД.
- **Rule:** pg_trgm: всегда нормализуй регистр (`lower()` с обеих сторон) и калибруй threshold/индексы по реальным данным, а не по предположениям. Моки не валидируют SQL-семантику.

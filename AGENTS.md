# Vroomly Project Documentation

## Overview

Vroomly is a microservice-based web application for vehicle management.

**Stack:**
- Backend: Python 3 + FastAPI
- Frontend: React 19 + TypeScript + Vite + Radix UI + Redux Toolkit + React Router
- Database: PostgreSQL 17
- Development: Docker-based environment

---

## Docker Containers

| Container | Purpose | Profiles | How to Run Scripts |
|-----------|---------|----------|-------------------|
| `backend` / `backend-build` | Main FastAPI application and backend scripts | `vr-backend`, `vr-frontend` | Scripts must run inside this container |
| `tests` | Backend pytest tests | `no-profiles` | `docker compose run --rm tests` |
| `linters` | Ruff linting + ty type checking | `no-profiles` | `make lint` |
| `frontend` | React development server (Vite) | `vr-frontend`, `vr-backend` | `docker compose run --rm frontend <cmd>` |
| `db` | PostgreSQL 17 database | `default` | Already running |
| `codegen` | Generates TypeScript types from Python models | `vr-frontend`, `vr-backend` | `make codegen` |
| `migrations` | Runs Alembic database migrations | `vr-frontend` | `docker compose run --rm migrations` |
| `seed` | Populates database with initial data | `no-profiles` | `make seeds` |
| `libretranslate` | Translation service (English/Russian) | `default` | Already running |
| `default_data_runner` | Runs persistent background scripts from `backend/default_data` | `background` | *No manual command needed; runs persistently.* |

**Important:** Scripts inside `backend/tests/` directory must use the `tests` container, not `backend-build`. All other backend scripts use `backend-build`.

---

## Project Structure

```
vroomly/
├── backend/                    # Python FastAPI backend
│   ├── apps/                  # Microservices (each is a FastAPI app)
│   │   ├── accounts/          # User accounts, authentication
│   │   ├── geo/               # Geographic data, locations
│   │   └── vehicles/          # Vehicle-related functionality
│   ├── common/                # Shared utilities (mixins, schemas, helpers)
│   ├── core/                  # Config, base ORM models, constants, DB setup
│   ├── migrations/            # Alembic migrations
│   │   └── versions/          # Migration files
│   ├── tests/                 # Backend tests (run in `tests` container)
│   │   ├── integration/      # Integration tests (external services)
│   │   └── unit/            # Unit tests (structure mirrors backend/)
│   │       ├── core/         # Tests for backend/core
│   │       ├── common/      # Tests for backend/common
│   │       └── apps/        # Tests for backend/apps/
│   │           ├── accounts/
│   │           ├── geo/
│   │           └── vehicles/
│   ├── default_data/          # Scripts to populate DB with initial data (Managed by default_data_runner service)

│   ├── scripts/               # Utility scripts (DB recreation, etc.)
│   ├── src/                   # Internal Python packages
│   ├── main.py               # FastAPI entry point
│   ├── Dockerfile             # Multi-stage: backend-base, codegen
│   └── pyproject.toml        # Python dependencies
│
├── frontend/                  # React + TypeScript frontend
│   ├── src/                   # Source code
│   │   └── (components, pages, hooks, store, types, etc.)
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── Dockerfile            # Node.js container
│
├── docker-compose.yaml       # All container definitions
├── Makefile                  # Development commands
├── .env                      # Environment variables (actual)
├── .env.example              # Environment variables template
└── README.md                 # Setup instructions
```

---

## Key Development Commands

```bash
# Setup for backend development
make setup-for-backend

# Setup for frontend development
make setup-for-frontend

# Populate database with initial data
make seeds

# Run default data scripts (if needed for non-seed operations)
docker compose run --rm default_data_runner bash -c "python backend/default_data/run_scripts.py" # Placeholder command to be refined

# Run backend tests
make tests

# Generate TypeScript types from backend models
make codegen

# Recreate database
make recreate-db

# Run ruff linter + ty type checker
make lint

# Run only type checker
make typecheck
```

---

## Environment Variables

Key variables (see `.env.example`):
- `DB_USER`, `DB_PASSWORD` - PostgreSQL credentials
- `BACKEND_PORT` - Backend API port (default: 8000)
- `EXPOSE_DB_PORT` - Database port (default: 5432)
- `LIBRETRANSLATE_PORT` - Translation service port (default: 5000)
- `LIBRETRANSLATE_HOST` - Hostname for translation service

---

## Code Generation (TypeScript from OpenAPI)

The `codegen` container runs `npm run codegen:openapi` inside the `frontend` container, which:
1. Fetches the OpenAPI schema from the running backend at `${BACKEND_URL}/openapi.json`
2. Generates TypeScript types in `frontend/src/types/schemas.ts` using [openapi-typescript](https://openapi-ts.dev/)

**Important:** The backend must be running before executing `make codegen`. After running codegen, TypeScript types in frontend will be updated based on the backend's OpenAPI schema.

```bash
# Run codegen (requires backend to be up)
make codegen
```

---

---

## Database Migrations

Migrations are managed with Alembic:
- Config: `backend/alembic.ini`
- Migration scripts: `backend/migrations/versions/`

To apply migrations: `docker compose run --rm migrations`

---

## Testing

Backend tests are located in `backend/tests/` and run in the `tests` container.

### Test Types

| Type | Location | Purpose |
|------|----------|---------|
| `unit` | `backend/tests/unit/` | Unit tests - test individual functions/classes. Structure mirrors `backend/` folder |
| `integration` | `backend/tests/integration/` | Integration tests - test interaction with external services (DB, APIs) |

### Unit Tests Structure

Unit tests must mirror the `backend/` directory structure:
- `tests/unit/core/` → tests for `backend/core/`
- `tests/unit/apps/accounts/` → tests for `backend/apps/accounts/`
- `tests/unit/common/` → tests for `backend/common/`

### Running Tests

```bash
# Run all tests (via Makefile)
make tests

# Run specific test type
docker compose run --rm tests pytest tests/unit/
docker compose run --rm tests pytest tests/integration/
```

---

## Design Resources

- **Figma**: https://www.figma.com/design/IiR4zoi5BtMXjO0pVmJCGt/vroomly-или-car-car-или...?node-id=6-2&p=f

---

## Code Style

### Python

**Formatter:** Ruff
**Type Checker:** ty (from the ruff team)
**Config files:** `backend/pyproject.toml`, `backend/ty.toml`

**Ruff Configuration** (`backend/pyproject.toml`):
- Quote style: single quotes `'`
- Indent style: tabs
- Line length: 120 characters
- Target Python: 3.13
- Enabled linters: E, F, W, D (docstrings), I (isort), N (naming), PLR (pylint)

**ty Configuration** (`backend/ty.toml`):
- Python version: 3.13
- Analyzes: `apps/`, `common/`, `core/`, `tests/`
- Excludes: `core/settings.py`

### Python Type Annotation Requirements

**All Python code must be fully typed.** This is not optional — type annotations are mandatory:

- **Every function and method** must have annotated parameters and return type
- **Variables** should have type hints where the type is not immediately obvious from the assignment
- **Class attributes** must have type annotations
- **Complex data structures** must be properly typed (dicts, lists with specific item types, etc.)
- **Generics** must be used appropriately (`list[str]`, `dict[str, int]`, `Optional[X]`, `Union[A, B]`)
- **Type aliases** should be defined for complex or repeated types

```python
# ✅ Correct
def get_user(user_id: int) -> User | None:
    ...

def process_items(items: list[ItemConfig]) -> dict[str, ValidationResult]:
    ...

UserId = int  # Type alias for clarity
def get_user(id: UserId) -> User:
    ...

# ❌ Incorrect - untyped
def get_user(user_id):
    ...

def process_items(items):
    ...
```

**Reasoning:** The project uses `ty` (static type checker from ruff team) and generates TypeScript types from Python models. Full type coverage ensures:
1. Catch bugs at development time with `ty check`
2. Reliable codegen to TypeScript frontend
3. Self-documenting code
4. Better IDE support and refactoring safety

### Code Coverage Requirements

**All code must be covered by tests.** This is not optional:

- **Backend (Python):** Every function, method, and class must have corresponding unit tests
- **Frontend (TypeScript):** Critical UI components and business logic must have tests (Vitest + React Testing Library)
- **No code without tests:** Before writing new functionality, ensure tests exist or create them first
- **Test completeness:** Tests should cover:
  - Happy path scenarios
  - Edge cases and boundary conditions
  - Error handling and exception cases
  - Invalid input validation
- **Test correctness:** Existing tests should be reviewed for correctness and completeness
  - Fix incorrect or outdated tests
  - Extend coverage where needed

**Workflow for new code:**
1. Write tests first (TDD) or alongside implementation
2. Ensure new code is covered by tests
3. If modifying existing code, update or add tests accordingly

**Running Ruff:**
```bash
# Inside backend-build container
ruff check .          # Lint
ruff format .         # Format
ruff check --fix .    # Auto-fix
```

**Running ty:**
```bash
# Inside backend-build container
ty check .
```

### Running Linters via Docker
```bash
# Run all linters (ruff + ty) in one command
make lint

# Run only ruff
docker compose run --rm linters ruff check .

# Run only ty
make typecheck
```

### TypeScript/JavaScript
- Formatter: Prettier
- Linter: ESLint + Stylelint
- Run linting: `npm run lint` in frontend container
- Auto-fix: `npm run lint:fix-all`

### Pre-commit Hooks
Installed in `backend-build` container via pre-commit.

---

## Frontend Development Rules

### Verification After Changes

**Обязательно после каждого изменения в frontend:**

1. Открыть главную страницу приложения в браузере (http://localhost:5173 или указанный порт)
2. Проверить консоль браузера на наличие ошибок (Error level)
3. Проверить логи frontend контейнера на наличие ошибок

**Команда для проверки логов:**
```bash
docker compose logs -f frontend
```

**Причина:** Vite делает hot reload, ошибки отображаются в браузере и в терминале. Это позволяет быстро обнаружить:
- Ошибки импорта модулей
- Ошибки TypeScript/ESLint
- Проблемы с маршрутизацией
- Проблемы с компонентами

### Path Conventions

Пути импортов в файлах `frontend/src/pages/`:
- `../utils/routes` — утилиты роутов
- `../api/*` — API модули
- `../types/*` — TypeScript типы
- `../styles/pages/*` — CSS модули страниц

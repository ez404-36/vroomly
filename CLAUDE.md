# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Vroomly** is a vehicle management web app — a monorepo with a Python/FastAPI backend and a React/TypeScript frontend, fully containerized with Docker Compose.

## Development Commands

All development runs inside Docker. The Makefile is the primary interface.

### Initial Setup

```bash
make setup-for-backend   # for backend work
make setup-for-frontend  # for frontend work
make seeds               # populate DB with initial data
```

### Running & Building

```bash
docker compose up -d     # start all services
# Backend Swagger UI: http://localhost:8077/docs
# Frontend dev server: http://localhost:5173
```

### Backend

```bash
make lint                # ruff + ty type checking
make typecheck           # ty only
make tests               # run all pytest tests
make codegen             # generate frontend TypeScript types from backend OpenAPI
make recreate-db         # drop and recreate database
```

Run a single test:
```bash
docker compose run --rm tests pytest tests/unit/apps/accounts/models/test_user_session.py -v
```

Alembic migrations (run inside the `migrations` container, working dir `/app`):
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Frontend (inside frontend container or `npm run` locally if node installed)

```bash
npm run dev              # dev server
npm run build            # production build
npm run lint             # ESLint + Stylelint
npm run lint:fix-all     # auto-fix linting
npm run format           # Prettier
npm run codegen:openapi  # regenerate src/types/schemas.ts from backend OpenAPI
```

## Architecture

### Monorepo Layout

```
vroomly/
├── backend/             # Python 3.13 FastAPI
├── frontend/            # React 19 + TypeScript + Vite
├── docker-compose.yaml
├── Makefile
└── .env                 # copied from .env.example on setup
```

### Backend

**Entry point:** `backend/main.py` — creates FastAPI app, calls `register_all_service_routers()`, and manages DB lifespan.

**App microservice pattern** — each app under `backend/apps/<name>/` follows this structure:
- `models/` — SQLAlchemy ORM models (inherit `AutoSchemaBase`)
- `api/routers.py` — must export `list_routers`; router prefix is `/api/<service_name>`
- `api/endpoints/` — class-based views using `@cbv` from `fastapi_utils`
- `api/schemas/` — Pydantic request/response models
- `service.py` — defines the service name used for prefix and DB schema

**Auto-wiring:** `core/micro_services/routers/utils.py:register_all_service_routers()` scans all `apps/*/api/routers.py` and registers every `list_routers` it finds. Adding a new app requires no manual registration.

**`AutoSchemaBase`** (`core/models/base.py`): adds UUID primary key, auto-generates table name from CamelCase class name, and assigns a PostgreSQL schema derived from the app name.

**Database:** SQLAlchemy 2.0 async + asyncpg + PostgreSQL 17. `OrmDatabase` in `core/db.py` wraps the async sessionmaker.

**Auth:** JWT (HS256) via `core/safety/`. Current user resolved from token in `common/auth/decode_token.py`. Sessions stored in DB (`UserSession` model).

**Config:** Pydantic Settings loaded from `.env` in `core/settings.py` — `DatabaseSettings`, `LibretranslateSettings`, etc.

**Tests:** pytest, organized under `backend/tests/unit/` (mirrors app structure) and `backend/tests/integrations/`.

**Linting:** Ruff (line length 120, single quotes, Python 3.13 target) + ty type checker.

### Frontend

**Entry point:** `frontend/src/main.tsx` → `src/components/App.tsx`

**Key directories:**
- `src/api/` — API call functions
- `src/store/slices/` — Redux Toolkit slices
- `src/types/schemas.ts` — **auto-generated** from backend OpenAPI; do not edit manually, run `make codegen`
- `src/AppRoutes/` — React Router v7 route definitions
- `src/ui/` — reusable Mantine-based UI components
- `src/styles/` — global CSS and Mantine theme

**State:** Redux Toolkit global store, Mantine for UI components and theming (dark/light via CSS variables).

### Docker Compose Services

Key services and their profiles:
| Service | Profile | Purpose |
|---|---|---|
| `db` | default | PostgreSQL 17 |
| `backend` | `vr-backend`, `vr-frontend` | FastAPI app (port 8077) |
| `frontend` | `vr-frontend` | React dev server (port 5173) |
| `migrations` | `vr-frontend` | Alembic (runs on frontend setup) |
| `tests` | none | pytest runner |
| `linters` | none | ruff + ty |
| `codegen` | `vr-frontend`, `vr-backend` | TypeScript generation |
| `libretranslate` | `vr-backend`, `vr-frontend` | Russian/English translation |

The Docker network uses subnet `10.245.0.0/16` to avoid VPN conflicts.

## Adding a New Backend Endpoint

1. Create `backend/apps/<service>/api/endpoints/myfeature.py` with a `@cbv` class
2. Import its router into `backend/apps/<service>/api/routers.py` and add to `list_routers`
3. Add Pydantic schemas in `api/schemas/`
4. If DB changes: `alembic revision --autogenerate -m "..."` then `alembic upgrade head`
5. Run `make codegen` to update frontend types

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

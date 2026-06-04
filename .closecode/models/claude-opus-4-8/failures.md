# Project Model Knowledge — failures & lessons

### Orchestrator-mapper split creates a service↔mapper import cycle (guess_by_vin)
- **Date:** Wed Jun 03 2026
- **Context:** Task #2 — slimmed `car_info/endpoints.py` by adding `services/guess_by_vin.py` (orchestrator) + `to_guess_by_vin_response` in `api/car_info/mappers.py`. The mapper needed to type-annotate its param with `GuessCommonCarInfoSchema`, which lives in `services/guess_common_car_info.py`. But that service module already does `from apps.vehicles.api.car_info.mappers import trims_to_choices` at runtime → a real circular import (`cannot import name 'trims_to_choices' from partially initialized module`).
- **Wrong approach:** A plain top-level `from ...guess_common_car_info import GuessCommonCarInfoSchema` in the mapper — breaks `import main`.
- **Correct approach:** The schema is used ONLY as a parameter type annotation in the mapper (never instantiated there), so import it under `if TYPE_CHECKING:` and quote the annotation (`guess: 'GuessCommonCarInfoSchema'`). Endpoint tests that previously patched the inner collaborators at the endpoint module (`...endpoints.CarInfoByVinProvider.get_info`, `...endpoints.GuessCommonCarInfo.get_from_vin01`) must be re-homed to mock the new service: `patch('...endpoints.GuessByVinService', return_value=mock)` returning a `GuessByVinResult`, then assert delegation + mapper output.
- **Rule:** When a mapper must reference a service-owned schema but the service already imports the mapper, break the cycle with `TYPE_CHECKING` + quoted annotation rather than relocating the schema. Re-point endpoint tests at the new orchestrator service.

### Frontend hook extraction: moving setState-in-effect into a custom hook trips `react-hooks/set-state-in-effect`
- **Date:** Wed Jun 03 2026
- **Context:** Extracted VehicleForm cascade into `useVehicleCatalogCascade`. The original `.tsx` had 3 override `useState` flags flipped to `false` inside `useEffect`s. After moving to a hook, ESLint (React Compiler plugin) raised `react-hooks/set-state-in-effect` ERRORS (3) on the `setXOverride(false)` calls.
- **Wrong approach:** Suppressing with eslint-disable, or keeping the `useState`+effect-mutation pattern.
- **Correct approach:** The override booleans are *derivable* from current vs prefill values (`seriesOverride = Boolean(prefill) && selectedBrand === prefillBrandId`, chained downward). Drop the `useState` + effect mutation entirely; compute them inline. Effects then only call the form-reset callback (not a `useState` setter), which is legitimate. `SerializedError` imports from `@reduxjs/toolkit`, NOT `@reduxjs/toolkit/query/react` (only `FetchBaseQueryError` is there). The `watch()` → `react-hooks/incompatible-library` is a WARNING (RHF limitation), acceptable.
- **Rule:** When extracting hooks, prefer deriving state over `useState`+effect-mutation; the React Compiler eslint rules treat synchronous setState-in-effect as an error. Verify import sources for RTK types (`SerializedError` lives in the root package).

### New test package under tests/unit/apps collides on bare `repositories` name (rootdir import mode)
- **Date:** Wed Jun 03 2026
- **Context:** Added `tests/unit/apps/geo/repositories/test_country.py` next to existing `tests/unit/apps/vehicles/repositories/`. Running both in one session failed `ModuleNotFoundError: No module named 'repositories.test_country'` — pytest `prepend` import mode walks up collecting `__init__.py` until a dir lacks one; intermediate `tests/unit/apps/`, `vehicles/`, `geo/` had NO `__init__.py`, so each leaf `repositories/__init__.py` resolved as a bare top-level `repositories` package → two dirs claim the same package name.
- **Wrong approach:** Asserting on column substrings for "no filter" tests (`assert 'generation_id' not in sql`) — the FK column is in the SELECT list regardless, so it always fails. Use `assert 'WHERE' not in sql` instead.
- **Correct approach:** Add the missing intermediate `__init__.py` (`tests/unit/apps/__init__.py`, `tests/unit/apps/vehicles/__init__.py`, `tests/unit/apps/geo/__init__.py`) so packages become fully-qualified `tests.unit.apps.<app>.<layer>` and are unique. (`tests/unit/__init__.py` already existed; the tree was inconsistently packaged.)
- **Rule:** When adding a test dir that duplicates a layer name (`repositories`, `services`) under a new app, ensure the full `__init__.py` chain exists up to `tests/unit` so the package path is unique; verify by running the new + sibling test together, not just alone. `scripts.generate_dataclasses` collection error is pre-existing/unrelated.

### God-class split (Phase 4): orchestrator keeps re-exporting moved symbols; LSP diagnostics go stale after full-file rewrite
- **Date:** Wed Jun 03 2026
- **Context:** Split `GuessCommonCarInfo` (331 lines) into `api/car_info/mappers.py` (labels + `trim_to_choice`), `repositories/fuzzy_lookup.py` (`fuzzy_lookup` + trigram consts + `GuessCommonCarInfoError`), `repositories/car_catalog.py` (generations/trims queries). Service became a thin orchestrator (translate→catalog→mapper).
- **Gotcha 1:** `GuessCommonCarInfoError` is imported across layers; define it in the lowest layer that raises it (`fuzzy_lookup.py`) and **re-export** from the service via `__all__` so existing `from ...guess_common_car_info import GuessCommonCarInfoError` callers/tests keep working without a circular import.
- **Gotcha 2:** After Write-replacing a whole file, the inline LSP "errors detected" block referenced OLD line numbers (21–460) from the pre-rewrite version — pure stale cache. Verified disk with `wc -l`/grep, then trusted `ruff`+`ty` (both clean). Do NOT chase LSP-reported errors whose line numbers exceed the new file length.
- **Rule:** On god-class splits, re-export moved public symbols from the original module; verify with `ruff`+`ty`+pytest, not the inline LSP diff (which can lag a full-file rewrite).

### SRP layer extraction: endpoint tests that patch `database` at the endpoint module break
- **Date:** Wed Jun 03 2026
- **Context:** Phase 2 — extracted reminder logic into `ReminderService`/repositories; endpoints became thin. Existing `test_reminder.py` patched `apps.vehicles.api.reminder.endpoints.database` and called endpoint methods directly, asserting on `session.add/commit/refresh`.
- **Wrong approach:** Leaving those tests as-is — after extraction the endpoint no longer touches `database`, so the patch target is gone and the DB assertions belong to a different layer.
- **Correct approach:** Split tests by layer: endpoint tests mock the *service* (`patch('...endpoints.ReminderService', return_value=mock)`) and assert delegation + `None`→404 mapping; business-logic/idempotency/ownership tests move to a new `services/test_<x>_service.py` that mocks `database.get_async_session` + the repositories. Keep schema-validation tests untouched.
- **Rule:** When extracting service/repo layers, re-home tests to the layer that now owns the behavior; endpoint tests should only verify delegation + HTTP mapping, never DB internals.

### Backend layer convention: repositories return `| None`, services own transactions, mappers do ORM→schema
- **Date:** Wed Jun 03 2026
- **Context:** Phases 0–2 established `apps/vehicles/repositories/` (data access, ownership filters by `user_id`, return `| None`), `services/` (transactions + invariants, return ORM-or-None / bool), `api/<x>/mappers.py` (ORM→Pydantic), thin `endpoints.py` (HTTP only). Schemas stay in `schemas` (NOT `serializers`).
- **Gotcha:** `database.fetch_all` returns `Any`, which masked an ORM-vs-schema return-type mismatch in list endpoints; `ty` caught it only once the repository was typed as `list[Model]`. Always map ORM→schema explicitly in the endpoint, don't rely on FastAPI implicit `model_validate` under a schema-typed annotation.
- **Rule:** New backend CRUD follows repo→service→mapper→endpoint. Repos/services never raise `HTTPException`; only endpoints do. Verify each phase with `ruff` + `ty` (authoritative; ignore Pyright/LSP false positives on dynamic mixin base classes) + scoped pytest + `import main; configure_mappers()`.

### RTK Query endpoint `query` builder is not directly callable in tests
- **Date:** Fri May 29 2026
- **Context:** Phase I — tried to unit-test reminder endpoint URL/method mapping via `vehiclesApi.endpoints.X.query(arg)`.
- **Wrong approach:** Accessing `endpoints.X.query` as a function — it is `undefined`/not a function. Also tried driving the store + `vi.stubGlobal('fetch')`, but the custom `baseQuery` (`createBaseQuery`) does `await import('../mocks')` and routes through a mock baseQuery, so the stubbed fetch was never hit.
- **Correct approach:** For request-mapping assertions prefer an integration test that goes through the store with the mock path forced off AND a reliably-intercepted transport — or skip low-value URL-mapping tests (they were "optional" in the plan). The high-value behavioral tests (component + page-level) are robust via `vi.mock('../api/vehiclesApi', ...)`.
- **Rule:** Don't assume RTK Query exposes raw `query` builders; test behavior through mocked hooks or the store, not internal endpoint fields.

### Subagent resume can duplicate work / leave broken artifacts
- **Date:** Fri May 29 2026
- **Context:** Phase H & I subagents returned only an acknowledgment (no final report); resuming the same task_id produced near-duplicate files (two `ReminderItem.test.tsx`, two GaragePage delete tests) and one broken test.
- **Wrong approach:** Trusting the subagent's (missing) report and moving on.
- **Correct approach:** After a subagent that returned INCOMPLETE-style output, always `git status`/inspect disk, de-duplicate, and run the actual gates (tests/tsc/eslint) yourself before marking a phase done.
- **Rule:** Verify subagent output on disk + run verification commands; never mark a phase complete on an unverified subagent report.

### Frontend codegen requires a running, ready backend
- **Date:** Fri May 29 2026
- **Context:** `make codegen` fetches `${BACKEND_URL}/openapi.json` over HTTP. First run failed `ECONNREFUSED` right after the backend container was recreated.
- **Rule:** Before `make codegen`, ensure the backend container is Up and "Application startup complete"; retry once if it was just (re)started. `schema-types.ts` is hand-maintained — add new aliases manually; only `schemas.ts` is generated.

### JTI + AutoSchemaBase: get_table_name must read cls.__dict__, not inherited __tablename__
- **Date:** Fri May 29 2026
- **Context:** Implementing Joined Table Inheritance (VehicleNode root + EngineNode detail). configure_mappers() failed: "Table 'vehicles.vehicle_node' is already defined".
- **Wrong approach:** Assuming JTI subclasses auto-get their own tablename. `AutoSchemaBase.get_table_name` used `getattr(cls, '__tablename__', None)`, which returns the PARENT's inherited `__tablename__`, so the child tried to redefine the parent table.
- **Correct approach:** Use `cls.__dict__.get('__tablename__')` so only an explicitly-set-on-this-class tablename is honored. JTI child `id` must be redefined as `mapped_column(UUID, ForeignKeyTo(parent,'CASCADE'), primary_key=True)` via a mixin. Cross-table unique constraints are impossible in JTI — keep ALL natural-key columns (name, brand_id, volume...) on the DETAIL table; the base node holds only the discriminator (node_type) + id.
- **Rule:** For JTI under AutoSchemaBase: detail tables own all data + natural keys; base = node_type + id only. Validate every incremental model with `docker compose run --rm backend-build python -c "...; configure_mappers()"` before moving on.

### JTI seed import: Core insert() writes one table; use ORM add_all for both
- **Date:** Fri May 29 2026
- **Context:** Phase 4 — seeding EngineNode/CarTransmissionNode (JTI). Base CSV importer used `insert(self.model).values(batch)` (Core), which writes only the detail table, leaving `vehicle_node` (base) empty → broken JTI rows.
- **Correct approach:** Added `ImportJTINodesFromCSVBase` overriding `bulk_insert` with ORM `session.add_all([self.model(**data) ...]); await session.flush()`. SQLAlchemy then populates BOTH `vehicle_node` (id + node_type from polymorphic_identity) and the detail table. CSV must include `id`. Regenerate seed CSVs from migrated DB via `\copy (SELECT <detail cols incl id>) TO STDOUT WITH CSV HEADER`.
- **Rule:** For JTI seeding never use Core `insert()`; use ORM `add_all`. node_type is auto-filled from polymorphic_identity — don't put it in CSV.

### replaceAll on a class name can corrupt its own import line
- **Date:** Fri May 29 2026
- **Context:** Renaming `CarTransmission`→`CarTransmissionNode` via Edit replaceAll across a file ALSO matched the substring inside the freshly-added `from ...transmission_node import CarTransmissionNode` import, mangling/duplicating it (F821 undefined name).
- **Rule:** When using replaceAll for a rename, do the import-line edit LAST, or verify imports with grep after; prefer renaming via distinct full-qualified edits when the new name contains the old as a substring.

### Mutual M2M relationship fails to init depending on import order
- **Date:** Sat May 30 2026
- **Context:** `VehicleReminder.nodes` ↔ `UserVehicleNode.reminders` (M2M via `reminder_node_link`). App startup failed: "mappers failed to initialize ... 'vehicles.reminder_node_link'" when only one side was imported (reminders API imports reminder.py alone; the association Table lived in user_vehicle_node.py).
- **Wrong approach:** String `secondary='vehicles.reminder_node_link'` alone — the table/other-class isn't registered unless both modules are imported. Importing the other module at the TOP of one side creates a real circular import.
- **Correct approach:** Both relationships use string refs (class + secondary table). Each module imports the OTHER at the BOTTOM (after its own class is defined): `reminder.py` ends with `import ...node.user_vehicle_node`, and `user_vehicle_node.py` ends with `import ...vehicle.reminder`. Trailing placement breaks the cycle (the importing module's class is already defined when the partial module is returned), and guarantees both sides register regardless of entry point. Verify with isolated imports of EACH side + `configure_mappers()` + `import main`.
- **Rule:** For mutually-dependent mapped classes (M2M/bidirectional), use string refs AND a trailing cross-import in each module. Always test BOTH single-side import paths, not just the loader.

### Frontend has no test infra by default; full-project eslint OOMs in container
- **Date:** Fri May 29 2026
- **Context:** No Vitest/RTL was installed pre-Phase I. Also `npm run lint` (eslint .) over the whole project times out / OOMs in the frontend container.
- **Rule:** Vitest+RTL stack: vitest ^3, @testing-library/react ^16, jsdom ^25, jest-dom ^6, user-event ^14. Scope eslint to changed files (`npx eslint <files>`, with `NODE_OPTIONS=--max-old-space-size=4096`); rely on `tsc --noEmit` for project-wide type safety.

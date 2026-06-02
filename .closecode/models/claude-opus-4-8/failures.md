# Project Model Knowledge — failures & lessons

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

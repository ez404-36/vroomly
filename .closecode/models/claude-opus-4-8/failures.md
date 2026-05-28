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

### Frontend has no test infra by default; full-project eslint OOMs in container
- **Date:** Fri May 29 2026
- **Context:** No Vitest/RTL was installed pre-Phase I. Also `npm run lint` (eslint .) over the whole project times out / OOMs in the frontend container.
- **Rule:** Vitest+RTL stack: vitest ^3, @testing-library/react ^16, jsdom ^25, jest-dom ^6, user-event ^14. Scope eslint to changed files (`npx eslint <files>`, with `NODE_OPTIONS=--max-old-space-size=4096`); rely on `tsc --noEmit` for project-wide type safety.

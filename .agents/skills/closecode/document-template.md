---
closecode_version: 1.1.0
provisionedAt: "2026-04-30T16:58:06.655Z"
provisionedFrom: templates/skills/closecode/SKILL.md
---

# Document Template Reference

This file shows the correct frontmatter format for each document type with realistic example values.

---

## Idea Example

```markdown
---
id: "3be5e1b7-47aa-4118-a0be-eb0e56f9013c"
title: "Add User Activity Dashboard"
tags:
  - feature
  - ui
  - dashboard
status: draft
priority: medium
linkedDialogIds:
  - "f1a2b3c4-d5e6-7890-abcd-111111111111"
createdAt: "2026-02-15T10:30:00.000Z"
updatedAt: "2026-02-20T14:45:00.000Z"
---

# Add User Activity Dashboard

## Concept

A dashboard showing user activity metrics — session counts, active projects,
and recent document changes. Would help users track their workflow patterns.

## Open Questions

- Should this be a standalone page or a panel widget?
- What time ranges make sense (daily, weekly, monthly)?

&nbsp;
```

---

## Plan Example

```markdown
---
id: "edaa96eb-40f4-47af-a4b5-287a05187136"
title: "API Authentication Overhaul"
tags:
  - backend
  - auth
  - security
status: active
priority: high
linkedDialogIds:
  - "a2138149-a6b6-4e23-8370-253f8d838cec"
createdAt: "2026-02-18T09:00:00.000Z"
updatedAt: "2026-02-25T16:20:00.000Z"
sourceDialogId: "a2138149-a6b6-4e23-8370-253f8d838cec"
sourceMessageId: "msg-7f8e9d0c-b1a2-3456-cdef-222222222222"
linkedIdeaIds:
  - "3be5e1b7-47aa-4118-a0be-eb0e56f9013c"
linkedReviewIds:
  - "5e6f7a8b-c9d0-4e1f-2a3b-4c5d6e7f8a9c"
---

# API Authentication Overhaul

## Objective

Replace the current session-based auth with JWT tokens and refresh token rotation.

## Approach

1. Add JWT signing/verification service
2. Create refresh token rotation middleware
3. Migrate existing session endpoints
4. Update all protected route guards

## Success Criteria

- All API endpoints use JWT authentication
- Refresh tokens rotate on each use
- Existing clients continue working via migration shim

&nbsp;
```

---

## Review Example

```markdown
---
id: "5e6f7a8b-c9d0-4e1f-2a3b-4c5d6e7f8a9c"
title: "Auth Library Comparison — jose vs jsonwebtoken vs passport-jwt"
tags:
  - research
  - auth
  - backend
  - security
status: done
priority: high
linkedDialogIds: []
createdAt: "2026-02-16T11:00:00.000Z"
updatedAt: "2026-02-22T09:15:00.000Z"
sourceDialogId: "b3c4d5e6-f7a8-9012-bcde-333333333333"
sourceMessageId: ""
linkedIdeaIds:
  - "3be5e1b7-47aa-4118-a0be-eb0e56f9013c"
linkedPlanIds:
  - "edaa96eb-40f4-47af-a4b5-287a05187136"
---

# Auth Library Comparison — jose vs jsonwebtoken vs passport-jwt

## Summary

Evaluated three JWT libraries for the authentication overhaul. Recommendation: **jose**.

## Comparison

| Library      | Bundle Size | Maintenance | ESM Support | Edge Runtime |
| ------------ | ----------- | ----------- | ----------- | ------------ |
| jose         | 12 KB       | Active      | Native      | Yes          |
| jsonwebtoken | 45 KB       | Slow        | CJS only    | No           |
| passport-jwt | 8 KB + deps | Active      | Partial     | No           |

## Recommendation

Use `jose` — smallest bundle, native ESM, active maintenance, and works in edge runtimes.
The `jsonwebtoken` package has known maintenance gaps and lacks ESM support.

&nbsp;
```

---

## Issue Example

```markdown
---
id: "c4d5e6f7-a8b9-0c1d-2e3f-4a5b6c7d8e9f"
title: "WebSocket Disconnects on Large Payloads"
tags:
  - bug
  - websocket
  - backend
status: active
priority: high
linkedDialogIds:
  - "d5e6f7a8-b9c0-1d2e-3f4a-555555555555"
createdAt: "2026-02-24T08:15:00.000Z"
updatedAt: "2026-02-27T11:30:00.000Z"
linkedIdeaIds: []
linkedPlanIds:
  - "edaa96eb-40f4-47af-a4b5-287a05187136"
linkedReviewIds: []
---

# WebSocket Disconnects on Large Payloads

## Problem

WebSocket connections drop when sending messages larger than ~64 KB. The client
receives a close frame with code 1006 (abnormal closure) and no error message.

## Steps to Reproduce

1. Open a dialog with a large codebase context
2. Send a message that triggers a response > 64 KB
3. Connection drops mid-stream

## Expected Behavior

Large messages should be chunked or the frame size limit should be increased.

## Investigation Notes

- Likely related to the default `maxPayload` setting in the `ws` library
- Check `WebSocketAdapter` configuration

&nbsp;
```

&nbsp;

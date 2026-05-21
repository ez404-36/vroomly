---
name: websocket-messages
description: WebSocket message format for dialog gateway - acp envelope pattern and parameter extraction
closecode_version: 1.0.0
scope: user
provisionedAt: "2026-04-30T16:58:06.666Z"
provisionedFrom: templates/skills/websocket-messages/SKILL.md
---

# WebSocket Messages Skill

This skill teaches agents how to correctly handle WebSocket messages in the dialog gateway. The frontend wraps payloads in an `acp` envelope, and extracting parameters from the wrong location causes silent failures.

## 1. Message Structure

The frontend sends messages via `sendDialogMessage()` which wraps all payload data in an `acp` envelope:

```typescript
// Frontend sends:
{
  type: "some/event",
  dialogId: "xxx",
  acp: {
    // All domain parameters go here
    serverName: "my-server",
    config: { ... },
    action: "start"
  }
}
```

## 2. Parameter Extraction

**CRITICAL: Extract parameters from the correct location.**

| Parameter     | Location                 | Example                                   |
| ------------- | ------------------------ | ----------------------------------------- |
| `dialogId`    | Top-level `msg.dialogId` | `const { dialogId } = msg;`               |
| Domain params | Inside `msg.acp`         | `const serverName = msg.acp?.serverName;` |

## 3. Correct Handler Pattern

```typescript
// CORRECT: Extract domain params from msg.acp
private async handleSomeEvent(
  msg: { type: string; dialogId?: string; acp?: { someParam?: string } },
  client: WebSocket
): Promise<void> {
  const { dialogId } = msg;
  const someParam = msg.acp?.someParam;  // Read from acp, not top-level

  if (!someParam) {
    this.sendError(client, "someParam is required", "MISSING_PARAM");
    return;
  }
  // ...
}
```

## 4. Common Mistakes

### Mistake 1: Reading from Top-Level

```typescript
// WRONG: someParam will always be undefined
const { dialogId, someParam } = msg;

// The frontend wraps someParam in acp, so it's at msg.acp.someParam
// Reading from msg.someParam returns undefined
```

### Mistake 2: Destructuring acp Without Checking

```typescript
// RISKY: Will throw if acp is undefined
const { someParam } = msg.acp;

// SAFER: Use optional chaining
const someParam = msg.acp?.someParam;
```

### Mistake 3: Inconsistent Type Definitions

```typescript
// WRONG: Type doesn't match actual message structure
interface SomeMessage {
  type: string;
  dialogId: string;
  someParam: string; // This doesn't exist at top-level!
}

// CORRECT: Type matches the acp envelope
interface SomeMessage {
  type: string;
  dialogId: string;
  acp?: {
    someParam?: string;
  };
}
```

## 5. Why This Matters

1. **Silent failures**: Reading from the wrong location returns `undefined` without errors
2. **Hard to debug**: The parameter exists in the message, just not where expected
3. **Inconsistent**: Different gateways may have different envelope patterns
4. **Breaking changes**: Refactoring sendDialogMessage requires updating all handlers

## 6. Handler Template

Use this template for new handlers:

```typescript
private async handleEvent(
  msg: {
    type: string;
    dialogId?: string;
    acp?: {
      param1?: string;
      param2?: number;
    };
  },
  client: WebSocket
): Promise<void> {
  const { dialogId } = msg;

  // Extract all domain params from acp
  const param1 = msg.acp?.param1;
  const param2 = msg.acp?.param2;

  // Validate required params
  if (!param1) {
    this.sendError(client, "param1 is required", "MISSING_PARAM");
    return;
  }

  // Business logic...
}
```

## 7. File References

| File                                    | Purpose                    |
| --------------------------------------- | -------------------------- |
| `<backend>/dialogs/dialogs.gateway.ts`  | WebSocket gateway handlers |
| `<frontend>/dialogs/dialog-messages.ts` | Frontend message sending   |
| `<frontend>/types/dialog.ts`            | Dialog message types       |

&nbsp;

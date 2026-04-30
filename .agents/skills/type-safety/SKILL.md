---
name: type-safety
description: Strict TypeScript type safety - prohibited patterns, type guards, DTO updates, and proper alternatives
closecode_version: 1.0.0
scope: any
provisionedAt: "2026-04-30T16:58:06.663Z"
provisionedFrom: templates/skills/type-safety/SKILL.md
---

# Type Safety Skill

This skill teaches agents how to maintain strict type safety in TypeScript projects. Type assertions that bypass TypeScript checking are prohibited.

## 1. Prohibited Patterns

**NEVER** use these patterns to bypass type checking:

| Pattern            | Why It's Bad                                  |
| ------------------ | --------------------------------------------- |
| `as any`           | Completely disables type checking             |
| `as unknown as T`  | Double assertion to force incompatible types  |
| `@ts-ignore`       | Silences errors without fixing the issue      |
| `@ts-expect-error` | Only acceptable in specific cases (see below) |

Type assertions hide bugs and defeat the purpose of TypeScript.

## 2. Proper Alternatives

### Update DTOs/Interfaces

If a property doesn't exist on a type, the type definition is incomplete — fix it:

```typescript
// BEFORE: Missing property causes error
interface SomeObject {
  existingProperty: string;
}

// AFTER: Add the missing property
interface SomeObject {
  existingProperty: string;
  missingProperty: string;
}
```

### Create Type Guards

For runtime validation, use type guards:

```typescript
function isServerConfig(obj: unknown): obj is ServerConfig {
  return typeof obj === "object" && obj !== null && "host" in obj && "port" in obj;
}

const config = isServerConfig(userInput) ? userInput : defaultConfig;
```

### Create Mapper Functions

For explicit type conversions:

```typescript
function mapResponseToModel(response: ApiResponse): MyType {
  return {
    id: response.id,
    name: response.name,
  };
}

const data = mapResponseToModel(response);
```

### Extend Types

When the actual type is a superset:

```typescript
interface ExtendedWindow extends Window {
  customProperty: string;
}

const value = (window as ExtendedWindow).customProperty;
```

## 3. Acceptable Use of @ts-expect-error

Only use `@ts-expect-error` in these specific cases:

### Testing Error Conditions

```typescript
test("should throw error for invalid input", () => {
  // @ts-expect-error - Testing invalid argument
  expect(() => myFunction(null)).toThrow();
});
```

### Documented Third-Party Issues

```typescript
// @ts-expect-error - Legacy library has incorrect type definition, see issue #1234
const result = legacyLibrary.incorrectlyTypedMethod();
```

**Requirements for third-party use:**

- Must include a comment explaining why
- Must reference an issue/ticket if applicable
- Should be temporary until the library is fixed

## 4. Examples

### Bad: Type Assertion Hacks

```typescript
// BAD: Bypasses all type checking
const config = response as any;

// BAD: Double assertion
const data = response as unknown as ServerConfig;

// BAD: Silent error suppression
// @ts-ignore
config.nonExistentProperty = "value";
```

### Good: Proper Solutions

```typescript
// GOOD: Update the interface
interface ApiResponse {
  host: string;
  port: number;
}

// GOOD: Type guard with validation
function isValidResponse(obj: unknown): obj is ApiResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as ApiResponse).host === "string" &&
    typeof (obj as ApiResponse).port === "number"
  );
}

// GOOD: Explicit mapper
function toServerConfig(response: ApiResponse): ServerConfig {
  return {
    host: response.host,
    port: response.port,
  };
}
```

## 5. Checklist

Before using a type assertion:

- [ ] Can I update the DTO/interface to include the property?
- [ ] Can I create a type guard for runtime validation?
- [ ] Can I create a mapper function for conversion?
- [ ] Can I extend the type to match reality?
- [ ] If using @ts-expect-error, is it for testing or a documented library issue?

If the answer to all of the above is "no", reconsider your approach.

&nbsp;

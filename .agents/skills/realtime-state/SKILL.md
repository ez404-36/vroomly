---
name: realtime-state
description: Zustand store patterns + WebSocket event handling for real-time UI updates
closecode_version: 1.0.0
scope: user
provisionedAt: "2026-04-30T16:58:06.661Z"
provisionedFrom: templates/skills/realtime-state/SKILL.md
---

# Real-time State Management Skill

This skill teaches agents how to implement real-time UI updates using Zustand stores and WebSocket events.

## 1. Architecture Overview

```
Backend                          WebSocket Gateway              Frontend
┌──────────────────┐            ┌──────────────────┐         ┌──────────────────┐
│ Service          │            │ EventsGateway    │         │ GlobalEvents     │
│ (EventEmitter2)  │ ─────────► │ @OnEvent()       │ ───────► │ Manager         │
│                  │            │ broadcastToProject│         │                  │
└──────────────────┘            └──────────────────┘         └────────┬─────────┘
                                                                       │
                                                                       ▼
                                                                ┌──────────────────┐
                                                                │ Zustand Store    │
                                                                │ (tasksStore,    │
                                                                │  schedulesStore)│
                                                                └────────┬─────────┘
                                                                         │
                                                                         ▼
                                                                ┌──────────────────┐
                                                                │ React Components│
                                                                │ (selectors)     │
                                                                └──────────────────┘
```

## 2. Event Flow

### 2.1 Backend Event Emission

**Location:** Service files (e.g., `tasks.service.ts`, `schedules.service.ts`)

**Pattern:**

```typescript
this.eventEmitter.emit("entity.action", {
  entity: FullEntity, // Include FULL entity, not just ID
  projectId: string,
  // ... other fields
});
```

**Critical Rule:** Always include full entity data in event payloads. Clients need the complete object to update their stores without additional API calls.

**Example:**

```typescript
// ✅ GOOD - Full entity included
this.eventEmitter.emit("task.created", { task });

// ❌ BAD - Only ID, client must fetch
this.eventEmitter.emit("task.created", { taskId, projectId });
```

### 2.2 WebSocket Gateway Forwarding

**Location:** `<backend>/events/events.gateway.ts`

**Pattern:**

```typescript
@OnEvent("backend.event.name")
handleEventName(event: EventPayload): void {
  this.broadcastToProject(event.projectId, {
    type: "websocket/event_name",  // Slash notation for client
    projectName: event.projectId,
    entity: event.entity,
  });
}
```

**Naming Convention:**

- Backend: `entity.action` (dot notation)
- WebSocket: `entity/action` (slash notation)

### 2.3 Frontend Event Handling

**Location:** `<frontend>/events/global-events-manager.ts`

**Pattern:**

```typescript
case "entity/action": {
  const msg = message as EntityActionMessage;

  // 1. UPDATE STORE FIRST
  useEntityStore.getState().updateAction(msg.projectName, msg.entity);

  // 2. THEN route to handlers (for useTaskMonitor, etc.)
  this.routeToProjectHandlers(message.projectName, (h) => h.onEntityAction?.(message));
  break;
}
```

**Critical Rule:** Always update the store BEFORE routing to handlers. This ensures store-based components see updates immediately.

### 2.4 Store Actions

**Location:** `<frontend>/stores/tasksStore.ts`, `<frontend>/stores/schedulesStore.ts`

**Pattern:**

```typescript
// Action updates the Map with immutable pattern
updateEntity: (projectId: string, entity: Entity) => {
  set((state) => {
    const projectMap = state.entitiesByProject.get(projectId);
    if (!projectMap) return state;

    const newProjectMap = new Map(projectMap);
    newProjectMap.set(entity.id, entity);

    const newByProject = new Map(state.entitiesByProject);
    newByProject.set(projectId, newProjectMap);

    return { entitiesByProject: newByProject };
  });
},
```

## 3. Zustand Stable Reference Patterns

### 3.1 The Problem

React 19's `useSyncExternalStore` + Zustand selectors can cause infinite re-renders if selectors return new references on every call.

**Symptoms:**

- Infinite render loops
- Browser tab crash/freeze
- CPU spike

**Root Cause:**

```typescript
// ❌ WRONG - Creates new array every render
export const useEntitiesList = (projectId: string): Entity[] =>
  useStore((state) => Array.from(state.entitiesByProject.get(projectId)?.values() ?? []));
```

Even if data hasn't changed, `Array.from()` creates a new array reference, triggering re-renders.

### 3.2 The Solution: useShallow + useMemo

**Pattern:**

```typescript
import { useMemo } from "react";
import { useShallow } from "zustand/react/shallow";

// Stable empty references at module level
const EMPTY_ENTITIES: Entity[] = [];

// Single entity selector - useShallow for reference stability
export const useEntity = (projectId: string, entityId: string): Entity | undefined =>
  useStore(useShallow((state) => state.entitiesByProject.get(projectId)?.get(entityId)));

// List selector - useShallow + useMemo for derived arrays
export const useEntitiesList = (projectId: string): Entity[] => {
  const entityMap = useStore(useShallow((state) => state.entitiesByProject.get(projectId)));
  return useMemo(() => (entityMap ? Array.from(entityMap.values()) : EMPTY_ENTITIES), [entityMap]);
};

// Computed selector - useMemo for derived data
export const useActiveEntities = (projectId: string): Entity[] => {
  const entities = useEntitiesList(projectId);
  return useMemo(() => entities.filter((e) => e.status === "active"), [entities]);
};
```

### 3.3 Key Rules

| Pattern                | When to Use               | Example                               |
| ---------------------- | ------------------------- | ------------------------------------- |
| `useShallow`           | Selecting from Map/object | `state.map.get(id)`                   |
| `useMemo`              | Deriving arrays/objects   | `Array.from()`, `.filter()`, `.map()` |
| Module-level constants | Empty fallbacks           | `const EMPTY: T[] = [];`              |
| `useShallow + useMemo` | Map → Array conversion    | `Array.from(map.values())`            |

### 3.4 Why This Works

1. `**useShallow**` caches the previous result and compares shallowly
   - If Map entries haven't changed, returns cached reference
   - Zustand's shallow comparison handles Maps natively
2. `**useMemo**` only recomputes when dependencies change
   - Dependency is the stable Map reference from useShallow
   - Array only recreated when Map actually changes
3. **Module-level constants** provide stable fallbacks
   - `?? []` creates new array every time
   - `?? EMPTY_ARRAY` returns same reference

## 4. Data Structure Design

### 4.1 Store Structure

Use nested Maps for O(1) lookups:

```typescript
interface StoreState {
  // projectId → entityId → entity
  entitiesByProject: Map<string, Map<string, Entity>>;

  // Track loaded/loading state
  loadedProjects: Set<string>;
  loadingProjects: Set<string>;
}
```

### 4.2 Initialization

Load data when project opens (in page component):

```typescript
// In IDEModePage.tsx or similar
useEffect(() => {
  if (projectName) {
    useTasksStore.getState().loadProjectTasks(projectName);
    useSchedulesStore.getState().loadProjectSchedules(projectName);
  }
}, [projectName]);
```

### 4.3 Cleanup

Clear data when leaving project:

```typescript
useEffect(() => {
  return () => {
    if (projectName) {
      useTasksStore.getState().clearProject(projectName);
      useSchedulesStore.getState().clearProject(projectName);
    }
  };
}, [projectName]);
```

## 5. Component Migration Pattern

### 5.1 From React Query to Zustand

**Before (with polling):**

```typescript
const {
  data: entities,
  isLoading,
  refetch,
} = useQuery({
  queryKey: ["entities", projectId],
  queryFn: () => api.list(projectId),
  refetchInterval: 10_000, // Polling
});
```

**After (real-time via store):**

```typescript
import { useEntitiesList, useEntitiesLoaded, useEntityStore } from "../stores/entityStore";

const entities = useEntitiesList(projectId);
const isLoaded = useEntitiesLoaded(projectId);
const isLoading = !isLoaded;

const handleRefresh = useCallback(async () => {
  await useEntityStore.getState().loadProjectEntities(projectId);
}, [projectId]);
```

**Benefits:**

- No polling (10s intervals removed)
- Real-time updates via WebSocket
- Single source of truth

### 5.2 Hybrid Pattern (for complex components)

Some components need data from both store and specialized sources:

```typescript
// Task data from store (real-time status, runs, etc.)
const task = useTask(projectName, taskId);

// Conversation messages from dialog WebSocket (not in store)
const { feedEntries, activityStatus } = useTaskMonitor(dialogId);
```

## 6. Event Types Reference

### 6.1 Tasks Events

| Backend Event        | WebSocket Type       | Store Action        |
| -------------------- | -------------------- | ------------------- |
| `task.created`       | `task/created`       | `addTask`           |
| `task.updated`       | `task/updated`       | `updateTask`        |
| `task.deleted`       | `task/deleted`       | `deleteTask`        |
| `task.status`        | `task/status`        | `updateTaskStatus`  |
| `task.run.started`   | `task/run_started`   | `addRunToTask`      |
| `task.run.progress`  | `task/run_progress`  | `updateRunProgress` |
| `task.run.completed` | `task/run_completed` | `completeRunInTask` |
| `task.notification`  | `task/notification`  | `addNotification`   |

### 6.2 Schedules Events

| Backend Event        | WebSocket Type       | Store Action           |
| -------------------- | -------------------- | ---------------------- |
| `schedule.created`   | `schedule/created`   | `addSchedule`          |
| `schedule.updated`   | `schedule/updated`   | `updateSchedule`       |
| `schedule.deleted`   | `schedule/deleted`   | `deleteSchedule`       |
| `schedule.status`    | `schedule/status`    | `updateScheduleStatus` |
| `schedule.triggered` | `schedule/triggered` | `markTriggered`        |

## 7. Common Mistakes

### 7.1 Creating New References in Selectors

```typescript
// ❌ WRONG
const useActiveCount = (projectId: string) =>
  useStore(
    (state) =>
      Array.from(state.entities.get(projectId)?.values() ?? []).filter((e) => e.active).length
  );

// ✅ CORRECT
const useActiveCount = (projectId: string) => {
  const entities = useEntitiesList(projectId);
  return useMemo(() => entities.filter((e) => e.active).length, [entities]);
};
```

### 7.2 Not Using useShallow for Map Access

```typescript
// ❌ WRONG - Reference changes every render
const useEntity = (projectId: string, entityId: string) =>
  useStore((state) => state.entities.get(projectId)?.get(entityId));

// ✅ CORRECT - Stable reference
const useEntity = (projectId: string, entityId: string) =>
  useStore(useShallow((state) => state.entities.get(projectId)?.get(entityId)));
```

### 7.3 Inline Object Creation

```typescript
// ❌ WRONG - New object every render
const { entity, status } = useStore((state) => ({
  entity: state.entities.get(id),
  status: state.statuses.get(id),
}));

// ✅ CORRECT - Separate selectors
const entity = useStore(useShallow((state) => state.entities.get(id)));
const status = useStore(useShallow((state) => state.statuses.get(id)));
```

## 8. File References

| File                                         | Purpose                   |
| -------------------------------------------- | ------------------------- |
| `<frontend>/stores/tasksStore.ts`            | Task state management     |
| `<frontend>/stores/schedulesStore.ts`        | Schedule state management |
| `<frontend>/events/global-events-manager.ts` | WebSocket event routing   |
| `<frontend>/events/types.ts`                 | Message type definitions  |
| `<backend>/events/events.gateway.ts`         | Backend event forwarding  |
| `<frontend>/types/task.ts`                   | Task/TaskRun types        |

## 9. Checklist for New Event Implementation

- Backend: Emit event with full entity data
- Backend: Event payload includes `projectId` for routing
- Gateway: Add `@OnEvent` handler
- Gateway: Broadcast with correct message type (slash notation)
- Frontend types: Add message interface
- Store: Add action for the update
- GlobalEventsManager: Add case handler that calls store action
- GlobalEventsManager: Update store BEFORE routing to handlers
- Components: Use store selectors (not React Query)
- Selectors: Use useShallow + useMemo pattern

&nbsp;

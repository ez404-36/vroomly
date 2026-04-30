---
name: workflow-authoring
description: How to author CloseCode ADE workflows — node types, socket compatibility, connection rules, and common patterns
closecode_version: 1.0.0
scope: user
provisionedAt: "2026-04-30T16:58:06.668Z"
provisionedFrom: templates/skills/workflow-authoring/SKILL.md
---

# Workflow Authoring Skill

This skill teaches agents how to author CloseCode ADE workflows — visual flow-based automations built from typed nodes connected by compatible sockets.

## 1. Overview

A **workflow** is a directed graph of typed nodes connected by edges. Workflows are persisted as `WorkflowDefinition` objects with nodes, edges, triggers, and settings.

**Key concepts:**
- **Nodes** — Processing units with typed input/output sockets
- **Edges** — Connections between an output socket on one node and an input socket on another
- **Triggers** — Binding nodes to external events (manual, cron, webhook, schedule)
- **Pipeline Interface** — Contract nodes (`pipeline-input` / `pipeline-output`) that define a sub-workflow's external API

## 2. MCP Tools Reference

Use these closecode MCP tools (activate closecode tools first):

| Tool | Purpose |
|------|---------|
| `closecode_list_workflow_node_types` | Discover all available node kinds with their I/O sockets |
| `closecode_suggest_compatible_nodes` | Find nodes compatible with a given socket |
| `closecode_create_workflow` | Create a new workflow with nodes and edges |
| `closecode_update_workflow` | Update existing workflow (partial) |
| `closecode_validate_workflow` | Validate structure (socket compatibility, cycles, required inputs) |
| `closecode_run_workflow` | Trigger a workflow run (returns runId) |
| `closecode_get_workflow_run` | Check run status and per-node results |
| `closecode_list_workflows` | List all workflows for a project |
| `closecode_get_workflow` | Get full workflow definition |
| `closecode_delete_workflow` | Delete a workflow |
| `closecode_cancel_workflow_run` | Cancel an in-flight run |
| `closecode_get_workflow_runs` | Paginated run history |

## 3. Node Kind Catalog

All built-in nodes use the kind format `builtin.<category>.<name>`.

### Triggers (category: trigger)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.trigger.manual` | Manual Trigger | — | `fire` (trigger) |
| `builtin.trigger.cron` | Cron Trigger | — | `fire` (trigger) |
| `builtin.trigger.webhook` | Webhook Trigger | — | `fire` (trigger), `body` (json), `headers` (json), `method` (string) |
| `builtin.trigger.event` | Event Trigger | `eventPattern` (string) | `fire` (trigger), `payload` (json) |
| `builtin.trigger.schedule` | Schedule Trigger | — | `fire` (trigger), `scheduleId` (string), `scheduleName` (string), `projectId` (string), `triggeredAt` (string) |
| `builtin.trigger.dialog-message` | Dialog Message Trigger | — | `fire` (trigger), + dialog/message fields |
| `builtin.trigger.task-completed` | Task Completed Trigger | — | `fire` (trigger), `taskName` (string), `dialogId` (string), `status` (string), `result` (task-result) |
| `builtin.trigger.task-failed` | Task Failed Trigger | — | `fire` (trigger), + task error fields |
| `builtin.trigger.calendar-upcoming` | Calendar Upcoming Trigger | — | `fire` (trigger), + event fields |
| `builtin.trigger.file-changed` | File Changed Trigger | — | `fire` (trigger), + file fields |

### Agent (category: agent)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.agent.invoke` | Invoke Agent | `fire` (trigger), `prompt` (string, required) | `message` (message), `text` (string), `done` (trigger) |
| `builtin.task.run` | Run Task | `fire` (trigger) | `result` (task-result), `message` (string), `done` (trigger) |

### Control (category: control)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.control.condition` | Condition | `in` (any, required), `test` (boolean) | `true` (any), `false` (any) |
| `builtin.control.switch` | Switch | `in` (any, required) | `case1..case4` (any), `default` (any) |
| `builtin.control.merge` | Merge | `in1..in3` (any) | `out` (any), `done` (trigger) |
| `builtin.control.wait` | Wait | `fire` (trigger), `in` (any) | `done` (trigger), `out` (any) |
| `builtin.control.sub-workflow` | Sub-workflow | `start` (trigger, required) | `done` (trigger) + dynamic from pipeline |
| `builtin.control.sub-workflow-fire-and-forget` | Sub-workflow (fire & forget) | `start` (trigger, required) | `done` (trigger) |

### Data (category: data)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.data.set` | Set Value | `fire` (trigger) | `value` (json), `done` (trigger) |
| `builtin.data.transform` | Transform | `in` (any, required) | `out` (any), `done` (trigger) |
| `builtin.data.json-parse` | JSON Parse | `in` (string, required) | `out` (json), `done` (trigger) |
| `builtin.data.json-stringify` | JSON Stringify | `in` (json, required) | `out` (string), `done` (trigger) |
| `builtin.data.template` | Template | `data` (json, required) | `out` (string), `done` (trigger) |
| `builtin.data.http-request` | HTTP Request | `fire` (trigger) | `body` (json), `status` (number), `done` (trigger) |
| `builtin.data.project-search` | Project Search | `fire` (trigger) | `results` (json), `count` (number), `done` (trigger) |
| `builtin.data.project-analyze` | Project Analyze | `fire` (trigger) | `analysis` (json), `done` (trigger) |

### I/O (category: io)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.io.read-file` | Read File | `fire` (trigger) | `content` (string), `done` (trigger) |
| `builtin.io.write-file` | Write File | `fire` (trigger), `content` (string, required) | `done` (trigger) |
| `builtin.io.cli-execute` | CLI Execute | `fire` (trigger) | `stdout` (string), `exitCode` (number), `done` (trigger) |
| `builtin.io.service-call` | Service Call | `body` (json) | `response` (json), `ok` (boolean), `done` (trigger) |

### Interaction (category: io / interaction)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.interaction.human-input` | Human Input | `trigger` (trigger, required), `message` (string) | `response` (string), `selectedAction` (string), `done` (trigger) |

### Notify (category: notify)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.notify.log` | Log Notify | `fire` (trigger), `text` (string) | `done` (trigger) |

### Chat (category: chat)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.chat.post` | Post Chat Message | `fire` (trigger), `text` (string, required), `attachments` (json) | `message` (json), `id` (string), `channelId` (string), `done` (trigger) |
| `builtin.chat.push` | Send Push Notification | `title` (string, required), `body` (string, required), `data` (json) | `sent` (boolean), `done` (trigger) |

### Git (category: git)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.git.checkout` | Git Checkout | `fire` (trigger) | `done` (trigger) |
| `builtin.git.stage` | Git Stage | `fire` (trigger) | `done` (trigger) |
| `builtin.git.commit` | Git Commit | `fire` (trigger) | `done` (trigger) |
| `builtin.git.push` | Git Push | `fire` (trigger) | `done` (trigger) |
| `builtin.git.create-branch` | Create Branch | `fire` (trigger) | `done` (trigger) |

### Docs (category: docs)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.docs.create` | Create Document | `fire` (trigger) | `doc` (json), `id` (string), `done` (trigger) |
| `builtin.docs.update` | Update Document | `fire` (trigger) | `doc` (json), `done` (trigger) |
| `builtin.docs.todo-create` | Create Todo | `fire` (trigger) | `todo` (json), `id` (string), `done` (trigger) |

### Ops (category: ops)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.ops.container-exec` | Container Exec | `fire` (trigger) | `stdout` (string), `done` (trigger) |
| `builtin.ops.container-restart` | Container Restart | `fire` (trigger) | `done` (trigger) |
| `builtin.ops.env-health-check` | Env Health Check | `fire` (trigger) | `status` (string), `healthy` (boolean), `checks` (json), `done` (trigger) |

### Calendar (category: io / calendar)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.calendar.query-events` | Query Calendar Events | `fire` (trigger) | `events` (json), `count` (number), `done` (trigger) |

### Pipeline (category: pipeline)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.pipeline.input` | Pipeline Input | — | Dynamic (from pipeline interface) |
| `builtin.pipeline.output` | Pipeline Output | Dynamic (from pipeline interface) | — |

### Entity (category: entity)

| Kind | Label | Inputs | Outputs |
|------|-------|--------|---------|
| `builtin.entity.user` | User | — | `ref` (entity-ref) |
| `builtin.entity.role` | Role | — | `ref` (entity-ref) |

## 4. Socket Types & Compatibility

### Socket Types

| Type | Description | Shape |
|------|-------------|-------|
| `trigger` | Signal-only, no payload. Fires when upstream completes | Diamond |
| `any` | Untyped passthrough, connects to anything | Circle |
| `string` | Plain text | Circle |
| `number` | Numeric (int or float) | Circle |
| `json` | Structured data (object, array, primitive) | Circle |
| `message` | LLM/dialog message | Hexagon |
| `task-result` | Task run output | Hexagon |
| `binary` | Raw file/blob content | Circle |
| `boolean` | True/false | Square |
| `file-path` | Path relative to project root | Square |
| `entity-ref` | Reference to a project entity (user, role) | Diamond |

### Compatibility Rules

`isCompatible(from, to)` determines if output type `from` can connect to input type `to`:

1. **Same type** → always allowed
2. **`any` on either side** → allowed
3. **Scalar widening to `json`** → `string`, `number`, `boolean`, `entity-ref` all widen to `json`
4. **Everything else** → rejected (use a Transform node for explicit conversion)

```
// Quick reference:
string    → json ✓    json → string    ✗ (use transform)
number    → json ✓    json → number    ✗ (use transform)
boolean   → json ✓    json → boolean   ✗ (use transform)
entity-ref → json ✓
trigger   → trigger ✓ (flow control only)
any       → anything ✓
anything  → any ✓
```

## 5. Workflow Creation Pattern

### Step-by-step

1. **Discover available nodes:**
   ```
   closecode_list_workflow_node_types()
   ```
   Returns all kinds with their input/output socket definitions.

2. **Plan the flow:** Start with a trigger → add processing nodes → add output nodes.

3. **Find compatible nodes** for a specific socket:
   ```
   closecode_suggest_compatible_nodes(
     sourceNodeKind: "builtin.trigger.manual",
     sourceHandleId: "fire",
     direction: "downstream"
   )
   ```

4. **Create the workflow** with nodes and edges:
   ```json
   {
     "title": "My Workflow",
     "nodes": [
       { "id": "t1", "kind": "builtin.trigger.manual", "position": { "x": 0, "y": 0 }, "config": {} },
       { "id": "n1", "kind": "builtin.io.read-file", "position": { "x": 300, "y": 0 }, "config": { "path": "input.txt" } },
       { "id": "n2", "kind": "builtin.notify.log", "position": { "x": 600, "y": 0 }, "config": {} }
     ],
     "edges": [
       { "id": "e1", "source": "t1", "sourceHandle": "fire", "target": "n1", "targetHandle": "fire" },
       { "id": "e2", "source": "n1", "sourceHandle": "content", "target": "n2", "targetHandle": "text" },
       { "id": "e3", "source": "n1", "sourceHandle": "done", "target": "n2", "targetHandle": "fire" }
     ]
   }
   ```

5. **Validate:**
   ```
   closecode_validate_workflow(workflowId: "my-workflow")
   ```

6. **Run:**
   ```
   closecode_run_workflow(workflowId: "my-workflow")
   ```

7. **Check results:**
   ```
   closecode_get_workflow_run(runId: "...")
   ```

### Edge Format

Each edge connects one output to one input:
```json
{
  "id": "unique-edge-id",
  "source": "source-node-id",
  "sourceHandle": "output-socket-id",
  "target": "target-node-id",
  "targetHandle": "input-socket-id"
}
```

## 6. Common Patterns

### Approval Workflow (Human-in-the-Loop)

```json
{
  "title": "Approval Workflow",
  "nodes": [
    { "id": "trigger", "kind": "builtin.trigger.webhook", "position": { "x": 0, "y": 0 }, "config": {} },
    { "id": "ask", "kind": "builtin.interaction.human-input", "position": { "x": 300, "y": 0 }, "config": {
      "message": "Approve this request?",
      "nextActions": [
        { "label": "Approve", "value": "approved" },
        { "label": "Reject", "value": "rejected" }
      ]
    }},
    { "id": "branch", "kind": "builtin.control.condition", "position": { "x": 600, "y": 0 }, "config": {
      "expression": "inputs.selectedAction === 'approved'"
    }},
    { "id": "approved", "kind": "builtin.notify.log", "position": { "x": 900, "y": -100 }, "config": {} },
    { "id": "rejected", "kind": "builtin.notify.log", "position": { "x": 900, "y": 100 }, "config": {} }
  ],
  "edges": [
    { "id": "e1", "source": "trigger", "sourceHandle": "fire", "target": "ask", "targetHandle": "trigger" },
    { "id": "e2", "source": "ask", "sourceHandle": "done", "target": "branch", "targetHandle": "in" },
    { "id": "e3", "source": "ask", "sourceHandle": "selectedAction", "target": "branch", "targetHandle": "test" },
    { "id": "e4", "source": "branch", "sourceHandle": "true", "target": "approved", "targetHandle": "fire" },
    { "id": "e5", "source": "branch", "sourceHandle": "false", "target": "rejected", "targetHandle": "fire" }
  ]
}
```

### Agent Pipeline

Trigger → Agent A → Agent B → Output:
```json
{
  "title": "Agent Pipeline",
  "nodes": [
    { "id": "t", "kind": "builtin.trigger.manual", "position": { "x": 0, "y": 0 }, "config": {} },
    { "id": "a1", "kind": "builtin.agent.invoke", "position": { "x": 300, "y": 0 }, "config": { "agent": "planner", "prompt": "Analyze: {{inputs.prompt}}" } },
    { "id": "a2", "kind": "builtin.agent.invoke", "position": { "x": 600, "y": 0 }, "config": { "agent": "coder", "prompt": "Implement based on: " } },
    { "id": "log", "kind": "builtin.notify.log", "position": { "x": 900, "y": 0 }, "config": {} }
  ],
  "edges": [
    { "id": "e1", "source": "t", "sourceHandle": "fire", "target": "a1", "targetHandle": "fire" },
    { "id": "e2", "source": "a1", "sourceHandle": "done", "target": "a2", "targetHandle": "fire" },
    { "id": "e3", "source": "a1", "sourceHandle": "text", "target": "a2", "targetHandle": "prompt" },
    { "id": "e4", "source": "a2", "sourceHandle": "done", "target": "log", "targetHandle": "fire" },
    { "id": "e5", "source": "a2", "sourceHandle": "text", "target": "log", "targetHandle": "text" }
  ]
}
```

### Sub-workflow Delegation

Use `builtin.control.sub-workflow` to call another workflow. The target workflow should have `pipeline-input` and `pipeline-output` nodes to define its contract.

### Entity-based Routing

Connect `entity.user` or `entity.role` outputs to nodes that accept `entity-ref` or `json` inputs to route messages or tasks to specific people/roles.

## 7. Tips & Best Practices

- **Always include a trigger node** — A workflow without a trigger cannot run
- **Separate data and trigger edges** — Most nodes need both a trigger edge (for execution order) and data edges (for values)
- **Use `human-input` for human-in-the-loop** — Pauses execution until a human responds
- **Use sub-workflow for reusable flows** — Encapsulate common patterns; pipeline interfaces define contracts
- **Use `validate` before `run`** — Catches socket mismatches, missing required inputs, and cycles
- **Position nodes for readability** — Space nodes ~300px apart horizontally
- **Use descriptive node labels** — Set `label` on nodes for clarity in the editor

## 8. Error Prevention

### Socket Mismatches
Use `closecode_suggest_compatible_nodes` before creating edges. Common mistake: connecting a `json` output to a `string` input (rejected — use `json-stringify` first).

### Missing Required Inputs
Required input sockets (`required: true`) must be connected. Validation catches this.

### Cycle Detection
Workflows must be a DAG (directed acyclic graph). Validation detects and reports cycles.

### Node Config
Each node has a `config` object specific to its kind. Check `closecode_list_workflow_node_types` for `configSchema`. Missing required config fields cause runtime errors.

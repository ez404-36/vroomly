---
name: closecode
description: CloseCode ADE management tools - projects, services, agents, tasks, skills, layouts, panels, documents, schedules, and git via embedded MCP server
closecode_version: 1.1.0
scope: any
provisionedAt: "2026-04-30T16:58:06.652Z"
provisionedFrom: templates/skills/closecode/SKILL.md
---

# Closecode Skill

This skill provides MCP tools for managing CloseCode ADE internals: projects, services, agents, tasks, skills, layouts, panels, documents (ideas, plans, reviews, issues), schedules, and git operations.

## Activation

The closecode MCP server is a deferred embedded server. Activate tools:

```
skill({ tools: ["closecode"] })
```

All tools are prefixed with `closecode_` to avoid naming conflicts.

## 1. Project Management

| Tool | Description |
|------|-------------|
| `closecode_list_projects` | List all projects (optionally filter by status) |
| `closecode_get_project` | Get project details |
| `closecode_create_project` | Create a new project (name + path) |
| `closecode_update_project` | Update project settings (status, description) |
| `closecode_delete_project` | Delete a project |

## 2. Service Management

| Tool | Description |
|------|-------------|
| `closecode_list_services` | List all registered services |
| `closecode_get_service` | Get service details |
| `closecode_create_service` | Register a new service (name, domain, port) |
| `closecode_delete_service` | Delete a service |

## 3. Agent Management

| Tool | Description |
|------|-------------|
| `closecode_list_agents` | List agents (global or project-scoped) |
| `closecode_get_agent` | Get agent definition |
| `closecode_create_agent` | Create agent (scope, name, systemPrompt, tools) |
| `closecode_update_agent` | Update agent configuration |
| `closecode_delete_agent` | Delete an agent |
| `closecode_provision_agents` | Provision all template agents for a project |

## 4. Task Management

| Tool | Description |
|------|-------------|
| `closecode_list_tasks` | List tasks (filter by project, status) |
| `closecode_get_task` | Get task definition details |
| `closecode_create_task` | Create task (name, type, command, schedule) |
| `closecode_update_task` | Update task definition |
| `closecode_delete_task` | Delete a task |
| `closecode_run_task` | Trigger immediate task execution |
| `closecode_cancel_task` | Cancel a running task |
| `closecode_get_task_runs` | Get run history for a task |

## 5. Skill Management

| Tool | Description |
|------|-------------|
| `closecode_list_deployed_skills` | List deployed skills for a project |
| `closecode_get_deployed_skill` | Get skill content |
| `closecode_update_skill` | Update skill SKILL.md content |
| `closecode_provision_skills` | Provision all skill templates |
| `closecode_provision_skill` | Provision a single skill template |
| `closecode_list_skill_templates` | List available skill templates |

## 6. Layout Management

| Tool | Description |
|------|-------------|
| `closecode_list_layouts` | List layouts for a project |
| `closecode_get_layout` | Get layout details (full panel tree) |
| `closecode_create_layout` | Create layout (name + panels JSON) |
| `closecode_update_layout` | Update layout name and/or panels |
| `closecode_delete_layout` | Delete a layout |
| `closecode_list_global_layouts` | List global (non-project) layouts |

## 7. Panel Reference

| Tool | Description |
|------|-------------|
| `closecode_list_panel_types` | Full catalog of 76 panel types with categories |

### Panel Type Categories

- **Dashboard**: ProjectsGrid, ServicesGrid, QuickSetup, CalendarPlanner
- **Development**: FileTree, TabGroup, Terminal, CodeView, MarkdownView, etc.
- **AI**: Conversation, ActiveDialogs, Chat, AgentsList, TaskDefinitions, etc.
- **Git**: GitHistory, GitCommitDetails, GitBranches, GitCommit, Changes
- **Analysis**: AnalysisOverview, NPMScripts, Dependencies, DocumentList
- **Tracking**: TodoList, QuestionList, NoteList, etc.
- **Configuration**: ConnectionConfig, ProvidersConfig, SettingsMegaPanel, etc.
- **Layout**: PagePanel (container), Empty (placeholder)

### Key Panel Properties

```
flexBasis   "300px" (fixed) or "0" (fills remaining space)
minWidth    Minimum width in pixels (default: 200)
intentFilter TabGroup only: filter allowed intents/file categories
panelConfig Per-panel configuration bag
pagePanelMode PagePanel only: "page", "stack", or "scroll"
children    PagePanel only: nested panel array
tabs        TabGroup only: pre-populated tabs
```

### Invariants

- At least one visible panel must have `flexBasis: "0"` to absorb remaining space
- FileTree defaults to `flexBasis: "300px"` (fixed sidebar)
- Cannot remove the last panel in a layout
- Panel IDs: `panel-<timestamp>-<random5>`

## 8. Panel Manipulation

Granular panel operations. Each tool reads the current layout, modifies the panel tree, and saves back.

| Tool | Description |
|------|-------------|
| `closecode_add_panel` | Add panel at position (end/start/after/before) |
| `closecode_remove_panel` | Remove panel (top-level or nested child) |
| `closecode_update_panel` | Update panel properties (type, size, config) |
| `closecode_move_panel` | Move panel to different position or parent |
| `closecode_duplicate_panel` | Deep-clone panel with new IDs |
| `closecode_get_layout_tree` | Visual ASCII tree + structured JSON of layout |
| `closecode_add_panel_to_tabgroup` | Add pre-populated tab to a TabGroup |

### Position Syntax

The `position` / `targetPosition` parameter supports:

- `"end"` (default) or `"start"`
- Numeric index: `"0"`, `"2"`
- Relative: `"after:<panelId>"`, `"before:<panelId>"`

### Common Workflows

**Add a sidebar to existing layout:**
```
closecode_add_panel(projectName, layoutId, panelType="FileTree", position="start")
```

**Add terminal next to an editor:**
```
closecode_add_panel(projectName, layoutId, panelType="Terminal", position="after:<editorPanelId>")
```

**Inspect layout before modifying:**
```
closecode_get_layout_tree(projectName, layoutId)
```

**Resize a panel:**
```
closecode_update_panel(projectName, layoutId, panelId, flexBasis="400px")
```

**Move sidebar to the right:**
```
closecode_move_panel(projectName, layoutId, panelId, targetPosition="end")
```

## 9. Layout Templates

Predefined layout templates for common use cases. Use `closecode_list_layout_templates` to see all options.

| Tool | Description |
|------|-------------|
| `closecode_list_layout_templates` | List all predefined templates with descriptions |
| `closecode_apply_layout_template` | Create a layout from a template (with optional customizations) |

### Available Templates

| Template | Panels | Use Case |
|----------|--------|----------|
| `coding-default` | FileTree + TabGroup + Terminal | General development |
| `code-review` | FileTree + TabGroup + Changes + GitHistory | Reviewing code changes |
| `ai-development` | FileTree + TabGroup + Terminal + Conversation | AI-assisted coding |
| `project-management` | ProjectsGrid + ServicesGrid + ActiveDialogs + TaskMonitor | Project monitoring |
| `documentation` | FileTree + DocumentList + DocumentEditor + MarkdownView | Writing docs |
| `git-workflow` | GitHistory + GitBranches + Changes + TabGroup | Git operations |
| `task-monitoring` | TaskDefinitions + TaskMonitor + TaskRunHistory + SchedulesList | Background tasks |
| `agent-workshop` | AgentsList + AgentEditor + SkillsList + Conversation | Agent development |
| `analysis` | AnalysisOverview + NPMScripts + Dependencies + DocumentationView | Project analysis |
| `minimal-coding` | TabGroup | Distraction-free editing |
| `messenger` | Channels + Chat + Conversation | Team communication |
| `settings` | SettingsMegaPanel | All configuration |

### Customizing Templates

The `customizations` parameter accepts a JSON string:

```json
{
  "addPanels": [{ "type": "Terminal", "position": "end" }],
  "removePanelTypes": ["Terminal"],
  "overrides": { "FileTree": { "flexBasis": "400px" } }
}
```

- `addPanels` — Add extra panels at "start" or "end"
- `removePanelTypes` — Remove panels by type name
- `overrides` — Override flexBasis/minWidth for panels by type

## 10. Document Management

Manage CloseCode ADE documents (ideas, plans, reviews, issues) via MCP tools. These replace the `closecode documents` CLI commands.

| Tool | Description |
|------|-------------|
| `closecode_list_documents` | List documents of a type (filter by status) |
| `closecode_get_document` | Get a document by slug with full body content |
| `closecode_create_document` | Create a new document (idea, plan, review, or issue) |
| `closecode_update_document` | Update document metadata, body, or cross-reference links |
| `closecode_search_documents` | Search documents by title, tags, or excerpt content |

All document tools accept `type` (idea, plan, review, issue) and `projectName` (auto-detected).

### Type-Specific Fields

Plans, reviews, and issues support additional fields beyond the common set:

| Field | Plans | Reviews | Issues |
|-------|-------|---------|--------|
| `sourceDialogId` | yes | yes | yes |
| `sourceMessageId` | yes | yes | yes |
| `linkedIdeaIds` | yes | yes | yes |
| `linkedPlanIds` | - | yes | yes |
| `linkedReviewIds` | yes | - | yes |

## 11. Document Format & File Conventions

Documents are markdown files with YAML frontmatter. The MCP tools handle UUID generation, slug creation, and timestamps automatically.

### Common fields (all types)

```yaml
---
id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890" # UUID v4, auto-generated
title: "Document Title"                       # Required
tags:                                         # String array
  - feature
  - backend
status: draft          # draft | active | done | archived
priority: medium       # low | medium | high
linkedDialogIds:       # String array, dialog references
  - "dialog-uuid-here"
createdAt: "2026-02-28T12:00:00.000Z"  # ISO 8601, auto-generated
updatedAt: "2026-02-28T14:30:00.000Z"  # ISO 8601, auto-updated
---
```

### File locations

| Type    | Default Path    | Config Override |
| ------- | --------------- | --------------- |
| Ideas   | `docs/ideas/`   | `ideasPath`     |
| Plans   | `docs/plans/`   | `plansPath`     |
| Reviews | `docs/reviews/` | `reviewsPath`   |
| Issues  | `docs/issues/`  | `issuesPath`    |

### Slug naming

Slugs are kebab-case, derived from the title: "My Feature Idea" -> `my-feature-idea.md`

### Subfolder organization

Documents can be organized in subdirectories: `docs/plans/backend/api-redesign.md`. Use the `folder` parameter when creating/getting documents in subfolders.

## 12. Document Workflows

### Status lifecycle

```
draft -> active -> done
                -> archived
```

- **draft**: Initial state. Concept captured but not yet acted on.
- **active**: Work has begun or the document is current/relevant.
- **done**: Completed. Implementation finished or research concluded.
- **archived**: Abandoned or superseded. Kept for reference.

### When to create each type

- **Ideas**: Feature concepts, brainstorming, high-level thinking.
- **Plans**: Implementation plans from conversations or design work.
- **Reviews**: Research reviews and analysis after investigating a technology or approach.
- **Issues**: Bugs, problems, and defects that need fixing.

### Priority assignment

- **high**: Blocking other work, urgent, or time-sensitive.
- **medium**: Normal priority, part of current development cycle.
- **low**: Nice-to-have, future consideration, non-blocking.

### Cross-referencing

Link related documents using `closecode_update_document` with link fields:

- Plans can link to ideas (`linkedIdeaIds`) and reviews (`linkedReviewIds`)
- Reviews can link to ideas (`linkedIdeaIds`) and plans (`linkedPlanIds`)
- Issues can link to ideas, plans, and reviews

### MCP tools vs direct file editing

Use **MCP tools** for:

- Creating documents (handles UUID, slug, timestamps, deduplication)
- Updating metadata (status, priority, tags, links)
- Searching and listing documents

Use **direct file editing** for:

- Writing or revising long-form body content
- Bulk changes across multiple documents
- Complex content that exceeds tool convenience

## 13. Schedule Management

Manage cron-based schedules that trigger tasks on a recurring basis.

| Tool | Description |
|------|-------------|
| `closecode_list_schedules` | List schedules for a project (filter by status) |
| `closecode_get_schedule` | Get full schedule details |
| `closecode_create_schedule` | Create a new schedule (name, cron, target task, options) |
| `closecode_update_schedule` | Update schedule title, cron, target, or options |
| `closecode_delete_schedule` | Delete a schedule |
| `closecode_pause_schedule` | Pause a schedule (stops triggering) |
| `closecode_resume_schedule` | Resume a paused schedule |
| `closecode_trigger_schedule` | Trigger a schedule immediately (outside cron cycle) |

### Schedule Configuration

Schedules target tasks via `target: { type: "task", taskId: "<id>" }`. Options control behavior:

- `skipIfRunning` (default: true) — skip trigger if the task is already running
- `catchUp` (default: false) — catch up missed triggers when resuming
- `maxConsecutiveFailures` (default: 3) — auto-pause after N consecutive failures

### Cron Examples

```
0 */6 * * *    Every 6 hours
0 0 * * *      Daily at midnight
0 9 * * 1-5    Weekdays at 9 AM
*/30 * * * *   Every 30 minutes
```

## 14. Git Operations

Read-only git information for a project's repository.

| Tool | Description |
|------|-------------|
| `closecode_git_status` | Get working copy status (modified, added, deleted, untracked, staged) |
| `closecode_git_commits` | Get commit history (paginated with limit/offset) |
| `closecode_git_branches` | Get branches with current branch info |

These tools query the backend analysis module. For git write operations (commit, push, etc.), use the `bash` tool directly.

## 15. Architecture Notes

- The closecode MCP server runs as an **embedded in-process server** in the ACP runtime sidecar
- Tools communicate with the CloseCode ADE backend via REST APIs using `server.json` credentials
- Panel manipulation uses **GET layout -> modify panel tree -> PUT layout** pattern
- The backend has no granular panel endpoints; all tree manipulation happens in the MCP tool layer
- The `ensureFlexPanel` invariant is enforced after every panel add/remove/move operation
- Document search is client-side (fetch all + filter) — matches CLI behavior

&nbsp;

---
name: implementation-guidelines
description: Task creation, task structure, implementation plans, and parallel vs sequential execution patterns
closecode_version: 1.0.0
scope: any
provisionedAt: "2026-04-30T16:58:06.659Z"
provisionedFrom: templates/skills/implementation-guidelines/SKILL.md
---

# Implementation Guidelines Skill

This skill teaches agents how to create implementation tasks, structure them, and decide between parallel vs sequential execution.

## 1. Task Creation

### Key Principles

1. **Self-Contained Tasks** - Each task completable independently
2. **No Timelines** - Don't include duration estimates
3. **Clear Success Criteria** - Measurable outcomes
4. **Comprehensive Context** - Goal, decisions, dependencies, files
5. **Explicit Dependencies** - What depends on what

### Task Template

```
Task: [Clear, specific action]

Context:
  - Overall Goal: [...]
  - Architectural Decisions: [...]
  - Related Work: [...]

Objective:
  - [Specific, measurable outcome]

Deliverables:
  - [Code changes - which files]
  - [Tests - verification steps]

File References:
  - [Specific file paths]

Success Criteria:
  - [How to verify task complete]

Notes:
  - [Additional context]
```

## 2. Implementation Plan Documents

**CRITICAL: When planning multi-phase implementations during a session, always create a Plan document.**

### When to Create a Plan

- Feature implementation requiring 3+ phases or tasks
- Architectural changes spanning multiple modules
- Refactoring efforts with coordinated backend + frontend changes
- Any work where decisions, phases, and file changes should be tracked

### How to Create

1. Use your project's document management system to create a plan document
2. Write the full plan body (preserving any generated frontmatter/metadata)
3. Include: overview, key decisions, phases, implementation order, file change summary

### Maintaining the Plan

- Update as implementation progresses (mark completed phases, note deviations)
- If scope changes significantly, update before continuing
- Mark as complete when done

### Why This Matters

- Plans survive session boundaries — future agents can pick up where you left off
- Plans document architectural decisions and rationale
- Plans prevent duplicate work and conflicting approaches
- Searchable for future reference

## 3. Parallel vs Sequential Execution

### Run Tasks in Parallel When

- Tasks modify different files
- Tasks have no dependencies
- No collision risks

### Run Tasks Sequentially When

- Tasks modify same files
- Tasks depend on each other
- Share resources

### Collision Detection Checklist

- [ ] No duplicate file paths
- [ ] No overlapping module boundaries
- [ ] No shared configuration files
- [ ] No dependency chains

## 4. Orchestrator Agent Behavior

**When acting as an orchestrator (coordinating subtasks):**

- **ALWAYS confirm with user** when subtasks provide suggestions, recommendations, or proposed approaches before proceeding with implementation
- **ALWAYS forward** subtask questions and options to the user
- **EXCEPTION:** Only proceed automatically if user explicitly requested it (e.g., "proceed automatically", "implement without asking")
- Default is ALWAYS to confirm - never assume implicit approval

**Orchestrators CAN decide autonomously:**

- Task ordering
- Parallel vs sequential execution
- Which agent to use
- Context to provide

## 5. Agent Types

### @general - Implementation Agent

- Use for code implementation, refactoring, bug fixes, and feature development
- Executes multi-step coding tasks autonomously
- Can modify files, run tests, and verify implementations
- Ideal for independent implementation work
- Also use it whenever playwright or ht-mcp testing is involved

### @explore - Discovery Agent

- Use for codebase exploration, API discovery, and investigation
- Fast at finding files, patterns, and answering questions about code structure
- Can test APIs and verify documentation
- Use when you need to understand the codebase or external systems

&nbsp;

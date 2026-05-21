---
name: documentation-management
description: Documentation analysis, changelog generation, cross-reference validation, and freshness tracking using git and file system tools
provisionedAt: "2026-05-07T19:36:42.113Z"
provisionedFrom: templates/skills/documentation-management/SKILL.md
---

# Documentation Management Skill

This skill provides workflows and patterns for managing project documentation as a background agent task. It covers changelog generation from git history, documentation freshness analysis, and cross-reference validation.

## 1. Changelog Generation

### Analyze git commits for changelog

Use bash to extract and analyze git log data:

```bash
# Get commits since a specific date, formatted for parsing
git log --since="{{since}}" --pretty=format:"%H|%s|%an|%ai" --no-merges

# Get commits with file changes for categorization
git log --since="{{since}}" --pretty=format:"%H|%s" --name-only --no-merges

# Get commits grouped by conventional commit prefix
git log --since="{{since}}" --pretty=format:"%s" --no-merges | grep -oP "^(feat|fix|refactor|docs|test|chore|perf|ci|build|style)(\(.+?\))?:" | sort | uniq -c | sort -rn
```

### Categorization heuristics

When commits don't follow conventional commit format, infer categories from file paths:


| File Pattern                             | Category                      |
| ---------------------------------------- | ----------------------------- |
| `src/**/*.ts`, `src/**/*.tsx`            | Feature or Fix (inspect diff) |
| `test/**/*`, `*.spec.*`, `*.test.*`      | Tests                         |
| `docs/**/*`, `*.md`, `CHANGELOG*`        | Documentation                 |
| `package.json`, `tsconfig*`, `.*rc*`     | Configuration                 |
| `Dockerfile*`, `.github/**/*`, `ci/**/*` | CI/Build                      |
| `*.css`, `*.scss`, `*.less`              | Styling                       |


### Write changelog

Write the generated changelog to the project's changelog file. Prefer appending to existing changelogs rather than replacing them:

```bash
# Check for existing changelog
ls CHANGELOG.md changelog.md docs/CHANGELOG.md 2>/dev/null
```

## 2. Documentation Freshness Analysis

### Compare documentation age against related code

```bash
# Find all markdown files with their last modification date
find docs/ -name "*.md" -exec stat -c "%Y %n" {} \; 2>/dev/null | sort -rn

# Find source files modified more recently than a specific doc file
find src/ -newer docs/some-doc.md -name "*.ts" -o -name "*.tsx" 2>/dev/null
```

### Detect stale documentation

A document is considered stale when related source code has been modified but the documentation has not been updated. Use these heuristics:

1. **Direct references** — If a doc references specific files/functions, check if those have changed
2. **Directory proximity** — If a doc is in `docs/api/`, check `src/api/` for recent changes
3. **Import/link analysis** — Parse markdown links and code references

```bash
# Extract file references from a markdown document
grep -oP '`[a-zA-Z0-9_/.-]+\.(ts|tsx|js|jsx)`' docs/some-doc.md

# Check if referenced files have been modified recently
git log --since="30 days ago" --name-only --pretty=format: -- src/api/some-file.ts
```

## 3. Cross-Reference Validation

### Validate internal links

```bash
# Find all markdown internal links
grep -rnoP '\[.*?\]\(((?!https?://)[^)]+)\)' docs/

# Find all markdown file references
grep -rnoP '`((?:src|docs|web|test)/[a-zA-Z0-9_/.-]+)`' docs/
```

### Check for broken references

For each extracted link or file reference:

1. Resolve relative paths from the document's directory
2. Check if the target file exists using glob/read tools
3. For anchor links (`#section`), verify the heading exists in the target document

## 4. Documentation Structure Analysis

### Inventory documentation

```bash
# Count documents by directory
find docs/ -name "*.md" | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn

# Find orphaned docs (no inbound links from other docs)
# Step 1: Get all doc filenames
find docs/ -name "*.md" -exec basename {} .md \;

# Step 2: For each, check if it's referenced elsewhere
grep -rl "filename" docs/ --include="*.md"
```

### Identify documentation gaps

Look for source directories without corresponding documentation:

```bash
# Source directories
find src/ -type d | head -20

# Documentation directories
find docs/ -type d | head -20
```

## 5. Output Format

When producing reports, write them as markdown files in the project's documentation directory:

- **Changelog** — `CHANGELOG.md` or `docs/CHANGELOG.md` (append, don't replace)
- **Freshness report** — `docs/reports/documentation-freshness-YYYY-MM-DD.md`
- **Validation report** — `docs/reports/cross-reference-validation-YYYY-MM-DD.md`

Always include a summary section at the top of reports with key metrics and actionable items.

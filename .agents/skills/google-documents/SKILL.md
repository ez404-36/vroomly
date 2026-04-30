---
name: google-documents
description: Work with Google Docs, Sheets, and Drive via the mcp-google-workspace MCP server
closecode_version: 1.0.0
scope: any
provisionedAt: "2026-04-30T16:58:06.657Z"
provisionedFrom: templates/skills/google-documents/SKILL.md
---

# Google Documents Skill

This skill teaches agents how to work with Google Docs, Google Sheets, and Google Drive using the mcp-google-workspace MCP server.

## MCP Server

The `mcp-google-workspace` server provides tools for reading, creating, and editing Google Docs and Sheets via the Google API.

**Note:** Requires Google OAuth authentication. The MCP server must be configured with valid Google API credentials.

---

## 1. Google Docs Tools

### Reading Documents

```bash
# Read full document content
mcp-google-workspace:google_docs_read(documentId: string, format?: "text" | "markdown" | "json")
# format: markdown (default), text, or json
# Returns: Document content with paragraphs, headings, tables

# Get document structure
mcp-google-workspace:google_docs_structure(documentId: string)
# Returns: All elements with indices (paragraphs, headings, tables, lists)
# Use contentIndex for targeted editing

# Search in document
mcp-google-workspace:google_docs_search(documentId: string, query: string, caseSensitive?: boolean)
# Returns: Matching paragraphs with content indices
```

### Creating Documents

```bash
# Create a new Google Doc
mcp-google-workspace:google_docs_create(title: string)
# Returns: Document ID and webViewLink
```

### Editing Documents

```bash
# Append text to end of document
mcp-google-workspace:google_docs_append(documentId: string, text: string)

# Insert text at a position
mcp-google-workspace:google_docs_insert(documentId: string, text: string, index: number)
# index: content index (0-based) from google_docs_structure

# Edit a specific paragraph
mcp-google-workspace:google_docs_edit_paragraph(documentId: string, index: number, text: string)
# index: content index (0-based) from google_docs_structure

# Delete content in a range
mcp-google-workspace:google_docs_delete(documentId: string, startIndex: number, endIndex: number)
# Use google_docs_structure to get startIndex/endIndex values

# Find and replace text
mcp-google-workspace:google_docs_replace(documentId: string, find: string, replace: string, all?: boolean, caseSensitive?: boolean)
# all: replace all occurrences (default: true)
```

### Formatting

```bash
# Apply inline text formatting
mcp-google-workspace:google_docs_apply_text_style(documentId: string, startIndex: number, endIndex: number, bold?: boolean, italic?: boolean, underline?: boolean, fontSize?: number, color?: string, backgroundColor?: string)
# color: hex format like "#FF0000"
# Use indices from google_docs_structure

# Apply paragraph formatting
mcp-google-workspace:google_docs_apply_paragraph_style(documentId: string, startIndex: number, endIndex: number, alignment?: "START" | "CENTER" | "END" | "JUSTIFIED", lineSpacing?: number, indentFirstLine?: number, indentStart?: number, heading?: "HEADING_1" | "HEADING_2" | "HEADING_3" | "HEADING_4" | "HEADING_5" | "HEADING_6" | "NORMAL_TEXT")
```

### Table Operations

```bash
# Insert a table
mcp-google-workspace:google_docs_insert_table(documentId: string, rows: number, columns: number, index?: number)
# index: optional content index (0-based), defaults to end of document

# Read table content
mcp-google-workspace:google_docs_table_read(documentId: string, tableIndex: number, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)
# tableIndex: 0-based index of table in document
# All parameters are 1-indexed

# Write data to a table
mcp-google-workspace:google_docs_table_write(documentId: string, tableIndex: number, data: string[][], rowFrom?: number, colFrom?: number)
# data: 2D array of strings
```

### Export

```bash
# Export to other formats
mcp-google-workspace:google_docs_export(documentId: string, format: "pdf" | "docx" | "txt" | "html" | "rtf")
# Returns: Exported file content
```

---

## 2. Google Sheets Tools

### Reading Spreadsheets

```bash
# List all sheets
mcp-google-workspace:google_sheets_list_sheets(spreadsheetId: string)

# Get sheet info
mcp-google-workspace:google_sheets_info(spreadsheetId: string, sheet?: string)

# Read a range
mcp-google-workspace:google_sheets_read_range(spreadsheetId: string, sheet?: string, range?: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)
# range: A1 notation (e.g., "A1:Z100")
# rowFrom/rowTo/colFrom/colTo: 1-indexed numeric parameters
# Returns: Row-per-block format with column letters

# Read a single cell
mcp-google-workspace:google_sheets_read_cell(spreadsheetId: string, sheet: string, row: number, col: number)
# Returns: Full cell info including formula and display value

# Search in sheet
mcp-google-workspace:google_sheets_search(spreadsheetId: string, sheet?: string, query: string)

# List formulas
mcp-google-workspace:google_sheets_list_formulas(spreadsheetId: string, sheet?: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)

# Get sheet overview
mcp-google-workspace:google_sheets_overview(spreadsheetId: string, sheet?: string)
# Shows structure, header detection, formula locations
```

### Writing Spreadsheets

```bash
# Write a range
mcp-google-workspace:google_sheets_write_range(spreadsheetId: string, values: string, sheet?: string, range?: string, rowFrom?: number, colFrom?: number, rawInput?: boolean)
# values: JSON 2D array, e.g. [["Name","Age"],["Alice",30]]
# Strings starting with '=' become formulas
# rawInput: if true, strings written as-is (not type-converted)

# Write a single cell
mcp-google-workspace:google_sheets_write_cell(spreadsheetId: string, sheet: string, row: number, col: number, value: string)

# Append rows
mcp-google-workspace:google_sheets_append(spreadsheetId: string, range: string, values: string, sheet?: string)
# range: A1 notation for starting position (e.g., "A1")

# Clear a range
mcp-google-workspace:google_sheets_clear(spreadsheetId: string, range: string, sheet?: string)
```

### Sheet Management

```bash
# Insert rows
mcp-google-workspace:google_sheets_insert_rows(spreadsheetId: string, sheet: string, row: number, count: number)

# Insert columns
mcp-google-workspace:google_sheets_insert_columns(spreadsheetId: string, sheet: string, col: number, count: number)

# Add a sheet
mcp-google-workspace:google_sheets_add_sheet(spreadsheetId: string, name: string)

# Delete a sheet
mcp-google-workspace:google_sheets_delete_sheet(spreadsheetId: string, sheetId: number)
# Note: sheetId is numeric (get from google_sheets_list_sheets)

# Rename a sheet
mcp-google-workspace:google_sheets_rename_sheet(spreadsheetId: string, sheetId: number, newName: string)
```

### Search and Replace

```bash
# Search and replace
mcp-google-workspace:google_sheets_search_replace(spreadsheetId: string, search: string, replace: string, sheet?: string, range?: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number, caseSensitive?: boolean, all?: boolean, regex?: boolean)
```

---

## 3. Google Drive Tools

```bash
# List files
mcp-google-workspace:google_drive_list_files(folderId?: string, mimeType?: string, query?: string)

# Get file info
mcp-google-workspace:google_drive_get_file(fileId: string)

# Export file (for Google Docs/Sheets)
mcp-google-workspace:google_drive_export(fileId: string, format: string)
# format: pdf, docx, xlsx, csv, etc.

# Download file
mcp-google-workspace:google_drive_download(fileId: string)

# Upload file
mcp-google-workspace:google_drive_upload(filePath: string, folderId?: string, name?: string)

# Create folder
mcp-google-workspace:google_drive_create_folder(name: string, parentId?: string)

# Delete file
mcp-google-workspace:google_drive_delete(fileId: string)
```

---

## 4. Important Notes

### Document/Sheet ID

- Use the full Google URL or just the ID
- Example IDs: `https://docs.google.com/document/d/ABC123xyz...` → `ABC123xyz`
- Same format works for spreadsheets (`/spreadsheets/d/...`)

### Index System

- Content indices are 0-based (sequential)
- Spreadsheet rows/columns are 1-indexed (Excel convention)
- Use `google_docs_structure` to get indices for editing
- Use `google_sheets_list_sheets` to get sheetId numbers

### Rate Limits

- Google API has quota limits
- Responses include quota warnings when approaching limits
- Check responses for `⚠️` warnings

### Formula Support

- Strings starting with `=` are treated as formulas
- Use `google_sheets_list_formulas` to audit formulas before structural changes

### Content Indices

- `google_docs_structure` returns both `contentIndex` (sequential, 0-based) and `startIndex`/`endIndex` (segment positions)
- For editing: use `contentIndex` with tools like `google_docs_edit_paragraph`
- For deletion: use `startIndex` and `endIndex` with `google_docs_delete`

### Error Handling

- All tools return structured responses with error details
- Check for rate limit warnings in responses
- Sheet operations use sheetId (numeric), not sheet name

&nbsp;

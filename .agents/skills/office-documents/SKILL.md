---
name: office-documents
description: Work with local office documents (DOCX, XLSX, PDF, ODT, PPTX) using mcp-documents MCP server
closecode_version: 1.0.0
scope: any
provisionedAt: "2026-04-30T16:58:06.660Z"
provisionedFrom: templates/skills/office-documents/SKILL.md
---

# Office Documents Skill

This skill teaches agents how to work with local office documents (DOCX, XLSX, PDF, ODT, PPTX) using the mcp-documents MCP server.

## MCP Server

The `mcp-documents` server provides tools for reading, writing, and converting office documents.

---

## 1. Document Tools (DOCX, DOC, ODT, PPTX, PPT, ODP)

### Reading Documents

```bash
# Read text content from a document
mcp-documents:read_document(filePath: string)
# Returns: JSON with extracted text

# Get document structure (paragraphs, headings, tables)
mcp-documents:docx_structure(filePath: string)
# Returns: Array of content elements with indices

# Search for text in a document
mcp-documents:docx_search(filePath: string, query: string, regex?: boolean, caseSensitive?: boolean, words?: boolean)
# Returns: Matching paragraphs with indices
```

### Editing Documents

```bash
# Search and replace text
mcp-documents:docx_replace(filePath: string, search: string, replace: string, regex?: boolean, caseSensitive?: boolean, words?: boolean, dryRun?: boolean)
# dryRun defaults to true - set to false to apply changes
# Creates .bak backup before modification

# Edit a specific paragraph by index
mcp-documents:docx_edit_paragraph(filePath: string, index: number, text: string)
# Use docx_structure first to get paragraph indices

# Apply formatting to a paragraph
mcp-documents:docx_format_paragraph(filePath: string, index: number, format: string)
# format: JSON object with bold, italic, underline, fontSize, color, backgroundColor, fontName, align

# Apply formatting to a character range
mcp-documents:docx_format_range(filePath: string, index: number, charFrom: number, charTo: number, format: string)
```

### Table Operations

```bash
# List all tables in a document
mcp-documents:docx_list_tables(filePath: string)

# Read table content as 2D array
mcp-documents:docx_table_read(filePath: string, table: number | string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)

# Write data to a table
mcp-documents:docx_table_write(filePath: string, table: number | string, data: string, rowFrom?: number, colFrom?: number)
# data: JSON 2D array, e.g. [["Name","Age"],["Alice",30]]

# Insert rows into a table
mcp-documents:docx_table_insert_row(filePath: string, table: number | string, row: number, count: number)

# Insert columns into a table
mcp-documents:docx_table_insert_column(filePath: string, table: number | string, col: number, count: number)

# Format table cells
mcp-documents:docx_table_format(filePath: string, table: number | string, format: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)
```

### Creating Documents

```bash
# Create a new empty DOCX file
mcp-documents:create_document(filePath: string)

# Insert a table at a position
mcp-documents:docx_insert_table(filePath: string, index: number, rows: number, cols: number)
```

---

## 2. Spreadsheet Tools (XLSX, XLS, ODS)

### Reading Spreadsheets

```bash
# List all sheet names
mcp-documents:list_sheets(filePath: string)

# Get sheet dimensions
mcp-documents:get_sheet_info(filePath: string, sheet: string)

# Read a range of cells
mcp-documents:read_range(filePath: string, sheet: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)
# All parameters are 1-indexed

# Read a single cell
mcp-documents:read_cell(filePath: string, sheet: string, row: number, col: number)

# Search for text
mcp-documents:search_sheet(filePath: string, sheet: string, query: string)

# Get formula locations
mcp-documents:list_formulas(filePath: string, sheet: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)

# Get sheet overview
mcp-documents:sheet_overview(filePath: string, sheet: string)
# Shows structure, header detection, formula locations
```

### Writing Spreadsheets

```bash
# Write a 2D range
mcp-documents:write_range(filePath: string, sheet: string, data: string, rowFrom?: number, colFrom?: number)
# data: JSON 2D array, e.g. [[1,"Alice"],[2,"Bob"]]
# Strings starting with '=' become formulas

# Write to a single cell
mcp-documents:write_cell(filePath: string, sheet: string, row: number, col: number, value: string)

# Save document (required after writes)
mcp-documents:save_doc(filePath: string)

# Apply formatting
mcp-documents:format_range(filePath: string, sheet: string, format: string, rowFrom?: number, rowTo?: number, colFrom?: number, colTo?: number)
# format: JSON with bold, italic, underline, fontSize, color, backgroundColor, align
```

### Sheet Management

```bash
# Add a new sheet
mcp-documents:add_sheet(filePath: string, name: string, position?: number)

# Delete a sheet
mcp-documents:delete_sheet(filePath: string, sheet: string)

# Rename a sheet
mcp-documents:rename_sheet(filePath: string, sheet: string, newName: string)

# Insert rows
mcp-documents:insert_rows(filePath: string, sheet: string, row: number, count: number)

# Insert columns
mcp-documents:insert_columns(filePath: string, sheet: string, col: number, count: number)

# Search and replace
mcp-documents:sheet_search_replace(filePath: string, sheet: string, search: string, replace: string, regex?: boolean, caseSensitive?: boolean, formula?: boolean, dryRun?: boolean)
```

### Lifecycle

```bash
# Close a document (release memory)
mcp-documents:close_doc(filePath: string)

# Close all documents
mcp-documents:close_all()

# Health check
mcp-documents:ping()
```

---

## 3. PDF Tools

```bash
# Read PDF content (via document CLI using pandoc)
# Use read_document with .pdf extension
```

---

## 4. Document Conversion

```bash
# Convert between formats
mcp-documents:convert_document(filePath: string, format: string)
# format: pdf, docx, txt, html, etc.
# Returns: path to converted file
```

---

## 5. Important Notes

### Index System

- Paragraph/element indices are 0-based
- Table indices are 0-based
- Cell/row/column references in spreadsheets are 1-based (Excel-style)
- Always get structure first with `docx_structure` or `sheet_overview` before editing

### Backup Files

- Write operations create `.bak` backup files automatically
- First modification to a file creates a backup of the original

### Formula Support

- In spreadsheets: strings starting with `=` are treated as formulas
- Example: `[["=SUM(A1:A10)","Total"]]`

### Cell Ranges

- Row and column parameters are 1-indexed (matching Excel convention)
- `rowFrom: 1` means first row
- `colFrom: 1` means first column (A)

### Error Handling

- `dryRun` defaults to `true` for search/replace operations
- Set `dryRun: false` explicitly to apply changes
- Always check results before setting dryRun to false

&nbsp;

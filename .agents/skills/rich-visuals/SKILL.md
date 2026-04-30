---
name: rich-visuals
description: Render color palettes, charts, progress bars, and other visual elements as inline HTML in conversations and tool output
closecode_version: 1.2.0
scope: any
provisionedAt: "2026-04-30T16:58:06.662Z"
provisionedFrom: templates/skills/rich-visuals/SKILL.md
---

# Rich Visuals Skill

Render visual elements -- color palettes, bar/line/donut charts, progress bars, stat cards, badges, and more -- as inline HTML that displays directly in the conversation.

The CloseCode ADE frontend renders raw HTML inside a **Shadow DOM** boundary for full CSS isolation. Inline styles work. `<style>` tags work (scoped to the shadow root -- they cannot leak into the parent app). SVG works. No JavaScript (stripped by sanitizer). No external resources. CSS custom properties (`var(--color-*)`) inherit through the shadow boundary.

> **CRITICAL: Two rendering paths exist. You MUST know which one you're targeting.**

### Rendering Paths


| Context                                    | Path                                            | Renderer                                 | Restrictions                 |
| ------------------------------------------ | ----------------------------------------------- | ---------------------------------------- | ---------------------------- |
| **Tool output** (MCP tools returning HTML) | `IsolatedHtml` → Shadow DOM                     | Clean HTML/SVG, no markdown interference | None — full HTML/SVG support |
| **Agent text messages** (conversation)     | `MarkdownContent` → react-markdown + rehype-raw | **Markdown parser processes HTML**       | See rules below              |


### Agent Text Message Rules (CRITICAL)

When embedding HTML/SVG in agent text messages (NOT tool output), the markdown parser (`react-markdown`) processes the content first. This causes breakage if you don't follow these rules:

1. **NO blank lines inside HTML blocks** — A blank line inside `<div>...</div>` makes the markdown parser treat the content after it as a new paragraph, breaking the DOM tree. Write HTML blocks as contiguous lines or with only single newlines (no double newlines).
2. **NO markdown syntax between HTML blocks** — Do NOT put `---`, `### headings`, `**bold**`, or other markdown between adjacent HTML blocks. Use EITHER markdown OR HTML in a section, not both interleaved. If you need a heading before an HTML block, use `<h3>` not `###`.
3. **SVG size is NOT limited** — There is no line count limit. An HTML block continues until the first blank line, regardless of size. A 500-line SVG works fine as long as there are no blank lines inside it.
4. **NO negative dimensions in SVG** — `width="-8"` is invalid SVG and browsers silently ignore the element. Use `x` offset to position bars that represent negative values instead.
5. **Separate HTML blocks with a single blank line** — Between independent HTML blocks, use exactly ONE blank line. More than one triggers paragraph breaks.
6. **Self-closing tags** — Use `<br/>` not `<br>`, `<hr/>` not `<hr>`. The XHTML-style is safer through the markdown parser.
7. **Avoid `text-anchor` and complex SVG attributes with quotes** — The markdown parser can mangle attributes that contain special characters. Prefer simple attribute values.

### Safe Pattern (Agent Text Messages)

```
Here is the data:

<div style="display:flex;gap:8px">
<div style="flex:1;padding:12px;background:var(--color-bg-secondary);border-radius:8px;border:1px solid var(--color-border-default)">
<div style="font-size:10px;color:var(--color-text-muted)">METRIC</div>
<div style="font-size:20px;font-weight:700;color:var(--color-text-primary)">1,234</div>
</div>
</div>

More text here...
```

### Unsafe Pattern (Agent Text Messages)

```
### My Header          ← markdown heading
                       ← blank line
<div>                  ← HTML block starts
                       ← BLANK LINE INSIDE = BREAKS DOM
  <span>text</span>
</div>
---                    ← markdown HR between HTML = breaks
<svg viewBox="...">    ← next HTML block confused
```

---

## 1. Theme Integration

All visuals MUST use CSS custom properties from the CloseCode ADE theme so they adapt to light/dark mode automatically.

### Available CSS Variables


| Variable                         | Tailwind Class         | Usage                      |
| -------------------------------- | ---------------------- | -------------------------- |
| `var(--color-bg-primary)`        | `bg-primary`           | Main background            |
| `var(--color-bg-secondary)`      | `bg-secondary`         | Card/container background  |
| `var(--color-bg-tertiary)`       | `bg-tertiary`          | Nested surface background  |
| `var(--color-surface-primary)`   | `bg-surface`           | Elevated surface           |
| `var(--color-surface-secondary)` | `bg-surface-secondary` | Secondary elevated surface |
| `var(--color-bg-hover)`          | `bg-hover`             | Hover state                |
| `var(--color-text-primary)`      | `text-primary`         | Main text                  |
| `var(--color-text-secondary)`    | `text-secondary`       | Secondary text             |
| `var(--color-text-muted)`        | `text-muted`           | Muted/dim text             |
| `var(--color-border-default)`    | `border`               | Default border             |
| `var(--color-accent-primary)`    | `text-accent`          | Accent/link color          |
| `var(--color-accent-secondary)`  | &nbsp;                 | Secondary accent           |
| `var(--color-success)`           | `text-success`         | Success green              |
| `var(--color-warning)`           | `text-warning`         | Warning amber              |
| `var(--color-error)`             | `text-error`           | Error red                  |
| `var(--color-info)`              | `text-info`            | Info blue                  |


### Rules

- Use `var(--color-*)` in all `style` attributes -- never hardcode background/text colors
- Data colors (chart bars, palette swatches) MAY use literal hex/rgb values -- they represent data, not UI chrome
- Containers, labels, axes, legends MUST use theme variables
- Always set `font-family: inherit` or omit font-family to match the app

---

## 2. Color Palettes

### Horizontal Bar

```html
<div style="display:flex;gap:3px;border-radius:6px;overflow:hidden;height:48px;border:1px solid var(--color-border-default)">
  <div style="flex:1;background:#FF6B6B" title="#FF6B6B"></div>
  <div style="flex:1;background:#4ECDC4" title="#4ECDC4"></div>
  <div style="flex:1;background:#45B7D1" title="#45B7D1"></div>
  <div style="flex:1;background:#96CEB4" title="#96CEB4"></div>
  <div style="flex:1;background:#FFEAA7" title="#FFEAA7"></div>
</div>
```

### Grid with Labels

```html
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:6px">
  <div style="text-align:center">
    <div style="background:#FF6B6B;height:48px;border-radius:6px;border:1px solid var(--color-border-default)"></div>
    <div style="font-size:10px;color:var(--color-text-muted);margin-top:3px">#FF6B6B</div>
  </div>
  <!-- repeat for each color -->
</div>
```

### Named Palette (with role labels)

```html
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:8px">
  <div>
    <div style="background:#FF6B6B;height:40px;border-radius:6px 6px 0 0"></div>
    <div style="background:var(--color-bg-secondary);padding:4px 6px;border-radius:0 0 6px 6px;border:1px solid var(--color-border-default);border-top:0">
      <div style="font-size:11px;color:var(--color-text-primary)">Primary</div>
      <div style="font-size:10px;color:var(--color-text-muted)">#FF6B6B</div>
    </div>
  </div>
  <!-- repeat for each color -->
</div>
```

---

## 3. Charts (SVG)

All charts use inline SVG. No JavaScript. Theme variables for chrome, literal colors for data.

### Bar Chart

```html
<svg viewBox="0 0 400 180" style="width:100%;height:auto">
  <rect x="0" y="0" width="400" height="180" rx="8" fill="var(--color-bg-secondary)"/>
  <!-- Title -->
  <text x="200" y="20" text-anchor="middle" fill="var(--color-text-muted)" font-size="11" font-family="inherit">Monthly Revenue</text>
  <!-- Axes -->
  <line x1="40" y1="30" x2="40" y2="150" stroke="var(--color-border-default)" stroke-width="1"/>
  <line x1="40" y1="150" x2="380" y2="150" stroke="var(--color-border-default)" stroke-width="1"/>
  <!-- Grid line -->
  <line x1="40" y1="90" x2="380" y2="90" stroke="var(--color-border-default)" stroke-width="0.5" stroke-dasharray="4"/>
  <!-- Y-axis labels -->
  <text x="36" y="35" text-anchor="end" fill="var(--color-text-muted)" font-size="9" font-family="inherit">100</text>
  <text x="36" y="93" text-anchor="end" fill="var(--color-text-muted)" font-size="9" font-family="inherit">50</text>
  <text x="36" y="153" text-anchor="end" fill="var(--color-text-muted)" font-size="9" font-family="inherit">0</text>
  <!-- Bars (data colors are literal) -->
  <rect x="55" y="70" width="40" height="80" rx="3" fill="#4ECDC4"/>
  <rect x="110" y="50" width="40" height="100" rx="3" fill="#4ECDC4"/>
  <rect x="165" y="90" width="40" height="60" rx="3" fill="#4ECDC4"/>
  <!-- X-axis labels -->
  <text x="75" y="165" text-anchor="middle" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Jan</text>
  <text x="130" y="165" text-anchor="middle" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Feb</text>
  <text x="185" y="165" text-anchor="middle" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Mar</text>
</svg>
```

### Line Chart

```html
<svg viewBox="0 0 400 180" style="width:100%;height:auto">
  <rect x="0" y="0" width="400" height="180" rx="8" fill="var(--color-bg-secondary)"/>
  <text x="200" y="20" text-anchor="middle" fill="var(--color-text-muted)" font-size="11" font-family="inherit">Trend</text>
  <line x1="40" y1="30" x2="40" y2="150" stroke="var(--color-border-default)" stroke-width="1"/>
  <line x1="40" y1="150" x2="380" y2="150" stroke="var(--color-border-default)" stroke-width="1"/>
  <!-- Line (data color) -->
  <polyline points="60,130 120,100 180,110 240,70 300,50 360,60" fill="none" stroke="#4ECDC4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Dots -->
  <circle cx="60" cy="130" r="3" fill="#4ECDC4"/>
  <circle cx="120" cy="100" r="3" fill="#4ECDC4"/>
  <circle cx="180" cy="110" r="3" fill="#4ECDC4"/>
  <circle cx="240" cy="70" r="3" fill="#4ECDC4"/>
  <circle cx="300" cy="50" r="3" fill="#4ECDC4"/>
  <circle cx="360" cy="60" r="3" fill="#4ECDC4"/>
  <!-- X-axis labels -->
  <text x="60" y="165" text-anchor="middle" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Mon</text>
  <text x="120" y="165" text-anchor="middle" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Tue</text>
</svg>
```

### Donut Chart

```html
<svg viewBox="0 0 200 200" style="width:100%;height:auto">
  <rect x="0" y="0" width="200" height="200" rx="8" fill="var(--color-bg-secondary)"/>
  <!-- Segments: stroke-dasharray = (fraction * 2 * pi * r), stroke-dashoffset = cumulative -->
  <circle cx="100" cy="95" r="55" fill="none" stroke="#FF6B6B" stroke-width="18" stroke-dasharray="125 346" stroke-dashoffset="0" transform="rotate(-90 100 95)"/>
  <circle cx="100" cy="95" r="55" fill="none" stroke="#4ECDC4" stroke-width="18" stroke-dasharray="87 346" stroke-dashoffset="-125" transform="rotate(-90 100 95)"/>
  <circle cx="100" cy="95" r="55" fill="none" stroke="#45B7D1" stroke-width="18" stroke-dasharray="69 346" stroke-dashoffset="-212" transform="rotate(-90 100 95)"/>
  <circle cx="100" cy="95" r="55" fill="none" stroke="#FFEAA7" stroke-width="18" stroke-dasharray="65 346" stroke-dashoffset="-281" transform="rotate(-90 100 95)"/>
  <!-- Center label -->
  <text x="100" y="92" text-anchor="middle" fill="var(--color-text-primary)" font-size="18" font-weight="bold" font-family="inherit">1.2k</text>
  <text x="100" y="106" text-anchor="middle" fill="var(--color-text-muted)" font-size="10" font-family="inherit">total</text>
  <!-- Legend -->
  <circle cx="30" cy="180" r="4" fill="#FF6B6B"/><text x="38" y="183" fill="var(--color-text-muted)" font-size="9" font-family="inherit">Web 36%</text>
  <circle cx="110" cy="180" r="4" fill="#4ECDC4"/><text x="118" y="183" fill="var(--color-text-muted)" font-size="9" font-family="inherit">API 25%</text>
</svg>
```

### Donut Math

To calculate `stroke-dasharray` and `stroke-dashoffset` for each segment:

- Circumference `C = 2 * pi * r` (for r=55, C ~= 345.6)
- Segment arc length = `fraction * C`
- `stroke-dasharray` = `"arcLength C"` (arc then gap = full circumference)
- `stroke-dashoffset` = negative cumulative of previous arcs

---

## 4. Progress Bars

### Simple

```html
<div style="background:var(--color-bg-tertiary);border-radius:6px;overflow:hidden;height:20px;border:1px solid var(--color-border-default)">
  <div style="width:72%;height:100%;background:var(--color-accent-primary);border-radius:5px;display:flex;align-items:center;justify-content:center">
    <span style="font-size:10px;color:var(--color-text-inverse);font-weight:600">72%</span>
  </div>
</div>
```

### Labeled

```html
<div>
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="font-size:11px;color:var(--color-text-secondary)">Build Progress</span>
    <span style="font-size:11px;color:var(--color-text-muted)">72%</span>
  </div>
  <div style="background:var(--color-bg-tertiary);border-radius:6px;overflow:hidden;height:8px;border:1px solid var(--color-border-default)">
    <div style="width:72%;height:100%;background:var(--color-accent-primary);border-radius:5px"></div>
  </div>
</div>
```

### Multi-segment

```html
<div style="display:flex;gap:2px;border-radius:6px;overflow:hidden;height:8px;background:var(--color-bg-tertiary);border:1px solid var(--color-border-default)">
  <div style="width:45%;background:var(--color-success)" title="Passed: 45%"></div>
  <div style="width:12%;background:var(--color-warning)" title="Pending: 12%"></div>
  <div style="width:8%;background:var(--color-error)" title="Failed: 8%"></div>
</div>
```

---

## 5. Stat Cards

### Single Stat

```html
<div style="display:inline-flex;flex-direction:column;padding:12px 16px;border-radius:8px;background:var(--color-bg-secondary);border:1px solid var(--color-border-default);min-width:100px">
  <span style="font-size:10px;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:0.05em">Revenue</span>
  <span style="font-size:22px;font-weight:700;color:var(--color-text-primary);line-height:1.2">$48.2k</span>
  <span style="font-size:10px;color:var(--color-success)">+12.5%</span>
</div>
```

### Stat Row

```html
<div style="display:flex;gap:8px;flex-wrap:wrap">
  <div style="flex:1;min-width:100px;padding:10px 14px;border-radius:8px;background:var(--color-bg-secondary);border:1px solid var(--color-border-default)">
    <div style="font-size:10px;color:var(--color-text-muted)">Users</div>
    <div style="font-size:20px;font-weight:700;color:var(--color-text-primary)">1,234</div>
  </div>
  <div style="flex:1;min-width:100px;padding:10px 14px;border-radius:8px;background:var(--color-bg-secondary);border:1px solid var(--color-border-default)">
    <div style="font-size:10px;color:var(--color-text-muted)">Sessions</div>
    <div style="font-size:20px;font-weight:700;color:var(--color-text-primary)">3,456</div>
  </div>
  <div style="flex:1;min-width:100px;padding:10px 14px;border-radius:8px;background:var(--color-bg-secondary);border:1px solid var(--color-border-default)">
    <div style="font-size:10px;color:var(--color-text-muted)">Errors</div>
    <div style="font-size:20px;font-weight:700;color:var(--color-error)">23</div>
  </div>
</div>
```

---

## 6. Badges & Tags

### Inline Status Badge

```html
<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:500;background:var(--color-bg-tertiary);color:var(--color-success);border:1px solid var(--color-border-default)">
  <span style="width:6px;height:6px;border-radius:50%;background:currentColor"></span>
  Active
</span>
```

### Tag Group

```html
<div style="display:flex;gap:4px;flex-wrap:wrap">
  <span style="padding:2px 8px;border-radius:4px;font-size:10px;background:var(--color-accent-muted);color:var(--color-accent-primary)">frontend</span>
  <span style="padding:2px 8px;border-radius:4px;font-size:10px;background:var(--color-accent-muted);color:var(--color-accent-primary)">react</span>
  <span style="padding:2px 8px;border-radius:4px;font-size:10px;background:var(--color-accent-muted);color:var(--color-accent-primary)">typescript</span>
</div>
```

---

## 7. Comparison Table (styled HTML)

For when a markdown table is insufficient (colored cells, embedded bars):

```html
<table style="width:100%;border-collapse:collapse;font-size:12px">
  <thead>
    <tr style="border-bottom:2px solid var(--color-border-default)">
      <th style="text-align:left;padding:6px 8px;color:var(--color-text-muted);font-weight:500">Metric</th>
      <th style="text-align:right;padding:6px 8px;color:var(--color-text-muted);font-weight:500">Current</th>
      <th style="text-align:right;padding:6px 8px;color:var(--color-text-muted);font-weight:500">Previous</th>
      <th style="text-align:right;padding:6px 8px;color:var(--color-text-muted);font-weight:500">Change</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid var(--color-border-default)">
      <td style="padding:6px 8px;color:var(--color-text-primary)">Revenue</td>
      <td style="padding:6px 8px;text-align:right;color:var(--color-text-primary)">$48.2k</td>
      <td style="padding:6px 8px;text-align:right;color:var(--color-text-secondary)">$42.8k</td>
      <td style="padding:6px 8px;text-align:right;color:var(--color-success)">+12.6%</td>
    </tr>
  </tbody>
</table>
```

---

## 8. Guidelines

### Do

- Use `var(--color-*)` for all UI chrome (backgrounds, text, borders, axes, labels)
- Use `font-family: inherit` or omit it entirely
- Use `style="width:100%;height:auto"` on SVGs to fill the available width
- Use `viewBox` on all SVGs for proper scaling
- Set `title` attributes on data elements (palette swatches, chart bars) for accessibility
- SVGs can be any size — no line limit. The only rule is no blank lines inside the SVG block
- Use `border-radius` for softer appearance consistent with the UI
- Write HTML blocks as contiguous lines — NO blank lines inside a `<div>` or `<svg>`
- When mixing text and visuals in agent messages, use ALL HTML (including headings via `<h3>`) or ALL markdown — never interleave

### Do Not

- Do NOT use `<script>` tags (stripped by sanitizer)
- Do NOT use `<link>` or `<style>` tags in agent messages (inline styles only). `<style>` works in tool output (Shadow DOM) but not in agent text.
- Do NOT use external resources (images, fonts, CSS files)
- Do NOT hardcode colors for UI chrome -- only for data values
- Do NOT use `class` attributes (Tailwind classes don't work in raw HTML output)
- Do NOT use `position: fixed` or `position: absolute` (breaks conversation flow)
- Do NOT add `onclick` or any event handlers (stripped by sanitizer)
- Do NOT put blank lines inside HTML blocks in agent messages (breaks markdown parser)
- Do NOT interleave markdown `---`, `###`, `**` with HTML blocks — use one or the other
- Do NOT use negative `width` or `height` in SVG — these are invalid and silently fail

### For Tool Output

When building MCP tools that return visual output, return the HTML as a plain string. The frontend will detect it as `HTML_CONTENT` and render it inline via `IsolatedHtml` (Shadow DOM). Full HTML/SVG is supported without markdown restrictions.

### For Agent Text Messages

Agents CAN embed HTML in text responses, but **the markdown parser processes it first**. Follow the Agent Text Message Rules at the top of this document. Key rule: NO blank lines inside HTML blocks, NO interleaved markdown syntax.

Prefer smaller, self-contained HTML blocks separated by single blank lines. For complex dashboards with multiple charts, consider returning the HTML from a tool call (which uses Shadow DOM) rather than embedding in text.

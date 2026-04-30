---
name: html-presentations
description: Create beautiful, self-contained HTML presentations with navigation, animations, and responsive design - zero dependencies
closecode_version: 1.0.0
scope: any
provisionedAt: "2026-04-30T16:58:06.658Z"
provisionedFrom: templates/skills/html-presentations/SKILL.md
---

# HTML Presentations Skill

This skill teaches agents how to generate beautiful, self-contained, single-file HTML presentations. Every presentation is one `.html` file with all CSS and JavaScript inline — zero external dependencies, works offline, easy to share.

## 1. Core Principles

| Principle | Detail |
|---|---|
| **Single file** | One `.html` file — all styles and scripts inline |
| **Zero dependencies** | No CDN links, no external CSS/JS/fonts |
| **Responsive** | Desktop, tablet (<=1024px), mobile (<=640px) |
| **Accessible navigation** | Keyboard, mouse click, touch swipe, mouse wheel |
| **Print-ready** | `@media print` styles — one slide per page, no UI chrome |
| **Deep-linkable** | URL hash sync (`#slide-3`) with browser back/forward |
| **System fonts** | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` |

**File naming:** `<topic-slug>-presentation.html`
**Output location:** project root or `docs/presentations/`

---

## 2. Base Template

Always start from this template. Copy it, then customize slides.

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Presentation Title</title>
<style>
/* ===== CSS Custom Properties (Theme) ===== */
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a2e;
  --color-heading: #16213e;
  --color-accent: #0f3460;
  --color-accent-light: #e2e8f0;
  --color-code-bg: #f1f5f9;
  --color-code-text: #334155;
  --color-slide-counter: #94a3b8;
  --color-progress: #0f3460;
  --color-nav-btn: rgba(15, 52, 96, 0.15);
  --color-nav-btn-hover: rgba(15, 52, 96, 0.3);
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  --font-heading: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace;
  --slide-padding: 80px;
  --transition-speed: 0.5s;
}

[data-theme="dark"] {
  --color-bg: #0f172a;
  --color-text: #e2e8f0;
  --color-heading: #f8fafc;
  --color-accent: #38bdf8;
  --color-accent-light: #1e293b;
  --color-code-bg: #1e293b;
  --color-code-text: #e2e8f0;
  --color-slide-counter: #64748b;
  --color-progress: #38bdf8;
  --color-nav-btn: rgba(56, 189, 248, 0.15);
  --color-nav-btn-hover: rgba(56, 189, 248, 0.3);
}

/* ===== Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; background: var(--color-bg); color: var(--color-text); font-family: var(--font-body); }

/* ===== Progress Bar ===== */
.progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--color-progress); transition: width 0.3s ease; z-index: 100; }

/* ===== Slide Container ===== */
.presentation { position: relative; width: 100%; height: 100vh; }
.slide {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  padding: var(--slide-padding);
  opacity: 0; visibility: hidden;
  transition: opacity var(--transition-speed) ease, transform var(--transition-speed) ease;
  transform: translateX(40px);
}
.slide.active { opacity: 1; visibility: visible; transform: translateX(0); }
.slide.prev { opacity: 0; transform: translateX(-40px); }

/* Transition variants */
.slide.transition-fade { transform: none; }
.slide.transition-fade.prev { transform: none; }
.slide.transition-zoom { transform: scale(0.85); }
.slide.transition-zoom.prev { transform: scale(1.15); }
.slide.transition-none { transition: none; }

/* ===== Typography ===== */
.slide h1 { font-family: var(--font-heading); font-size: 3.2rem; font-weight: 800; color: var(--color-heading); line-height: 1.15; margin-bottom: 0.5em; text-align: center; letter-spacing: -0.02em; }
.slide h2 { font-family: var(--font-heading); font-size: 2.2rem; font-weight: 700; color: var(--color-heading); line-height: 1.25; margin-bottom: 0.6em; }
.slide h3 { font-size: 1.5rem; font-weight: 600; color: var(--color-heading); margin-bottom: 0.5em; }
.slide p { font-size: 1.25rem; line-height: 1.7; margin-bottom: 0.8em; max-width: 800px; }
.slide ul, .slide ol { font-size: 1.2rem; line-height: 1.8; margin-bottom: 1em; padding-left: 1.5em; max-width: 800px; }
.slide li { margin-bottom: 0.4em; }
.slide a { color: var(--color-accent); text-decoration: underline; }
.slide .subtitle { font-size: 1.4rem; color: var(--color-slide-counter); font-weight: 400; margin-top: -0.3em; margin-bottom: 1em; text-align: center; }
.slide .author { font-size: 1.1rem; color: var(--color-slide-counter); margin-top: 1.5em; text-align: center; }
.slide .small { font-size: 0.95rem; color: var(--color-slide-counter); }

/* ===== Code Blocks ===== */
.slide pre { background: var(--color-code-bg); border-radius: 12px; padding: 1.5em; overflow-x: auto; max-width: 900px; width: 100%; margin-bottom: 1em; }
.slide code { font-family: var(--font-mono); font-size: 1rem; color: var(--color-code-text); line-height: 1.6; }
.slide p code, .slide li code { background: var(--color-code-bg); padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.9em; }
.kw { color: #8b5cf6; font-weight: 600; }  /* keyword */
.str { color: #059669; }                     /* string */
.cm { color: #94a3b8; font-style: italic; }  /* comment */
.fn { color: #2563eb; }                      /* function */
.num { color: #d97706; }                     /* number */

/* ===== Layout Utilities ===== */
.columns { display: flex; gap: 2.5em; width: 100%; max-width: 1000px; align-items: flex-start; }
.col { flex: 1; min-width: 0; }
.text-center { text-align: center; }
.text-left { text-align: left; width: 100%; max-width: 800px; }
.full-width { width: 100%; max-width: 1000px; }

/* ===== Slide Type: Section Divider ===== */
.slide.section-divider { background: var(--color-accent); }
.slide.section-divider h1, .slide.section-divider h2 { color: #fff; }
.slide.section-divider .subtitle { color: rgba(255,255,255,0.7); }

/* ===== Slide Type: Quote ===== */
.slide blockquote { font-size: 1.6rem; font-style: italic; line-height: 1.6; max-width: 750px; text-align: center; border: none; padding: 0; position: relative; }
.slide blockquote::before { content: '\201C'; font-size: 5rem; color: var(--color-accent); position: absolute; top: -0.4em; left: -0.15em; line-height: 1; opacity: 0.3; }
.slide .attribution { font-size: 1rem; color: var(--color-slide-counter); margin-top: 1em; text-align: center; }

/* ===== Images ===== */
.slide img { max-width: 100%; max-height: 60vh; object-fit: contain; border-radius: 8px; }
.slide .caption { font-size: 0.95rem; color: var(--color-slide-counter); margin-top: 0.5em; text-align: center; }

/* ===== Tables ===== */
.slide table { border-collapse: collapse; width: 100%; max-width: 900px; font-size: 1.05rem; margin-bottom: 1em; }
.slide th, .slide td { padding: 0.7em 1em; text-align: left; border-bottom: 1px solid var(--color-accent-light); }
.slide th { font-weight: 700; color: var(--color-heading); border-bottom-width: 2px; }

/* ===== Fragments (Build Animations) ===== */
.fragment { opacity: 0; transform: translateY(15px); transition: opacity 0.4s ease, transform 0.4s ease; }
.fragment.visible { opacity: 1; transform: translateY(0); }
.fragment-fade-in { opacity: 0; transition: opacity 0.4s ease; }
.fragment-fade-in.visible { opacity: 1; }
.fragment-grow { opacity: 0; transform: scale(0.8); transition: opacity 0.4s ease, transform 0.4s ease; }
.fragment-grow.visible { opacity: 1; transform: scale(1); }
.fragment-highlight { transition: background-color 0.4s ease; }
.fragment-highlight.visible { background-color: rgba(56, 189, 248, 0.15); }

/* ===== Navigation Controls ===== */
.nav-controls { position: fixed; bottom: 30px; right: 30px; display: flex; gap: 10px; z-index: 90; }
.nav-btn { width: 44px; height: 44px; border-radius: 50%; border: none; background: var(--color-nav-btn); color: var(--color-text); font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.nav-btn:hover { background: var(--color-nav-btn-hover); }
.slide-counter { position: fixed; bottom: 36px; left: 30px; font-size: 0.9rem; color: var(--color-slide-counter); z-index: 90; font-variant-numeric: tabular-nums; }

/* ===== Overview Mode ===== */
.presentation.overview .slide {
  position: relative; opacity: 1; visibility: visible; transform: none;
  width: calc(25% - 15px); height: 180px; flex: none;
  border: 2px solid var(--color-accent-light); border-radius: 8px;
  cursor: pointer; overflow: hidden; font-size: 0.35rem;
  padding: 10px; transition: border-color 0.2s;
}
.presentation.overview .slide:hover { border-color: var(--color-accent); }
.presentation.overview .slide.active { border-color: var(--color-accent); box-shadow: 0 0 0 2px var(--color-accent); }
.presentation.overview { display: flex; flex-wrap: wrap; gap: 15px; padding: 30px; height: 100vh; overflow-y: auto; align-content: flex-start; }

/* ===== Speaker Notes ===== */
.speaker-notes { position: fixed; bottom: 0; left: 0; right: 0; background: var(--color-code-bg); border-top: 2px solid var(--color-accent-light); padding: 1em 2em; font-size: 0.95rem; display: none; z-index: 95; max-height: 30vh; overflow-y: auto; }
.speaker-notes.visible { display: block; }

/* ===== Responsive: Tablet ===== */
@media (max-width: 1024px) {
  :root { --slide-padding: 50px; }
  .slide h1 { font-size: 2.4rem; }
  .slide h2 { font-size: 1.8rem; }
  .slide p, .slide ul, .slide ol { font-size: 1.1rem; }
  .columns { gap: 1.5em; }
  .presentation.overview .slide { width: calc(33.33% - 12px); }
}

/* ===== Responsive: Mobile ===== */
@media (max-width: 640px) {
  :root { --slide-padding: 24px; }
  .slide h1 { font-size: 1.8rem; }
  .slide h2 { font-size: 1.4rem; }
  .slide h3 { font-size: 1.15rem; }
  .slide p, .slide ul, .slide ol { font-size: 1rem; }
  .slide pre { padding: 1em; font-size: 0.85rem; border-radius: 8px; }
  .slide blockquote { font-size: 1.2rem; }
  .columns { flex-direction: column; gap: 1.2em; }
  .nav-controls { bottom: 16px; right: 16px; }
  .slide-counter { bottom: 22px; left: 16px; }
  .presentation.overview .slide { width: calc(50% - 10px); height: 120px; }
}

/* ===== Print ===== */
@media print {
  .nav-controls, .slide-counter, .progress-bar, .speaker-notes { display: none !important; }
  .presentation { display: block; height: auto; overflow: visible; }
  .slide {
    position: relative; opacity: 1 !important; visibility: visible !important;
    transform: none !important; page-break-after: always;
    height: 100vh; display: flex;
  }
  .fragment { opacity: 1 !important; transform: none !important; }
}
</style>
</head>
<body>

<div class="progress-bar" id="progress"></div>

<div class="presentation" id="deck">

  <!-- SLIDE 1: Title -->
  <section class="slide active">
    <h1>Presentation Title</h1>
    <p class="subtitle">Subtitle or tagline goes here</p>
    <p class="author">Author Name &middot; Date</p>
  </section>

  <!-- SLIDE 2: Content -->
  <section class="slide">
    <h2>Slide Heading</h2>
    <ul class="text-left">
      <li class="fragment">First point builds in</li>
      <li class="fragment">Second point builds in</li>
      <li class="fragment">Third point builds in</li>
    </ul>
    <aside class="notes">Speaker notes for this slide go here.</aside>
  </section>

  <!-- Add more slides here -->

</div>

<div class="slide-counter" id="counter"></div>
<div class="nav-controls">
  <button class="nav-btn" id="prevBtn" aria-label="Previous slide">&#8592;</button>
  <button class="nav-btn" id="nextBtn" aria-label="Next slide">&#8594;</button>
</div>
<div class="speaker-notes" id="notes"></div>

<script>
class Presentation {
  constructor() {
    this.deck = document.getElementById('deck');
    this.slides = [...this.deck.querySelectorAll('.slide')];
    this.current = 0;
    this.overview = false;
    this.notesVisible = false;
    this.touchStartX = 0;
    this.wheelTimer = null;

    this.readHash();
    this.bindEvents();
    this.update();
  }

  get total() { return this.slides.length; }

  readHash() {
    const m = location.hash.match(/^#slide-(\d+)$/);
    if (m) this.current = Math.max(0, Math.min(parseInt(m[1], 10) - 1, this.total - 1));
  }

  bindEvents() {
    document.addEventListener('keydown', e => this.onKey(e));
    document.addEventListener('touchstart', e => { this.touchStartX = e.touches[0].clientX; }, { passive: true });
    document.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - this.touchStartX;
      if (Math.abs(dx) > 50) dx > 0 ? this.prev() : this.next();
    });
    document.addEventListener('wheel', e => {
      if (this.wheelTimer) return;
      this.wheelTimer = setTimeout(() => { this.wheelTimer = null; }, 400);
      e.deltaY > 0 ? this.next() : this.prev();
    }, { passive: true });
    document.getElementById('prevBtn').addEventListener('click', () => this.prev());
    document.getElementById('nextBtn').addEventListener('click', () => this.next());
    window.addEventListener('hashchange', () => { this.readHash(); this.update(); });
    if (this.overview) return;
    this.slides.forEach((s, i) => s.addEventListener('click', () => {
      if (this.overview) { this.current = i; this.toggleOverview(); }
    }));
  }

  onKey(e) {
    const handlers = {
      ArrowRight: () => this.next(), ArrowDown: () => this.next(),
      Space: () => this.next(), Enter: () => this.next(), PageDown: () => this.next(),
      ArrowLeft: () => this.prev(), ArrowUp: () => this.prev(),
      Backspace: () => this.prev(), PageUp: () => this.prev(),
      Home: () => { this.current = 0; this.update(); },
      End: () => { this.current = this.total - 1; this.update(); },
      KeyO: () => this.toggleOverview(),
      KeyF: () => { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); },
      KeyS: () => this.toggleNotes(),
    };
    const fn = handlers[e.code];
    if (fn) { e.preventDefault(); fn(); }
  }

  next() {
    if (this.overview) return;
    const slide = this.slides[this.current];
    const pending = slide.querySelectorAll('.fragment:not(.visible), .fragment-fade-in:not(.visible), .fragment-grow:not(.visible), .fragment-highlight:not(.visible)');
    if (pending.length) { pending[0].classList.add('visible'); return; }
    if (this.current < this.total - 1) { this.current++; this.update(); }
  }

  prev() {
    if (this.overview) return;
    if (this.current > 0) { this.current--; this.update(); }
  }

  update() {
    this.slides.forEach((s, i) => {
      s.classList.remove('active', 'prev');
      if (i === this.current) s.classList.add('active');
      else if (i < this.current) s.classList.add('prev');
      // Reset fragments on non-active slides
      if (i !== this.current) s.querySelectorAll('.visible').forEach(f => f.classList.remove('visible'));
    });
    document.getElementById('counter').textContent = `${this.current + 1} / ${this.total}`;
    document.getElementById('progress').style.width = `${((this.current + 1) / this.total) * 100}%`;
    history.replaceState(null, '', `#slide-${this.current + 1}`);
    // Speaker notes
    const noteEl = this.slides[this.current].querySelector('.notes, aside.notes');
    document.getElementById('notes').innerHTML = noteEl ? noteEl.innerHTML : '';
  }

  toggleOverview() {
    this.overview = !this.overview;
    this.deck.classList.toggle('overview', this.overview);
    if (!this.overview) this.update();
  }

  toggleNotes() {
    this.notesVisible = !this.notesVisible;
    document.getElementById('notes').classList.toggle('visible', this.notesVisible);
  }
}

document.addEventListener('DOMContentLoaded', () => new Presentation());
</script>
</body>
</html>
```

---

## 3. Slide Types & Content Patterns

Use these patterns when building slides. Each is a `<section class="slide">` block.

### Title Slide

```html
<section class="slide">
  <h1>Main Title Here</h1>
  <p class="subtitle">Subtitle or tagline</p>
  <p class="author">Author Name &middot; January 2026</p>
</section>
```

### Section Divider

```html
<section class="slide section-divider">
  <h1>Section Name</h1>
  <p class="subtitle">Brief description of this section</p>
</section>
```

### Content with Fragments (Build-in)

```html
<section class="slide">
  <h2>Key Points</h2>
  <ul class="text-left">
    <li class="fragment">First point appears on click/keypress</li>
    <li class="fragment">Second point appears next</li>
    <li class="fragment">Third point appears last</li>
  </ul>
</section>
```

### Two-Column Layout

```html
<section class="slide">
  <h2>Comparison</h2>
  <div class="columns">
    <div class="col">
      <h3>Before</h3>
      <ul><li>Manual process</li><li>Error-prone</li></ul>
    </div>
    <div class="col">
      <h3>After</h3>
      <ul><li>Automated</li><li>Reliable</li></ul>
    </div>
  </div>
</section>
```

### Code Slide

```html
<section class="slide">
  <h2>Code Example</h2>
  <pre><code><span class="kw">function</span> <span class="fn">greet</span>(name) {
  <span class="cm">// Return a greeting</span>
  <span class="kw">return</span> <span class="str">`Hello, ${name}!`</span>;
}</code></pre>
</section>
```

For plain code without highlighting, omit the `<span>` classes — the monospace styling still applies.

### Image Slide

```html
<section class="slide">
  <h2>Architecture Overview</h2>
  <img src="diagram.png" alt="System architecture diagram">
  <p class="caption">Figure 1: High-level system architecture</p>
</section>
```

For self-contained files, use base64 data URIs:

```html
<img src="data:image/png;base64,iVBORw0KGgo..." alt="Description">
```

### Quote Slide

```html
<section class="slide">
  <blockquote>The best way to predict the future is to invent it.</blockquote>
  <p class="attribution">&mdash; Alan Kay</p>
</section>
```

### Table Slide

```html
<section class="slide">
  <h2>Feature Comparison</h2>
  <table>
    <thead><tr><th>Feature</th><th>Option A</th><th>Option B</th></tr></thead>
    <tbody>
      <tr><td>Performance</td><td>Fast</td><td>Moderate</td></tr>
      <tr><td>Bundle Size</td><td>12 KB</td><td>45 KB</td></tr>
    </tbody>
  </table>
</section>
```

### Summary / Recap Slide

```html
<section class="slide">
  <h2>Key Takeaways</h2>
  <ul class="text-left">
    <li class="fragment">&#10003; First key insight</li>
    <li class="fragment">&#10003; Second key insight</li>
    <li class="fragment">&#10003; Third key insight</li>
  </ul>
</section>
```

### Inline SVG Diagram

```html
<section class="slide">
  <h2>Data Flow</h2>
  <svg viewBox="0 0 600 200" style="max-width:600px;width:100%">
    <rect x="10" y="70" width="120" height="60" rx="8" fill="var(--color-accent)" opacity="0.15" stroke="var(--color-accent)" stroke-width="2"/>
    <text x="70" y="105" text-anchor="middle" fill="var(--color-text)" font-size="14">Client</text>
    <line x1="130" y1="100" x2="220" y2="100" stroke="var(--color-accent)" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="220" y="70" width="120" height="60" rx="8" fill="var(--color-accent)" opacity="0.15" stroke="var(--color-accent)" stroke-width="2"/>
    <text x="280" y="105" text-anchor="middle" fill="var(--color-text)" font-size="14">API</text>
    <line x1="340" y1="100" x2="430" y2="100" stroke="var(--color-accent)" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="430" y="70" width="120" height="60" rx="8" fill="var(--color-accent)" opacity="0.15" stroke="var(--color-accent)" stroke-width="2"/>
    <text x="490" y="105" text-anchor="middle" fill="var(--color-text)" font-size="14">Database</text>
    <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-accent)"/></marker></defs>
  </svg>
</section>
```

---

## 4. Themes

Switch themes by changing CSS custom properties in the `:root` block, or set `data-theme` on `<html>`.

### Light (Default)

Already defined in the base template. Clean white background, dark text, navy accents.

### Dark

Set `<html data-theme="dark">`. Already defined in the base template. Dark slate background, light text, sky-blue accents.

### Corporate

Replace the `:root` custom properties block:

```css
:root {
  --color-bg: #fafafa;
  --color-text: #1e293b;
  --color-heading: #0c2340;
  --color-accent: #b8860b;
  --color-accent-light: #e8e0d0;
  --color-code-bg: #f5f0e8;
  --color-code-text: #1e293b;
  --color-slide-counter: #78716c;
  --color-progress: #b8860b;
  --color-nav-btn: rgba(184, 134, 11, 0.12);
  --color-nav-btn-hover: rgba(184, 134, 11, 0.25);
  --font-heading: Georgia, 'Times New Roman', serif;
}
```

### Creative

Replace the `:root` custom properties block:

```css
:root {
  --color-bg: #faf5ff;
  --color-text: #3b0764;
  --color-heading: #581c87;
  --color-accent: #a855f7;
  --color-accent-light: #f3e8ff;
  --color-code-bg: #faf5ff;
  --color-code-text: #581c87;
  --color-slide-counter: #a78bfa;
  --color-progress: #a855f7;
  --color-nav-btn: rgba(168, 85, 247, 0.12);
  --color-nav-btn-hover: rgba(168, 85, 247, 0.25);
  --slide-padding: 60px;
}
```

---

## 5. Animations & Transitions

### Slide Transitions

Set a default transition on all slides by adding a class to each `<section>`:

| Class | Effect |
|---|---|
| *(default)* | Slide horizontally (left/right) |
| `transition-fade` | Crossfade between slides |
| `transition-zoom` | Zoom in/out |
| `transition-none` | Instant switch, no animation |

Per-slide override — add the class directly to one `<section>`:

```html
<section class="slide transition-zoom">
  <h2>This slide zooms in</h2>
</section>
```

### Fragment Animations

Elements with fragment classes appear one-by-one when advancing within a slide.

| Class | Effect |
|---|---|
| `fragment` | Fade in + slide up (default) |
| `fragment-fade-in` | Fade in only |
| `fragment-grow` | Fade in + scale up |
| `fragment-highlight` | Highlight background color |

```html
<p class="fragment">Appears first</p>
<p class="fragment-grow">Grows in second</p>
<p class="fragment-highlight">Gets highlighted third</p>
```

---

## 6. Keyboard Shortcuts

| Key | Action |
|---|---|
| Right / Down / Space / Enter / PageDown | Next slide or fragment |
| Left / Up / Backspace / PageUp | Previous slide |
| Home | First slide |
| End | Last slide |
| O | Toggle overview (grid of all slides) |
| F | Toggle fullscreen |
| S | Toggle speaker notes panel |

Touch: swipe left/right. Mouse wheel: scroll to advance.

---

## 7. Agent Instructions

When generating a presentation, follow these rules:

1. **Always start from the base template** in Section 2 — copy it entirely, then replace the slide `<section>` blocks with actual content
2. **Keep it single-file** — all CSS and JS must remain inline; never add `<link>` or `<script src="...">`
3. **Use system font stacks** — never reference Google Fonts or external font files
4. **One idea per slide** — keep slides focused; aim for 10-20 slides for a typical presentation
5. **Use semantic HTML** — `<h1>` for title slides, `<h2>` for slide headings, `<ul>`/`<ol>` for lists, `<pre><code>` for code, `<blockquote>` for quotes
6. **Include speaker notes** — add `<aside class="notes">` inside slides when the user provides talking points
7. **Use fragments sparingly** — build-in animations work well for 3-5 items per slide, not for every element
8. **Choose an appropriate theme** — match the presentation topic (dark for technical talks, corporate for business, creative for design)
9. **Set the `<title>`** — always update the HTML `<title>` tag to match the presentation title
10. **Test mentally for overflow** — ensure text fits within one viewport height; split long content into multiple slides
11. **Images** — if the user provides image paths, use relative paths; for fully self-contained files, suggest base64 encoding
12. **File naming** — use `<topic-slug>-presentation.html` (e.g., `api-architecture-presentation.html`)
13. **Output location** — save to `docs/presentations/` if the directory exists, otherwise project root

---

## 8. Customization Guide

### Custom Accent Colors

Change only the `--color-accent` and related properties in `:root`:

```css
--color-accent: #e11d48;          /* rose */
--color-progress: #e11d48;
--color-nav-btn: rgba(225, 29, 72, 0.12);
--color-nav-btn-hover: rgba(225, 29, 72, 0.25);
```

### Custom Slide Background

Add inline style to a single slide:

```html
<section class="slide" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); --color-heading: #fff; --color-text: #fff;">
  <h1>Gradient Background</h1>
</section>
```

### Simple Bar Chart (Inline SVG)

```html
<svg viewBox="0 0 400 200" style="max-width:400px;width:100%">
  <rect x="30" y="120" width="60" height="60" rx="4" fill="var(--color-accent)" opacity="0.7"/>
  <text x="60" y="115" text-anchor="middle" fill="var(--color-text)" font-size="12">30%</text>
  <rect x="120" y="60" width="60" height="120" rx="4" fill="var(--color-accent)" opacity="0.85"/>
  <text x="150" y="55" text-anchor="middle" fill="var(--color-text)" font-size="12">60%</text>
  <rect x="210" y="20" width="60" height="160" rx="4" fill="var(--color-accent)"/>
  <text x="240" y="15" text-anchor="middle" fill="var(--color-text)" font-size="12">80%</text>
  <line x1="20" y1="180" x2="300" y2="180" stroke="var(--color-accent-light)" stroke-width="1"/>
</svg>
```

### Embedding Base64 Images

For fully self-contained presentations with images, convert images to base64:

```bash
base64 -w 0 image.png
```

Then use in the HTML:

```html
<img src="data:image/png;base64,<base64-string>" alt="Description">
```

**Note:** Base64 increases file size by ~33%. Use sparingly for essential images only.

&nbsp;

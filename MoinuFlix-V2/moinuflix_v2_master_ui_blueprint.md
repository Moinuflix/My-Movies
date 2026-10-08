# MoinuFlix V2 — Master UI Blueprint

## 1. Master UI Architecture

The MoinuFlix V2 Master UI is a centralized, modular design system and shared component layer built specifically for OTT administration, media staging, synchronization, and catalog inspection.

### Architecture Overview

```
                      +------------------------------------------+
                      |               HTML Document              |
                      | (p_push.html, d_sync.html, m_view, etc.) |
                      +--------------------+---------------------+
                                           |
                    +----------------------+---------------------+
                    |                                            |
         [Design & Styles Layer]                      [Behavioral Layer]
                    |                                            |
      +-------------+-------------+                              |
      |                           |                              |
+-----+--------------+  +---------+------------+                 |
| c_core/ui_style.css|  |c_core/ui_components  |                 |
| - Design Tokens    |  | - App Shell          |                 |
| - Reset & Layout   |  | - Buttons & Inputs   |                 |
| - Base Typography  |  | - Cards & Modals     |                 |
+--------------------+  +----------------------+                 |
      |                           |                              |
      +-------------+-------------+                              |
                    |                                            |
                    +--------------------+                       |
                                         |                       |
                               +---------v-----------+   +-------v--------+
                               | Page-specific CSS   |   | c_core/ui.js   |
                               | (e.g., p_push.css)  |   | (Modals/Toast) |
                               +---------------------+   +-------+--------+
                                                                 |
                                                         +-------v--------+
                                                         | Page-specific  |
                                                         | JS (Logic)     |
                                                         +----------------+
```

### Core Architecture Principles
1. **Zero Domain Logic in UI Core:** Master UI CSS and JS must never know what TMDB, Drive IDs, torrent metadata, or audio channel layouts represent.
2. **Single Source of Layout Truth:** Shell layouts (desktop sidebar, mobile bottom navigation, workspace frame) exist exclusively in `c_core/ui_components.css`.
3. **Strict Separation of Concerns:**
   - Global primitives $\to$ `c_core/ui_style.css`
   - Common reusable UI patterns $\to$ `c_core/ui_components.css`
   - Common UI interactivity $\to$ `c_core/ui.js`
   - Feature-specific business rules $\to$ isolated page scripts/styles.

---

## 2. File Responsibilities

| File Path | Direct Responsibility | Strictly Forbidden |
| :--- | :--- | :--- |
| `c_core/ui_style.css` | CSS Custom Properties (tokens), CSS reset, base typography rules, root dark background styling, spacing primitives, native scrollbars, focus outlines, safe-area margins. | Component-specific rules, grid assemblies, fixed layouts, absolute overlays. |
| `c_core/ui_components.css` | Reusable structural components: App shell, sidebar, mobile navigation bar, studio cards, unified form controls, buttons, status badges, toasts, modal windows, tabular structures, and micro-loaders. | TMDB result formatting, release name parser cards, Drive folder tree rendering, audio channel pills. |
| `c_core/ui.js` | UI behavior engines: Toast dispatch and queueing, modal lifecycle management (`showModal`/`closeModal`), active navigation state resolution, loading scrim toggling, clipboard interactions. | API fetching (TMDB, GitHub, Google Drive), parsing filenames, regex routines, deduplication checking, JSON assembling. |

---

## 3. Design Tokens

All tokens are defined in `:root` inside `c_core/ui_style.css`.

### 3.1 Colors
```css
/* Surfaces & Backgrounds */
--bg-void: #07090e;              /* Root viewport deep black */
--bg-surface-base: #0c1017;      /* Base workspace container */
--bg-surface-elevated: #131923;  /* Studio cards, panels */
--bg-surface-overlay: #1a2332;   /* Modals, menus, dropdowns */
--bg-surface-highlight: #222d3d; /* Hovered item fills */

/* Borders & Separators */
--border-subtle: rgba(255, 255, 255, 0.06);
--border-default: rgba(255, 255, 255, 0.12);
--border-strong: rgba(255, 255, 255, 0.22);
--border-accent: rgba(0, 240, 255, 0.35);

/* Typography & Contrast */
--text-primary: #f0f4fc;
--text-secondary: #94a3b8;
--text-tertiary: #64748b;
--text-muted: #475569;
--text-inverse: #07090e;

/* Brand & Accents */
--accent-cyan: #00f0ff;          /* Primary interactive accent */
--accent-cyan-hover: #38f4ff;
--accent-cyan-glow: rgba(0, 240, 255, 0.2);

/* Status Accents */
--status-success: #10b981;       /* Neon Emerald (AUTO / Passed) */
--status-success-bg: rgba(16, 185, 129, 0.12);
--status-warning: #f59e0b;       /* Amber / Manual Override */
--status-warning-bg: rgba(245, 158, 11, 0.12);
--status-danger: #ef4444;        /* Crimson / Error */
--status-danger-bg: rgba(239, 68, 68, 0.12);
--status-info: #3b82f6;          /* Cobalt Blue / Information */
--status-info-bg: rgba(59, 130, 246, 0.12);
```

### 3.2 Typography & Fonts
```css
--font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;

/* Font Sizes */
--text-xs: 0.6875rem; /* 11px */
--text-sm: 0.8125rem; /* 13px */
--text-base: 0.9375rem; /* 15px */
--text-md: 1.0625rem; /* 17px */
--text-lg: 1.25rem;   /* 20px */
--text-xl: 1.5rem;    /* 24px */
--text-2xl: 1.875rem; /* 30px */

/* Font Weights */
--fw-regular: 400;
--fw-medium: 500;
--fw-semibold: 600;
--fw-bold: 700;
```

### 3.3 Spacing, Radii, Shadows, Transitions & Z-Index
```css
/* Spacing Scale */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */

/* Border Radii */
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 14px;
--radius-xl: 20px;
--radius-full: 9999px;

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);
--shadow-lg: 0 12px 28px rgba(0, 0, 0, 0.65);
--shadow-accent: 0 0 16px var(--accent-cyan-glow);

/* Transitions */
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-normal: 220ms cubic-bezier(0.4, 0, 0.2, 1);

/* Z-Index Hierarchy */
--z-base: 1;
--z-sticky: 100;
--z-navigation: 500;
--z-drawer: 800;
--z-modal-backdrop: 900;
--z-modal: 950;
--z-toast: 1000;
--z-tooltip: 1100;

/* Breakpoints (Reference for media queries) */
/* Mobile: < 768px */
/* Tablet: 768px - 1024px */
/* Desktop: > 1024px */
```

---

## 4. Component Inventory (40 Components)

| # | Component Name | CSS Class Naming | Primary Purpose | Scope |
|---|---|---|---|---|
| 1 | App Shell | `.mf-app-shell` | Root wrapper managing sidebar vs main viewport | Master UI |
| 2 | Desktop Sidebar | `.mf-sidebar` | Left navigation frame on desktop viewports | Master UI |
| 3 | Brand/Logo Area | `.mf-brand` | Logo icon, studio badge, version marker | Master UI |
| 4 | Sidebar Navigation | `.mf-nav-list`, `.mf-nav-item`, `.mf-nav-link` | Main routing list items | Master UI |
| 5 | Active Nav State | `.mf-nav-link--active` | Glowing cyan border/fill for active page | Master UI |
| 6 | Main Workspace | `.mf-workspace` | Primary scrollable canvas containing page content | Master UI |
| 7 | Workspace Header | `.mf-header` | Top bar with breadcrumb/title and contextual controls | Master UI |
| 8 | Page Title | `.mf-page-title` | High-contrast `<h1>` level display text | Master UI |
| 9 | Page Subtitle | `.mf-page-subtitle` | Secondary muted descriptive text | Master UI |
| 10 | Studio Card | `.mf-card`, `.mf-card--elevated` | Rounded content container with subtle borders | Master UI |
| 11 | Section Header | `.mf-section-header` | Card/block header with title and action container | Master UI |
| 12 | Form Group | `.mf-form-group` | Stacked container for label, input, and hint text | Master UI |
| 13 | Text Input | `.mf-input` | Unified dark text input with cyan focus ring | Master UI |
| 14 | Search Input | `.mf-input-search` | Input adorned with search icon and clear button | Master UI |
| 15 | Select Control | `.mf-select` | Custom styled select element with dropdown arrow | Master UI |
| 16 | Button Base | `.mf-btn` | Common interactive button base styles | Master UI |
| 17 | Primary Button | `.mf-btn--primary` | High-emphasis cyan fill button | Master UI |
| 18 | Secondary Button | `.mf-btn--secondary` | Neutral surface button with outline | Master UI |
| 19 | Danger Button | `.mf-btn--danger` | Destructive action button with crimson style | Master UI |
| 20 | Icon Button | `.mf-btn-icon` | Compact square/round button for icons only | Master UI |
| 21 | Status Badge | `.mf-badge` | Universal status pill | Master UI |
| 22 | AUTO Badge | `.mf-badge--auto` | Emerald green glowing automation indicator | Master UI |
| 23 | MANUAL Badge | `.mf-badge--manual` | Amber warning indicator for user overrides | Master UI |
| 24 | Provider Card | `.mf-provider-card` | Multi-field card container for stream sources | Master UI |
| 25 | Match Result Card | `.mf-match-card` | Card displaying parsed/matched entities | Master UI |
| 26 | Metadata Card | `.mf-meta-card` | Overview container for media poster/details | Master UI |
| 27 | Tech Info Card | `.mf-tech-card` | High-density grid container for mono specs | Master UI |
| 28 | Pipeline Indicator | `.mf-pipeline`, `.mf-pipeline__step` | Multi-step workflow progression tracker | Master UI |
| 29 | Progress Indicator | `.mf-progress`, `.mf-progress__bar` | Linear loading or transfer bar | Master UI |
| 30 | Loading State | `.mf-loading-state`, `.mf-spinner` | Scrim or card-level spinner overlay | Master UI |
| 31 | Empty State | `.mf-empty-state` | Placeholder with icon, title, and action for zero items | Master UI |
| 32 | Error State | `.mf-state--error` | Error visual alert container | Master UI |
| 33 | Success State | `.mf-state--success` | Success confirmation container | Master UI |
| 34 | Toast | `.mf-toast`, `.mf-toast-container` | Floating notification messages (top/bottom) | Master UI |
| 35 | Modal Window | `.mf-modal`, `.mf-modal__backdrop` | Accessible centered dialog overlay | Master UI |
| 36 | Confirmation Dialog| `.mf-dialog` | Pre-formatted modal for affirmative/negative decisions | Master UI |
| 37 | Table Base | `.mf-table` | Dark matrix table styling with bordered cells | Master UI |
| 38 | Responsive Table | `.mf-table-container--scroll` | Horizontally-scrollable table wrapper | Master UI |
| 39 | Grid System | `.mf-grid`, `.mf-grid-2`, `.mf-grid-3`, `.mf-grid-4` | 12-column and auto-fit responsive flex/grid helpers | Master UI |
| 40 | Mobile Bottom Nav | `.mf-bottom-nav`, `.mf-bottom-nav__item` | Fixed bottom bar on mobile with raised action button | Master UI |

---

## 5. Component States

Every interactive element in the Master UI must support standard state variants:

| State | Visual Behavior | Classes / Pseudo-classes |
|---|---|---|
| **Default** | Clear surface hierarchy, standard borders | `.mf-component` |
| **Hover** | Surface lighting increases (+8% brightness), subtle accent border tint | `.mf-component:hover` |
| **Focus-Visible**| Prominent $2\text{px}$ `--accent-cyan` ring with $2\text{px}$ offset | `.mf-component:focus-visible` |
| **Active / Pressed**| Inner depth shadow, slight transform `scale(0.98)` | `.mf-component:active` |
| **Disabled** | Opacity reduced to $0.4$, pointer events disabled, cursor set to `not-allowed` | `.mf-component[disabled]`, `.is-disabled` |
| **Loading** | Children hidden or dimmed, spinner visible, pointer events disabled | `.mf-component.is-loading` |
| **Selected** | Glowing border `--border-accent`, background highlight | `.is-selected`, `.aria-selected` |

---

## 6. Navigation System

### Desktop Sidebar Navigation
- Docked permanently to the left viewport on screens $> 1024\text{px}$.
- Fixed width: $260\text{px}$.
- Full viewport height (`100vh`) with internal vertical scroll if needed.
- Contains:
  1. Header with `MoinuFlix V2 Studio` branding.
  2. Main navigation links:
     - Push Studio (Movies)
     - Drive Sync
     - Media Library
     - 5.1 Songs Studio
     - Web Series Studio
  3. Footer item displaying engine status and version.

### Mobile Bottom Navigation
- Fixed to the viewport bottom on screens $< 768\text{px}$.
- Height: $64\text{px} + \text{env(safe-area-inset-bottom)}$.
- Display layout: Strict 5-slot flex distribution:
  1. **Home** (`d_sync` or general hub)
  2. **Search** (Library lookups)
  3. **Push** (Emphasized Center Button — elevated, cyan pill/circle, dedicated accent glow)
  4. **Library** (`m_view.html`)
  5. **Profile / Settings**
- *Rule:* Sub-studios (5.1 Songs, Web Series) are accessible from within the Studio Switcher or desktop sidebar; they do not crowd the 5 primary slots on mobile.

---

## 7. Responsive System

### Viewport Targets
- **Mobile:** $0\text{px} \dots 767\text{px}$
- **Tablet:** $768\text{px} \dots 1023\text{px}$
- **Desktop:** $\ge 1024\text{px}$

### Responsive Rules
1. **No Horizontal Overflow:** All viewports must strictly maintain `max-width: 100vw; overflow-x: hidden` at root.
2. **Layout Transition:**
   - Desktop: `.mf-app-shell` uses grid: `[sidebar: 260px] [workspace: 1fr]`.
   - Tablet: Collapsible icon-only sidebar ($72\text{px}$) or top workspace with bottom nav.
   - Mobile: Sidebar is hidden (`display: none`), workspace takes $100\text{vw}$, bottom nav appears (`display: flex`).
3. **Form Grid Behavior:** All multi-column grids (`.mf-grid-2`, `.mf-grid-3`, `.mf-grid-4`) automatically collapse to a single column (`grid-template-columns: 1fr`) at $< 768\text{px}$.
4. **Touch Target Size:** Interactive elements on touchscreens must maintain a minimum bounding box of $44 \times 44\text{px}$.
5. **Safe-Area Insets:** Navigation and container margins must respect `env(safe-area-inset-bottom)` and `env(safe-area-inset-top)` for modern mobile displays.

---

## 8. Accessibility Considerations

- **Color Contrast:** Base text-to-background contrast ratio must exceed $4.5:1$ (WCAG AA). Text using `--text-primary` on `--bg-surface-elevated` satisfies $> 7:1$.
- **Focus Rings:** Non-disruptive keyboard accessibility via `:focus-visible` displaying a distinct cyan ring. Never suppress outlines without focus replacements.
- **ARIA Attributes:** Modals use `role="dialog"` with `aria-modal="true"`. Toggles and buttons must specify `aria-expanded` and `aria-label` when using icon-only triggers.
- **Reduced Motion:** Honor `@media (prefers-reduced-motion: reduce)` by disabling non-essential transitions and animations.

---

## 9. Page Integration Model

Master UI is consumed by client pages as an unopinionated foundation:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MoinuFlix V2 Studio</title>

  <!-- 1. Master UI Base Foundation -->
  <link rel="stylesheet" href="c_core/ui_style.css">

  <!-- 2. Master UI Component System -->
  <link rel="stylesheet" href="c_core/ui_components.css">

  <!-- 3. Page-Specific Styling (Loaded AFTER Master UI) -->
  <link rel="stylesheet" href="p_push.css">
</head>
<body class="mf-body">
  <div class="mf-app-shell">
    <!-- Master UI Sidebar -->
    <aside class="mf-sidebar" id="mfSidebar">...</aside>

    <!-- Main Workspace -->
    <main class="mf-workspace">
      <!-- Page Content Goes Here -->
    </main>

    <!-- Master UI Mobile Navigation -->
    <nav class="mf-bottom-nav" id="mfBottomNav">...</nav>
  </div>

  <!-- Master UI Core Controller -->
  <script src="c_core/ui.js"></script>

  <!-- Page-Specific Business Controller -->
  <script src="p_push.js"></script>
</body>
</html>
```

---

## 10. CSS Responsibility Boundaries

- **Master UI CSS Owns:**
  - Standard spacing, layout grids, container dimensions.
  - Button shapes, colors, hover transitions, and active clicks.
  - Card shells, headers, body padding, and border radius.
  - Modal backdrops, positions, and standard dialog chrome.
  - Universal badges (AUTO, MANUAL, Success, Danger, Info).
- **Page-Specific CSS Owns:**
  - TMDB poster backdrop aspect ratios and overlay gradients.
  - Audio channel matrix displays (5.1, 7.1 speaker layouts).
  - Google Drive tree node depth indentation.
  - Custom file dropzone animation specific to raw release ingestion.

---

## 11. JavaScript Responsibility Boundaries (`c_core/ui.js`)

`c_core/ui.js` exposes a single global namespace: `window.MF_UI`.

### Allowed Functions
```javascript
window.MF_UI = {
  // Toast notifications
  toast: function(message, type = 'info', duration = 3500) {},

  // Global & container loading indicators
  showLoading: function(targetSelector = null, message = 'Loading...') {},
  hideLoading: function(targetSelector = null) {},

  // Modals
  openModal: function(modalId) {},
  closeModal: function(modalId) {},

  // Active Navigation Helper
  setActiveNav: function(pageKey) {},

  // Dialog helpers
  confirm: function({ title, message, confirmText, cancelText, onConfirm }) {}
};
```

### Strictly Forbidden in `ui.js`
- Filename parsing expressions.
- TMDB API network requests.
- Google Drive file queries.
- GitHub commit payloads or catalog compilation.
- Business rule validation (e.g. "is resolution 1080p?").

---

## 12. Migration Rules from V1

| V1 UI Feature | Decision | Detailed Reason |
|---|---|---|
| Inline CSS in `<head>` | **REPLACE** | Violates code deduplication; all shared styles move to `ui_style.css` and `ui_components.css`. |
| Hardcoded element-level styles (`style="..."`) | **REMOVE** | Replaced with semantic utility classes and tokens to ensure consistency. |
| Cyan / Neon Studio Dark Palette | **KEEP & IMPROVE** | Retained as the visual signature of MoinuFlix; standardized through CSS custom variables. |
| AUTO vs MANUAL pills | **KEEP & IMPROVE** | Crucial operational visual cue; promoted to standard Master UI component badges (`.mf-badge--auto`, `.mf-badge--manual`). |
| Desktop sidebar | **KEEP & IMPROVE** | Promoted from page-bound markup to reusable shell component with reliable active-state logic. |
| Mobile bottom navigation | **KEEP & IMPROVE** | Redesigned with proper safe-area support, touch targets, and a distinct center action button. |
| Inline `alert()` calls | **REPLACE** | Replaced by `MF_UI.toast()` and `MF_UI.confirm()` for non-blocking, modern user feedback. |
| Custom raw JSON preview card | **KEEP** | Abstracted so any studio page can use `.mf-card` and `.mf-tech-card` for debugging payloads. |

---

## 13. Testing Checklist

Before any phase based on Master UI is accepted, verify:
- [ ] **Desktop Grid:** Sidebar docks on the left, workspace scrolls independently without double scrollbars.
- [ ] **Mobile Responsive:** Sidebar hides on viewport widths $< 768\text{px}$, bottom nav docks to bottom.
- [ ] **Zero Horizontal Overflow:** Page never produces horizontal scrollbars at 320px, 375px, 768px, or 1440px.
- [ ] **Safe-Area Respect:** Mobile bottom navigation does not collide with home indicators on modern devices.
- [ ] **Toast System:** Multiple toasts stack neatly and auto-dismiss after their duration.
- [ ] **Modal Trapping:** Opening a modal locks root scroll and closes reliably on background click or `Escape` key.
- [ ] **Theme Uniformity:** Every card, button, and input strictly uses tokens from `ui_style.css`.

---

## 14. Master UI Freeze Criteria

The Master UI will be officially frozen once:
1. `c_core/ui_style.css`, `c_core/ui_components.css`, and `c_core/ui.js` are created and pass standalone visual testing.
2. An isolated test harness displays every component without broken styles or script errors.
3. Zero business logic exists in `c_core/`.
4. No horizontal overflow occurs across all viewports.
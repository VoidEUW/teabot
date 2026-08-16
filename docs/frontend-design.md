# TeaBot Frontend Design

Authoritative specification for the TeaBot web interface: design tokens, CSS
architecture, component inventory, the design harness, and the UI test strategy.

**Status:** Normative. Code that contradicts this document is wrong, not the
document. Changes go through a PR that edits this file in the same commit.

**Stack context:** Jinja2 templates + Alpine.js, served by FastAPI. No JS build
step, no CSS preprocessor, no utility framework. Everything below is plain CSS
custom properties and hand-written stylesheets.

---

## 1. Design intent

TeaBot is an administration surface for a Discord bot. The people using it are
server administrators making consequential changes — timeouts, message deletion,
emergency stops. The interface has one job: make the current configuration
legible and make changing it feel deliberate.

Three principles follow from that:

**Calm over dense.** A generous single column with clearly separated sections,
not a dashboard grid competing for attention. Density is not a virtue here;
there are maybe forty settings in the entire product.

**Warmth without softness.** The palette is cream and olive — natural, low
tension, easy on the eyes during long configuration sessions. But destructive
actions break the palette on purpose. Emergency Stop is red, not olive. The
visual system does not smooth over consequences.

**Structure carries meaning.** Section headers, icon tints, and card boundaries
encode which feature module you are inside. They are not decoration; the module
accent is the primary wayfinding cue once you are three levels deep.

### Signature element

The **module accent** system. Each feature module owns one of four sanctioned
hues, applied consistently to its icon tile, section header icons, and active
states. Navigating from the feature grid into a module carries the colour
forward, so the page you are on is identifiable at a glance without reading the
breadcrumb. This is the one place the design spends colour; everything else
stays quiet.

---

## 2. Token architecture

Three layers, strictly separated. This is the rule that makes dark mode
maintainable — get it wrong and every theme change becomes a hunt through
component files.

| Layer | Lives in | Example | May be used by |
|---|---|---|---|
| 1. Palette | `tokens.css` | `--olive-600: #587340` | Layer 2 only |
| 2. Semantic | `tokens.css` | `--color-accent` | Any stylesheet |
| 3. Component | the component's own file | `--card-padding` | That component only |

**Hard rules:**

- Components never reference layer 1. `color: var(--olive-600)` in `card.css` is
  a violation; `color: var(--color-accent-text)` is correct.
- Only layer 2 changes between themes. Layer 1 is theme-independent raw values.
- No raw hex in any file except `tokens.css`. No exceptions, including the
  terminal.
- No `rgba()` literals in components. If you need a translucent surface, add a
  semantic token for it.

### Theme switching

Theme is set by `data-theme` on `<html>`, with values `light` and `dark`.
`prefers-color-scheme` provides the initial default; an explicit user choice
persists and wins.

```html
<html lang="en" data-theme="light">
```

The attribute — not a media query alone — is required because the harness must
render both themes on one page and because a manual toggle is a stated feature.

A small inline script in `<head>` sets the attribute before first paint to avoid
a flash of the wrong theme. This is the only inline script permitted in the
application.

---

## 3. Palette (layer 1)

Raw values. Never referenced outside `tokens.css`.

### Neutrals — warm

```
--cream-50:   #FBF8F2    /* page background, light */
--cream-100:  #F5EFE4    /* sunken surfaces, section header bands */
--cream-200:  #EDE4D4
--tan-300:    #E4D9C6    /* borders, light */
--tan-400:    #D2C3AA
--bark-500:   #8A6A4F
--bark-600:   #6E5340
--bark-700:   #574030    /* muted text, light */
--bark-900:   #2B2520    /* body text, light */
--ink-950:    #191610    /* page background, dark */
--ink-900:    #221E17    /* surface, dark */
--ink-800:    #2B261D    /* raised surface, dark */
--ink-700:    #393227    /* borders, dark */
--ink-500:    #6B6153
--sand-300:   #A39684    /* muted text, dark */
--sand-100:   #F3EEE4    /* body text, dark */
--white:      #FFFFFF
```

### Olive — primary accent

```
--olive-50:   #F0F4E8
--olive-100:  #DFE8CE
--olive-200:  #C6D6AC
--olive-300:  #A8BE87    /* accent, dark theme */
--olive-400:  #8AA366
--olive-500:  #6E8C4E
--olive-600:  #587340    /* accent, light theme — fills */
--olive-700:  #445A31    /* accent text on cream, hover fills */
--olive-800:  #334420
```

### Module accent hues

Four sanctioned hues. A module picks exactly one. Adding a fifth requires an ADR.

```
/* Sage */
--sage-100:   #E3EEE6
--sage-500:   #5E8A6B
--sage-600:   #4A7057
--sage-300:   #92B79E    /* dark-theme variant */

/* Olive — reuses the primary ramp above */

/* Clay */
--clay-100:   #FAE9DC
--clay-500:   #B96C3E
--clay-600:   #9C5731
--clay-300:   #DDA179

/* Bark — reuses the bark ramp above, plus: */
--bark-100:   #F1E8DE
--bark-300:   #C0A489
```

### Status

Semantic meaning is fixed. These never serve as decoration.

```
--success-100: #E4EFE6   --success-500: #4A7C59   --success-300: #8FBB9C
--warning-100: #FAF0DA   --warning-500: #A9741C   --warning-300: #E0B565
--danger-100:  #FBE8E5   --danger-500:  #C0392B   --danger-300:  #E88B7F
--info-100:    #E6EFF4   --info-500:    #4A7290   --info-300:    #92B5CC
```

---

## 4. Semantic tokens (layer 2)

The complete contract available to stylesheets. Both themes define every token —
a token missing from one theme is a bug.

### Light

```css
:root, [data-theme="light"] {
  /* Surfaces */
  --color-bg:              var(--cream-50);
  --color-surface:         var(--white);
  --color-surface-sunken:  var(--cream-100);
  --color-surface-raised:  var(--white);
  --color-overlay:         rgb(43 37 32 / 0.45);

  /* Borders */
  --color-border:          var(--tan-300);
  --color-border-strong:   var(--tan-400);
  --color-border-subtle:   var(--cream-200);

  /* Text */
  --color-text:            var(--bark-900);
  --color-text-muted:      var(--bark-700);
  --color-text-faint:      var(--bark-500);
  --color-text-inverse:    var(--sand-100);

  /* Accent — split by role. This split is mandatory: one value cannot
     serve both as a fill behind white text and as text on cream. */
  --color-accent:          var(--olive-600);  /* fills, active toggles */
  --color-accent-hover:    var(--olive-700);
  --color-accent-text:     var(--olive-700);  /* links, icons on bg */
  --color-accent-subtle:   var(--olive-100);  /* icon tiles, soft bands */
  --color-accent-border:   var(--olive-200);
  --color-on-accent:       var(--white);      /* text on --color-accent */

  /* Status — each has fill, text-on-background, and subtle variants */
  --color-success:         var(--success-500);
  --color-success-subtle:  var(--success-100);
  --color-warning:         var(--warning-500);
  --color-warning-subtle:  var(--warning-100);
  --color-danger:          var(--danger-500);
  --color-danger-hover:    #A32E22;
  --color-danger-subtle:   var(--danger-100);
  --color-on-danger:       var(--white);
  --color-info:            var(--info-500);
  --color-info-subtle:     var(--info-100);

  /* Focus */
  --color-focus-ring:      var(--olive-500);

  /* Shadows */
  --shadow-sm:  0 1px 2px rgb(87 64 48 / 0.06);
  --shadow-md:  0 2px 8px rgb(87 64 48 / 0.08);
  --shadow-lg:  0 8px 24px rgb(87 64 48 / 0.12);

  /* Default module accent — overridden per module */
  --module-accent:         var(--color-accent);
  --module-accent-subtle:  var(--color-accent-subtle);
}
```

### Dark

Not an inversion. Backgrounds keep a warm brown cast rather than going neutral
grey, surfaces get *lighter* than the page background instead of relying on
shadow for elevation, and the accent moves up the ramp so it reads as
foreground.

```css
[data-theme="dark"] {
  --color-bg:              var(--ink-950);
  --color-surface:         var(--ink-900);
  --color-surface-sunken:  #14110C;
  --color-surface-raised:  var(--ink-800);
  --color-overlay:         rgb(10 8 6 / 0.65);

  --color-border:          var(--ink-700);
  --color-border-strong:   var(--ink-500);
  --color-border-subtle:   #2F2920;

  --color-text:            var(--sand-100);
  --color-text-muted:      var(--sand-300);
  --color-text-faint:      #7D7264;
  --color-text-inverse:    var(--bark-900);

  --color-accent:          var(--olive-300);
  --color-accent-hover:    var(--olive-200);
  --color-accent-text:     var(--olive-300);
  --color-accent-subtle:   #2F3A22;
  --color-accent-border:   #46552F;
  --color-on-accent:       var(--ink-950);   /* dark text on light fill */

  --color-success:         var(--success-300);
  --color-success-subtle:  #1E2E22;
  --color-warning:         var(--warning-300);
  --color-warning-subtle:  #33280F;
  --color-danger:          var(--danger-300);
  --color-danger-hover:    #F0A79C;
  --color-danger-subtle:   #3A1F1A;
  --color-on-danger:       var(--ink-950);
  --color-info:            var(--info-300);
  --color-info-subtle:     #1C2A33;

  --color-focus-ring:      var(--olive-300);

  --shadow-sm:  0 1px 2px rgb(0 0 0 / 0.35);
  --shadow-md:  0 2px 8px rgb(0 0 0 / 0.45);
  --shadow-lg:  0 8px 24px rgb(0 0 0 / 0.55);
}
```

> **Note on `--color-on-danger` in dark mode.** The danger fill flips to a light
> red with dark text, mirroring the accent. Do not keep a dark red fill with
> white text in dark mode — it disappears against the background.

### Contrast requirements

All pairs below must be verified in the harness contrast readout (§10.3), not
assumed. Values here are targets, not measurements.

| Pair | Minimum |
|---|---|
| `--color-text` on `--color-bg` / `--color-surface` | 7:1 (AAA body) |
| `--color-text-muted` on `--color-bg` / `--color-surface` | 4.5:1 |
| `--color-text-faint` on any surface | 4.5:1 (never used below 14px) |
| `--color-on-accent` on `--color-accent` | 4.5:1 |
| `--color-accent-text` on `--color-bg` / `--color-surface` | 4.5:1 |
| `--color-on-danger` on `--color-danger` | 4.5:1 |
| `--color-border` against adjacent surfaces | 3:1 where it carries meaning |
| Focus ring against adjacent surface | 3:1 |

If a token fails, the fix is the token — never a local override in a component.

---

## 5. Module accents

Each feature module sets two tokens on its page root. Nothing else.

```css
/* modules/blackout/static/blackout.css */
.module-blackout {
  --module-accent:        var(--clay-500);
  --module-accent-subtle: var(--clay-100);
}
[data-theme="dark"] .module-blackout {
  --module-accent:        var(--clay-300);
  --module-accent-subtle: #3A2418;
}
```

Applied to the page wrapper via a template variable:

```jinja
{% block body_class %}module-{{ module_slug }}{% endblock %}
```

**Assignment registry.** Kept here so two modules do not silently claim the same
hue. Update in the same PR that adds a module.

| Module | Hue |
|---|---|
| Roles | Sage |
| Tickets | Olive |
| Violations | Clay |
| Announcements | Bark |
| Events | Sage |
| Citations | Olive |
| Settings (framework) | Olive |

**Rules:**

- A module may only set `--module-accent` and `--module-accent-subtle`.
- Status colours are never overridden by a module accent. A destructive button
  inside the Sage module is still red.
- Where the module accent is used: the page-header icon, section-header icon
  tiles, the feature-grid card icon, and the left border of active nav items.
  Not on buttons, not on links, not on form controls.

---

## 6. Typography

| Role | Family | Fallback stack |
|---|---|---|
| Display — page titles, section headers, brand | **Outfit** | `system-ui, sans-serif` |
| Body — everything else | **Inter** | `system-ui, sans-serif` |
| Mono — terminal, IDs, snowflakes, code | **JetBrains Mono** | `ui-monospace, monospace` |

Self-hosted as WOFF2 under `static/fonts/`. No Google Fonts request — this is a
self-hosted deployment and must work without external network access.
`font-display: swap`, and the fallback stacks above are metric-adjusted where
possible to limit layout shift.

Load only the weights listed. Outfit 600/700, Inter 400/500/600, JetBrains Mono
400/500. Subset to Latin + Latin Extended.

### Scale

```css
--font-display: "Outfit", system-ui, sans-serif;
--font-body:    "Inter", system-ui, sans-serif;
--font-mono:    "JetBrains Mono", ui-monospace, monospace;

--text-2xs:  0.6875rem;  /* 11px — badge text only */
--text-xs:   0.75rem;    /* 12px — list group labels (USERS/ROLES), captions */
--text-sm:   0.8125rem;  /* 13px — help text, terminal */
--text-base: 0.9375rem;  /* 15px — body default */
--text-md:   1rem;       /* 16px — setting labels, card titles */
--text-lg:   1.125rem;   /* 18px — section headers */
--text-xl:   1.375rem;   /* 22px — card titles in feature grid */
--text-2xl:  2rem;       /* 32px — page title */

--leading-tight:  1.2;   /* display */
--leading-snug:   1.4;   /* headings, labels */
--leading-normal: 1.6;   /* body, help text */

--tracking-tight: -0.02em;  /* --text-2xl and above */
--tracking-wide:   0.06em;  /* uppercase group labels only */
```

**Rules:**

- Uppercase is reserved for list group labels (`USERS`, `ROLES`). It always
  pairs with `--text-xs`, `--tracking-wide`, weight 600, and
  `--color-text-muted`. Nowhere else.
- Body copy is never below `--text-sm`. Help text under form fields uses
  `--text-sm` with `--color-text-muted`.
- Display face on headings only. Never on body copy, never on buttons.
- Line length in the settings column is capped at ~72ch for prose blocks.

---

## 7. Space, shape, motion, layers

```css
/* Spacing — 4px base */
--space-1:  0.25rem;   --space-2:  0.5rem;    --space-3: 0.75rem;
--space-4:  1rem;      --space-5:  1.25rem;   --space-6: 1.5rem;
--space-8:  2rem;      --space-10: 2.5rem;    --space-12: 3rem;
--space-16: 4rem;      --space-20: 5rem;

/* Radius */
--radius-sm:   6px;    /* badges, inline chips */
--radius-md:  10px;    /* inputs, buttons */
--radius-lg:  14px;    /* cards, panels */
--radius-xl:  20px;    /* page-level containers, modals */
--radius-full: 9999px; /* pills, avatars, toggles */

/* Layout */
--container-narrow: 56rem;   /* 896px — settings pages, single column */
--container-wide:   72rem;   /* 1152px — feature grid, tables */
--container-gutter: var(--space-6);
--navbar-height:    4rem;

/* Motion */
--ease-out:   cubic-bezier(0.22, 1, 0.36, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--duration-fast: 120ms;   /* hover, focus */
--duration-base: 180ms;   /* toggles, disclosure */
--duration-slow: 260ms;   /* toasts, modals */

/* Z-index — the complete set. No arbitrary values anywhere. */
--z-base:     0;
--z-sticky:   100;   /* sticky save bar */
--z-dropdown: 200;
--z-overlay:  300;   /* modal backdrop */
--z-modal:    400;
--z-toast:    500;
--z-tooltip:  600;
```

### Breakpoints

Mobile-first. Media queries use `min-width` only.

```
sm:  30rem   (480px)   — stack form field pairs
md:  48rem   (768px)   — feature grid 2 columns, navbar full
lg:  64rem   (1024px)  — feature grid 3 columns
xl:  80rem   (1280px)  — max gutters
```

### Reduced motion

Global, in `base.css`. Not opt-in per component.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Motion never carries information on its own. If a toast animates in, it must
also be announced to assistive technology.

### Focus

One ring, everywhere, on `:focus-visible` only.

```css
:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

Removing the outline without an equivalent replacement is a hard violation.

---

## 8. Terminal palette

The SSE log terminal is a deliberate island. It does not inherit page surface or
text tokens, and it does not follow the light/dark theme — it is always dark,
the way a terminal is always dark. This is the one place where breaking the
system is correct: a log view that looks like the rest of the admin UI is harder
to scan.

Tokens live in `terminal.css`, scoped to `.terminal`, and are the only
component-local colour definitions permitted in the codebase.

```css
.terminal {
  --term-bg:        #13110D;
  --term-bg-alt:    #1A1712;   /* alternating row / hover */
  --term-fg:        #D6D0C4;
  --term-fg-dim:    #7E7668;   /* timestamps, logger names */
  --term-selection: #3A4A2A;
  --term-cursor:    #A8BE87;

  /* ANSI 16 — tuned warm to sit next to the app palette */
  --term-black:   #13110D;  --term-bright-black:   #4E483D;
  --term-red:     #D4685C;  --term-bright-red:     #EE8B7E;
  --term-green:   #8FB56B;  --term-bright-green:   #ACD189;
  --term-yellow:  #D6A648;  --term-bright-yellow:  #EFC470;
  --term-blue:    #6B96B8;  --term-bright-blue:    #8FB6D4;
  --term-magenta: #B084B8;  --term-bright-magenta: #CBA3D2;
  --term-cyan:    #6BAFA8;  --term-bright-cyan:    #8CCCC4;
  --term-white:   #D6D0C4;  --term-bright-white:   #F0EBE1;

  background: var(--term-bg);
  color: var(--term-fg);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.55;
}
```

### Log transport and level mapping

**The server sends structured JSON over SSE, not ANSI escape sequences.**

```json
{"ts": "2026-08-16T14:22:03.481Z", "level": "WARNING",
 "logger": "teabot.modules.violations.service",
 "msg": "Timeout applied to 4711 for 300s"}
```

Rationale: parsing ANSI in the browser means shipping and maintaining a parser
for a problem you can avoid. The client maps `level` to a CSS class; the colours
*look* like a terminal without any escape-code handling.

The server-side log handler must strip ANSI from upstream records — `uvicorn`
and several libraries emit coloured output by default — before serialising.

| Level | Class | Colour |
|---|---|---|
| DEBUG | `.log--debug` | `--term-bright-black` |
| INFO | `.log--info` | `--term-fg` |
| WARNING | `.log--warning` | `--term-yellow` |
| ERROR | `.log--error` | `--term-red` |
| CRITICAL | `.log--critical` | `--term-bright-red`, bold, `--term-bg-alt` row |

Line structure: dim timestamp, dim logger name (truncated from the left, full
value in `title`), level-coloured message. Long lines wrap with a hanging indent
rather than scrolling horizontally — `overflow-wrap: anywhere`.

The terminal must remain readable in forced-colors mode; do not rely on colour
alone to distinguish levels. The level is also rendered as text.

---

## 9. Icons

**Lucide, exclusively.** Mixing icon libraries produces visibly inconsistent
stroke weights and optical sizing. Material Symbols were considered and rejected
for this reason; the screenshots that inspired the design use Lucide-style
stroke icons, and Lucide's rounded caps already give the intended feel.

Delivery is an **SVG sprite**, not an icon font and not inline per-use SVG:

- No external network request at runtime.
- No FOUT / layout shift.
- One cacheable file.
- Only the icons actually used are included.

### Build

`scripts/build_icon_sprite.py` scans templates for `icon("name")` calls, pulls
those symbols from the vendored Lucide source, and emits
`static/icons/sprite.svg`. It runs in CI and fails the build if a template
references an icon that is not in the sprite. The generated sprite is committed
so runtime never depends on the script.

### Macro

```jinja
{% macro icon(name, size=20, class="") -%}
<svg class="icon {{ class }}" width="{{ size }}" height="{{ size }}"
     aria-hidden="true" focusable="false">
  <use href="{{ url_for('static', path='icons/sprite.svg') }}#{{ name }}"></use>
</svg>
{%- endmacro %}
```

```css
.icon {
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}
```

**Rules:**

- Icons inherit `currentColor`. Never set `stroke` on an icon directly.
- Sizes: 16 (inline with text), 20 (buttons, list rows), 24 (section headers),
  32 (feature card tiles). No other sizes.
- Every icon is `aria-hidden`. An icon-only control carries an `aria-label` on
  the control itself.
- An icon is never the sole indicator of state. Pair it with text.

---

## 10. CSS architecture

### File layout

```
src/teabot/web/static/css/
  tokens.css              layers 1 + 2, both themes
  base.css                reset, element defaults, typography,
                          focus ring, reduced motion, [x-cloak]
  layout.css              page shell, containers, grids, section headers
  components/
    button.css
    card.css
    form.css              inputs, labels, help text, errors, fieldsets
    toggle.css
    badge.css
    table.css
    modal.css
    toast.css
    empty-state.css
    breadcrumb.css
    tooltip.css
    avatar.css
  navbar.css
  terminal.css

src/teabot/modules/<name>/static/<name>.css   module-local only
```

### Load order

Normative — specificity depends on it.

```
tokens → base → layout → components/* → navbar → terminal → module
```

Module CSS loads last, via `{% block extra_css %}`. It may only set
`--module-accent*` and lay out module-specific structures. **A module stylesheet
that restyles a shared component is a violation of the vertical-slice rule** and
must be rejected in review — if a module needs a component variant, the variant
belongs in `components/`.

### Naming

BEM-light. Block, element, modifier; no deeper nesting.

```
.card               .card__header       .card--disabled
.setting-row        .setting-row__label .setting-row--danger
.btn                .btn__icon          .btn--primary  .btn--danger
```

Forced state classes exist for the harness and mirror real pseudo-states
one-to-one:

```
.is-hover  .is-focus  .is-active  .is-loading  .is-disabled  .is-error
```

Every component defines the pseudo-state and the forced class in a single
grouped selector, so they cannot drift:

```css
.btn:hover, .btn.is-hover { background: var(--color-accent-hover); }
```

### Prohibitions

- No `!important` outside the reduced-motion block.
- No element selectors in component files (`.card p` is out; use
  `.card__body`).
- No ID selectors for styling.
- No nesting deeper than two levels.
- No hard-coded colour, spacing, radius, or duration values. Every one is a
  token.
- No `localStorage` for anything other than the theme preference.

---

## 11. Component inventory

Derived from the reference screens. Each entry is a Jinja2 macro in
`templates/components/`, and each must appear in the harness.

### Chrome

| Component | Notes |
|---|---|
| **Navbar** | Brand (icon + wordmark), user chip (avatar + name), logout, theme toggle. Sticky, `--navbar-height`, bottom border. |
| **Breadcrumb** | `Servers › Guild › Feature`. Last item is current, non-link, `--color-text`. Truncates from the middle on narrow screens. |
| **Back link** | Arrow + label, `--color-info`. Duplicates the breadcrumb parent deliberately — it is the primary target on mobile. |
| **Page header** | Guild avatar, module icon, title (`--text-2xl`), subtitle, optional status badge and external-link badge. |
| **Footer** | Copyright line, `--color-text-faint`, `--text-sm`. |

### Structure

| Component | Notes |
|---|---|
| **Section header** | Icon tile (`--module-accent-subtle` circle, `--module-accent` icon, 24px), title `--text-lg`, description `--text-sm` muted. Not inside the card — sits above it. |
| **Panel** | Bordered container, `--color-surface`, `--radius-lg`, `--shadow-sm`. The default content wrapper. |
| **Feature card** | 32px icon tile, title `--text-xl`, description, action button. Variants: `--disabled` (dashed border, reduced opacity, "Coming Soon" button), `--danger`. |
| **Action card** | Icon, title, prose body, single action button. Used for Force Cache Reload, Emergency Stop. Variant `--danger` tints border and uses a red button. |
| **List group** | Uppercase label header (`USERS`, `ROLES`) + rows or empty state. |
| **Empty state** | Centred muted sentence. Copy states what is absent and what to do: "No administrators yet. Add a user or role to grant full access." Never a bare "Nothing here". |
| **Add row** | Full-width dashed button, plus icon + label. Inherits `--module-accent`. |

### Controls

| Component | Variants |
|---|---|
| **Button** | `--primary` (accent fill), `--secondary` (outline), `--ghost`, `--danger` (red fill). Sizes `sm`/`md`. States: default, hover, focus-visible, active, disabled, loading (spinner replaces leading icon, label persists, width locked). |
| **Toggle** | Off, on, disabled, `--danger` (Force Active Now — red track when on, red-tinted row). Always paired with a label and a description that states the *current* consequence, not the control's name. |
| **Setting row** | Label + help trigger + description + control, in a bordered row. Variants `--danger`, `--disabled`. Rows stack with `--space-3` gaps. |
| **Text / number input** | Label, optional help trigger, input, optional help text, optional error. States: default, focus, disabled, error, readonly. |
| **Textarea** | As above, plus a template-variable chip row beneath that inserts at cursor position. |
| **Chip** | Small pill button for variable insertion. `--radius-full`, `--text-xs`, mono. |
| **Help trigger** | Circle-question icon button opening a tooltip/popover. Keyboard reachable, `aria-describedby`. Never hover-only. |
| **Select** | Native `<select>`, restyled. No custom dropdown unless multi-select is genuinely required. |

### Feedback

| Component | Notes |
|---|---|
| **Badge** | `--success`, `--warning`, `--danger`, `--info`, `--neutral`. `--text-2xs`, `--radius-full`, dot optional. Text always present. |
| **Toast** | Bottom-right, `--radius-lg`, `--shadow-lg`, icon + message, auto-dismiss 4s, dismissible. `role="status"` for success, `role="alert"` for errors. Stacks vertically, max 3. |
| **Sticky save bar** | Appears on dirty form state at `--z-sticky`. Contains "Save changes" and "Discard". Does not obscure the last field — page gets matching bottom padding when visible. |
| **Modal** | Backdrop `--color-overlay`, panel `--radius-xl`, focus trap, Escape closes, focus restored to trigger on close. Destructive confirmations require typing the target name. |
| **Inline error** | Below the field, `--color-danger`, `--text-sm`, alert-circle icon, `aria-describedby` linked, field gets `aria-invalid`. |
| **Skeleton** | Muted block with a slow shimmer. Suppressed under reduced motion. |

### Specialised

| Component | Notes |
|---|---|
| **Terminal** | §8. Virtualised above 1000 lines, auto-scroll with pause-on-scroll-up, level filter, copy button, connection-state badge. |
| **Avatar** | `--radius-full`. Falls back to initials on a `--color-accent-subtle` background when the image fails. |
| **Table** | Used for violation history. Sticky header, zebra via `--color-surface-sunken`, horizontal scroll on small screens with the first column pinned. |

### Copy conventions

- Sentence case for all labels, buttons, and headings. No Title Case.
- Buttons name the action that occurs: "Save changes", "Reload caches", "Stop
  bot" — not "Submit", "OK", "Confirm".
- The verb stays constant through the flow: "Save changes" → toast "Changes
  saved".
- Toggle descriptions state the current effect: "The bot deletes non-Korean
  messages during Blackout Day." Not "Enable message deletion."
- Errors say what happened and what to do. They do not apologise and are never
  vague.
- Never expose implementation vocabulary. "Reload caches", not "flush the
  in-memory store".

---

## 12. Accessibility floor

Non-negotiable; verified automatically per §14.

- WCAG 2.2 AA on all contrast pairs. Body text targets AAA.
- Every interactive element reachable and operable by keyboard, in visual order.
- Visible focus on every focusable element. Focus never removed without an
  equivalent replacement.
- Touch targets ≥ 44×44 CSS px. Small visual controls (toggles, icon buttons)
  get padded hit areas.
- Every form control has a programmatically associated `<label>`. Placeholder is
  never a label.
- Errors are linked with `aria-describedby` and the field carries
  `aria-invalid="true"`.
- Live regions: toasts `role="status"` / `role="alert"`; the terminal is
  `aria-live="polite"` with `aria-atomic="false"`, and the live region is
  disabled while the user has scrolled up.
- Modals trap focus, close on Escape, and restore focus to the trigger.
- Colour is never the only carrier of meaning. Status badges include text.
- Page has one `<h1>`; heading levels do not skip.
- `prefers-reduced-motion` respected globally.
- Layout usable at 320px width and at 200% zoom without horizontal scroll.

---

## 13. Design harness

A development-only route that renders every component in every state on a single
page. It exists so a token change can be evaluated in one place instead of by
navigating the live application, and it doubles as the fixture surface for
visual regression tests (§14).

### Placement

```
src/teabot/web/design/
  router.py                 registered only when settings.dev_mode is true
  fixtures.py               fake guild, user, roles, channels, log lines,
                            form state, error state
  templates/design/
    base.html               harness shell: theme switch, section nav
    index.html
    tokens.html
    components.html
    patterns.html
    frames.html
```

It is **not** a feature module: no models, no database access, no service layer,
no `BotGateway` use. It reads nothing and writes nothing. All data comes from
`fixtures.py`.

`router.py` is included conditionally in the app factory. In production the
route does not exist — it returns 404, not 403, and the templates are not
reachable.

### The rule that makes it work

**The harness imports the production macros. It never duplicates markup.**

```jinja
{% from "components/button.html" import button %}
```

If a piece of UI is not a macro, it cannot appear in the harness — which forces
macro-first construction and prevents the harness from drifting away from the
real interface. A harness that copies markup is worse than no harness, because
it reports green while the application changes underneath it.

### Routes

| Route | Contents |
|---|---|
| `/design` | Index, links to sections, current theme state |
| `/design/tokens` | Colour swatches, type scale, spacing, radius, shadow, motion — all read from computed styles |
| `/design/components` | Every component × every state, light and dark side by side |
| `/design/patterns` | Full page compositions: feature grid, settings page, permissions page, terminal view |
| `/design/frames` | Pattern pages in iframes at 375 / 768 / 1280 simultaneously |

### Required capabilities

1. **State matrix.** Each component renders in default, hover, focus, active,
   disabled, loading, error, and empty — using the forced `.is-*` classes so all
   states are visible at once without interaction.

2. **Dual theme on one page.** Two panels side by side, `data-theme="light"` and
   `data-theme="dark"` on wrapper elements rather than on `<html>`. Catches
   dark-mode-only regressions that a global toggle hides. A global toggle also
   exists for realistic inspection.

3. **Live token readout.** The tokens page reads values via
   `getComputedStyle(document.documentElement)` rather than hard-coding hex
   strings in the template. Documentation that restates values inevitably drifts
   from the values.

4. **Contrast readout.** Each documented pair from §4 renders with its computed
   ratio and a pass/fail marker against its target. Failures are visually
   obvious.

5. **Content stress tests.** Fixtures deliberately include: a 64-character guild
   name, an unbroken 300-character log line, a missing avatar, zero / one / many
   list items, a setting description of three sentences, and a form with two
   simultaneous field errors.

6. **Viewport frames.** The `/design/frames` route renders pattern pages in
   fixed-width iframes so responsive breaks are visible without resizing the
   browser.

### Discipline

- A new component without a harness entry is incomplete. This is enforceable in
  review and stated in `web/AGENTS.md`.
- Harness pages contain no logic beyond rendering fixtures.
- Fixtures never import module models. Duplicating a small amount of shape data
  is correct here; coupling the harness to feature modules is not.

---

## 14. Testing

Four layers, deliberately unequal in size. Dependencies: `pytest`,
`pytest-playwright`, `selectolax`, `axe-core`.

**Playwright, not Cypress.** Playwright has official Python bindings, installs
via `uv add --dev pytest-playwright`, runs inside pytest next to every other
test, and keeps the CI image Python-only. Cypress would introduce Node, a
`package.json`, and a second toolchain into a repository that otherwise has no
JavaScript build step.

### Layer 1 — Route tests (many, fast)

`pytest` + `httpx.AsyncClient` against the ASGI app, parsing responses with
`selectolax`. No browser.

Covers: status codes, redirects, auth and permission gates (403 for a
non-administrator), presence of expected form fields and CSRF tokens, rendered
values matching service output, correct empty-state rendering, error markup on
invalid submissions.

This is the bulk of the suite. Milliseconds per test.

### Layer 2 — Interaction tests (few, targeted)

`pytest-playwright`, only where Alpine.js produces behaviour that HTML alone
cannot express.

Covers: toggle change enables the save bar; save produces a toast; Escape closes
a modal; focus returns to the trigger; the template-variable chip inserts at
cursor position; the terminal appends an SSE line; auto-scroll pauses when
scrolled up; the theme toggle persists across reload; keyboard-only traversal of
a settings page.

Target roughly 15–25 tests. This layer is expensive; keep it deliberate.

### Layer 3 — Visual regression (against the harness)

Playwright screenshots of `/design/components` and `/design/patterns`, per
section and per theme, compared to committed baselines.

**Baselines are generated and compared only inside a pinned container.** Font
rasterisation differs between a local machine and the Docker image on Tiger, and
locally-generated baselines will fail in CI for reasons unrelated to any change.

```
image:  mcr.microsoft.com/playwright/python:v1.xx-jammy   (exact tag pinned)
fonts:  baked into the image, not installed at test time
```

Tolerance is not zero — `max_diff_pixel_ratio=0.01` catches real regressions
while ignoring antialiasing noise. Animations are disabled for capture
(`animations="disabled"`). A `make snapshots` target regenerates baselines
inside the container; regenerating is a reviewable diff, not a routine step.

### Layer 4 — Accessibility

`axe-core` injected via Playwright, run against every harness section and every
pattern page, in both themes.

Fails the build on any violation at `serious` or `critical`. Contrast, missing
labels, invalid ARIA, and heading order are caught here rather than by
inspection. A rule may only be suppressed with an inline justification comment
and a linked issue.

### CI

`ci.yml` runs layer 1 on every push. Layers 2–4 run on pull requests and on
`main`, in the pinned Playwright container. A failing visual diff uploads the
actual, expected, and diff images as artefacts.

---

## 15. Hard rules

Restated for reference from `web/AGENTS.md`.

1. No raw colour, spacing, radius, or duration values outside `tokens.css`.
2. Components reference semantic tokens only, never palette tokens.
3. Module stylesheets set `--module-accent*` and module-specific layout only.
   Restyling a shared component from a module is a violation.
4. Every component is a Jinja2 macro under `templates/components/`.
5. Every component appears in the design harness before the PR is complete.
6. Both themes define every semantic token.
7. Focus is never removed without an equivalent visible replacement.
8. Colour is never the sole carrier of meaning.
9. Icons are Lucide, via the sprite macro. No second icon set. No inline SVG.
10. No `!important` outside the reduced-motion block.
11. The terminal is the only component permitted to define local colour values.
12. `localStorage` is used for the theme preference and nothing else.
13. The design harness never touches the database, the service layer, or
    `BotGateway`.
14. New tokens, new module accents, and new component variants are documented in
    this file in the same commit that introduces them.

---
name: Commercial Performance Intelligence Platform
description: Consulting-grade executive analytics for a B2B industrial distributor
colors:
  page-bg: "#161311"
  surface: "#201c19"
  surface-border: "#37312c"
  ink-primary: "#eae7e0"
  ink-secondary: "#948d84"
  ink-muted: "#6b655d"
  accent: "#c1725a"
  success: "#5a9c6e"
typography:
  eyebrow:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.7rem"
    fontWeight: 600
    letterSpacing: "0.14em"
    textTransform: "uppercase"
    color: "{colors.accent}"
  display:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "1.9rem"
    fontWeight: 600
    color: "{colors.ink-primary}"
  chart-title:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontStyle: "italic"
    fontSize: "0.95rem"
    color: "{colors.ink-primary}"
  label:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.7rem"
    letterSpacing: "0.06em"
    textTransform: "uppercase"
    color: "{colors.ink-secondary}"
  data:
    fontFamily: "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
    fontVariantNumeric: "tabular-nums"
    color: "{colors.ink-primary}"
components:
  kpi-tile:
    backgroundColor: "transparent"
    textColor: "{colors.ink-primary}"
    typography: "{typography.data}"
  kpi-delta-positive:
    textColor: "{colors.accent}"
    typography: "{typography.data}"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "4px"
    padding: "28px 32px"
---

## Overview

The Commercial Performance Intelligence Platform is a Streamlit + FastAPI executive analytics dashboard for a fictional B2B industrial distributor (Grainger/Fastenal-style). Its committed direction is **Consulting Deck / Financial Press** — the register real executives read (McKinsey/FT/Economist), rendered on a warm dark surface rather than the category's default white or the AI-generic near-black/neon look. This is an **Operate**-mode surface: expression never obscures the task, and color stays Restrained (neutrals + one accent).

## Colors

### Primary

- `page-bg` `#161311` — outer page canvas, slightly darker than panels so cards read as raised
- `surface` `#201c19` — panel/card background (warm espresso-charcoal, not blue-black or pure `#000`)
- `accent` `#c1725a` — terracotta/oxblood. Used only for: KPI deltas, chart bars/lines, the eyebrow label, and the italic chart-title rule. Never decorative, never background fill.

### Neutral

- `ink-primary` `#eae7e0` — headlines, KPI values, primary body text
- `ink-secondary` `#948d84` — labels, axis text, secondary figures
- `ink-muted` `#6b655d` — hairline borders, dividers, disabled states
- `success` `#5a9c6e` — reserved for a future explicit "good" status use (not currently used for ordinary positive deltas — those use `accent`, matching the comp)

### Named Rules

- The accent is a single hue used consistently for "this number/series matters" — never cycle multiple hues across a chart's bars/lines. A second series (if ever needed) uses `ink-secondary`, not a second saturated color.
- Dark mode here is a deliberate warm charcoal, not desaturated black. If implementing elsewhere, do not drift toward `#000`/`#0a0a0a` or a cool blue-black — that reads as the generic "AI dark mode."

## Typography

One sans for UI (`system-ui` stack — Operate mode doesn't need a display face for labels/data), one serif (`Georgia` stack) reserved *only* for headlines and italic chart titles — this pairing is what signals "report" rather than "app." All numeric data (KPI values, deltas, chart value labels) renders in the monospace stack with `tabular-nums`, never the sans.

### Hierarchy

1. Eyebrow (accent, uppercase, tracked) → 2. Serif display headline → 3. Sans labels (uppercase, secondary ink) → 4. Monospace data values (primary ink) → 5. Monospace deltas (accent)

## Layout

Sidebar (filters) + main content: eyebrow/headline pair, hairline-divided KPI row, then chart panels. One consistent card treatment (`surface` background, `surface-border` 1px border, 4px radius, no shadows, no glass/blur).

## Components

### Cards / Containers

Single panel style: `surface` background, `surface-border` hairline (1px), 4px radius. No drop shadows, no backdrop-filter/glass effects — flat and precise, like a printed report page, not a floating UI card.

### KPI Tiles

No boxed background (Streamlit's default `st.metric` card is overridden away). Label in `label` typography above a monospace value in `ink-primary`, with the delta below in monospace `accent` text — no colored arrow icons.

### Charts (Plotly)

Thin horizontal bars in `accent` on `surface` background (not white plot area). No gridlines — row separation via a hairline dotted rule (mirrors the comp's `line-row` treatment) rather than chart gridlines. Axis/tick text in `ink-secondary`. Direct value labels in monospace at the bar end rather than relying on a scale axis. Chart title in italic serif (`chart-title` typography), not Plotly's default bold sans title.

## Do's and Don'ts

### Do:

- Keep the accent to a single hue across the whole surface
- Use monospace exclusively for numeric/data values, everywhere
- Keep the dark surface warm (espresso-charcoal), bordered with hairlines, not shadows

### Don't:

- Introduce a second saturated accent color (no purple, no gradient)
- Use glass/blur, neon glow, or drop shadows — this is a flat, printed-report aesthetic
- Let the sans typeface carry a headline, or the serif carry a label/button

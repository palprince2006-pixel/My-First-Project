---
name: Student Result Analyzer
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#444651'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#00311f'
  on-tertiary: '#ffffff'
  tertiary-container: '#004a31'
  on-tertiary-container: '#27c38a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.005em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
  metric-stat:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  tabular-data:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  gutter-lg: 2rem
  margin: 1.5rem
  margin-mobile: 1rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system delivers an executive, institutional analytics experience engineered for university registrars, department deans, and academic researchers. The aesthetic balances collegiate authority with the velocity and clarity of modern enterprise software. 

The aesthetic is Modern Minimal with Analytical Precision. It relies on pristine, uncrowded canvases, razor-sharp tabular structures, and micro-metric clarity. The visual emotional tone communicates trust, impartiality, and zero-latency decision-making—shifting the user's perception from standard administrative reporting to proactive institutional intelligence.

## Colors

The palette is engineered to support dense statistical visualization and instant grade status comprehension without causing visual fatigue.

- **Primary Canvas & Backgrounds**: The foundational canvas uses crisp white (`#FFFFFF`) layered over soft slate canvas backdrops (`#F8FAFC`). Structural dividers, internal sub-panels, and elevated sheets employ slate-50 (`#F8FAFC`) to slate-100 (`#F1F5F9`).
- **Core Tones**: Deep Sapphire (`#1E3A8A`) commands interactive authority and active navigation states. Deep Slate (`#0F172A`) is reserved for primary metrics and high-contrast typography. Vibrant Cobalt (`#2563EB`) acts as the interactive accent for links, selected rows, focused states, and action states.
- **Academic Status Semantics**:
  - **Excellence / Pass**: Emerald (`#10B981`) paired with Emerald-50 (`#ECFDF5`) for high performance, percentiles >80%, and passing classifications.
  - **Warning / At-Risk**: Amber (`#F59E0B`) with Amber-50 (`#FFFBEB`) for borderline thresholds, academic probation alerts, and review tags.
  - **Deficiency / Failure**: Rose (`#EF4444`) with Rose-50 (`#FEF2F2`) for non-passing marks, administrative holds, and error flags.
- **Neutrals**: Slate-200 (`#E2E8F0`) establishes standard structural table grids and card borders, while Slate-500 (`#64748B`) and Slate-600 (`#475569`) serve secondary labels and tertiary metadata.

## Typography

The typographic system utilizes a dual-font structure: **Plus Jakarta Sans** provides structural elegance and punch for brand headers, page summaries, and quantitative metrics, while **Inter** delivers neutral, highly legible render fidelity for deep data matrices, table cells, and nested administrative forms.

All tabular data sets must enforce monospace numerical formatting (`font-feature-settings: "tnum" 1`) to ensure decimal numbers, grade-point averages, and student IDs align vertically along clean linear axes. Line heights in table rows are deliberately locked to tight standards to maximize vertical viewport capacity without sacrificing touch or pointer precision.

## Layout & Spacing

The layout model is anchored by a persistent collapsible vertical navigation rail (64px collapsed, 260px expanded) paired with an analytical main work canvas. Content sections use a 12-column responsive fluid grid designed specifically for data dashboarding.

- **Breakpoints & Layout Logic**:
  - **Desktop (≥1280px)**: 12-column fluid grid, 2rem gutter, 2.5rem canvas margins. Metric summary cards sit in 4-column groupings (`col-span-3`); master data tables stretch across full 12 columns.
  - **Tablet (768px - 1279px)**: 8-column reflow, 1.5rem gutter, 1.5rem margin. Metric cards drop to 2x2 grids (`col-span-4`); analytical charts stack into single-column views.
  - **Mobile (<768px)**: 4-column single flow, 1rem gutter, 1rem margin. Global sidebar converts into an off-canvas drawer. Tables unlock horizontal swipe behavior with locked primary columns (e.g., Student ID & Name).
- **Rhythm**: Internal card padding uses `space-lg` (24px) for analytical dashboards and `space-md` (16px) for compact data tables. Vertical layout separation between analytical tiers adheres to an exact 24px rhythm.

## Elevation & Depth

Visual hierarchy uses a refined hybrid of tonal separation and ambient diffusion rather than heavy physical drops. Cards and dashboards never look detached from the plane; they feel surfaced.

- **Layer 0 (Canvas Base)**: Flat `#F8FAFC`.
- **Layer 1 (Card & Module Surfaces)**: Pure `#FFFFFF` fill bounded by a continuous 1px hairline border of `#E2E8F0`. Depth is communicated using an ambient dual shadow:
  - `box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.03);`
- **Layer 2 (Hover States, Flyouts & Action Bars)**: Interactive cards elevate on pointer hover to:
  - `box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.06), 0 4px 6px -4px rgba(15, 23, 42, 0.02);`
  - Border transitions gently to `#CBD5E1`.
- **Layer 3 (Modals, Overlays, Command Palettes)**: High-level focus overlays use:
  - `box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);`
  - Backdrop is veiled with `rgba(15, 23, 42, 0.4)` coupled with a `4px` blur filter.

## Shapes

The design system standardizes on **Level 2 (Rounded)** with a purposeful expansion into `rounded-xl` for large-scale administrative surfaces.

- **Standard Cards & Containers**: Use `rounded-xl` (1rem / 16px) to soften the analytical rigidity of data tables and charts while maintaining contemporary software balance.
- **Controls & Data Inputs**: Use standard `rounded` (0.5rem / 8px) for buttons, form inputs, segmented control blocks, and dropdown menus.
- **Status Badges & Pill Indicators**: Use full continuous radii (`rounded-full` / 9999px) to distinctly contrast qualitative metadata chips from squared structural containers.

## Components

### Buttons
- **Primary**: Solid background `#1E3A8A`, text `#FFFFFF`, borderless, padding `8px 16px`, typography `label-md`. Subtle hover state shifts to `#172554` with a 1px vertical translation.
- **Secondary**: Surface `#FFFFFF`, border 1px `#E2E8F0`, text `#0F172A`. Hover shifts background to `#F8FAFC` and border to `#CBD5E1`.
- **Ghost/Tertiary**: No background, text `#475569`. Hover triggers `#F1F5F9`.

### Badges & Pill Chips
- **Academic Performance Tags**: Fully rounded (`rounded-full`), padding `2px 10px`, typography `label-sm`, uppercase tracking.
  - *Distinction/Pass*: Background `#ECFDF5`, text `#065F46`, border 1px `#A7F3D0`.
  - *At Risk/Probation*: Background `#FFFBEB`, text `#92400E`, border 1px `#FDE68A`.
  - *Remedial/Fail*: Background `#FEF2F2`, text `#991B1B`, border 1px `#FECACA`.

### Metric Summary Cards (KPIs)
- Encapsulated inside `rounded-xl` white containers with `#E2E8F0` borders. Top section features a micro-label (`label-sm` in Slate-500) and an optional trend indicator chip. Center features the massive statistic (`metric-stat` in Deep Slate). Bottom row features contextual benchmark text (e.g., "vs. Department Avg") in `body-sm`.

### Data-Dense Tables
- Structure uses full-width borders with horizontal separation only (`border-b border-slate-100`).
- **Header Cells (`th`)**: Background `#F8FAFC`, typography `label-sm`, text `#475569`, text-transform uppercase, padding `12px 16px`.
- **Row Cells (`td`)**: Typography `tabular-data`, color `#0F172A`, height `48px`, padding `8px 16px`. Active row hover changes background to `#F8FAFC`.
- **Pinned Columns**: Student ID and Name columns maintain subtle `#E2E8F0` right-hand border shadows when scrolling horizontally.

### Input Fields & Select Dropdowns
- Height `40px`, border 1px `#CBD5E1`, background `#FFFFFF`, text `#0F172A`, corner radius `8px`. Focused state applies outline ring `2px solid #2563EB` with an offset of `1px`.
- Placeholders style in `#94A3B8`.

### Navigation Sidebar
- Full-height `#0F172A` deep navy-slate background. Nav items feature `#94A3B8` typography with 8px radius. Active item triggers `#1E3A8A` surface fill with `#FFFFFF` text and a 3px accent bar in `#2563EB` on the leading edge.
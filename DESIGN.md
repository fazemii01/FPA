# Design System: FPA (Fingerprint Analysis App)
**Project ID:** fazemii01/FPA

This document serves as the design system and UI/UX source of truth for the FPA project. It is structured to help Google Stitch generate new pages and components that maintain a consistent, premium, and unified user experience across the mobile app and generated PDF reports.

---

## 1. Visual Theme & Atmosphere

The FPA application presents a **trustworthy, technical, and clean** aesthetic, balancing a professional diagnostic feel with high usability.
* **Mood:** Trustworthy, Analytical, Calm, and Precise.
* **Density:** Comfortable, balanced spacing with distinct visual groupings to present complex metric data without cognitive overload.
* **Philosophy:** Clean card-based layouts, soft backgrounds, and strong color-coded semantics to guide user actions and data interpretation.

---

## 2. Color Palette & Roles

The color palette is split into **Mobile Interface Color Tokens** and **PDF Report Output Tokens**. Both systems share identical semantic cues (green/orange/red) to convey recommendations and diagnostics consistently.

### Mobile App Color Tokens
* **Deep Muted Slate Blue (#1F4788):** Primary brand color, used for app bars, main action buttons, active tab indicators, and dominant theme highlights.
* **Bright Cyan (#00BCD4):** Secondary brand color, used for progress bars, secondary controls, and interactive elements.
* **Soft Warm Coral Red (#FF6B6B):** Accent color, used for important highlights, notifications, or call-to-actions.
* **Vibrant Leaf Green (#4CAF50):** Success indicator, used for successfully completed states (e.g. 10/10 scanned fingers, "Siap Kirim").
* **Bright Amber Gold (#FFC107):** Warning indicator, used for pending reviews or intermediate session states.
* **Bright Crimson Red (#F44336):** Error color, used for validation issues, failed processes, or delete actions.
* **Whisper-Soft Off-White (#FAFAFA):** Light mode scaffold background, providing a clean canvas.
* **Ink Dark (#121212):** Dark mode scaffold background.

### PDF Report Output Tokens
* **Deep Muted Navy (#1B365D):** Primary report header background, participant highlights, and primary metric labels.
* **Warm Tangerine Orange (#F15A24):** Accent headers, auditori-type indicators, and warning callout outlines.
* **Alabaster Grey (#F4F6F9):** Alternate row backgrounds, bento grid background boxes, and empty progress bar tracks.
* **Sunset Soft Peach (#FFF2ED):** Warning box background, challenges callout boxes, and attention blocks.
* **Forest Emerald Green (#2E7D32):** Indicates "Highly Recommended" (Sangat Direkomendasikan) items in tables (Extracurriculars 1-6, Careers 1-20).
* **Amber Orange (#EF6C00):** Indicates "Recommended" (Direkomendasikan) items in tables (Extracurriculars 7-11, Careers 21-40).
* **Crimson Red (#C62828):** Indicates "Sufficiently Recommended" (Cukup Direkomendasikan) items in tables (Extracurriculars 12-16, Careers 41-60).

---

## 3. Typography Rules

* **Font Families:** Modern, highly-legible sans-serif typography (e.g., `Inter` or `Roboto` for Mobile; clean system sans-serif for PDF print).
* **Weights:**
  - **Headers:** Bold (`font-weight: 700` or `800`) to create strong visual hierarchy.
  - **Primary Body:** Regular (`font-weight: 400`) for text readability.
  - **Subtitles/Labels:** Semi-bold (`font-weight: 600`) for navigation, form labels, and table headers.
* **Scale:**
  - Title/Hero: 20pt - 24pt
  - Section Header: 14pt - 16pt
  - Cards & List Tiles: 10pt - 12pt
  - Body Text & Footnotes: 7.5pt - 9pt

---

## 4. Component Stylings

### Buttons
* **Shape:** Pill-shaped or modern rounded rectangles with subtly rounded corners (`border-radius: 8px`).
* **Sizing:** Generous tap targets (minimum height `48px`) with adequate padding (`16px` vertical, `32px` horizontal).
* **Style:** Solid brand color fill (Deep Slate Blue) for primary actions; clean outlines or soft grey backgrounds for secondary actions.

### Cards/Containers
* **Corner Radius:** Softly curved corners (`border-radius: 12px` to `16px`).
* **Background:** Solid white (`#FFFFFF`) in light mode; dark slate in dark mode.
* **Elevation & Shadow:** Whisper-soft, highly diffused drop shadows (`elevation: 1` or `box-shadow: 0 4px 12px rgba(0,0,0,0.03)`) to indicate depth without adding visual noise.

### Inputs & Forms
* **Stroke Style:** Thin outline (`1px` width) in soft grey (`#E0E0E0`) when idle; switches to a thicker brand highlight (`2px` Deep Slate Blue) on focus.
* **Background:** Filled with plain white (`#FFFFFF`) for crisp contrast.
* **Padding:** Comfortable interior text boundaries (`12pt` vertical, `16pt` horizontal).

---

## 5. Layout Principles

* **Grid System:** Consistent padding block of `16px` across screens to keep layouts aligned and clean.
* **Vertical Rhythm:** Section margins use a standard double unit (`32px` or `24px` spacing) to separate major blocks of information, while sub-items are spaced with micro-units (`8px` or `12px`).
* **Data Presentation:** Metric lists (like VAK gaya belajar, quotients, or adaptability) use horizontal bar graphs with a colored active progress bar alongside an explicit-width light grey background track, ensuring the layout remains robust across viewport sizes and rendering engine limitations.

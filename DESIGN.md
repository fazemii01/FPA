# Design System: Allia FPA Ecosystem (Dashboard & Mobile App)
**Project ID:** fazemii01/FPA

This document serves as the unified design system and visual specification for the **Allia FPA** ecosystem. It covers the **Admin & Super Admin Web Dashboard** (`dashboard/`), the **Mobile Flutter Application** (`mobile/`), and the **Diagnostic PDF Report Engine** (`backend/`), structured for Google Stitch to generate consistent, production-aligned screens and components.

---

# Part 1: Allia FPA Web Dashboard Design System

## 1. Visual Theme & Atmosphere (Dashboard)

The Allia FPA Dashboard delivers a **modern enterprise SaaS command center** aesthetic, built for biometric identity diagnostics, institution hierarchy governance, credit quota distribution, and financial transaction auditing.

* **Aesthetic Mood:** Analytical, Precise, Professional, High-Tech, and Trustworthy.
* **Dual Display Themes:**
  * **Light Mode (Default Operational Canvas):** Clean, crisp, high-contrast interface with soft slate backgrounds (`#FAFAFA` / `#F8FAFC`), pure white container surfaces (`#FFFFFF`), and vibrant gradient metric cards.
  * **Dark Mode & Auth Portal (Security Command Aesthetic):** Obsidian midnight background (`#0A0A0A` / `#121212`) enhanced with frosted glassmorphism (`backdrop-blur-xl`, `bg-white/[0.02]`, `border-white/10`), dual ambient lighting glow halos (`bg-primary/10` and `bg-blue-600/10` with `120px` Gaussian blur), and live telemetry monitoring badges.
* **Visual Density:** Comfortable, spatially structured hierarchy. Large data-dense tables are paired with micro-badges and quick action popovers to minimize cognitive fatigue during prolonged administrative sessions.
* **Layout Structure:** Fixed-width collapsible sidebar navigation (`256px`), sticky glass topbar with institutional breadcrumbs and search, and a responsive fluid content canvas constrained up to `1520px` (`max-w-[95rem]`).

---

## 2. Color Palette & Roles (Dashboard)

### Primary Brand & Accent Colors
* **Electric Royal Blue (`#006FEE` / `#0361FC`):**
  * *Role:* Primary brand highlight, primary action buttons, active navigation item indicators, focused input borders, and primary gradient hero cards.
* **Deep Indigo-Purple (`#7828C8` / `#9353D3`):**
  * *Role:* Secondary brand tone, total users stat gradient, partner institution category chips, and user profile avatar badges.
* **Vibrant Emerald Green (`#17C964` / `#2E7D32`):**
  * *Role:* Success indicators, "Lunas" invoice badges, active status dot indicators, total credit balance stat card gradient, and positive telemetry heartbeats.
* **Warm Amber Gold (`#F5A524` / `#EF6C00`):**
  * *Role:* Pending actions, "Menunggu Verifikasi" / "Waiting for Review" badges, warning callouts, and reports generated stat card gradient.
* **Crimson Coral Red (`#F31260` / `#E11D48`):**
  * *Role:* Danger states, delete confirmation buttons, "Belum Dibayar" invoice tags, low quota warnings (`< 10 credits`), and regional reseller credit balance gradient.

### Background, Neutral & Structural Colors
* **Obsidian Midnight (`#0A0A0A`):** Dark mode login portal background and dark theme scaffold base.
* **Pure Light Canvas (`#FAFAFA` / `#F8FAFC`):** Main application layout background in light mode.
* **Surface Card White (`#FFFFFF`):** High-contrast background for content cards, data tables, modals, and printable invoice documents.
* **Subtle Slate Grey (`#F4F4F5` / `#E4E4E7`):** Table header fill, disabled backgrounds, and subtle dividers (`border-divider`).
* **Text Dark Charcoal (`#11181C` / `#1E293B`):** Primary headings, main table cell values, and bold text.
* **Text Muted Slate (`#71717A` / `#64748B`):** Subtitles, helper text, empty states, and metadata labels.

### Stat Card Gradients
* **Reseller Pool Card:** `linear-gradient(to bottom right, #F31260, #E11D48)` (Danger Red)
* **Total Lembaga Card:** `linear-gradient(to bottom right, #006FEE, #0284C7)` (Primary Blue)
* **Total Users Card:** `linear-gradient(to bottom right, #7828C8, #9353D3)` (Secondary Violet)
* **Total Credit Pool Card:** `linear-gradient(to bottom right, #17C964, #16A34A)` (Success Green)
* **Reports Generated Card:** `linear-gradient(to bottom right, #F5A524, #D97706)` (Warning Amber)

---

## 3. Typography Rules (Dashboard)

* **Font Families:**
  * **Primary Interface Font:** `Inter` (applied via `font-sans antialiased` across all dashboard routes).
  * **Public Invoice & Print Pages:** `Plus Jakarta Sans` (`font-['Plus_Jakarta_Sans',sans-serif]`) for refined commercial invoice typography.
  * **Data & Technical Identifiers:** `Fira Code` / Monospace (`font-mono`) for invoice UUIDs, reference codes, currency tables, and permission keys.

* **Type Hierarchy & Scale:**
  * **Hero Metric Numbers:** `30px` - `36px` (`text-3xl font-bold`), high visual prominence inside stat cards.
  * **Page Titles:** `24px` (`text-2xl font-bold text-default-900 tracking-tight`).
  * **Section Headers:** `18px` (`text-lg font-bold text-default-900`).
  * **Modal & Card Titles:** `16px` - `18px` (`font-bold text-default-800`).
  * **Standard Body & Cell Text:** `14px` (`text-sm font-normal text-default-700`).
  * **Subtitles & Secondary Descriptions:** `13px` - `14px` (`text-sm text-default-500`).
  * **Table Column Headers:** `11px` - `12px` (`text-[10px]` to `text-xs font-bold uppercase tracking-widest text-default-400 / text-slate-400`).
  * **Micro Badges & Telemetry Labels:** `10px` (`text-[10px] font-bold uppercase tracking-wider`).

---

## 4. Component Stylings (Dashboard)

### Navigation Sidebar (`SidebarWrapper`)
* **Dimensions & Position:** Fixed-width `256px` (`w-64`), sticky left column (`h-screen sticky top-0`), right-bordered (`border-r border-divider`).
* **Header Area:** Centered logo (`w-36 max-h-16 object-contain`), bold project title "Allia" (`text-xl font-extrabold`), and uppercase tracking label "FINGERPRINT FPA" (`text-[10px] text-default-500 font-bold uppercase tracking-widest`).
* **Menu Navigation Items (`SidebarItem`):**
  * Generously proportioned interactive pills (`min-h-[44px] px-3.5 rounded-xl`).
  * Inactive state: `text-default-900 hover:bg-default-100 transition-all active:scale-[0.98]`.
  * Active state: Solid subtle brand tint `bg-primary-100` with `fill-primary-500` icon coloring.
* **Footer Quick-Dock:** Centered horizontal icon dock with tooltips for Settings (`SettingsIcon`), Adjustments (`FilterIcon`), and User Avatar with dropdown trigger.

### Header Topbar (`NavbarWrapper`)
* **Styling:** Sticky top navbar with bottom border (`isBordered w-full`), background blur support.
* **Institution Context Badge:** Dedicated vertical lockup (`border-r border-divider pr-4`) displaying the logged-in administrator's active institution (`text-sm font-bold text-default-800`).
* **Global Search Bar:** Full-width pill input with embedded magnifying glass icon (`startContent={<SearchIcon />} isClearable`).
* **Right Controls:** Notification dropdown trigger and User Profile dropdown with integrated dark/light theme switch.

### Stat Metric Cards (`Stats Cards Grid`)
* **Shape & Elevation:** Smoothly rounded rectangle (`rounded-2xl` / `rounded-3xl`) with rich drop shadow (`shadow-lg`).
* **Padding:** Generous interior padding `24px` (`p-6`).
* **Interior Layout:** Vertical flex stack:
  1. Upper label (`text-sm font-medium opacity-80`)
  2. Giant metric counter (`text-3xl font-bold`)
  3. Descriptive context sub-label (`text-xs opacity-60`)

### Data Tables (`NextUI Table`)
* **Container:** Wrapped in clean card container (`bg-default-50 shadow-md rounded-2xl`) or frameless bordered view.
* **Header Row:** Crisp uppercase typography with letter spacing (`text-[10px] font-bold uppercase tracking-widest text-slate-400`).
* **Status Badges (`Chip`):**
  * `success`: Flat/Dot badge for "Aktif", "Lunas", "REPORT GENERATED".
  * `warning`: Flat badge for "Menunggu Verifikasi", "WAITING FOR REVIEW", "Admin Pusat".
  * `danger`: Flat/Dot badge for "Non-aktif", "Belum Dibayar", "REJECTED", Low Credits (`< 10`).
  * `secondary`: Flat badge for "Super Admin", "Partner", "Credits Top-Up".
* **Action Row Controls:** Compact action button pairs (`size="sm" variant="flat"` in `primary`, `secondary`, or `danger`).

### Forms, Inputs & Selects
* **Text & Number Inputs:** Bordered variant (`variant="bordered"`), rounded corners (`rounded-xl`), clean `1.5px` border with smooth focus ring transition (`focus-within:!border-primary`).
* **Switches (`Switch`):** NextUI modern toggle pills for boolean settings (Institution active toggle, Partner mode toggle, Delay rilis toggle).
* **Dropdown Selects:** Native styled select containers with subtle border (`border-2 border-default-200 rounded-xl bg-transparent px-3 py-2.5 text-sm outline-none focus:border-primary`).

### Modals & Dialogs
* **Backdrop:** Smooth diffused black overlay (`bg-black/50 backdrop-blur-sm`).
* **Dialog Container:** Deep rounded cards (`rounded-2xl` to `rounded-3xl` with NextUI `ModalContent`).
* **Header & Footer:** Clear header title with divider spacing; footer features flat cancel action and solid primary confirmation action.

### Public Invoice Document Layout (`/invoice/[uuid]`)
* **Canvas:** Printable paper layout (`bg-slate-50 min-h-screen py-12 px-4`).
* **Document Container:** High-fidelity white invoice card (`max-w-4xl bg-white rounded-3xl border border-slate-200 shadow-sm p-8 sm:p-12`).
* **Branding Header:** Deep blue badge (`#0361FC`, `h-16 w-16 rounded-2xl`) with bold "ALLIA FPA" branding, institution metadata, and uppercase watermark "TAGIHAN".
* **Interactive Proof Upload:** Dashed drag-and-drop file upload zone with instant file name indicator and action buttons.

### Auth & Login Portal (`/login`)
* **Background:** Deep midnight `#0A0A0A` with floating dual ambient color orbs (`bg-primary/10` and `bg-blue-600/10` with `120px` Gaussian blur).
* **Form Container:** Frosted glass card (`w-full max-w-[420px] p-8 rounded-3xl bg-white/[0.02] border border-white/10 shadow-2xl backdrop-blur-xl`).
* **Telemetry Live Sidebar:** Dual metric widgets (Engine API: 98% Optimal, Clarity Rate: 92% Ready, Database Sync: Pulsing green live indicator).

---

## 5. Layout Principles & Grid System (Dashboard)

* **Screen Margin & Constraints:**
  * Root dashboard container: `max-w-[90rem]` to `max-w-[95rem]` with auto horizontal margins (`mx-auto`).
  * Horizontal screen padding: `px-4 lg:px-6`.
  * Vertical page rhythm: `py-6` or `my-10` with `gap-4` to `gap-6` between major section blocks.
* **Grid Hierarchy:**
  * **Top Metrics Grid:** Responsive multi-column layout (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`, adapting to `lg:grid-cols-5` when regional reseller quota is present).
  * **Dashboard 2-Column Split:** Main column `2/3` width (`lg:col-span-2`) for recent scanning sessions table; side column `1/3` width (`lg:col-span-1`) for credit allocation rankings.
* **Responsive Breakpoints:**
  * Mobile (`< 768px`): Sidebar collapses into off-canvas drawer with backdrop overlay; hamburger toggle activates.
  * Desktop (`>= 768px`): Sidebar becomes static persistent left pillar; navbar expands to full width with search bar and institution indicators.

---

# Part 2: Mobile App & Diagnostic Report Tokens

## 1. Mobile Interface Color Tokens
* **Deep Muted Slate Blue (`#1F4788`):** Primary mobile brand color for app bars, main action buttons, and active tab indicators.
* **Bright Cyan (`#00BCD4`):** Secondary progress bars and interactive elements.
* **Soft Warm Coral Red (`#FF6B6B`):** Accent highlights, notifications, or call-to-actions.
* **Vibrant Leaf Green (`#4CAF50`):** Success indicator (e.g. 10/10 scanned fingers, "Siap Kirim").
* **Bright Amber Gold (`#FFC107`):** Pending review indicator or intermediate session states.
* **Bright Crimson Red (`#F44336`):** Error color for validation issues or failed processes.
* **Whisper-Soft Off-White (`#FAFAFA`):** Light mode scaffold background.
* **Ink Dark (`#121212`):** Dark mode scaffold background.

## 2. PDF Report Output Tokens
* **Deep Muted Navy (`#1B365D`):** Primary report header background and primary metric labels.
* **Warm Tangerine Orange (`#F15A24`):** Accent headers and warning callout outlines.
* **Alabaster Grey (`#F4F6F9`):** Alternate row backgrounds and empty progress tracks.
* **Sunset Soft Peach (`#FFF2ED`):** Warning callout background boxes.
* **Forest Emerald Green (`#2E7D32`):** "Highly Recommended" rating indicator.
* **Amber Orange (`#EF6C00`):** "Recommended" rating indicator.
* **Crimson Red (`#C62828`):** "Sufficiently Recommended" rating indicator.

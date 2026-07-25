# CHITTI V2 — PRESENTATION STUDIO DESIGN SYSTEM

## 1. Overview
The Presentation Studio Design System establishes canonical guidelines, color tokens, typography scales, grid layouts, component naming conventions, responsive rules, and accessibility standards for all CHITTI Presentation Experiences (Productivity, Navigation, Browser, Vision, OCR, Calendar, Reminders).

---

## 2. Color System & Design Tokens
All themes (`dark.css`, `light.css`, `glass.css`, `executive.css`, `corporate.css`, `terminal.css`, `accessibility.css`) map to standardized CSS custom variables:

```css
:root {
  /* Brand Tokens */
  --vizzu-primary: #6366f1;
  --vizzu-primary-hover: #4f46e5;
  --vizzu-secondary: #06b6d4;
  --vizzu-accent: #f43f5e;
  
  /* Neutral Tokens */
  --vizzu-bg: #0f172a;
  --vizzu-surface: #1e293b;
  --vizzu-surface-border: #334155;
  --vizzu-text-primary: #f8fafc;
  --vizzu-text-secondary: #94a3b8;
  --vizzu-text-muted: #64748b;
  
  /* Status Tokens */
  --vizzu-success: #10b981;
  --vizzu-warning: #f59e0b;
  --vizzu-error: #ef4444;
  --vizzu-info: #3b82f6;

  /* Typography Tokens */
  --vizzu-font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --vizzu-font-mono: 'JetBrains Mono', monospace;

  /* Elevation Tokens */
  --vizzu-radius: 12px;
  --vizzu-shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}
```

---

## 3. Typography Scale
- **Display / Hero:** `2.5rem` (`40px`), Weight: 800, Line Height: `1.2`
- **Heading 1 (`h1`):** `1.875rem` (`30px`), Weight: 700, Line Height: `1.3`
- **Heading 2 (`h2`):** `1.5rem` (`24px`), Weight: 600, Line Height: `1.35`
- **Heading 3 (`h3`):** `1.25rem` (`20px`), Weight: 600, Line Height: `1.4`
- **Body Regular:** `1rem` (`16px`), Weight: 400, Line Height: `1.5`
- **Caption / Label:** `0.875rem` (`14px`), Weight: 500, Line Height: `1.4`
- **Code / Monospace:** `0.875rem` (`14px`), Font: `var(--vizzu-font-mono)`

---

## 4. Spacing & Grid System
- **Spacing Units:** 4px (0.25rem), 8px (0.5rem), 12px (0.75rem), 16px (1rem), 24px (1.5rem), 32px (2rem), 48px (3rem).
- **Layout Grid:** 12-column responsive CSS Grid system with 24px gutters.
- **Breakpoints:**
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px

---

## 5. Component Naming & Architecture
- All reusable components reside in `desktop/presentation/studio/assets/shared/components/`.
- Each component consists of:
  - `ComponentName.tsx` (React + TypeScript)
  - `ComponentName.module.css` (CSS Module)
  - `ComponentName.README.md` (Component documentation)

---

## 6. Accessibility & WCAG Standards
- High contrast ratio ($\ge 4.5:1$ for normal text, $\ge 3:1$ for large text).
- Full keyboard navigation focus rings (`outline: 2px solid var(--vizzu-primary)`).
- Dedicated high-contrast theme (`accessibility.css`) for vision-impaired users.
- `aria-label` and `role` attributes on interactive components.

---

## 7. Presentation Platform Boundary
- **Presentation Studio Isolation:** Presentation Studio SHALL NEVER contain Character assets (avatar models, avatar profiles, voice profiles, lip sync definitions, personality models, or emotion mappings).
- **Character Studio Ownership:** All character assets and behavioral definitions belong exclusively to Character Studio (`desktop/character/studio/`).
- **Decoupled Communication:** Presentation Studio communicates with the Character Platform exclusively through decoupled EventBus runtime events. Presentation Runtime SHALL NEVER directly invoke avatar animation or voice synthesis engines.


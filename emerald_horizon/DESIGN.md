# Design System Specification: The Precision Ecosystem

## 1. Overview & Creative North Star
This design system is built to transform complex agricultural data into a high-end editorial experience. We are moving away from the "SaaS Dashboard" look and toward a concept we call **"The Synthetic Greenhouse."** 

The Creative North Star for this system is **Luminous Vitality.** 

The goal is to blend the raw, organic unpredictability of nature with the sharp, clinical precision of AI. We achieve this through intentional asymmetry, overlapping glass surfaces, and a typography scale that favors dramatic contrast. This system rejects the rigid, boxy grid in favor of breathing room and tonal depth, making the user feel like they are "looking through a lens" at their fields rather than just staring at a database.

---

## 2. Colors & Surface Logic
The palette is rooted in the deep darkness of soil (`surface`) and the vibrant life of a healthy crop (`primary`).

### The "No-Line" Rule
To achieve a premium, custom feel, **1px solid borders are strictly prohibited for sectioning.** We define boundaries through tonal shifts. If you need to separate a sidebar from a main view, do not draw a line; instead, transition from `surface-container-low` to `surface`.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. We use the `surface-container` tokens to "nest" depth:
- **Base Layer:** `surface` (#0b1326) — The deep background.
- **Sectioning Layer:** `surface-container-low` — For large content areas.
- **Interactive Layer:** `surface-container-high` — For cards and primary modules.
- **Prominent Layer:** `surface-container-highest` — For active states or pop-overs.

### The "Glass & Gradient" Rule
Floating elements (modals, dropdowns, floating action buttons) must utilize **Glassmorphism**. Use a semi-transparent `surface-variant` with a 20px to 40px backdrop blur. 
To add "soul" to the UI, main CTAs and hero data points should utilize a subtle linear gradient transitioning from `primary` (#4edea3) to `primary-container` (#10b981) at a 135-degree angle.

---

## 3. Typography: Editorial Precision
The typography system uses a high-contrast pairing to create an authoritative, tech-forward voice.

*   **Headers (Plus Jakarta Sans):** These are our "hero" elements. Use `display-lg` and `headline-lg` with tight letter-spacing (-0.02em) to create a bold, geometric presence. This represents the AI's "voice"—structured and modern.
*   **Body & Data (Inter):** For technical agricultural data (yield numbers, GPS coordinates, sensor logs), Inter provides maximum legibility. 
*   **Editorial Scaling:** Don't be afraid of the "Empty Space" principle. A single `display-sm` headline on a large `surface-container` card is more powerful than a crowded grid of small text.

---

## 4. Elevation & Depth
We eschew traditional "drop shadows" in favor of **Tonal Layering**.

### The Layering Principle
Depth is achieved by "stacking." A `surface-container-lowest` card placed on a `surface-container-low` section creates a natural, soft recession. 

### Ambient Shadows
When a floating effect is mandatory (e.g., a floating AI insight card), use a shadow with a 40px–60px blur at 6% opacity. The shadow color must be a tinted version of `on-surface` (#dae2fd) rather than pure black. This creates a "glow" effect rather than a "weight" effect.

### The "Ghost Border" Fallback
If accessibility requires a container edge, use the **Ghost Border**: the `outline-variant` token at 15% opacity. It should be felt, not seen.

---

## 5. Components

### Buttons
- **Primary:** Gradient-filled (`primary` to `primary-container`). No border. `md` roundedness (0.75rem).
- **Secondary:** `surface-container-highest` background with `on-surface` text. This makes the button feel like it's carved out of the UI.
- **Tertiary:** Ghost style. No background, `primary` text.

### Glassmorphic Cards
Cards should not have a solid background. Use a 60% opaque `surface-container` with a backdrop blur. Forbid dividers within cards; use `body-lg` vs `body-sm` hierarchy and vertical white space from the 8px spacing scale to separate content.

### Agricultural Insights (Specific Component)
- **Sensor Nodes:** Small, `md` roundedness chips using `secondary-container` for the background and `on-secondary-container` for text.
- **Trend Charts:** High-quality line charts. Use `primary` for positive trends and `tertiary` (Amber) for warnings. The area under the line should be a soft gradient fading into the card background.

### Input Fields
Avoid the "boxed" look. Use a `surface-container-highest` background with a `sm` roundedness. The focus state should not be a thick border, but a subtle "glow" using a 1px `primary` Ghost Border at 40% opacity.

---

## 6. Do’s and Don’ts

### Do:
- **Use Intentional Asymmetry:** If you have a 3-column layout, try making one column 50% width and the others 25% to create a custom, editorial feel.
- **Embrace Dark Mode:** This is a dark-first system. Use `surface-bright` only for very specific high-attention callouts.
- **Micro-animations:** Data points should "count up" on load, and glass cards should have a subtle 2px vertical float animation when hovered.

### Don't:
- **Don't use Divider Lines:** Never use a 1px line to separate list items. Use a 4px or 8px gap or a subtle shift in the background `surface` tier.
- **Don't use Pure White:** Use `on-surface` (#dae2fd) for text. Pure white (#FFFFFF) is too harsh for our deep slate environment and breaks the "organic" feel.
- **Don't over-round:** Keep to the `md` (0.75rem) or `lg` (1rem) roundedness for cards. Avoid "pill" shapes unless they are small action chips.
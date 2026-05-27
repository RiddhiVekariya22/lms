---
name: Technical Academic
colors:
  surface: '#fbf9f9'
  surface-dim: '#dbdad9'
  surface-bright: '#fbf9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f3'
  surface-container: '#efeded'
  surface-container-high: '#e9e8e7'
  surface-container-highest: '#e3e2e2'
  on-surface: '#1b1c1c'
  on-surface-variant: '#5b403a'
  inverse-surface: '#303031'
  inverse-on-surface: '#f2f0f0'
  outline: '#8f7068'
  outline-variant: '#e4beb5'
  surface-tint: '#b32b00'
  primary: '#b32b00'
  on-primary: '#ffffff'
  primary-container: '#ff5a2e'
  on-primary-container: '#571000'
  inverse-primary: '#ffb4a1'
  secondary: '#5f5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e5e2e1'
  on-secondary-container: '#656464'
  tertiary: '#5d5f5d'
  on-tertiary: '#ffffff'
  tertiary-container: '#919291'
  on-tertiary-container: '#292b2a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbd2'
  primary-fixed-dim: '#ffb4a1'
  on-primary-fixed: '#3c0800'
  on-primary-fixed-variant: '#891e00'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c9c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#e2e3e1'
  tertiary-fixed-dim: '#c6c7c5'
  on-tertiary-fixed: '#1a1c1b'
  on-tertiary-fixed-variant: '#454746'
  background: '#fbf9f9'
  on-background: '#1b1c1c'
  surface-variant: '#e3e2e2'
  ink: '#0a0a0a'
  paper: '#fafaf8'
  accent-orange: '#ff5a2e'
  accent-blue: '#2e6bff'
  accent-green: '#00b075'
  accent-purple: '#7a5af8'
  accent-pink: '#ff1a75'
  border-subtle: '#e5e5e0'
  glass-surface: rgba(250, 249, 248, 0.85)
typography:
  display-h1:
    fontFamily: Space Grotesk
    fontSize: 96px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-h1-mobile:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  heading-h2:
    fontFamily: Space Grotesk
    fontSize: 64px
    fontWeight: '700'
    lineHeight: '1.1'
  heading-h2-mobile:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.1'
  hero-body:
    fontFamily: Space Grotesk
    fontSize: 17px
    fontWeight: '400'
    lineHeight: '1.6'
  body:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  ui-large:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.5'
  ui-button:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.0'
  terminal:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.8'
  ui-small:
    fontFamily: Space Grotesk
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.0'
  label-badge:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: '1.3'
  eyebrow:
    fontFamily: Space Grotesk
    fontSize: 11px
    fontWeight: '600'
    lineHeight: '1.0'
    letterSpacing: 0.14em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gap-compact: 16px
  gap-regular: 24px
  gap-comfy: 36px
  section-padding-desktop: 80px
  section-padding-mobile: 60px
  container-max-width: 1280px
---

## Brand & Style

This design system embodies a **Technical Academic** personality, specifically engineered for high-end educational environments centered on artificial intelligence and development. It targets an audience of engineers, researchers, and technical practitioners who value precision, clarity, and a "builder" aesthetic.

The visual style is a sophisticated blend of **Minimalist Neo-Brutalism** and **Modern Engineering**. It prioritizes high-contrast "Ink and Paper" surfaces, utilizing a rigorous 1.5px border weight to evoke the feel of blueprints and terminal interfaces. The emotional response is one of intellectual rigor, transparency, and modern authority. The interface avoids artificial depth, opting for flat surfaces, intentional whitespace, and subtle glassmorphism for functional overlays.

## Colors

The palette is rooted in the **Ink and Paper** philosophy, ensuring maximum legibility and a classic document feel. 

- **Ink (`#0a0a0a`)**: Used for all primary text, heavy borders, and structural icons.
- **Paper (`#fafaf8`)**: The primary canvas, providing a soft, warm-neutral background that reduces eye strain compared to pure white.
- **Accent Orange (`#ff5a2e`)**: The default brand signal, used for critical actions, terminal prompts, and active states. 

The system supports a dynamic accent toggle (Blue, Green, Purple, Pink) to allow for personalization while maintaining the core structural contrast. For dark mode, the roles of Ink and Paper are inverted, with muted colors shifting to higher lightness (`#a0a0a0`) to maintain accessible contrast ratios.

## Typography

The typographic system utilizes a dual-font approach to balance editorial impact with technical utility. 

**Space Grotesk** is the workhorse, used for all headlines and UI elements to provide a modern, geometric feel with quirky, readable details. **JetBrains Mono** is reserved for metadata, terminal outputs, and badges to reinforce the developer-centric nature of the platform.

Key scaling logic:
- **Headlines**: Use `clamp` functions for fluid scaling.
- **Eyebrows**: Always uppercase with high letter-spacing for section categorization.
- **Terminal Text**: Increased line-height (1.8) to ensure readability in code-dense blocks.

## Layout & Spacing

The design system employs a **Fluid Grid** model centered around a dynamic `--gap` token. This token controls the density of the entire interface, allowing the UI to shift between `compact`, `regular`, and `comfy` modes.

- **Grid**: A 12-column system is used within a maximum container width of 1280px.
- **Margins**: Horizontal page margins are tied to the current `--gap` value.
- **Vertical Rhythm**: Section spacing is generous (80px desktop / 60px mobile) to maintain clear separation between different curriculum modules or content blocks.
- **Reflow**: On mobile, multi-column layouts stack vertically, and horizontal padding reduces to the `compact` gap setting (16px).

## Elevation & Depth

Hierarchy is established primarily through **Tonal Layers** and **Strong Outlines** rather than traditional shadows. 

1.  **Flat Base**: Most cards and containers sit flush on the `paper` background with a 1.5px `ink` border.
2.  **Glassmorphism**: The Navigation Bar and floating Tweak Panels use a 16px to 24px backdrop blur with a semi-transparent `paper` fill. This creates a sense of "overlay" without breaking the minimalist aesthetic.
3.  **Subtle Depth**: Low-opacity ambient shadows (`rgba(0,0,0,0.1)`) are used sparingly on floating elements like the Nav Bar or active modals to provide a slight lift from the content below.
4.  **Interaction**: Interactive depth is signaled via "Magnetic" movement (elements following the cursor) rather than Z-axis elevation changes.

## Shapes

The shape language is "Soft" yet structured. The default border radius is 8px, which provides a professional, modern look that isn't overly organic or playful.

- **Containers (Cards, Terminal)**: 8px radius.
- **Floating Panels**: 12px radius for a softer, more approachable feel.
- **Interactive Triggers (Chips, Badges)**: 20px (fully rounded/pill-shaped) to differentiate them from structural content.
- **System Controls**: 6px for smaller UI components like navigation buttons.
- **Identity Elements**: Circular shapes (50%) are reserved for active status dots and the cursor blob.

## Components

### Buttons
- **Primary Action**: Solid `accent` background with `paper` text. Magnetic hover effect.
- **Secondary Action**: `ink` border (1.5px), transparent background, `ink` text.
- **Nav Buttons**: 6px radius, `ui-small` typography, high-contrast hover state.

### Terminal & Code Blocks
- **Styling**: `paper` background, 1.5px `ink` border, 8px radius.
- **Content**: `terminal` typography. Includes a blinking cursor element using the `accent` color.

### Chips & Badges
- **Styling**: Pill-shaped (20px radius), 1px border.
- **Typography**: `label-badge` (JetBrains Mono).
- **Usage**: Used for status indicators and technology tags.

### Input Fields & Selectors
- **Segmented Picker**: `ink` track with a `white` thumb for contrast. 
- **Forms**: Minimalist approach with 1px bottom borders for inputs, shifting to 1.5px `accent` on focus.

### Cards
- **Structure**: 8px radius, 1.5px `border-subtle` or `ink` border.
- **Content**: Clear hierarchy starting with an `eyebrow` label, followed by a `heading-h2` and `body` text.

### Navigation Bar
- **Styling**: Fixed position, `glass-surface` background, 16px backdrop blur. 
- **Layout**: Centered within the viewport with `ui-small` links and prominent CTA.
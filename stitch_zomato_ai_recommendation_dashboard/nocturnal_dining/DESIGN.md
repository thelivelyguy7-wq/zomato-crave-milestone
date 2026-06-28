---
name: Nocturnal Dining
colors:
  surface: '#121317'
  surface-dim: '#121317'
  surface-bright: '#38393d'
  surface-container-lowest: '#0d0e12'
  surface-container-low: '#1a1b1f'
  surface-container: '#1e1f23'
  surface-container-high: '#292a2e'
  surface-container-highest: '#343539'
  on-surface: '#e3e2e7'
  on-surface-variant: '#e4bdbb'
  inverse-surface: '#e3e2e7'
  inverse-on-surface: '#2f3034'
  outline: '#ab8886'
  outline-variant: '#5b403e'
  surface-tint: '#ffb3af'
  primary: '#ffb3af'
  on-primary: '#68000d'
  primary-container: '#cb202d'
  on-primary-container: '#ffe2e0'
  inverse-primary: '#bc1124'
  secondary: '#c6c6c7'
  on-secondary: '#2f3131'
  secondary-container: '#454747'
  on-secondary-container: '#b4b5b5'
  tertiary: '#80d0f8'
  on-tertiary: '#003548'
  tertiary-container: '#007195'
  on-tertiary-container: '#d0edff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad7'
  primary-fixed-dim: '#ffb3af'
  on-primary-fixed: '#410005'
  on-primary-fixed-variant: '#930017'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#c1e8ff'
  tertiary-fixed-dim: '#80d0f8'
  on-tertiary-fixed: '#001e2b'
  on-tertiary-fixed-variant: '#004d66'
  background: '#121317'
  on-background: '#e3e2e7'
  surface-variant: '#343539'
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Sora
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 80px
  margin-mobile: 20px
---

## Brand & Style
The design system focuses on a premium, high-fidelity experience tailored for late-night discovery and refined culinary exploration. The personality is sophisticated, tech-forward, and immersive, utilizing a **Glassmorphic** approach to create depth within a deep-space environment. 

The aesthetic prioritizes clarity and appetite appeal through high-contrast accents and expansive white space (or "dark space"). The interface should feel like a high-end digital concierge—unobtrusive yet authoritative. 

**Key Principles:**
- **Lustrous Depth:** Using semi-transparent layers and background blurs to simulate physical glass.
- **Precision:** Sharp, purposeful movements and micro-interactions that mirror the precision of high-end cooking.
- **Vibrancy:** Using the primary red sparingly but with high impact to draw the eye to core actions and "crave-worthy" content.

## Colors
This design system utilizes a high-contrast dark palette to make food photography and map elements "pop" against the UI.

- **Background:** `#0A0A0A` serves as the base layer for all views.
- **Primary (Zomato Red):** `#CB202D` is reserved for primary buttons, active states, and critical brand moments. It represents energy and appetite.
- **Glass Surfaces:** Surfaces are constructed using `#FFFFFF` at 5% to 10% opacity with a background blur, allowing the underlying content to bleed through subtly.
- **Success/Warning:** Use standard semantic greens and ambers, but desaturate them slightly (approx 10%) to maintain the dark mode harmony.

## Typography
The system pairs **Sora** for headlines to provide a modern, geometric, and distinctively "tech" feel, with **Inter** for body text to ensure maximum legibility at smaller sizes.

- **Headlines:** Use Sora Bold/SemiBold for all restaurant names and section headers.
- **Body:** Use Inter for descriptions, reviews, and UI labels.
- **Tracking:** Headlines use tighter tracking (`-0.01em` to `-0.02em`) to feel more compact and premium. Labels use slightly wider tracking to increase readability against dark backgrounds.

## Layout & Spacing
The layout follows a **Fluid Grid** model with generous outer margins to emphasize the premium nature of the content.

- **Desktop:** 12-column grid. 80px side margins. Elements typically span 3, 4, 6, or 12 columns.
- **Mobile:** 4-column grid. 20px side margins. 
- **Rhythm:** All spacing must be a multiple of 8px. Use 24px (md) for standard component spacing and 64px (xl) for section vertical separation.
- **Alignment:** Content should feel spacious; avoid crowding restaurant cards. Use "Airy" padding within cards to allow the glass effect to be visible.

## Elevation & Depth
Depth is not communicated through shadows, but through **Tonal Layers** and **Backdrop Blurs**.

1.  **Level 0 (Base):** Deep black (`#0A0A0A`).
2.  **Level 1 (Cards/Surface):** Semi-transparent white overlay (`rgba(255, 255, 255, 0.05)`) with a `blur(20px)` filter.
3.  **Level 2 (Modals/Overlays):** Slightly brighter overlay (`rgba(255, 255, 255, 0.08)`) with a `blur(40px)` filter and a 1px solid border (`rgba(255, 255, 255, 0.1)`).

**Outlines:** Avoid heavy shadows. Instead, use thin, 1px "inner glows" or borders with low opacity to define the edges of glass containers.

## Shapes
The shape language is consistently **Rounded**. This softens the high-contrast "tech" aesthetic and makes the app feel more approachable and appetizing.

- **Standard Elements:** 8px (0.5rem) for buttons and input fields.
- **Large Elements:** 16px (1rem) for restaurant cards and main containers.
- **Hero Elements:** 24px (1.5rem) for main promotional banners or featured restaurant images.

## Components
- **Buttons:** 
  - **Primary:** Solid `#CB202D` background with White text. No border.
  - **Secondary:** Glass background (`rgba(255,255,255,0.1)`) with a 1px white border at 20% opacity.
- **Cards:** 
  - Featured restaurant cards should be wide (span 6 or 12 columns).
  - Background: Glassmorphic blur.
  - Border: 1px solid `#FFFFFF` at 10% opacity.
  - Image: 16:9 aspect ratio with a subtle vignette to ensure text overlay readability.
- **Inputs:** 
  - High-contrast: Deep black background with a 1px border that brightens to `#CB202D` on focus.
- **Chips:** 
  - Small, pill-shaped tags for cuisine types (e.g., "Italian", "Steakhouse").
  - Subtle dark grey background with high-legibility Inter SemiBold text.
- **AI Recommendation Engine:**
  - Use a subtle animated gradient border (shifting between Red and a soft Violet) to indicate "AI-powered" sections or suggestions.
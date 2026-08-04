---
name: Kinetic Horizon
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#434655'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#9d4300'
  on-secondary: '#ffffff'
  secondary-container: '#fd761a'
  on-secondary-container: '#5c2400'
  tertiary: '#006058'
  on-tertiary: '#ffffff'
  tertiary-container: '#007b71'
  on-tertiary-container: '#b3fff3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#ffdbca'
  secondary-fixed-dim: '#ffb690'
  on-secondary-fixed: '#341100'
  on-secondary-fixed-variant: '#783200'
  tertiary-fixed: '#89f5e7'
  tertiary-fixed-dim: '#6bd8cb'
  on-tertiary-fixed: '#00201d'
  on-tertiary-fixed-variant: '#005049'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Manrope
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
  gutter: 24px
  margin: 32px
  container-max: 1280px
---

## Brand & Style
The design system is built for a premium travel directory that balances high-energy exploration with professional reliability. The aesthetic is **Modern Corporate with a Kinetic Edge**, utilizing expansive whitespace and high-contrast accents to evoke a sense of movement. 

The target audience consists of discerning travelers and industry professionals who value efficiency and inspiration. The UI relies on clean, structured layouts with subtle glassmorphism to add depth without sacrificing the speed and clarity required of a high-end SaaS platform.

## Colors
The palette is centered around "Electric Indigo" (#2563EB), a primary hue representing the boundless sky and deep oceans, signaling trust and movement. This is paired with "Sunset Orange" (#F97316) for high-impact calls to action and "Bright Teal" (#0D9488) for success states and supplementary navigation cues.

- **Primary:** Use for main navigation, primary buttons, and active states.
- **Secondary:** Reserved for highlighting unique travel opportunities, badges, and "Book Now" actions.
- **Neutral:** A deep slate blue (#0F172A) is used for typography and structural borders to maintain a professional, high-end directory feel, avoiding pure blacks to keep the interface feeling airy.

## Typography
This design system utilizes a dual-font strategy. **Plus Jakarta Sans** provides a friendly yet geometric energy for headlines, reinforcing the "exploration" narrative with its soft curves and modern apertures. **Manrope** is used for body and functional text to ensure maximum legibility and a professional, tech-forward tone. 

Headlines should use tight tracking to emphasize the bold, "kinetic" nature of the brand. Labels are always set in uppercase with increased letter spacing to provide a distinct hierarchy in data-heavy directory views.

## Layout & Spacing
The design system employs a **12-column fluid grid** for desktop, collapsing to a 4-column layout for mobile. Spacing follows a strict 8px linear scale to ensure mathematical harmony across all components.

- **Desktop:** 32px outer margins with 24px gutters to allow the UI to breathe.
- **Mobile:** 16px outer margins with 16px gutters.
- **Vertical Rhythm:** Use 48px or 64px sections to separate major content blocks, maintaining a spacious, premium feel that avoids the "clutter" common in travel booking sites.

## Elevation & Depth
Depth is achieved through **Tonal Layers** and **Soft Ambient Shadows**. 
1. **Surface:** The base layer is a light off-white (#F8FAFC).
2. **Cards:** Use a pure white background with a very soft, diffused shadow (15% opacity of the primary color) to suggest they are floating.
3. **Glassmorphism:** Navigation bars and modal overlays use a 20px backdrop blur with a 70% white tint to maintain context of the underlying travel imagery.
4. **Interactive States:** Elements should lift slightly on hover (increased shadow spread) to provide tactile feedback.

## Shapes
A **Rounded (0.5rem)** logic is applied to the majority of components. This balance provides enough softness to feel approachable and modern without losing the professional structure required for a directory. 
- Large containers and featured images use `rounded-xl` (1.5rem).
- Input fields and standard buttons use `rounded-md` (0.5rem).
- Search bars and tags use `rounded-full` to emphasize the "capsule" or "token" nature of travel metadata.

## Components
- **Buttons:** Primary buttons use a solid Electric Indigo fill with white text. Secondary "Action" buttons use Sunset Orange to draw immediate attention.
- **Cards:** Travel listing cards must feature a high-aspect-ratio image with a subtle 1px inner border in a light neutral tint to define edges against white backgrounds.
- **Input Fields:** Search inputs should be oversized with a persistent "Location" icon to ground the user's intent.
- **Chips/Badges:** Use semi-transparent backgrounds of the primary or secondary colors (10% opacity) with high-contrast text for categories like "Trending" or "Verified."
- **Progressive Disclosure:** Use accordions and tabs to hide technical details, keeping the initial "Discovery" phase of the directory uncluttered.
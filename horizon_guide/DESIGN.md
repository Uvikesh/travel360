---
name: Horizon Guide
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#424752'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#727784'
  outline-variant: '#c2c6d4'
  surface-tint: '#115cb9'
  primary: '#003f87'
  on-primary: '#ffffff'
  primary-container: '#0056b3'
  on-primary-container: '#bbd0ff'
  inverse-primary: '#acc7ff'
  secondary: '#006e25'
  on-secondary: '#ffffff'
  secondary-container: '#80f98b'
  on-secondary-container: '#007327'
  tertiary: '#004954'
  on-tertiary: '#ffffff'
  tertiary-container: '#006270'
  on-tertiary-container: '#6ddff7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#acc7ff'
  on-primary-fixed: '#001a40'
  on-primary-fixed-variant: '#004491'
  secondary-fixed: '#83fc8e'
  secondary-fixed-dim: '#66df75'
  on-secondary-fixed: '#002106'
  on-secondary-fixed-variant: '#00531a'
  tertiary-fixed: '#a4eeff'
  tertiary-fixed-dim: '#62d6ed'
  on-tertiary-fixed: '#001f25'
  on-tertiary-fixed-variant: '#004e5a'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
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
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  max-width: 1280px
---

## Brand & Style

The brand personality is professional, reliable, and optimistic. It positions itself as a premium gateway to global expertise, targeting both leisure travelers and corporate clients who value curated experiences over mass-market bookings. 

The design style is **Corporate Modern** with a focus on high-clarity information architecture. It employs a "Soft Professionalism" approach—utilizing generous whitespace and high-quality photography to evoke a sense of freedom, while maintaining a strict, systematic grid to communicate the reliability of the directory. The interface is clean and airy, avoiding unnecessary decoration to ensure the travel agents' expertise and the destinations themselves remain the focal point.

## Colors

The palette is anchored by a Trust Blue primary (#0056b3), used for navigation, primary buttons, and structural elements to establish authority. The Highlight Green (#28a745) is reserved strictly for high-impact Call-to-Actions and positive status indicators, ensuring a clear path to conversion. 

A light gray (#f8f9fa) is utilized for surface-level differentiation, creating subtle "containers" for content sections without the visual weight of heavy borders. Text utilizes a deep charcoal (#1a1d23) rather than pure black to maintain a softer, more modern contrast against the crisp white background.

## Typography

This design system uses **Inter** exclusively to ensure maximum legibility and a systematic, clean aesthetic across all platforms. The typographic hierarchy relies on weight differentiation and subtle negative letter-spacing on larger headings to maintain a compact, premium feel. 

Large displays are used for hero sections to capture attention, while body copy is kept at a comfortable 16px/18px with generous line height for long-form agent bios. Labels use a slightly heavier weight (Medium 500) to ensure they remain distinct from body text even at smaller sizes.

## Layout & Spacing

The layout follows a **Fixed Grid** model on desktop, centered with a maximum width of 1280px. It utilizes a 12-column system with 24px gutters. 

- **Desktop:** 64px side margins, 12 columns.
- **Tablet:** 32px side margins, 8 columns.
- **Mobile:** 16px side margins, 4 columns.

Spacing is based on an 8px scale. Large vertical spacing (80px+) is used between major homepage sections to reinforce the "clean and airy" brand attribute. Grouped elements (like search filters) use tighter 8px or 16px intervals to show relationship.

## Elevation & Depth

Hierarchy is established through **Ambient Shadows** and tonal layering. Surfaces are generally flat, but interactive cards (such as Agent Profiles) utilize a soft, diffused shadow to indicate "lift" and interactivity.

- **Level 0 (Floor):** White (#ffffff) or Light Gray (#f8f9fa) backgrounds.
- **Level 1 (Cards):** White background with a 1px #e9ecef border or a soft shadow (0px 4px 20px rgba(0, 0, 0, 0.05)).
- **Level 2 (Dropdowns/Modals):** Elevated with a more pronounced shadow (0px 10px 30px rgba(0, 0, 0, 0.1)) to sit clearly above the page content.

Avoid heavy dark shadows; the goal is to feel light and "sun-drenched," mirroring the travel industry's aspirational nature.

## Shapes

The design system employs **Rounded** shapes (8px to 16px) to soften the professional tone and make the directory feel accessible and friendly. 

- **Standard Elements (Buttons, Inputs):** 8px (0.5rem) radius.
- **Large Elements (Cards, Hero Banners):** 16px (1rem) radius.
- **Search Bars:** Often utilize a "Super-Rounded" or pill-shape (100px) to differentiate them as the primary functional tool of the website.

## Components

### Buttons
- **Primary:** Trust Blue background, white text. 8px radius.
- **CTA:** Highlight Green background, white text. Reserved for "Contact Agent" or "Book Now."
- **Secondary:** Transparent with a 1px Blue border or Light Gray background.

### Cards (Agent Profiles)
Cards are the core unit of the directory. They should feature a 16px corner radius, a subtle border, and a shadow on hover. Content includes a high-res headshot, name (Headline-SM), rating (stars in green), and specialty tags (Chips).

### Search & Filters
A high-impact search bar should be placed in the hero section. It uses a pill-shape, large 24px internal padding, and integrates dropdown filters for "Destination," "Budget," and "Travel Type." 

### Rating System
Five-star scale using the Highlight Green (#28a745) for filled stars. The numerical score should be placed adjacent in a Label-MD style.

### Input Fields
Inputs use a white background, a 1px #dee2e6 border, and an 8px radius. On focus, the border transitions to Primary Blue with a subtle outer glow.

### Chips/Tags
Used for "Specialties" (e.g., Luxury, Cruise, Safari). Small, light gray backgrounds with Label-SM text, using a full pill-radius for a distinct "tag" look.
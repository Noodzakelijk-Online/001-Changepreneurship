# Changepreneurship Manus Design System

## Overview
This document defines the visual and interaction standards for the Manus enhancements to the Changepreneurship platform.

## Color Palette

### Primary Colors
- **Primary Orange:** `#FF6B35` - Main brand color for CTAs and highlights
- **Dark Background:** `#0F1419` - Primary background (dark mode)
- **Surface:** `#1A1F2E` - Secondary background for cards/containers
- **Border:** `#2D3748` - Subtle borders and dividers

### Semantic Colors
- **Success:** `#10B981` - Positive actions, completion
- **Warning:** `#F59E0B` - Caution, pending actions
- **Error:** `#EF4444` - Errors, destructive actions
- **Info:** `#3B82F6` - Information, neutral actions

### Text Colors
- **Primary Text:** `#F3F4F6` - Main text on dark backgrounds
- **Secondary Text:** `#D1D5DB` - Muted text, descriptions
- **Tertiary Text:** `#9CA3AF` - Disabled, placeholder text

## Typography

### Font Families
- **Display:** `Poppins` (Bold, 700) - Headlines, major sections
- **Heading:** `Inter` (SemiBold, 600) - Section titles
- **Body:** `Inter` (Regular, 400) - Main content
- **Mono:** `Fira Code` (Regular, 400) - Code, technical content

### Font Sizes & Hierarchy
- **H1 (Display):** 48px, Bold, Line height 1.2
- **H2 (Heading):** 32px, SemiBold, Line height 1.3
- **H3 (Subheading):** 24px, SemiBold, Line height 1.4
- **H4 (Section):** 18px, SemiBold, Line height 1.5
- **Body (Large):** 16px, Regular, Line height 1.6
- **Body (Regular):** 14px, Regular, Line height 1.6
- **Body (Small):** 12px, Regular, Line height 1.5
- **Caption:** 11px, Regular, Line height 1.4

## Spacing Scale (8px Grid)

- **xs:** 4px
- **sm:** 8px
- **md:** 16px
- **lg:** 24px
- **xl:** 32px
- **2xl:** 48px
- **3xl:** 64px

## Component Standards

### Buttons
- **Primary:** Orange background, white text, 8px border-radius
- **Secondary:** Dark border, orange text, transparent background
- **Tertiary:** No border, orange text, hover effect
- **Disabled:** 50% opacity, cursor not-allowed
- **Padding:** 12px 24px (md), 10px 20px (sm), 14px 28px (lg)

### Cards
- **Background:** `#1A1F2E`
- **Border:** 1px solid `#2D3748`
- **Border Radius:** 12px
- **Padding:** 24px
- **Shadow:** `0 4px 12px rgba(0, 0, 0, 0.3)`
- **Hover:** Subtle lift effect (2px shadow increase)

### Inputs
- **Background:** `#0F1419`
- **Border:** 1px solid `#2D3748`
- **Border Radius:** 8px
- **Padding:** 12px 16px
- **Focus:** Orange border, subtle glow
- **Placeholder:** `#9CA3AF`

### Progress Indicators
- **Track:** `#2D3748`
- **Fill:** Linear gradient from `#FF6B35` to `#FF8C5A`
- **Height:** 4px
- **Border Radius:** 2px

### Badges
- **Background:** `#FF6B35` with 20% opacity
- **Text:** `#FF6B35`
- **Padding:** 4px 12px
- **Border Radius:** 12px
- **Font Size:** 12px

## Animation & Transitions

### Timing Functions
- **Fast:** 150ms (micro-interactions, hover effects)
- **Standard:** 300ms (transitions, modal opens)
- **Slow:** 500ms (page transitions, major animations)

### Easing
- **Ease In:** `cubic-bezier(0.4, 0, 1, 1)` - Deceleration
- **Ease Out:** `cubic-bezier(0, 0, 0.2, 1)` - Acceleration
- **Ease In Out:** `cubic-bezier(0.4, 0, 0.2, 1)` - Smooth

### Common Animations
- **Fade In:** Opacity 0 → 1, 300ms ease-out
- **Slide Up:** Transform translateY(20px) → 0, 300ms ease-out
- **Scale:** Transform scale(0.95) → 1, 300ms ease-out
- **Hover Lift:** Transform translateY(-2px), 150ms ease-out

## Accessibility Standards

### WCAG 2.1 AA Compliance
- **Color Contrast:** Minimum 4.5:1 for text, 3:1 for graphics
- **Focus Indicators:** Visible 2px orange outline
- **Keyboard Navigation:** All interactive elements accessible via Tab
- **Motion:** Respect `prefers-reduced-motion` media query
- **Alt Text:** All images have descriptive alt text

### Interactive Elements
- **Minimum Touch Target:** 44x44px
- **Focus Visible:** Always visible, never hidden
- **Disabled State:** Clear visual indication
- **Error Messages:** Associated with form fields

## Dark Mode (Default)

All components are designed with dark mode as the default. The palette above reflects this.

### Light Mode (Future)
If light mode is added in the future:
- **Background:** `#FFFFFF`
- **Surface:** `#F9FAFB`
- **Text Primary:** `#111827`
- **Text Secondary:** `#6B7280`
- **Orange:** `#FF6B35` (unchanged)

## Implementation Guidelines

### CSS Variables
```css
:root {
  /* Colors */
  --color-primary: #FF6B35;
  --color-dark-bg: #0F1419;
  --color-surface: #1A1F2E;
  --color-border: #2D3748;
  --color-text-primary: #F3F4F6;
  --color-text-secondary: #D1D5DB;
  --color-text-tertiary: #9CA3AF;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-display: 'Poppins', sans-serif;
  --font-heading: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 1, 1);
  --transition-standard: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Tailwind Configuration
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#FF6B35',
        'dark-bg': '#0F1419',
        surface: '#1A1F2E',
        border: '#2D3748',
      },
      fontFamily: {
        display: ['Poppins', 'sans-serif'],
        heading: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      transitionDuration: {
        fast: '150ms',
        standard: '300ms',
        slow: '500ms',
      },
    },
  },
};
```

## Component Examples

### Module Container
- **Background:** Surface color with subtle border
- **Padding:** 24px
- **Border Radius:** 12px
- **Shadow:** Soft shadow for depth
- **Hover:** Slight lift effect

### Context Panel
- **Width:** 300px (sidebar)
- **Background:** Dark background with 80% opacity
- **Border:** Right border in orange (2px)
- **Content:** Relevant previous answers with icons
- **Scrollable:** If content exceeds container height

### Magic Button
- **Style:** Primary button with orange background
- **Icon:** Sparkle or lightning bolt
- **Animation:** Subtle pulse on hover
- **Tooltip:** "Pre-fill from [previous module]"

### Progress Map (Metro Style)
- **Stations:** Circles representing completed modules
- **Lines:** Connecting stations
- **Colors:** Orange for completed, gray for pending
- **Labels:** Module names below stations
- **Animation:** Fade in as modules complete

## Responsive Design

### Breakpoints
- **Mobile:** 320px - 640px
- **Tablet:** 641px - 1024px
- **Desktop:** 1025px+

### Guidelines
- **Mobile:** Single column, full-width components
- **Tablet:** Two-column layout where appropriate
- **Desktop:** Multi-column, sidebar layouts
- **Touch Targets:** Minimum 44x44px on mobile

## Micro-interactions

### Button Hover
- Background color shift (5% lighter)
- Subtle shadow increase
- Cursor change to pointer

### Input Focus
- Border color change to orange
- Subtle glow effect (box-shadow)
- Placeholder text fade out

### Card Hover
- Shadow increase (lift effect)
- Slight scale (1.02x)
- Smooth transition

### Loading States
- Skeleton screens with pulse animation
- Spinner with orange color
- Progress bar with gradient fill

## Consistency Checklist

- [ ] All text uses defined typography scale
- [ ] All spacing uses 8px grid
- [ ] All colors from palette
- [ ] All buttons follow button standards
- [ ] All cards follow card standards
- [ ] All inputs follow input standards
- [ ] All interactive elements have focus states
- [ ] All animations use defined timing
- [ ] Color contrast meets WCAG AA
- [ ] Touch targets minimum 44x44px
- [ ] Responsive design tested on all breakpoints

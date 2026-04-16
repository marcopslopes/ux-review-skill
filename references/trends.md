# UX Trends & Best Practices (2024-2026)

Use these trends as context when evaluating modern web pages. A page that follows outdated patterns isn't necessarily broken, but noting the gap is valuable feedback.

## Layout & Visual Design

- **Bento grid layouts** — modular card-based layouts that group related content in visually distinct containers. Replaces flat full-width sections.
- **Generous whitespace** — premium brands use more whitespace, not less. Cramped layouts signal low quality.
- **Large typography** — hero headlines at 48-80px+, body text at 16-18px minimum. Small text is a red flag.
- **Reduced visual noise** — fewer gradients, fewer shadows, fewer competing colors. Flat or subtle depth.
- **Dark mode support** — increasingly expected, especially for developer and productivity tools.
- **Scroll-driven animations** — subtle parallax, fade-ins on scroll. Heavy animation is dated; subtle is current.

## Navigation & Interaction

- **Sticky headers** — primary navigation stays visible on scroll. Standard expectation.
- **Command palettes** — Cmd+K / Ctrl+K for power users in SaaS/productivity tools.
- **Bottom navigation on mobile** — thumb-friendly primary nav at bottom, not top hamburger.
- **Reduced hamburger reliance** — visible navigation preferred on tablet+. Hamburger acceptable only on phone.
- **Skeleton screens** — show layout shape while loading, not spinners. Reduces perceived wait time.
- **Inline validation** — validate form fields on blur, not on submit.

## Content & Copy

- **Conversational UI copy** — buttons say "Get started" not "Submit". Labels are human, not technical.
- **Progressive disclosure** — show essentials first, details on demand. Reduce initial cognitive load.
- **Social proof near CTAs** — testimonials, user counts, trust badges close to conversion points.
- **Microcopy on forms** — helper text under fields explaining format, purpose, or "why we ask."
- **Plain language** — Flesch-Kincaid grade 6-8 for consumer products. Technical products can go higher.

## Accessibility & Inclusion

- **WCAG 2.1 AA as baseline** — not optional, increasingly legally required.
- **Focus indicators** — visible, high-contrast focus rings. Browser defaults are often insufficient.
- **Reduced motion** — respect `prefers-reduced-motion` media query. Don't force animations.
- **Semantic HTML over ARIA** — native `<button>`, `<nav>`, `<main>` preferred over `div` + `role=`.
- **Touch targets 44px+** — WCAG 2.5.5. Minimum tap target size for mobile.
- **Color not sole indicator** — error states need icons/text in addition to red color.

## Performance & Trust

- **Core Web Vitals** — LCP < 2.5s, FID < 100ms, CLS < 0.1. Users notice slow pages.
- **HTTPS everywhere** — no mixed content. Trust badges visible for e-commerce.
- **Cookie consent done right** — easy reject, not dark-patterned. Users notice and judge.
- **Privacy-first language** — "We don't sell your data" > "We value your privacy."

## Mobile-Specific

- **Thumb zone design** — primary actions within easy thumb reach (bottom half of screen).
- **Swipe gestures** — expected for carousels, dismissing, navigation. But always with visible alternatives.
- **Responsive images** — proper srcset/sizes, not desktop images scaled down.
- **Input types** — `type="email"`, `type="tel"`, `inputmode="numeric"` for appropriate keyboards.
- **Viewport meta** — `width=device-width, initial-scale=1`. Missing = broken mobile experience.

## Anti-Patterns to Flag

- **Intrusive interstitials** — full-screen popups on load, especially on mobile.
- **Infinite scroll without "back to top"** — user loses position.
- **Auto-playing video with sound** — universally disliked.
- **Disabled submit buttons without explanation** — user can't figure out what's wrong.
- **Carousel as primary content** — low engagement, content hidden by default.
- **Light gray on white text** — aesthetic but unreadable, fails contrast.
- **Custom scrollbars** — often break accessibility and feel unfamiliar.
- **Newsletter popup within 5 seconds** — user hasn't even read the page yet.

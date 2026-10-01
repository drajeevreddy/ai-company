# GSAP ScrollTrigger + Lenis Integration

Complete setup for smooth scroll with GSAP animations that sync perfectly.

## Provider Component (SmoothScroll.tsx)

```tsx
"use client";

import { useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

// CRITICAL: Register plugin ONCE at module level
gsap.registerPlugin(ScrollTrigger);

export default function SmoothScroll({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      touchMultiplier: 2,
    });

    function raf(time: number) {
      lenis.raf(time);
      ScrollTrigger.update(); // MUST call this to sync GSAP with Lenis
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);

  return <>{children}</>;
}
```

## Usage in Layout

```tsx
// app/layout.tsx
import SmoothScroll from "@/components/SmoothScroll";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <SmoothScroll>
          {children}
        </SmoothScroll>
      </body>
    </html>
  );
}
```

## Showreel Pin/Scrub Component

```tsx
"use client";

import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export default function Showreel() {
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const totalScroll = track.scrollWidth - window.innerWidth;

    gsap.to(track, {
      x: -totalScroll,
      ease: "none",
      scrollTrigger: {
        trigger: track.parentElement,
        start: "top top",
        end: `+=${totalScroll}`,
        scrub: 1,
        pin: true,
      },
    });

    return () => {
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);

  return (
    <section className="relative overflow-hidden bg-ink py-24">
      <div className="overflow-hidden">
        <div ref={trackRef} className="flex gap-4 px-6" style={{ width: "max-content" }}>
          {/* video cards */}
        </div>
      </div>
    </section>
  );
}
```

## Critical Rules

| Rule | Why |
|------|-----|
| `gsap.registerPlugin(ScrollTrigger)` at module level | Without this, pin/scrub silently does nothing |
| `ScrollTrigger.update()` in Lenis RAF | Syncs GSAP's scroll position with Lenis's smoothed position |
| `ScrollTrigger.getAll().forEach(t => t.kill())` in cleanup | Prevents memory leaks and stale triggers |
| `prefers-reduced-motion` check | Accessibility: disable for users who want reduced motion |
| `scrub: 1` (not `true`) | Smooth 1-frame lag scrub, not instant |

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pin doesn't work | `ScrollTrigger` not registered | `gsap.registerPlugin(ScrollTrigger)` |
| Stuttering scroll | Missing `ScrollTrigger.update()` | Call in Lenis RAF loop |
| Trigger fires wrong | Lenis smooth offset | Use `track.parentElement` as trigger |
| Memory leak | No cleanup | Kill all triggers in `useEffect` return |

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  .lenis.lenis-smooth {
    scroll-behavior: auto !important;
  }
  .reveal-up {
    clip-path: inset(0 0 0 0) !important;
    transition: none !important;
  }
}
```

In components:
```tsx
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (prefersReduced) return; // skip GSAP animations
```
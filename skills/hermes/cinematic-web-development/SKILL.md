---
name: cinematic-web-development
description: Build cinematic agency sites with WebGL heroes, GSAP scroll.
---

# Cinematic Web Development

Class-level skill for building unforgettable marketing agency websites where the site *is* the case study — WebGL hero animations, GSAP scroll-triggered cinematography, cinematic design systems, and dark-mode branding with logo variants.

## When to Use
- Building agency/portfolio sites that need "unforgettable" first impressions
- WebGL hero animations (particle countdowns, cursor-reactive fields, shader morphs)
- GSAP + Lenis scroll choreography (pin/scrub, horizontal reels, clip-path reveals)
- Cinematic design systems (film/production aesthetics, projector-light palettes)
- Dark-mode sites needing light/dark logo variants
- R3F + Next.js 15/16 integration with proper linting

## Core Patterns

### 1. R3F + Next.js Lint Configuration
Next.js ESLint flags R3F's intentional mutation patterns. Add `.eslintrc.js` or `eslint.config.mjs`:

```js
// eslint.config.mjs
{
  rules: {
    "react-hooks/refs": "off",
    "react-hooks/immutability": "off",
    "react-hooks/ref-assignment": "off",
    "react-hooks/set-state-in-effect": "off",
    "react-hooks/exhaustive-deps": "warn",
    "@next/next/no-img-element": "warn",
  }
}
```

Or use inline disables in component files:
```tsx
// eslint-disable-next-line react-hooks/ref-assignment -- sync ref update pattern
onCompleteRef.current = onComplete;

// eslint-disable-next-line react-hooks/exhaustive-deps -- R3F useFrame intentionally mutates uniforms
useFrame(({ clock }) => { ... });
```

### 2. Shader-Side Morphing (Not Per-Frame BufferAttribute Updates)
**Anti-pattern** (causes GPU stalls, lint errors):
```tsx
// BAD: forces GPU→CPU sync every frame
useFrame(() => {
  attrA.array.set(newPositions);
  attrA.needsUpdate = true;
});
```

**Correct pattern** — single position attribute + multiple target attributes + `uProgress` uniform:
```glsl
// vertex shader
attribute vec3 positionIdle;
attribute vec3 position3;
attribute vec3 position2;
attribute vec3 position1;
attribute vec3 positionScatter;
uniform float uProgress;
uniform int uPhase;

vec3 getTarget() {
  if (uPhase == 1) return position3;
  else if (uPhase == 2) return position2;
  else if (uPhase == 3) return position1;
  else if (uPhase == 4) return positionScatter;
  return positionIdle;
}

void main() {
  vec3 target = getTarget();
  vec3 pos = mix(positionIdle, target, uProgress);
  // ... mouse interaction, projection
}
```

```tsx
// Component: pass all targets as separate bufferAttributes
<points>
  <bufferGeometry>
    <bufferAttribute attach="attributes-positionIdle" args={[idle, 3]} />
    <bufferAttribute attach="attributes-position3" args={[d3, 3]} />
    <bufferAttribute attach="attributes-position2" args={[d2, 3]} />
    <bufferAttribute attach="attributes-position1" args={[d1, 3]} />
    <bufferAttribute attach="attributes-positionScatter" args={[scatter, 3]} />
  </bufferGeometry>
  <shaderMaterial uniforms={uniforms} vertexShader={...} />
</points>
```

### 3. Proper Mouse Unproject in R3F
```tsx
const onPointerMove = useCallback(
  (e: React.PointerEvent<THREE.Points>) => {
    const rect = (e.target as HTMLCanvasElement).getBoundingClientRect();
    const x = ((e.nativeEvent.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((e.nativeEvent.clientY - rect.top) / rect.height) * 2 + 1;
    const vec = new THREE.Vector3(x, y, 0.5);
    vec.unproject(camera);
    const dir = vec.sub(camera.position).normalize();
    const distance = -camera.position.z / dir.z;
    const pos = camera.position.clone().add(dir.multiplyScalar(distance));
    uniforms.uMouse.value.set(pos.x, pos.y);
    uniforms.uMouseActive.value = 1;
  },
  [camera, uniforms]
);
```

### 4. GSAP ScrollTrigger + Lenis Integration
Register plugin **once** in a provider/wrapper:
```tsx
// SmoothScroll.tsx
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger); // CRITICAL: missing this = silent failure

export default function SmoothScroll({ children }) {
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.2, ... });
    function raf(time) {
      lenis.raf(time);
      ScrollTrigger.update(); // sync GSAP with Lenis
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
    return () => { lenis.destroy(); ScrollTrigger.getAll().forEach(t => t.kill()); };
  }, []);
  return <>{children}</>;
}
```

Then in components:
```tsx
gsap.to(track, {
  x: -totalScroll,
  scrollTrigger: { trigger: track.parentElement, start: "top top", end: `+=${totalScroll}`, scrub: 1, pin: true },
});
```

### 5. Light/Dark Logo Variants for Dark-Mode Sites
Never use a single logo designed for light backgrounds on dark navs.
- **Dark logo** (for light sections): black ink `#0a0a0a` on transparent
- **Light logo** (for dark navs/sections): cream `#f1efe8` on transparent

```tsx
// Nav.tsx - light logo on semi-transparent dark nav
<nav className={scrolled ? "bg-ink/90" : "bg-ink/70"}>
  <img src="/brand/logo-light.svg" alt="brand" className="h-10 w-auto" />
</nav>
```

### 6. Particle Countdown Hero — Complete Pattern
```tsx
// HeroCanvas.tsx (client-only, ssr: false)
export default function HeroCanvas({ onComplete }) {
  const [ready, setReady] = useState(false);
  const [positions, setPositions] = useState(null);

  useEffect(() => {
    setPositions({ idle: genIdle(), d3: genDigit("3"), d2: genDigit("2"), d1: genDigit("1"), scatter: genScatter() });
    setTimeout(() => setReady(true), 0); // avoid sync setState warning
  }, []);

  if (!ready) return <Canvas><color attach="background" args={["#0a0a0a"]} /></Canvas>;

  return (
    <Canvas camera={{ position: [0,0,5], fov: 60 }} dpr={[1,1.5]}>
      <ParticlePoints uniforms={uniforms} {...positions} onComplete={onComplete} />
    </Canvas>
  );
}
```

**Timing phases** (total ~6.5s):
| Phase | Duration | Morph |
|-------|----------|-------|
| idle → "3" | 1.5s | 0.8s |
| "3" → "2" | 1.5s | 0.8s |
| "2" → "1" | 1.5s | 0.8s |
| "1" → scatter | 2.0s | 1.0s |

### 7. Real Client Data — Instagram Follower Scraping
```python
# Scrape public IG profile metadata (og:description)
pat = re.compile(r'([\d,.]+[KM]?)\s*Followers,\s*([\d,.]+[KM]?)\s*Following,\s*([\d,.]+[KM]?)\s*Posts', re.I)

async def scrape_ig(handle):
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{handle}/")
    desc = await page.locator('meta[property="og:description"]').get_attribute("content")
    m = pat.search(desc)
    return {"followers": parse_num(m.group(1)), "posts": parse_num(m.group(3))}
```

Use for: headline stats ("3.1M+ audience"), Results section count-ups, WorkGrid follower badges.

### 8. Cinematic Design Tokens
```json
{
  "ink": "#0a0a0a",
  "paper": "#f1efe8",
  "orange": "#ff4d00",
  "gray-mid": "#606060",
  "font-display": "Instrument Serif (lowercase, tight tracking)",
  "font-body": "Space Grotesk",
  "motion": "film-leader countdowns, slate claps, projector flicker, dust in light beam"
}
```

## Pitfalls & Gotchas

| Issue | Symptom | Fix |
|-------|---------|-----|
| GSAP ScrollTrigger not registered | Pin/scrub does nothing, no error | `gsap.registerPlugin(ScrollTrigger)` in SmoothScroll |
| R3F hooks outside Canvas | "Hooks can only be used within Canvas" | Move `useFrame`/`useThree` into child of `<Canvas>` |
| WebGL context lost | Canvas disappears after animation | `dpr={[1, 1.5]}`, `powerPreference: "high-performance"`, mobile fallback |
| Logo invisible on dark nav | Black logo on dark bg | Create `logo-light.svg` with cream `#f1efe8` fills |
| Lint errors on R3F patterns | `react-hooks/refs`, `immutability` errors | Disable specific rules in eslint config |
| `setState` in effect warning | "Avoid calling setState synchronously" | `setTimeout(() => setReady(true), 0)` |
| Mouse interaction dead zone | Particles don't react to cursor | Use `unproject(camera)` not viewport coords |

## References
- `references/r3f-lint-config.md` — full ESLint config with explanations
- `references/shader-morph-pattern.md` — vertex/fragment shader templates
- `references/gsap-lenis-setup.md` — complete provider + component examples
- `references/logo-variants.md` — SVG templates for dark/light logos
- `references/particle-countdown-hero.md` — complete HeroCanvas component

## Templates
- `templates/hero-canvas.tsx` — production-ready HeroCanvas with all patterns
- `templates/smooth-scroll.tsx` — Lenis + GSAP provider
- `templates/logo-light.svg` / `templates/logo-dark.svg` — SVG logo templates
- `templates/eslint.config.mjs` — R3F-friendly lint config

## Scripts
- `scripts/scrape-ig-followers.py` — batch scrape 25+ handles with Playwright
- `scripts/verify-hero-animation.py` — Playwright test: canvas renders, headline appears, scroll works
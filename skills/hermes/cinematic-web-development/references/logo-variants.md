# Logo Variants for Dark-Mode Sites

Dark-mode cinematic sites need **two logo variants** — one for light backgrounds, one for dark.

## The Rule

> **Never use a single logo designed for light backgrounds on dark navs/sections.**

| Variant | Use Case | Fill Color | Background |
|---------|----------|------------|------------|
| **Dark logo** (`logo.svg`) | Light sections, printed collateral | `#0a0a0a` (ink) | Transparent |
| **Light logo** (`logo-light.svg`) | Dark navs, hero overlays, footers | `#f1efe8` (paper/cream) | Transparent |

## Dark Logo (logo.svg) — For Light Backgrounds

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 200" width="500" height="200">
  <defs>
    <linearGradient id="inkGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0a0a0a"/>
      <stop offset="100%" style="stop-color:#1a1a1a"/>
    </linearGradient>
  </defs>
  <!-- Film slate/clapperboard fused into 'A' -->
  <g transform="translate(40, 20)">
    <!-- Slate body -->
    <rect x="0" y="0" width="120" height="160" rx="8" fill="url(#inkGrad)"/>
    <!-- Clapper top -->
    <rect x="-10" y="-15" width="140" height="20" rx="3" fill="#0a0a0a"/>
    <!-- Clapper hinge -->
    <circle cx="60" cy="-5" r="6" fill="#0a0a0a"/>
    <!-- Slate lines -->
    <g stroke="#333" stroke-width="1.5" stroke-linecap="round">
      <line x1="15" y1="30" x2="105" y2="30"/>
      <line x1="15" y1="55" x2="105" y2="55"/>
      <line x1="15" y1="80" x2="105" y2="80"/>
      <line x1="15" y1="105" x2="105" y2="105"/>
      <line x1="15" y1="130" x2="105" y2="130"/>
    </g>
    <!-- Scene/Take labels -->
    <text x="20" y="48" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="600" fill="#444" letter-spacing="1">SCENE</text>
    <text x="20" y="73" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="600" fill="#444" letter-spacing="1">TAKE</text>
    <!-- Microphone element forming the crossbar of 'A' -->
    <ellipse cx="60" cy="95" rx="28" ry="10" fill="none" stroke="#222" stroke-width="2"/>
    <ellipse cx="60" cy="95" rx="22" ry="6" fill="#111"/>
    <line x1="60" y1="105" x2="60" y2="125" stroke="#222" stroke-width="3" stroke-linecap="round"/>
    <circle cx="60" cy="130" r="4" fill="#222"/>
  </g>
  <!-- Wordmark "adory creatives" -->
  <text x="180" y="135" font-family="Georgia, serif" font-size="36" font-weight="400" fill="#0a0a0a" letter-spacing="-0.5">adory</text>
  <text x="180" y="172" font-family="Georgia, serif" font-size="22" font-weight="400" fill="#0a0a0a" letter-spacing="0.5">creatives</text>
  <!-- Orange period -->
  <circle cx="342" cy="128" r="4" fill="#ff4d00"/>
</svg>
```

## Light Logo (logo-light.svg) — For Dark Backgrounds

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 200" width="500" height="200">
  <!-- Film slate/clapperboard fused into 'A' - LIGHT VERSION for dark backgrounds -->
  <g transform="translate(40, 20)">
    <!-- Slate body - white/cream -->
    <rect x="0" y="0" width="120" height="160" rx="8" fill="#f1efe8"/>
    <!-- Slate border -->
    <rect x="0" y="0" width="120" height="160" rx="8" fill="none" stroke="#f1efe8" stroke-width="2"/>
    <!-- Clapper top -->
    <rect x="-10" y="-15" width="140" height="20" rx="3" fill="#f1efe8"/>
    <rect x="-10" y="-15" width="140" height="20" rx="3" fill="none" stroke="#f1efe8" stroke-width="1"/>
    <!-- Clapper hinge -->
    <circle cx="60" cy="-5" r="6" fill="#f1efe8"/>
    <!-- Slate lines -->
    <g stroke="#888" stroke-width="1.5" stroke-linecap="round">
      <line x1="15" y1="30" x2="105" y2="30"/>
      <line x1="15" y1="55" x2="105" y2="55"/>
      <line x1="15" y1="80" x2="105" y2="80"/>
      <line x1="15" y1="105" x2="105" y2="105"/>
      <line x1="15" y1="130" x2="105" y2="130"/>
    </g>
    <!-- Scene/Take labels -->
    <text x="20" y="48" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="600" fill="#999" letter-spacing="1">SCENE</text>
    <text x="20" y="73" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="600" fill="#999" letter-spacing="1">TAKE</text>
    <!-- Microphone element forming the crossbar of 'A' -->
    <ellipse cx="60" cy="95" rx="28" ry="10" fill="none" stroke="#f1efe8" stroke-width="2"/>
    <ellipse cx="60" cy="95" rx="22" ry="6" fill="#f1efe8"/>
    <line x1="60" y1="105" x2="60" y2="125" stroke="#f1efe8" stroke-width="3" stroke-linecap="round"/>
    <circle cx="60" cy="130" r="4" fill="#f1efe8"/>
  </g>
  <!-- Wordmark "adory creatives" - LIGHT -->
  <text x="180" y="135" font-family="Georgia, serif" font-size="36" font-weight="400" fill="#f1efe8" letter-spacing="-0.5">adory</text>
  <text x="180" y="172" font-family="Georgia, serif" font-size="22" font-weight="400" fill="#f1efe8" letter-spacing="0.5">creatives</text>
  <!-- Orange period -->
  <circle cx="342" cy="128" r="4" fill="#ff4d00"/>
</svg>
```

## Usage in Components

```tsx
// Nav.tsx — light logo on semi-transparent dark nav
<nav className={scrolled ? "bg-ink/90 backdrop-blur-md py-4" : "bg-ink/70 backdrop-blur-sm py-6"}>
  <Link href="/" className="flex items-center gap-2">
    <img src="/brand/logo-light.svg" alt="adory creatives" className="h-10 w-auto" />
  </Link>
</nav>

// Footer.tsx — dark logo on light bg (if footer is light)
// or light logo on dark bg (if footer is dark)
<footer className="bg-ink/50">
  <img src="/brand/logo-light.svg" alt="adory creatives" className="h-12 w-auto" />
</footer>
```

## Design Token Mapping

| Element | Dark Logo | Light Logo |
|---------|-----------|------------|
| Primary fill | `#0a0a0a` (ink) | `#f1efe8` (paper) |
| Gradient | `#0a0a0a` → `#1a1a1a` | Solid `#f1efe8` |
| Stroke/border | `#333` / `#222` | `#888` / `#f1efe8` |
| Text labels | `#444` | `#999` |
| Wordmark | `#0a0a0a` | `#f1efe8` |
| Orange period | `#ff4d00` | `#ff4d00` (unchanged) |

## File Locations

```
/public/brand/
├── logo.svg          # Dark logo (for light backgrounds)
├── logo-light.svg    # Light logo (for dark backgrounds)
├── favicon-32.png
├── favicon-128.png
├── favicon-256.png
└── og-image.png      # 800x320, uses light logo on dark bg
```

## Nav Background Strategy

```tsx
// Nav.tsx
const [scrolled, setScrolled] = useState(false);

useEffect(() => {
  const onScroll = () => setScrolled(window.scrollY > 50);
  window.addEventListener("scroll", onScroll, { passive: true });
  return () => window.removeEventListener("scroll", onScroll);
}, []);

<nav className={`
  fixed top-0 left-0 z-50 w-full transition-all duration-500
  ${scrolled ? "bg-ink/90 backdrop-blur-md py-4" : "bg-ink/70 backdrop-blur-sm py-6"}
`}>
```

The semi-transparent dark background (`bg-ink/70` → `bg-ink/90`) works with the **light logo** at all times.
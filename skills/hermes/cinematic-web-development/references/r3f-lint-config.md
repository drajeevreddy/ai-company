# R3F + Next.js Lint Configuration

Next.js ESLint (eslint-config-next) includes react-hooks rules that flag R3F's intentional mutation patterns. R3F legitimately mutates refs and uniforms every frame — this is how WebGL works.

## Recommended Config

**Option A: eslint.config.mjs (flat config, Next.js 15+)**
```js
import { defineConfig } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      "react-hooks/refs": "off",
      "react-hooks/immutability": "off",
      "react-hooks/ref-assignment": "off",
      "react-hooks/set-state-in-effect": "off",
      "react-hooks/exhaustive-deps": "warn",
      "@next/next/no-img-element": "warn",
    },
  },
]);
```

**Option B: .eslintrc.js (legacy)**
```js
module.exports = {
  extends: ["next/core-web-vitals"],
  rules: {
    "react-hooks/refs": "off",
    "react-hooks/immutability": "off",
    "react-hooks/ref-assignment": "off",
    "react-hooks/set-state-in-effect": "off",
    "react-hooks/exhaustive-deps": "warn",
    "@next/next/no-img-element": "warn",
  },
};
```

## Inline Disables (for targeted fixes)

```tsx
// Ref sync pattern — standard R3F callback update
// eslint-disable-next-line react-hooks/ref-assignment -- sync ref update pattern
onCompleteRef.current = onComplete;

// useFrame intentionally mutates uniforms every frame
// eslint-disable-next-line react-hooks/exhaustive-deps -- R3F useFrame intentionally mutates uniforms
useFrame(({ clock }) => { ... });

// useState in useEffect — use setTimeout to avoid sync warning
// eslint-disable-next-line react-hooks/exhaustive-deps -- one-time init
}, []);
```

## Why These Rules Are Disabled

| Rule | R3F Pattern | Why It's Safe |
|------|-------------|---------------|
| `react-hooks/refs` | `ref.current = value` in render | Sync pattern for callback refs |
| `react-hooks/immutability` | `uniforms.uTime.value = t` in useFrame | Uniform objects are mutable by design |
| `react-hooks/ref-assignment` | `onCompleteRef.current = onComplete` | Standard React ref update pattern |
| `react-hooks/set-state-in-effect` | `setTimeout(() => setReady(true), 0)` | Async init pattern, not sync setState |
| `@next/next/no-img-element` | Static SVG/logo assets | No optimization benefit for tiny SVGs |

## Verification

```bash
# Should pass with 0 errors (warnings OK)
npm run lint
```

**Expected output:** 0 errors, only warnings about `<img>` elements (acceptable for static brand assets).
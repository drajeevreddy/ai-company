# Custom Dialog Footer Button Overlap — Fix Pattern

## Problem
A custom Dialog component (not Radix) renders inline when `open=true`. The content wrapper uses a plain `div` with `space-y-4`. A full-width `<label class="block">` in the form body overlaps the `DialogFooter` because both are `position: relative` with `z-index: auto`. The label intercepts clicks on the footer's "Schedule" / "Submit" button.

## Symptoms
- Playwright: `element intercepts pointer events` pointing to a `<label>` from the dialog footer subtree
- Button visually appears clickable but never fires onClick
- No console error — just silent click capture

## Root Cause
The dialog's inner container is a single flow layout:
```
<div class="relative z-50 ...">
  <header>...</header>
  {children}  // form with full-width block labels
  <footer>...</footer>  // buttons
</div>
```
A `<label class="block">` has `width: 100%` and covers the footer area in the stacking context.

## Fix: Flex Column Layout
Make the dialog inner container a flex column so header, content, and footer are structurally separated stacking contexts.

```tsx
// In Dialog component (src/components/ui/dialog.tsx)
<div className={cn(
  "relative z-50 w-full max-w-lg animate-scale-in rounded-xl border border-border bg-surface shadow-lg flex flex-col",  // ADD flex flex-col
  className
)}>
  <div className="flex items-center justify-between border-b border-border p-4 shrink-0">
    {title && <h2 className="text-base font-semibold text-primary">{title}</h2>}
    {description && <p className="text-sm text-secondary mt-1">{description}</p>}
    <button onClick={onClose} className="h-8 w-8 rounded-lg hover:bg-hover flex items-center justify-center transition-colors shrink-0">
      <X className="h-4 w-4 text-secondary" />
    </button>
  </div>
  <div className="flex-1 overflow-y-auto p-4">
    {children}
  </div>
  {/* Footer is now a separate flex child with shrink-0 */}
</div>
```

```tsx
// DialogFooter
export function DialogFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("flex items-center justify-end gap-3 mt-4 pt-4 border-t border-border shrink-0", className)}>
      {children}
    </div>
  );
}
```

## Key CSS Properties
| Element | Properties | Why |
|---------|------------|-----|
| Dialog wrapper | `flex flex-col` | Creates column stacking context |
| Header | `shrink-0` | Never shrinks, stays at top |
| Content | `flex-1 overflow-y-auto` | Grows, scrolls internally |
| Footer | `shrink-0` | Never shrinks, stays at bottom |

## Verification
- Click the footer button → onClick fires
- No Playwright "intercepts pointer events" errors
- Dialog scrolls internally if content is long
- Footer always visible at bottom

## When to Apply
Any custom Dialog/Modal component where:
- Content is rendered inline (not portal-based like Radix)
- Footer buttons exist below form content
- Form uses full-width block labels or inputs

## Related
- vercel-deployment-troubleshooting: build verification caught this via Playwright E2E test
- supabase-nextjs-debugging: this was the final blocker for appointment creation flow
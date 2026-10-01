# Mobile Touch Target Sizing Standards

## Minimum Touch Targets (WCAG 2.5.5 / iOS HIG / Material Design)

| Element | Desktop Min | Mobile (≤480px) | Implementation |
|---------|-------------|-----------------|----------------|
| Primary buttons | 52px | 48px | `min-height: 52px` + `@media (max-width: 480px) { min-height: 48px }` |
| Secondary buttons | 44px | 40px | `min-height: 44px` |
| Progress steps | 44px | 40px | `min-height: 44px` |
| List items (doctor/date) | 80px | 72-76px | `min-height: 80px` |
| Date cards | 96px | 84-88px | `min-height: 96px` + `min-width: 88px` |
| Time slots | 64px | 56-60px | `min-height: 64px` |
| Form inputs | 16px font | 16px font | `font-size: 16px` prevents iOS zoom |
| Checkboxes | 20×20px | 20×20px | `width: 20px; height: 20px; accent-color` |

## Touch Feedback
```css
.doctor-list-item:active,
.date-card:active,
.time-slot:active:not(.disabled),
.btn:active {
    transform: scale(0.98);
}
```

```javascript
// Opacity feedback on touch
el.addEventListener('touchstart', () => el.style.opacity = '0.85', { passive: true });
el.addEventListener('touchend', () => el.style.opacity = '', { passive: true });
```

## Responsive Breakpoints
```css
@media (max-width: 768px) { /* tablet */ }
@media (max-width: 480px) { /* phone */ }
```

At 768px: stack grids, reduce padding, hide step labels, shrink buttons
At 480px: further reduce sizes, single-column layouts

## Viewport Meta (Required)
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## Verification Checklist
- [ ] All interactive elements ≥ 44×44px (48×48px for primary)
- [ ] Form inputs 16px+ (no iOS zoom on focus)
- [ ] Active/touch states visible
- [ ] No horizontal scroll on mobile
- [ ] Content readable without zoom
- [ ] Touch targets don't overlap
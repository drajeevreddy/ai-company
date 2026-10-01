# Local Template Migration Pattern

Used when you have:
- Old site source files (PHP/HTML) available locally
- A new UI template (single HTML file, or similar) to migrate into

## Core Technique: Anchor-Based Replacement with Assertions

```python
# Load template
src = template.read_text()

def rep(old, new, count=1, all=False):
    assert old in src, f"ANCHOR NOT FOUND: {old[:90]!r}"
    src = src.replace(old, new) if all else src.replace(old, new, count)

def regex(pat, new):
    import re
    ns, n = re.subn(pat, lambda m: new, src, count=1, flags=re.DOTALL)
    assert n == 1, f"REGEX FAILED: {pat[:70]!r}"
    src = ns
```

### Why anchors + assertions?
- Template HTML is stable; unique text strings ("WE MAKE", "TREND-AWARE") make precise targets
- Assertions fail fast if the template changed — no silent partial migrations
- `all=True` for global fixes (email, phone, theme toggle removal)
- `regex` with callback for JS data objects avoids escaping hell

### Migration Steps (from this session)

1. **Extract source data** from old PHP files:
   - Read `includes/header.php`, `includes/footer.php` for nav/social/contact
   - Read each page (`index.php`, `about.php`, `services.php`, etc.) for content blocks
   - Parse portfolio items from `our-work.php` (categories, URLs, images, descriptions)
   - Extract events from `events.php`
   - Copy entire `images/` folder

2. **Replace in template** using anchors:
   - Meta tags: title, description, GA, favicon
   - Nav items: labels, routes, phone/email
   - Hero: tagline, headline lines, subtext, CTA text
   - Services: replace `const SERVICES = [...]` entirely with 6 real services
   - Portfolio: replace `const PROJECTS = {...}` with 20 real projects + `LAYOUT`
   - Events/Blog: replace `const POSTS = [...]` with 9 real events
   - About: principles→objectives, journey→strategies, team→why-choose-us, add platforms
   - Contact: form fields, FAQ, testimonials
   - Footer: services list, contact info, year, links

3. **Remove unwanted features entirely**:
   - Dark mode: delete `data-theme` on `<html>`, theme boot script, theme-toggle button, theme CSS blocks, theme JS
   - Custom cursor: delete cursor HTML, CSS, JS
   - Preloader: keep or remove per design

4. **Responsive cleanup**:
   - Services grid: `gap:0`, remove `margin-top` on nth-child
   - Update media queries to drop staggered layout rules

5. **Verify**: local server + check `data-theme` gone, images 200, no console errors, footer correct

## Gotchas
- **Escaping in regex replacements**: Use `re.subn(pat, lambda m: new, ...)` not `re.sub(pat, new, ...)` — avoids backslash doubling in replacement
- **JS template literals**: `${p.id}` in source stays as-is; only replace the *array definition*, not the template usage
- **Phone number format**: Old site used masked `7****8979` in href but displayed `98490 12345` — fix both
- **Theme color meta**: Update `<meta name="theme-color">` to light value
- **Unicode in source**: HTML may contain literal Unicode (₹) or escapes (\u20B9) — handle both
- **Complete feature removal**: When deleting a component (hero-pin, theme toggle, custom cursor), remove HTML, CSS rules, AND JS references — don't just hide with CSS
- **Contact form UX**: Opening WhatsApp with pre-filled message is better than fake success screen; user sends manually
- **Footer giant nowrap**: `flex-wrap:nowrap; white-space:nowrap; overflow-x:auto` keeps brand name on one line
- **Budget dropdown**: Use actual Unicode symbols (₹) in HTML, not escapes, for reliable rendering

## Files Changed This Session
- `/home/painarise/Downloads/dizitrends-new/index.html` — migrated single-page UI
- `/home/painarise/Downloads/dizitrends-new/privacy.html` — standalone light page
- `/home/painarise/Downloads/dizitrends-new/terms.html` — standalone light page
- `/home/painarise/Downloads/dizitrends-new/images/` — copied from old site

## Source Files (Old DiziTrends)
- `/home/painarise/Downloads/public_html (1)/*.php` — 7 pages
- `/home/painarise/Downloads/public_html (1)/includes/*.php` — header, footer, analytics
- `/home/painarise/Downloads/public_html (1)/css/style.css` — old styling
- `/home/painarise/Downloads/public_html (1)/images/` — logo, favicon, 20 portfolio images

## Target Template
- `/home/painarise/Downloads/DOCTYPE html html lang.html` — Quivane-style single-file UI with Lenis/GSAP, data-driven sections, dark/light theme, custom cursor, preloader, page transitions

## New Patterns This Session

### Complete Animation/Component Removal
- **Pinwheel spin**: Remove `data-spin` attrs, `.spin` CSS class, `@keyframes spin`, JS ticker animation block (`pinEl`, `pinBlades`, `pinRot`, `pinTilt`)
- **Hero-pin element**: Delete HTML, CSS rules (`.hero-pin`, `.hero-pin svg`, `.pin-tilt`), JS animations (`pageIntro`, `PAGE_INIT.home()`)
- **Theme system**: Remove `data-theme` attr, theme boot script, theme-toggle button, `:root[data-theme]` CSS blocks, theme JS, media query overrides
- **Custom cursor**: Remove cursor HTML (`.cursor-dot`, `.cursor-ring`), CSS, JS ticker block

### Contact Form → WhatsApp
```js
const wa = 'https://wa.me/+91XXXXXXXXXX?text=' + encodeURIComponent(
  'New Contact Form Submission:\n\nName: ' + $('#cfName').value +
  '\nEmail: ' + $('#cfEmail').value +
  '\nPhone: ' + ($('#cfPhone').value || 'Not provided') +
  '\nBudget: ' + $('#cfBudget').value +
  '\nService: ' + $('#cfService').value +
  '\nMessage: ' + $('#cfMsg').value
);
window.open(wa, '_blank');
toast('Opening WhatsApp...', 'Send the message from WhatsApp to reach us.');
```
No fake success screen, no form reset auto-reveal.

### Budget Dropdown with Real Unicode
```html
<select id="cfBudget">
  <option>Under ₹25,000</option>
  <option selected>₹25,000 – ₹1,00,000</option>
  <option>₹1,00,000+</option>
  <option>Project-based</option>
</select>
```

### Footer Giant — Brand on One Line
```css
.foot-giant {
  display:flex; justify-content:space-between;
  flex-wrap:nowrap; white-space:nowrap;
  overflow-x:auto;
}
.foot-giant .mask { flex-shrink:0; }
```
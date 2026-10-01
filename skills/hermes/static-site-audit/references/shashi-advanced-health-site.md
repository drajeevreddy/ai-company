# Shashi Advanced Health — site map & known issues

Site: shashiadvancedhealth.com (Hostinger). Endocrinology/diabetes/thyroid clinic chain, Bangalore. Recurring audit target for the user.

## Project layout (as of Aug 2026)

- `~/shashi-advanced-health-fixed-source/shashi aug/` — full site source (zip sibling exists). **NOT under git.**
  - Main site: 264 static HTML pages, extensionless internal links (`doctors`, `services`, `blog`, `contact`) resolved by Apache MultiViews on Hostinger. Main pages audit clean.
  - `blog/` — PHP blog app: clean URLs via `blog/.htaccess` rewrite to `post.php?slug=`, posts as JSON in `blog/data/posts/`, uploads in `blog/uploads/`, admin in `blog/admin/`.
  - `dr mahesh book/` — separate endocrine-atlas sub-project (folder name has a SPACE). Contains canonical `topics/` (136 files) + `hostinger_upload/` staging copy (70 files — BROKEN, see below).
  - `contact-submissions/` — PHP contact-form store with per-IP rate-limit JSON.
- `~/shashi-advanced-health-seo/` — SEO content kit: blog-posts/, meta-descriptions/, schema-markup/, gbp-optimization/, doctor-profiles/, technical-seo/.

## Known issues (audit 2026-08-05)

1. 🔴 `dr mahesh book/hostinger_upload/` staging copy is broken: 66 of 136 topic pages missing from `topics/`; mixed link depths for `endocrine-atlas.html`/`contact.html` (`../../../` vs `../../../../` vs `../../../../../`) — ~80 links resolve to 404. Do NOT upload this copy as-is.
2. 🟠 Canonical book: `dr mahesh book/index.html` links `topics/bone-calcium/albright-hereditary-osteodystrophy.html` but the file is named `aho.html`.
3. 🟠 `blog/data/admin.json` ships default credentials (admin / Admin@123); `blog/admin/includes/auth.php` auto-creates it if missing. `.htaccess` blocks direct web access to blog/data/, but change the password before going live.
4. 🟡 `endocrine-atlas.html` links into the book folder with `%20`-encoded `dr%20mahesh%20book/...` (132 links). Works, but renaming the folder to `dr-mahesh-book/` requires rewriting those links together.
5. 🟡 Project not under git — recommended `git init` + first commit.

## GA4
- `audit_report.md` in site root: June 2026 GA4 export audit. Known discrepancies (all GA4 export-config, not site bugs): event-count mismatch 1650 vs 1653, new-users vs first-user-source gap 214 vs 216, missing Platform dimension rows.

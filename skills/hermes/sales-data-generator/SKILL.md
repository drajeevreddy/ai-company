---
name: sales-data-generator
description: Generate realistic sales CSVs with Excel and PDF output.
version: 0.1.0
author: Rajeev Reddy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sales, data, csv, excel, pdf, report]
    related_skills: [pdf, nano-pdf, xlsx]
---

# Sales Data Generator Skill

Generate realistic sales datasets with 600+ entries, proper financial formatting (₹ with GST), and formatted Excel/PDF deliverables.

## When to Use

- User wants a fake but realistic sales dataset
- User needs CSV, Excel, or PDF sales reports
- User wants sales split between specific salespeople
- User needs dashboard summaries with category/city/year breakdowns

## How to Run

1. Determine requirements: entry count (typically 650), total revenue target (typically ₹3.2 Cr), salesperson names and split ratios, company name sources (real brands vs fictional), output formats (CSV, XLSX, PDF).

2. Write Python using `csv`, `random`, `datetime`.

3. Generate entries with: random dates across 3 years, category-based pricing, 18% GST, realistic payment methods (NEFT, RTGS, UPI, Cash, Credit Card, Cheque), Status field.

4. Scale amounts via uniform scale factor to hit target total.

5. Export CSV via `csv.DictWriter` (always use `f'{val:,.2f}'` for numbers). Excel via `openpyxl` with color-coded rows, frozen header, auto-filter, summary sheets, charts. PDF via WeasyPrint from HTML.

## Key Formulas

```
Subtotal = Qty × Unit Price
GST = Subtotal × 0.18
Total = Subtotal + GST
New Total = Old Total × (Target / Current)
New Subtotal = New Total / 1.18
New GST = New Total - New Subtotal
```

## Pitfalls

- **Column name mismatch between dict and header**: if headers say "Company Name" but dict key is "Company", all values in that column will be blank. Always verify keys match headers exactly.
- **Invoice numbers must be assigned AFTER sorting by date**.
- **Always verify**: row count, total sum, salesperson split, zero empty cells.
- **WeasyPrint + f-strings**: avoid `{{` in f-string HTML — use template approach.

## References

- `references/website-meta-audit.md` — meta/header audit checklist for websites

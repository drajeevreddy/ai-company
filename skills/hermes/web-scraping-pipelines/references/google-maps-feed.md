# Google Maps Internal Feed — Extraction Recipe

Validated Aug 2026 with Playwright headless Chromium on Fedora. The Maps UI page
(`/maps/search/...`) is a JS shell containing zero place data. All listing data
arrives via XHR to `google.com/search?tbm=map&authuser=0&hl=en&gl=in&q=<query>&pb=<blob>`.

## Capture pattern

```python
bodies = []
def on_resp(resp):
    if "/search?" in resp.url and "tbm=map" in resp.url:
        t = resp.text()
        if len(t) > 5000:
            bodies.append(t)
pg.on("response", on_resp)
```

Then load `https://www.google.com/maps/search/<query>?hl=en&gl=in`, wait for
`div[role="feed"]`, and scroll it repeatedly:

```python
feed.evaluate("el => el.scrollBy(0, el.scrollHeight)")
```

Stop when `"reached the end of the list"` appears in `pg.content()` or the place-link
count (`a[href*="/maps/place"]`) is unchanged for 3 consecutive scrolls. Each scroll
triggers one new feed page (~20 records) as a separate tbm=map response.

## Response envelope formats (BOTH occur in one session)

1. Raw: body starts with `)]}'` followed by newline-delimited JSON arrays.
2. Wrapped: body is `{"c":0,"d":"<escaped inner payload>","e":...,"p":...,"u":...}/*""*/`.

Robust unwrap:

```python
if body_text.lstrip().startswith("{"):
    env, _ = json.JSONDecoder().raw_decode(body_text.lstrip())  # trailing /*""*/ breaks json.loads
    body_text = env.get("d", "")
data = json.loads(body_text.split(")]}'", 1)[1].strip())
```

## Place-record signature and field layout

A place record is a long list (>150 slots). Signature: slot 10 is a fid string
matching `0x...:0x...` and slot 11 is the name.

| Slot | Content |
|---|---|
| `[2]` | address lines list (street, sublocal, city, "City, State PIN") |
| `[4][7]` | star rating (float; absent/None for unrated) |
| `[4][8]` | review count (int) |
| `[9]` | `[null, null, lat, lon]` |
| `[10]` | feature id `0x..:0x..` (dedupe key) |
| `[11]` | name (often with marketing suffixes: "\| Best...", "- Top...") |
| `[13][0]` | category ("Diabetologist", "Diabetes center", ...) |
| `[39]` | single-line full address |
| `[78]` | place_id `ChIJ...` |
| `[178]` | list of contact blocks; phone = `blk[3]` display + normalized digits |

Phone extraction:

```python
for blk in r[178]:
    p = blk[3]
    if isinstance(p, str) and re.fullmatch(r"\+?[0-9][0-9 \-\d]{7,15}", p.strip()):
        phones.append(re.sub(r"[^\d+]", "", p))
```

Ratings/reviews are sometimes on a companion 9-slot entry adjacent to the main
record (`[7]=rating float, [8]=count int`) — when the main record's `[4]` is None,
scan neighbors before concluding "unrated".

## Coverage model

- One query returns at most ~120 results (6 feed pages × 20).
- For country-scale coverage: sweep many geographic queries (71 Indian cities ×
  specialty worked well), dedupe globally by place_id.
- Yield: metros ~115–120 records/query; small cities 5–80. Overall ~97% of records
  carry a phone number.
- Politeness that avoided blocks for a 142-query run: 1.8–3.2 s between scrolls,
  2–5 s between queries, stable UA, timezone Asia/Kolkata.

## Known limits

- ~120-result cap per query means the long tail of any metro is not visible.
- Entries are whatever Maps lists — clinics/centres appear alongside individuals.
- Layout indices are current as of Aug 2026; re-validate by dumping one body and
  walking slots before trusting them blindly.

# Next.js RSC Protocol — Extracting Structured JSON from JS Shells

When a Next.js App Router site renders data client-side and curl returns an empty
or shell HTML (e.g. diabetes.co.in, justdial-style defenses), send an RSC
(React Server Components) request to get the same structured JSON the browser uses
internally.

## RSC request pattern

```
curl -sL \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
  -H 'RSC: 1' \
  -H 'Accept: text/x-component' \
  'https://example.com/path'
```

The response is the RSC flight-data stream (line-based).
- Lines starting with a number (e.g. `0:`, `1:`) are JSON objects
- Lines starting with `I[...]` are component references

## Extracting embedded JSON

### Method 1: Regex on known data blocks
If the page embeds data like `initialDoctors":[...]`, extract directly:

```python
import re, json

rsc = fetch_rsc(url)

# Full doctor objects with all fields
full_pattern = r'\{"id":"[a-f0-9-]+","name":"(Dr\. [^\"]+)","username":"[^\"]+","avatarUrl":"[^\"]+","degree":"[^\"]*","specialization":"[^\"]*"\}'
# Minimal objects (missing degree/specialization)
minimal_pattern = r'\{"id":"[a-f0-9-]+","name":"(Dr\. [^\"]+)","username":"[^\"]+","avatarUrl":"[^\"]+"\}'

full_matches = re.findall(full_pattern, rsc)
minimal_matches = re.findall(minimal_pattern, rsc)
```

### Method 2: Extract arrays with balanced-brace parsing
For arrays like `mapMarkers":[...],"mapAccessToken":`:

```python
markers_match = re.search(r'mapMarkers":(\[.*?\]),"mapAccessToken"', rsc, re.DOTALL)
if markers_match:
    markers = json.loads(markers_match.group(1))
```

## Pagination with random offsets

Some sites (e.g. diabetes.co.in) use **randomized pagination**: each `offset=`
value returns a *different random set* of ~90 records, not sequential pages.
Implications:
- Standard `?page=N` pagination will NOT work as expected
- Collecting all records requires many random/large offsets to achieve coverage
- Each 15-step offset returns mostly unique records; diminishing returns after ~500
- The total record count is unknown; estimate by collecting until new-unique-rate drops

Strategy: sweep offsets in a stepped pattern (0, 15, 30, ... up to several hundred,
then larger jumps 500, 1000, 2000, 5000, 10000, ...) and union the results.

## Profile page extraction

Individual entity pages (e.g. `/dr-name`) also return RSC data. Doctor details are in
the metadata section:

```python
# Title: "Dr. NAME, DEGREE"
title_match = re.search(r'"title","0",\{"children":"(Dr\. [^\"]+)"\}', rsc)
if title_match:
    parts = title_match.group(1).split(', ', 1)
    degree = parts[1] if len(parts) > 1 else ''

# Meta description: "Dr. NAME, SPECIALIZATION - DEGREE, ..."
meta_match = re.search(r'"name":"description","content":"([^"]+)"', rsc)
if meta_match:
    header = meta_match.group(1).split(' - ', 1)[0]
    spec_match = re.search(r',\s*(.+)$', header)
    specialization = spec_match.group(1) if spec_match else ''
```

Clinic/address info appears in the clinics section as component children:
`"children":"Clinic Name"` near the clinic section.

## Caveats

- The `RSC: 1` header sometimes returns HTTP 500 (server-side rendering error);
fall back to the browser tool in that case
- Profile pages may have empty `__next_f` push data; the RSC flight format embeds
data inline as flat text, which is denser but harder to parse than the
`__next_f.push()` encoded format
- Some sites return different data to RSC requests vs. browser requests (caching/delivery
differences); verify record counts match
- The `initialHasMore` flag in the JSON may be stale (True even when no new records
arrive at the next offset) due to the randomized seed mechanism
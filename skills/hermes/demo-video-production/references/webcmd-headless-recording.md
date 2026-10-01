# Headless screen recording via webcmd (proven recipe)

Capture a web app's own browser surface as video when no desktop GUI capture works
(cua-driver 0x0, Camofox down, etc.). The stealth Chromium behind webcmd exposes
`getDisplayMedia` to page JS and auto-grants it — so the page records ITSELF via
MediaRecorder. No CDP (`newCDPSession` is blocked inside `browser run`), no ffmpeg x11grab.

## Session pattern

```
webcmd session create                      # → "id: session_<uuid>"
printf 'return await page.title();' | webcmd --session <id> browser run --stdin
webcmd session close <id>
```

Or write programs to a file: `webcmd --session <id> browser run --file prog.js --timeout 45 --max-output 1200000`.
Default output cap is ~64KB — MUST raise `--max-output` for binary/base64 slices.

## QuickJS sandbox rules (browser run)

- Program runs in a QuickJS sandbox; Playwright APIs on `page` only.
- **`document`, `window`, `navigator`, `fetch` DO NOT EXIST at program top level** — they exist
  ONLY inside `page.evaluate(() => {...})`. A stray top-level DOM call fails with
  `'document' is not defined`. (This bit twice in one session.)
- `page.waitForResponse` / network events work; SSE pages never reach `networkidle`
  — use `waitUntil: 'domcontentloaded'`.

## CRITICAL: passing data into evaluate()

NEVER string-interpolate user/query data into the evaluate body — backslash escaping through
the generator gets doubled (`\\d` in source ⇒ literal `\d` in the regex ⇒ silent zero matches).
Pass data as an evaluate ARGUMENT instead:

```js
return await page.evaluate((qTokens) => {
  const PACK_RE = /^(?:\d+\s*(?:tablet|bottle)...)/i;   // single-escaped, lives in ONE place
  ...
}, JSON.parse('["thyronorm","50"]'));                      // arg, not interpolation
```

Debugging loop that worked: replicate the generated program inline via `--stdin`/`--file`,
compare against production output, dump `JSON.stringify(line)` of emitted lines to see real escaping.

## Capture recipe (in-page recorder)

```js
// start (run once):
return await page.evaluate(async () => {
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: { width:1920, height:1080, frameRate:12 } });
  if (!stream || !stream.getVideoTracks().length) return { started:false };
  window.__chunks = [];
  window.__rec = new MediaRecorder(stream, { mimeType:'video/webm;codecs=vp8', videoBitsPerSecond:2500000 });
  window.__rec.ondataavailable = e => { if (e.data && e.data.size) window.__chunks.push(e.data); };
  window.__rec.start(1000);
  return { started:true };
});
```

During recording: drive the app via its HTTP API from the host script (curl/fetch), timed to beats.

```js
// stop (separate run — keep each run short):
return await page.evaluate(async () => {
  if (window.__rec.state !== 'inactive') { const d=new Promise(r=>window.__rec.onstop=r); window.__rec.stop(); await d; }
  window.__size = window.__chunks.reduce((a,c)=>a+c.size,0);
  return { stopped:true, chunks:window.__chunks.length, bytes:window.__size };
});
```

```js
// encode to base64 (separate run — blob→b64 can take >30s for multi-MB):
return await page.evaluate(async () => {
  if (window.__b64) return { b64len: window.__b64.length };
  const blob = new Blob(window.__chunks, { type:'video/webm' });
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let bin=''; for (let i=0;i<bytes.length;i+=0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i,i+0x8000));
  window.__b64 = btoa(bin); window.__chunks = null;
  return { b64len: window.__b64.length };
});
```

Pull base64 out in ~700KB slices (`window.__b64.slice(off, off+N)` per run) with
`--max-output 1200000`, join, write via `Buffer.from(b64,'base64')`.

## Mux + QC

```
ffmpeg -y -i screen.webm -i narration.mp3 -c:v libx264 -preset veryfast -crf 26 \
  -pix_fmt yuv420p -c:a aac -b:a 128k -shortest -movflags +faststart final.mp4
ffmpeg -ss <t> -i final.mp4 -vframes 1 frame.png    # QC frames at key beats → vision-check them
```

Real-world numbers: ~100s capture @1080p ≈ 6MB webm ≈ 8MB b64 (12 slice pulls) → 3.5MB final mp4.
Full working implementation: ~/slotdeck/scripts/record-demo.mjs.

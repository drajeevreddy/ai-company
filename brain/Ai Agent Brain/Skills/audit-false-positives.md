# Audit false positives

Written after the Crestorflow audit (62 findings, 6 parallel workstreams, a pentest-ai MCP pass). The MCP's automated output was **93% false positive**. Every real finding in that audit came from reading source and hand-driving a proof; the tooling produced leads and noise in roughly equal measure.

The rule: **a finding is not a finding until you have tried to disprove it.** Half the work of an audit is deleting things that look wrong and are not. Report a false positive as a finding and you burn the owner's trust on the ones that matter.

## The catalogue

**An SPA catch-all manufactures "exposed path" findings for free.** With `/* /index.html 200`, every path returns 200 with the app shell, so a path-probe heuristic reports `/admin`, `/debug`, `/actuator`, `/.env`, `/.git/config` as reachable. Prove it by `md5sum`-ing the response against `/` — byte-identical means it is the shell, not a finding. In the Crestorflow run this was *all 15* of the scanner's "medium vulnerabilities". The catch-all itself is still worth raising (the app cannot distinguish a route from a typo), but as one finding, not fifteen.

Corollary: missing assets that *do* carry a known file extension correctly 403 from S3, and the 403 body is byte-identical for missing and forbidden — so there is no enumeration oracle either way. Do not report that as either a leak or a hardening miss.

**Secret patterns match inside ordinary words.** `sk-[A-Za-z0-9]{20,}` matches `di**sk-for**ensics`, `ta**sk-con**currency`, `ri**sk-a**ssessment`. Anchor the pattern (`(?<![A-Za-z])sk-[A-Za-z0-9]{24,}(?![A-Za-z])`) *and* read every hit in context before reporting. A raw count is not evidence.

**Documented example credentials are not leaks.** `AKIAIOSFODNN7EXAMPLE` is the AWS canonical example key; `ghp_xx...xxxx` is a placeholder. Expect both in security-education content, where they are the *point*. Report them as cleared, not as findings.

**Transparent text computes to a bogus contrast ratio.** A gradient-clipped display wordmark with `rgba(0,0,0,0)` colour measures ~1.0:1 against any background. Exclude any colour with `alpha === 0`, and any element whose effective background is a `background-image` you cannot resolve — otherwise the report fills with artefacts and the real 1.08:1 failures get lost in them.

**A page can pass in one theme and be blank in the other.** The single highest-severity bug in the Crestorflow audit was invisible to a reviewer who looked once: `text-white` renders correctly on the dark theme and computes to `rgb(236,237,240)` on a `rgb(245,246,248)` light background — **1.08:1**, not low contrast, *invisible*. Set the theme storage key and `color-scheme` in an init script before load, then measure per theme. Chasing the root cause to `tailwind.config.js` (`textColor.white` pinned to the dark theme's literal, theme-blind) is what turned "334 bad call sites" into a one-line diagnosis.

**Do not accept the obvious one-line fix without checking what else it moves.** That same `text-white` was correct on coloured surfaces — `bg-brand-blue`, `bg-[#8b5cf6]`, `bg-brand-gradient`. Rebinding the token to `var(--color-text-main)` turns those CTAs black-on-blue. The correct fix is per-instance: 5 of 13 hits on `/board`.

**"Ungated function" is usually a scanner artefact.** A public handler gated by a *private* helper reads as ungated. Brace-match each exported handler body, flag the ones with no exported-helper call and no direct identity read, then read every flagged body by hand. In Crestorflow, all 14 flagged functions were gated by `setProgressFlag` / `requireOpenPart`-style private helpers.

**A concurrency finding needs the mechanism, not the shape.** "Read-then-write" is only a finding when the read and the write straddle the paid/side-effecting call *and* the dedup key cannot rescue it. `verification.verify` qualified because the idempotency key was a fresh `randomUUID()` per call, so the idempotency lookup could never dedupe. Without that detail it is just a code smell.

**Unreachable-from-here is not the same as absent.** The live harness measured exactly one `<h1>` on every public page, refuting a static-audit claim of two — but the pages that claim was about (`GroupPage`, `BuildPage`) sit behind auth and were unreachable. Label it unverified, do not silently drop it and do not report it as confirmed.

## Auditing delegated workstreams

Fanning an audit out to parallel subagents is right for coverage and wrong as a finish line.

- **Diff the child's finding list against the report item by item.** In the Crestorflow run a genuine MEDIUM (two entry points claiming the same artifact row under different cache keys) was read but never itemised, because it sat under higher-severity items while skimming. Diff by count and by topic, not by memory.
- **Re-examine severities the child set higher than you did.** That same workstream rated a confirmed double-billing HIGH while the report had it MEDIUM, and it was right — the impact class was the one the threat model named as primary.
- **Re-probe every live-behaviour claim yourself.** One child asserted a build file was "publicly readable at `/_headers`"; a live probe showed the SPA rewrite answering that path with the shell, so it was source hygiene, not exposure. Claims about *source* are cheap to check and usually sound. Claims about *live behaviour* are where children drift.
- Children over-claim in both directions. Never transcribe a child's summary into a report without the check above.

## Before publishing anything derived from this work

A secret-shape scan does not make a tree safe to publish. It matches key *shapes* only, and two other classes ride along without tripping it:

- **Personal identifiers** — phone numbers, emails, chat ids, handles. Found in 5 skill files headed for a public repo: the owner's mobile and Gmail written into hardening checklists and migration notes, plus a third-party client's phone. Redacted before push. A hit on a *machine path* or a *display name* is a false positive; a hit on an identifier is a finding.
- **Client and engagement detail** — this vault's own `Projects/` notes name clients and carry business specifics. Publishing the vault to a public repo publishes those. Decide the destination with that in mind.

Build a pattern file of the actual values (from `.env`, config, and known identifiers) and grep the **finished** artifact by value, not by shape. Read every hit. `scripts/verify-no-value-leaks.sh` in the portability skill does this.

See also: [[Skills/verify-by-running-it]] · [[Projects/Crestorflow]] · [[System/Code-Quality-Bar]]

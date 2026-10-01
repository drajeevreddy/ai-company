---
name: third-party-license-audit
description: Verify a third-party license boundary before building.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Licensing, Compliance, Dependencies, Open Source, AGPL]
    related_skills: []
    editorial_name: Third-Party License Audit
    editorial_description: Establish what may legally be imported, forked, vendored or image-baked before a build depends on it.
    requires_tools: [terminal, read_file, write_file, search_files]
---

# Third-party license audit

## When this applies

The user wants to build on, extend, self-host, white-label, or vendor an external project — a CRM, a UI library, a registry of components, a coding CLI. Before any code is written, establish what may legally be imported, forked, vendored, or baked into an image. This is architectural licensing, not vulnerability scanning: the question is "may we depend on this at all, in this way", not "has this package got a CVE".

## Procedure

1. **Read the repo's own license signal, then distrust it.**

```bash
curl -s https://api.github.com/repos/<org>/<repo> | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('license') or {}).get('spdx_id'), d.get('default_branch'))"
```

`NOASSERTION`, a missing field, or a custom `LICENSE` means the root file is the actual answer. Read it: mature projects publish a *split* — a copyleft core, a permissive subset, and files under a commercial header. The qualification paragraphs are the whole point; the SPDX badge is not.

2. **Enumerate per-package licenses in a monorepo.** A sibling package can be permissive while its neighbour is copyleft, and the SDK you need is often the permissive one.

```bash
R=https://raw.githubusercontent.com/<org>/<repo>/<branch>/packages
for p in $(curl -s https://api.github.com/repos/<org>/<repo>/contents/packages | python3 -c "import sys,json;print(' '.join(x['name'] for x in json.load(sys.stdin)))"); do
  printf '%-34s ' "$p"
  curl -s "$R/$p/package.json" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('license'),'| bin:',list((d.get('bin') or {}).keys()) if isinstance(d.get('bin'),dict) else d.get('bin'))" 2>/dev/null || echo UNREADABLE
 done
```

A package with **no** `license` field is not permissive — the root terms apply, so treat it as the strictest bucket.

3. **Name the sanctioned extension channel and use it.** Vendors document the supported way to customise them: runtime configuration in the product's own settings, a plugin/app framework scaffolded by a permissive CLI, official container images configured only by env vars. Prefer that over forking or patching. It usually avoids copyleft reach by construction, and it survives a review that a fork does not.

4. **Check the binary trap before depending on a CLI.** The package that ships the command you type may not be the package you should install. A deprecated CLI and the permissive SDK often both expose a `bin` with the same name; install the one whose `license` field you verified, and confirm which package declares the bin you actually run.

5. **Grep for the vendor's commercial tier marker and for deprecated packages.**

```bash
grep -rIn "@license Enterprise" --include='*.ts' --include='*.tsx' --include='*.js' . | grep -v node_modules
```

A file-level commercial marker means paid terms regardless of modification, and which files carry it can differ between the community and paid builds of the same feature. Deprecated packages linger in docs, examples and older posts — the current tool is usually a different package on a different license.

6. **Write the verdict where the code will look.** A `LICENSING.md` at the repo root containing: the allowed-package list with licenses, the forbidden list, the extension channels actually used, an explicit assertion that no copyleft source or commercially-marked file is vendored, the firewall commands to run before a release, and an open-questions section flagging that this is an engineering record and needs counsel before commercial launch (white-labeling scope, a copyleft network clause, trademark use, distributing the client to third parties, data-protection duties once logs live on someone's machine).

7. **Enforce it in the build.** Run the package manager's license listing in CI and fail on copyleft identifiers; keep the vendored-file greps in the pre-release checklist. Add a grep asserting that a reference-only project's name appears in prose only, if a repo was read for patterns rather than code.

## Pitfalls

- **A root license badge is not per-package truth.** The LICENSE file is where the split lives; read the paragraphs after the headline.
- **Absence of a license field is not permission.** No declared license means the root terms, which means the strictest reading.
- **Patterns and code are different acts.** Reading a permissively-licensed project to adopt its architecture is fine; copying code, assets, or bundled media that the repo licensed separately from itself is not — including art or font assets sourced under a third-party asset license.
- **Vendor images are configured, not built.** Consuming an official container unmodified through documented env vars is a different act from baking a patched image; the second one is a distribution.
- **Marketplaces are per-item.** For a component or asset marketplace, the aggregate site's license does not cover items contributed by authors, the per-item license field is the operative term, and preview/demo media is often owned separately from the code. Install caps and account requirements at a marketplace are build constraints too — a source that needs an API key and allows two installs a day changes how much of it a design can lean on.
- **Free tier and license are separate questions.** An item can be free to install and still carry terms that block re-publication, training models on it, or commercial reuse of the site's own media.
- **A "deprecated" CLI is a trap for anyone following old docs.** Pin the current package explicitly in the pack so the next agent does not install the dead one.

## Reporting

Report the boundary as three buckets — allowed, forbidden, needs-counsel — with the check command for each, and state plainly what was not verifiable. Never present the analysis as legal advice, in the files or in the reply.

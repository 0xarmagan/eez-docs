# EEZ Docs: Mintlify → Docusaurus Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate all 23 EEZ protocol docs pages from Mintlify (`0xarmagan/mintlify-docs`) into a working Docusaurus site in this repo (`0xarmagan/eez-docs`), preserving URLs, nav grouping, and branding.

**Architecture:** Docusaurus classic template (JavaScript) with two `@docusaurus/plugin-content-docs` instances — default instance (`path: docs`, `routeBasePath: /`) for the "Documentation" tab, and a second instance (`id: contracts`, `path: contracts`, `routeBasePath: /contracts`) for the "Contract Reference" tab. Content is fetched from the live `mintlify-docs` repo and converted per the mapping table in the approved spec.

**Tech Stack:** Docusaurus 3.x (classic preset), Node.js, npm, plain MDX (no custom React components).

## Global Constraints

- Source of truth for every source file: `https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/<path>` — always fetch fresh, never guess content.
- No custom MDX components. Every conversion must use only: built-in admonitions (`:::note`/`:::tip`/`:::info`/`:::warning`/`:::danger`), native `<details><summary>`, plain Markdown tables, plain Markdown headings, plain Markdown bullet/link lists.
- `sidebarTitle` front matter → `sidebar_label`. `title`/`description` unchanged.
- Every task must end with `npm run build` succeeding with zero errors and zero broken-link warnings before committing.
- Plans/specs live under `project/` at repo root — never under `docs/` (that's the live Documentation instance's content folder) or `contracts/` (the Contract Reference instance's content folder).
- Full target-path inventory is in the spec: `project/specs/2026-07-07-mintlify-to-docusaurus-migration-design.md`.

---

### Task 1: Scaffold the Docusaurus project

**Files:**
- Create: everything `create-docusaurus@latest` generates (package.json, docusaurus.config.js, sidebars.js, docs/intro.mdx, src/, static/, etc.)

**Interfaces:**
- Produces: a runnable `npm run start` / `npm run build` Docusaurus site at repo root, for Task 2 to configure.

- [ ] **Step 1: Scaffold into a temp subdirectory (repo root already has `.git` and `project/`, so scaffolding must not run directly into `.`)**

```bash
cd /Users/armagan/eez-docs
npx create-docusaurus@latest .tmp-scaffold classic --javascript
```

If prompted interactively, choose npm as the package manager.

- [ ] **Step 2: Move scaffolded files into repo root, preserving `.git` and `project/`**

```bash
cd /Users/armagan/eez-docs
rsync -a .tmp-scaffold/ ./
rm -rf .tmp-scaffold
ls
```

Expected: `docusaurus.config.js`, `sidebars.js`, `package.json`, `docs/`, `src/`, `static/` now exist alongside `project/` and `.git`.

- [ ] **Step 3: Install dependencies and verify the default site builds**

```bash
npm install
npm run build
```

Expected: build completes with `Generated static files in "build".` and no errors.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Scaffold Docusaurus classic template"
```

---

### Task 2: Configure two docs-plugin instances and branding shell

**Files:**
- Modify: `docusaurus.config.js`
- Create: `sidebars.js` (Documentation instance — start with just the placeholder intro), `sidebarsContracts.js` (Contract Reference instance — starts empty), `contracts/` directory
- Delete: default scaffolded blog (`blog/`), scaffolded `docs/tutorial-basics/`, `docs/tutorial-extras/` (not needed — this site has one flat docs tree per the spec's page inventory)

**Interfaces:**
- Produces: `docusaurus.config.js` with `presets[0][1].docs` = the default (Documentation) instance config, and a `plugins` array entry for the second (`contracts`) instance. Later tasks add real sidebar entries and content files under `docs/` and `contracts/`.

- [ ] **Step 1: Remove unused scaffolded content**

```bash
cd /Users/armagan/eez-docs
rm -rf blog docs/tutorial-basics docs/tutorial-extras
rm -f docs/intro.mdx
mkdir -p contracts
```

- [ ] **Step 2: Create a placeholder doc so the default instance's sidebar has something to point at until Task 5 adds real content**

```bash
cat > docs/introduction.mdx << 'EOF'
---
title: "Introduction"
---

placeholder — replaced in Task 5
EOF
```

- [ ] **Step 3: Write `sidebars.js` (Documentation instance) with a single placeholder entry**

```js
// sidebars.js
export default {
  docsSidebar: [
    { type: 'doc', id: 'introduction' },
  ],
};
```

- [ ] **Step 4: Write `sidebarsContracts.js` (Contract Reference instance) with a placeholder doc + entry**

```bash
cat > contracts/eez.mdx << 'EOF'
---
title: "EEZ.sol Reference"
---

placeholder — replaced in Task 10
EOF
```

```js
// sidebarsContracts.js
export default {
  contractsSidebar: [
    { type: 'doc', id: 'eez' },
  ],
};
```

- [ ] **Step 5: Edit `docusaurus.config.js`** — keep whatever module syntax (`module.exports` vs `export default`) the scaffold already generated; only change/add the keys below. Add the second docs-plugin instance and wire up the navbar:

```js
// In the classic preset's docs options:
docs: {
  sidebarPath: './sidebars.js',
  routeBasePath: '/',
},

// Add a plugins array (sibling to `presets`) with the second instance:
plugins: [
  [
    '@docusaurus/plugin-content-docs',
    {
      id: 'contracts',
      path: 'contracts',
      routeBasePath: 'contracts',
      sidebarPath: './sidebarsContracts.js',
    },
  ],
],

// In themeConfig.navbar.items, replace the scaffolded items with:
items: [
  {
    type: 'doc',
    docId: 'introduction',
    docsPluginId: 'default',
    position: 'left',
    label: 'Documentation',
  },
  {
    type: 'doc',
    docId: 'eez',
    docsPluginId: 'contracts',
    position: 'left',
    label: 'Contract Reference',
  },
  {
    href: 'https://github.com/0xarmagan/eez-core-protocol',
    label: 'GitHub',
    position: 'right',
  },
],
```

Also set `title: 'Ethereum Economic Zone'` and `tagline: 'EEZ enables atomic cross-chain calls between Ethereum rollups in a single L1 block.'` at the top level of the config (values from the source `docs.json`).

- [ ] **Step 6: Build and verify both instances route correctly**

```bash
npm run build
npm run serve &
sleep 3
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/introduction
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/contracts/eez
kill %1
```

Expected: both `curl` calls print `200`.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "Configure two docs-plugin instances (Documentation + Contract Reference)"
```

---

### Task 3: Branding — colors, favicon, logos, footer

**Files:**
- Modify: `src/css/custom.css`, `docusaurus.config.js` (favicon, footer, `themeConfig.colorMode` untouched)
- Create: `static/img/favicon.svg`, `static/img/eez-logo.png`, `static/img/eez-logo-ref.png`, `static/img/01-mark-on-black.png`, `static/img/02-mark-on-purple-50.png`

**Interfaces:**
- Consumes: nothing from earlier tasks besides the scaffolded `src/css/custom.css`.
- Produces: brand colors and assets available to every later page (no interface other tasks call into).

- [ ] **Step 1: Download the brand assets from the source repo**

```bash
cd /Users/armagan/eez-docs
mkdir -p static/img
for f in favicon.svg images/eez-logo.png images/eez-logo-ref.png images/01-mark-on-black.png images/02-mark-on-purple-50.png; do
  curl -sL "https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/$f" -o "static/img/$(basename "$f")"
done
ls -la static/img
```

Expected: 5 files downloaded, all non-zero size.

- [ ] **Step 2: Set the favicon and site logo in `docusaurus.config.js`**

```js
favicon: 'img/favicon.svg',

// In themeConfig.navbar:
logo: {
  alt: 'EEZ Logo',
  src: 'img/eez-logo.png',
},
```

- [ ] **Step 3: Replace the primary color variables in `src/css/custom.css`** (values from source `docs.json`: primary `#6366F1`, light `#818CF8`, dark `#4338CA`)

```css
:root {
  --ifm-color-primary: #6366F1;
  --ifm-color-primary-dark: #4338CA;
  --ifm-color-primary-darker: #3730A3;
  --ifm-color-primary-darkest: #312E81;
  --ifm-color-primary-light: #818CF8;
  --ifm-color-primary-lighter: #A5B4FC;
  --ifm-color-primary-lightest: #C7D2FE;
  --ifm-code-font-size: 95%;
}

[data-theme='dark'] {
  --ifm-color-primary: #818CF8;
  --ifm-color-primary-dark: #6366F1;
  --ifm-color-primary-darker: #4F46E5;
  --ifm-color-primary-darkest: #4338CA;
  --ifm-color-primary-light: #A5B4FC;
  --ifm-color-primary-lighter: #C7D2FE;
  --ifm-color-primary-lightest: #E0E7FF;
}
```

- [ ] **Step 4: Set the footer socials in `docusaurus.config.js`** (values from source `docs.json`)

```js
footer: {
  style: 'dark',
  links: [
    {
      title: 'Community',
      items: [
        { label: 'GitHub', href: 'https://github.com/eez-association' },
        { label: 'Website', href: 'https://eez.io/' },
        { label: 'X', href: 'https://x.com/etheconomiczone' },
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} Ethereum Economic Zone.`,
},
```

- [ ] **Step 5: Build and visually spot-check**

```bash
npm run build
npm run serve &
sleep 3
open http://localhost:3000/introduction
```

Confirm in the browser: primary color is the indigo `#6366F1` (links, active nav item), favicon tab icon loads, footer shows GitHub/Website/X links. Then:

```bash
kill %1
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Apply EEZ branding: colors, favicon, logo, footer"
```

---

### Task 4: Landing page + shared partial

**Files:**
- Create: `src/pages/index.mdx`, `docs/_unaudited-warning.mdx`

**Interfaces:**
- Produces: `docs/_unaudited-warning.mdx`, imported by every later doc/contract page that had `import UnauditedWarning from '/snippets/unaudited-warning.mdx'` in the source. Import path from a file at `docs/<subdir>/<file>.mdx` is `../_unaudited-warning.mdx`; from a file directly in `docs/` it's `./_unaudited-warning.mdx`; from a file under `contracts/` (a sibling top-level dir) it's `../docs/_unaudited-warning.mdx`, adjusted for subdirectory depth (e.g. `contracts/interfaces/*.mdx` uses `../../docs/_unaudited-warning.mdx`).

- [ ] **Step 1: Fetch and convert the shared snippet**

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/snippets/unaudited-warning.mdx
```

Write the result to `docs/_unaudited-warning.mdx`, converting any `<Warning>`/`<Info>`/`<Note>` tags to `:::warning`/`:::info`/`:::note` blocks per the mapping table. The leading underscore in the filename makes Docusaurus treat it as a partial: excluded from the sidebar and not built as a standalone page.

- [ ] **Step 2: Fetch `index.mdx` and convert it**

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/index.mdx
```

Apply these conversions:
- Front matter unchanged (`title`, `description`).
- `<Warning>...</Warning>` → `:::warning ... :::`.
- `<Steps><Step title="...">...</Step></Steps>` → `## Step N — <title>` headings, one per `<Step>`, in source order.
- `<CardGroup cols={N}><Card title="X" href="Y">Z</Card>...</CardGroup>` → a plain Markdown list:
  ```markdown
  - **[X](Y)** — Z
  ```
  one bullet per `<Card>`, in source order.
- Remove the `import UnauditedWarning ...` line and `<UnauditedWarning />` usage if present, replacing with an explicit import from the new partial path (`./_unaudited-warning.mdx` since this file lives in `docs/`) and the same `<UnauditedWarning />` usage — the import line changes, the usage does not.

Write the converted result to `src/pages/index.mdx` (Docusaurus renders `.mdx` files under `src/pages/` directly as standalone pages — no front matter `sidebar_*` fields apply there since it's not part of a docs-plugin instance).

- [ ] **Step 3: Build and verify the homepage renders**

```bash
npm run build
npm run serve &
sleep 3
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/
kill %1
```

Expected: `200`.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Add landing page and shared unaudited-warning partial"
```

---

### Task 5: Documentation — Get Started group (introduction, quickstart, architecture)

**Files:**
- Modify: `docs/introduction.mdx` (replace Task 2's placeholder)
- Create: `docs/quickstart.mdx`, `docs/architecture.mdx`
- Modify: `sidebars.js`

**Interfaces:**
- Consumes: `docs/_unaudited-warning.mdx` from Task 4 (import path `./_unaudited-warning.mdx` since these files live directly in `docs/`).
- Produces: `introduction`, `quickstart`, `architecture` doc IDs, consumed by later tasks' cross-links and by Task 2's navbar `docId: 'introduction'`.

- [ ] **Step 1: Fetch and convert `introduction.mdx`**

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/introduction.mdx
```

Conversions needed (confirmed present in this file): `sidebarTitle` → `sidebar_label`; `import UnauditedWarning from '/snippets/unaudited-warning.mdx'` → `import UnauditedWarning from './_unaudited-warning.mdx'` (usage tag unchanged); `<CardGroup>`/`<Card>` → plain Markdown link list per Task 4's rule. Write to `docs/introduction.mdx`, overwriting the Task 2 placeholder.

- [ ] **Step 2: Fetch and convert `quickstart.mdx`**

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/quickstart.mdx
```

Conversions needed (confirmed present): `sidebarTitle` → `sidebar_label`; `<Warning>...</Warning>` → `:::warning ... :::`. This file already uses plain `## Step N — ...` headings (not the `<Steps>` component), so no heading restructuring is needed. Write to `docs/quickstart.mdx`.

- [ ] **Step 3: Fetch and convert `architecture.mdx`**

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/architecture.mdx
```

Confirmed: this file has no Mintlify JSX components (verified via component scan) — only `sidebarTitle` → `sidebar_label` front matter conversion is needed. Write to `docs/architecture.mdx`.

- [ ] **Step 4: Update `sidebars.js`** to the real Get Started group:

```js
// sidebars.js
export default {
  docsSidebar: [
    {
      type: 'category',
      label: 'Get Started',
      items: ['introduction', 'quickstart', 'architecture'],
    },
  ],
};
```

- [ ] **Step 5: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings (all three pages cross-link each other and `/quickstart`, `/architecture` per the source — these now resolve since `routeBasePath: '/'`).

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Convert Get Started pages: introduction, quickstart, architecture"
```

---

### Task 6: Documentation — Core Concepts group (5 files)

**Files:**
- Create: `docs/concepts/sync-composability.mdx`, `docs/concepts/execution-model.mdx`, `docs/concepts/rolling-hash.mdx`, `docs/concepts/multi-prover.mdx`, `docs/concepts/cross-chain-proxy.mdx`
- Modify: `sidebars.js`

**Interfaces:**
- Consumes: `docs/_unaudited-warning.mdx` from Task 4, import path `../_unaudited-warning.mdx` (these files are one level deeper, under `docs/concepts/`).
- Produces: `concepts/sync-composability`, `concepts/execution-model`, `concepts/rolling-hash`, `concepts/multi-prover`, `concepts/cross-chain-proxy` doc IDs.

- [ ] **Step 1: Fetch and convert each file**, per this per-file conversion list (confirmed via component scan):

| Source | Conversions needed |
|---|---|
| `concepts/sync-composability.mdx` | `<Info>` → `:::info`, `<Note>` → `:::note` |
| `concepts/execution-model.mdx` | `<Accordion>` → `<details><summary>`, `<Note>` → `:::note`, `UnauditedWarning` import path fix |
| `concepts/rolling-hash.mdx` | `<Accordion>` → `<details><summary>`, `<Info>` → `:::info`, `UnauditedWarning` import path fix |
| `concepts/multi-prover.mdx` | `<Accordion>` → `<details><summary>`, `<Info>` → `:::info`, `<Note>` → `:::note`, `UnauditedWarning` import path fix |
| `concepts/cross-chain-proxy.mdx` | `<Accordion>` → `<details><summary>`, `<Note>` → `:::note`, `UnauditedWarning` import path fix |

For every `<Accordion title="X">...</Accordion>` (not wrapped in `<AccordionGroup>` in these 5 files — confirmed no `AccordionGroup` here), convert to:
```html
<details>
<summary>X</summary>

...body...

</details>
```
(blank line after `<summary>` is required for the Markdown body inside to render as Markdown, not raw text).

All 5 files also need `sidebarTitle` → `sidebar_label`.

Fetch each with:
```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/concepts/<name>.mdx
```
and write the converted result to `docs/concepts/<name>.mdx`.

- [ ] **Step 2: Update `sidebars.js`** — add the Core Concepts category after Get Started:

```js
{
  type: 'category',
  label: 'Core Concepts',
  items: [
    'concepts/sync-composability',
    'concepts/execution-model',
    'concepts/rolling-hash',
    'concepts/multi-prover',
    'concepts/cross-chain-proxy',
  ],
},
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert Core Concepts pages"
```

---

### Task 7: Documentation — Guides group (6 files)

**Files:**
- Create: `docs/guides/register-rollup.mdx`, `docs/guides/build-execution-entries.mdx`, `docs/guides/post-verify-batch.mdx`, `docs/guides/bridge-tokens.mdx`, `docs/guides/flash-loans.mdx`, `docs/guides/lookup-calls.mdx`
- Modify: `sidebars.js`

**Interfaces:**
- Consumes: `docs/_unaudited-warning.mdx` from Task 4, import path `../_unaudited-warning.mdx`.
- Produces: `guides/register-rollup`, `guides/build-execution-entries`, `guides/post-verify-batch`, `guides/bridge-tokens`, `guides/flash-loans`, `guides/lookup-calls` doc IDs.

- [ ] **Step 1: Fetch and convert each file**, per this per-file conversion list (confirmed via component scan):

| Source | Conversions needed |
|---|---|
| `guides/register-rollup.mdx` | `UnauditedWarning` import path fix only |
| `guides/build-execution-entries.mdx` | `<Steps>`/`<Step title="X">` → `## Step N — X` headings, `UnauditedWarning` import path fix |
| `guides/post-verify-batch.mdx` | `<Steps>`/`<Step>` → `## Step N — X` headings, `UnauditedWarning` import path fix |
| `guides/bridge-tokens.mdx` | `<Steps>`/`<Step>` → `## Step N — X` headings, `<Warning>` → `:::warning` |
| `guides/flash-loans.mdx` | `<Steps>`/`<Step>` → `## Step N — X` headings, `UnauditedWarning` import path fix |
| `guides/lookup-calls.mdx` | `<Note>` → `:::note`, `UnauditedWarning` import path fix |

For every `<Steps><Step title="X">body</Step>...</Steps>`, convert to sequential `## Step N — X` headings (N starting at 1) with `body` as the section content, dropping the `<Steps>`/`<Step>` wrapper tags entirely. This matches the convention `quickstart.mdx` (Task 5) already uses natively.

All 6 files also need `sidebarTitle` → `sidebar_label`.

Fetch each with:
```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/guides/<name>.mdx
```
and write the converted result to `docs/guides/<name>.mdx`.

- [ ] **Step 2: Update `sidebars.js`** — add the Guides category:

```js
{
  type: 'category',
  label: 'Guides',
  items: [
    'guides/register-rollup',
    'guides/build-execution-entries',
    'guides/post-verify-batch',
    'guides/bridge-tokens',
    'guides/flash-loans',
    'guides/lookup-calls',
  ],
},
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert Guides pages"
```

---

### Task 8: Documentation — Tools group (2 files)

**Files:**
- Create: `docs/tools/trace-decoder.mdx`, `docs/tools/visualizator.mdx`
- Modify: `sidebars.js`

**Interfaces:**
- Produces: `tools/trace-decoder`, `tools/visualizator` doc IDs.

- [ ] **Step 1: Fetch and convert each file**

| Source | Conversions needed |
|---|---|
| `tools/trace-decoder.mdx` | `<Steps>`/`<Step>` → `## Step N — X` headings, `<Warning>` → `:::warning`. Note: this file contains CLI placeholder syntax like `<TRANSACTION_HASH>` inside backtick code spans/fences (e.g. `` `--tx <TRANSACTION_HASH>` ``) — these are NOT JSX components, leave them exactly as-is; they render fine since they're inside code spans. |
| `tools/visualizator.mdx` | `<Steps>`/`<Step>` → `## Step N — X` headings only |

Both need `sidebarTitle` → `sidebar_label`.

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/tools/trace-decoder.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/tools/visualizator.mdx
```

Write converted results to `docs/tools/trace-decoder.mdx` and `docs/tools/visualizator.mdx`.

- [ ] **Step 2: Update `sidebars.js`** — add the Tools category:

```js
{
  type: 'category',
  label: 'Tools',
  items: ['tools/trace-decoder', 'tools/visualizator'],
},
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert Tools pages"
```

---

### Task 9: Documentation — Reference group (2 files)

**Files:**
- Create: `docs/reference/caveats.mdx`, `docs/reference/glossary.mdx`
- Modify: `sidebars.js`

**Interfaces:**
- Produces: `reference/caveats`, `reference/glossary` doc IDs — consumed by earlier tasks' links to `/reference/glossary#based-rollup`, `/reference/glossary#executionentry`, `/reference/glossary#transient-vs-deferred` (these now resolve since `reference/glossary` builds to `/reference/glossary`, matching `routeBasePath: '/'`).

- [ ] **Step 1: Fetch and convert each file**

| Source | Conversions needed |
|---|---|
| `reference/caveats.mdx` | `<Note>` → `:::note`, `<Warning>` → `:::warning` |
| `reference/glossary.mdx` | No components (confirmed via scan) — only `sidebarTitle` → `sidebar_label` |

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/reference/caveats.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/reference/glossary.mdx
```

Write converted results to `docs/reference/caveats.mdx` and `docs/reference/glossary.mdx`. Confirm `glossary.mdx` retains its heading anchors (e.g. `## Based rollup`, `## ExecutionEntry`, `## Transient vs deferred`) exactly as in the source — anchor text changes would break the cross-links from Task 5/6's pages.

- [ ] **Step 2: Update `sidebars.js`** — add the Reference category (last one in the Documentation sidebar):

```js
{
  type: 'category',
  label: 'Reference',
  items: ['reference/caveats', 'reference/glossary'],
},
```

- [ ] **Step 3: Build and verify — full Documentation instance link check**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings. This is the first build where every page in the Documentation tab exists, so this is the definitive check that all internal `/introduction`, `/quickstart`, `/architecture`, `/concepts/...`, `/guides/...`, `/tools/...`, `/reference/...` cross-links resolve.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert Reference pages — Documentation instance complete"
```

---

### Task 10: Contract Reference — L1 Contracts (eez, rollup, bridge)

**Files:**
- Modify: `contracts/eez.mdx` (replace Task 2's placeholder)
- Create: `contracts/rollup.mdx`, `contracts/bridge.mdx`
- Modify: `sidebarsContracts.js`

**Interfaces:**
- Consumes: `docs/_unaudited-warning.mdx` from Task 4, import path `../docs/_unaudited-warning.mdx` (these files live in the sibling top-level `contracts/` dir, one level deep relative to repo root, matching `docs/`'s depth).
- Produces: `eez`, `rollup`, `bridge` doc IDs in the `contracts` docs-plugin instance, consumed by Task 2's navbar `docId: 'eez'`.

- [ ] **Step 1: Fetch and convert each file**

| Source | Conversions needed |
|---|---|
| `contracts/eez.mdx` | `<Info>` → `:::info`, `<AccordionGroup>` (wrapper — drop the tag, keep children) / `<Accordion title="X">` → `<details><summary>X</summary>`, `<ParamField path="p" type="T" required>body</ParamField>` → a row in a `\| Name \| Type \| Description \|` table under a `#### Parameters` heading, `<ResponseField name="n" type="T">body</ResponseField>` → a row in a `\| Name \| Type \| Description \|` table under a `#### Returns` heading, `UnauditedWarning` import path fix |
| `contracts/rollup.mdx` | Same component set as `eez.mdx` — `<Info>`, `<AccordionGroup>`/`<Accordion>`, `<ParamField>`, `<ResponseField>`, `UnauditedWarning` import path fix |
| `contracts/bridge.mdx` | `<AccordionGroup>`/`<Accordion>`, `<ParamField>`, `<ResponseField>`, `<Warning>` → `:::warning` |

Concretely, for each `<Accordion title="functionName — description">` block containing `#### Parameters` with one or more `<ParamField path="name" type="Type" required>description text</ParamField>` and a `#### Returns` with `<ResponseField name="name" type="Type">description text</ResponseField>`, produce:

```markdown
<details>
<summary>functionName — description</summary>

...(unchanged prose, "Who can call it", "Reverts if", "Emits", the ```solidity code block)...

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| `name` | `Type` | description text |

#### Returns

| Name | Type | Description |
| --- | --- | --- |
| `name` | `Type` | description text |

...(unchanged #### Errors table, already plain Markdown in the source)...

</details>
```

Drop the `required` attribute (not representable in a 3-column table — Solidity function parameters are implicitly required unless the prose says otherwise, which is preserved in the Description column).

Fetch each with:
```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/eez.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/rollup.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/bridge.mdx
```

Write to `contracts/eez.mdx` (overwriting Task 2's placeholder), `contracts/rollup.mdx`, `contracts/bridge.mdx`.

- [ ] **Step 2: Update `sidebarsContracts.js`** to the real L1 Contracts group:

```js
// sidebarsContracts.js
export default {
  contractsSidebar: [
    {
      type: 'category',
      label: 'L1 Contracts',
      items: ['eez', 'rollup', 'bridge'],
    },
  ],
};
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert L1 Contracts reference pages: eez, rollup, bridge"
```

---

### Task 11: Contract Reference — L2 Contracts + Data Types (eezl2, data-types)

**Files:**
- Create: `contracts/eezl2.mdx`, `contracts/data-types.mdx`
- Modify: `sidebarsContracts.js`

**Interfaces:**
- Produces: `eezl2`, `data-types` doc IDs.

- [ ] **Step 1: Fetch and convert each file**

| Source | Conversions needed |
|---|---|
| `contracts/eezl2.mdx` | `<Note>` → `:::note`, `<ParamField>` → Parameters table row, `<ResponseField>` → Returns table row (no `<Accordion>` in this file — confirmed via scan), `UnauditedWarning` import path fix |
| `contracts/data-types.mdx` | `<ResponseField>` → table row only (confirmed no other components) |

Apply the same `<ParamField>`/`<ResponseField>` → table conversion rule defined in Task 10.

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/eezl2.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/data-types.mdx
```

Write to `contracts/eezl2.mdx`, `contracts/data-types.mdx`.

- [ ] **Step 2: Update `sidebarsContracts.js`** — add L2 Contracts and Data Types categories after L1 Contracts:

```js
{
  type: 'category',
  label: 'L2 Contracts',
  items: ['eezl2'],
},
{
  type: 'category',
  label: 'Data Types',
  items: ['data-types'],
},
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert L2 Contracts and Data Types reference pages"
```

---

### Task 12: Contract Reference — Interfaces (3 files)

**Files:**
- Create: `contracts/interfaces/iproofsystem.mdx`, `contracts/interfaces/irollupcontract.mdx`, `contracts/interfaces/imetacrosschainreceiver.mdx`
- Modify: `sidebarsContracts.js`

**Interfaces:**
- Consumes: none besides earlier pages' cross-links.
- Produces: `interfaces/iproofsystem`, `interfaces/irollupcontract`, `interfaces/imetacrosschainreceiver` doc IDs — completes the Contract Reference instance.

- [ ] **Step 1: Fetch and convert each file**

| Source | Conversions needed |
|---|---|
| `contracts/interfaces/iproofsystem.mdx` | `<ParamField>`/`<ResponseField>` → tables (no Accordion in this file — confirmed via scan) |
| `contracts/interfaces/irollupcontract.mdx` | `<ParamField>`/`<ResponseField>` → tables |
| `contracts/interfaces/imetacrosschainreceiver.mdx` | No components at all (confirmed via scan) — only `sidebarTitle` → `sidebar_label` |

```bash
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/interfaces/iproofsystem.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/interfaces/irollupcontract.mdx
curl -s https://raw.githubusercontent.com/0xarmagan/mintlify-docs/main/contracts/interfaces/imetacrosschainreceiver.mdx
```

Write to `contracts/interfaces/iproofsystem.mdx`, `contracts/interfaces/irollupcontract.mdx`, `contracts/interfaces/imetacrosschainreceiver.mdx`.

- [ ] **Step 2: Update `sidebarsContracts.js`** — add the Interfaces category (last one):

```js
{
  type: 'category',
  label: 'Interfaces',
  items: [
    'interfaces/iproofsystem',
    'interfaces/irollupcontract',
    'interfaces/imetacrosschainreceiver',
  ],
},
```

- [ ] **Step 3: Build and verify — full Contract Reference instance link check**

```bash
npm run build
```

Expected: zero errors, zero broken-link warnings. This is the definitive check for the entire `contracts` instance, including links from `contracts/eez.mdx`/`rollup.mdx` to `/contracts/interfaces/...` pages.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Convert Interfaces reference pages — Contract Reference instance complete"
```

---

### Task 13: Full-site verification and push

**Files:**
- None created — verification only.

**Interfaces:**
- Consumes: the complete site from Tasks 1–12.

- [ ] **Step 1: Clean build from scratch**

```bash
cd /Users/armagan/eez-docs
rm -rf build .docusaurus node_modules
npm install
npm run build
```

Expected: build completes with zero errors, zero broken-link warnings.

- [ ] **Step 2: Serve and spot-check every nav group**

```bash
npm run serve &
sleep 3
for path in / /introduction /quickstart /architecture \
  /concepts/sync-composability /concepts/execution-model /concepts/rolling-hash /concepts/multi-prover /concepts/cross-chain-proxy \
  /guides/register-rollup /guides/build-execution-entries /guides/post-verify-batch /guides/bridge-tokens /guides/flash-loans /guides/lookup-calls \
  /tools/trace-decoder /tools/visualizator \
  /reference/caveats /reference/glossary \
  /contracts/eez /contracts/rollup /contracts/bridge /contracts/eezl2 /contracts/data-types \
  /contracts/interfaces/iproofsystem /contracts/interfaces/irollupcontract /contracts/interfaces/imetacrosschainreceiver; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$path")
  echo "$code $path"
done
kill %1
```

Expected: every line prints `200`. Any `404` means that page is missing from its sidebar or was written to the wrong path — go back to the task that should have created it.

- [ ] **Step 3: Push to GitHub**

```bash
git push -u origin main
```

- [ ] **Step 4: Report completion** — confirm to the user: all 23 pages converted, both docs instances build and route correctly, repo pushed. Hosting/deploy target remains an open follow-up per the spec.

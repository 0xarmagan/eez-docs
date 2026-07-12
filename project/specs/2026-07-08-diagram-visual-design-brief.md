# EEZ Docs — Technical Diagram Visual Design Brief

**Date:** 2026-07-08
**Audience:** a designer (or Claude Design session) doing the visual pass — not an engineering brief.
**Status:** content is verified accurate as of this brief. This document is about *how these diagrams should look*, not what they say.

---

## 1. Why this brief exists

`eez-docs` has 7 technical Mermaid diagrams explaining EEZ's cross-rollup execution machinery to builders. They were styled ad hoc — inline Mermaid `style`/`linkStyle` hex codes chosen to loosely match EEZ green — not against the actual EEZ Design System. The person styling them (an engineer, working diagram-by-diagram over several sessions) was reinventing a visual vocabulary — chain boxes, call arrows, revert states — that the brand system had already solved for marketing motion work. The result is 7 diagrams that are each internally reasonable but collectively inconsistent, and none of them draw on the literal, reusable design assets that already exist for exactly this purpose (see §4.3).

Before investing more in their look, we audited them for correctness first (§2) — a diagram that's beautifully on-brand but describes the wrong function is worse than the current state, not better. This brief is the handoff for the visual pass that comes next, so it starts from the real brand system instead of another round of guessing hex codes.

## 2. Accuracy audit (completed, prerequisite to this brief)

All 7 diagrams were checked against the live source, `github.com/eez-association/eez-core-protocol` (cloned and read directly — not a doc-vs-doc comparison, which a prior [[eez-docs]] audit lesson showed can point at the wrong file entirely when two pages disagree with each other). 3 issues found and fixed in commit `9881f99`:

1. **`_execution-flow-diagram.mdx`, actor graph** — the arrow `App1 -->|helloL2World| Proxy` claimed `HelloWorldL1` calls a function named `helloL2World` *on the proxy*. Backwards: `helloL2World()` is the entry point defined *on* `HelloWorldL1` itself (`test/mocks/helloword.sol:37`); what it actually invokes through the proxy is `getWord()`. Fixed to `App1 -->|getWord| Proxy`.
2. **`guides/build-execution-entries.mdx`, rolling-hash walkthrough** — the worked example showed `CALL_END(1, success1, returnData1)` for the outer call's completion tag. This is a real protocol-semantics error, not a typo: `_rollingHashCallEnd` (`EEZ.sol:1072`) always tags with the *live* `_currentL2ToL1Call` cursor at the moment the call returns — and by the time the outer call returns, the nested reentrant frame has already advanced that shared cursor to 3. Confirmed against `test/EEZ.t.sol:816`'s own comment ("Flat[0]'s CALL_END reads the LIVE cursor, which the nested frame advanced 1 -> 2") applied to this example's two-call nested frame. Fixed to `CALL_END(3, success1, returnData1)`.
3. **Same file, same paragraph** — a `callCount` value of `3` for the outer entry-level frame directly contradicted the doc's own partition-invariant arithmetic one sentence later (`2 + 2 == 4`, i.e., `callCount` must be `2`). Fixed to `2`.

**One item is a judgment call, not a bug, and matters directly for the redesign (see §3.2):** the actor graph in `_execution-flow-diagram.mdx` collapses two differently-authorized roles into one "Off-chain Sequencer" node — `postAndVerifyBatch` (permissionless, anyone can call it) and `executeIncomingCrossChainCall` (gated by `onlySystemAddress`, `EEZL2.sol:126-127`). `architecture.mdx` itself uses two different nouns for these ("the off-chain sequencer" vs. "the system address"). This is softened by the project's "based rollup" framing elsewhere, which treats them as the same physical operator in practice — so it's defensible, but it was collapsed implicitly rather than decided deliberately. The redesign should make that call on purpose.

All other content — the 6-step `postAndVerifyBatch` pipeline, the STATICCALL routing decision tree, the multi-prover threshold/revert branching, the CrossChainProxy tstore probe, and the flash-loan call sequence — matched source exactly, including exact function names, revert conditions, and branch outcomes.

**A related, smaller finding not fixed as part of this pass (flagging, not resolving):** every guide/concept page that carries a diagram includes an `<UnauditedWarning />` pre-mainnet banner at the top — except `docs/architecture.mdx`, which embeds the `_execution-flow-diagram.mdx` partial with no such banner anywhere on the page. Whether that's intentional (architecture.mdx reads as more "how it works" than "how to build against it") or an oversight is a content-editorial call, not a visual one — surfaced here because §3.1's "concept · pre-mainnet" lockup question depends on the answer.

## 3. Diagram-by-diagram brief

Each diagram below: what question it answers for the reader, what it looks like today, and specifically how the brand grammar in §4 should apply to it. Read this section together with the format recommendation in §8 — some of these are called out as Mermaid-appropriate, others as hand-design candidates, and the reasoning is diagram-specific, not a blanket policy.

### 3.1 Execution flow — the 3-phase overview (`docs/_execution-flow-diagram.mdx`, diagram a)

**Reader's question:** "At the highest level, what happens when I make a cross-rollup call?"
**Today:** 3 boxes, left-to-right, labeled "Off-chain / prove & queue," "L1 / execute the call," "L2 / execute independently." Flat color fills, no other ornamentation.
**This is the single best candidate in the whole set for the full grammar treatment.** It's the first diagram a reader sees (top of `architecture.mdx`), it's conceptually simple, and it is *exactly* the "one transaction, multiple environments" story the **transaction capsule** (`assets/grammar/capsule.svg`) was built to tell: one capsule elongating across all three phase-boxes rather than three separate arrows. Recommend: render the three phases as **chain-node**-style panels (`assets/grammar/chain-node.svg` — rounded rect, subtle inner grid, 160×90 native proportions) even though they're phases rather than literal chains, since visually this is the reader's first exposure to the "boxed environment" motif used everywhere else in the docs. Drop a **proof-glyph** (`assets/grammar/proof-glyph.svg`, small hexagon, mint fill/green stroke) at the Off-chain→L1 boundary, where the proof is actually produced and first checked. No friction/amber anywhere — this diagram has no failure path, it's the happy-path overview.

### 3.2 Execution flow — the full actor graph (`docs/_execution-flow-diagram.mdx`, diagram b)

**Reader's question:** "Contract by contract, who calls whom for a real `HelloWorldL1.helloL2World()` → `HelloWorldL2.getWord()` round trip?"
**Today:** 6 boxes (`Seq`, `EEZ Registry`, `CrossChainProxy`, `HelloWorldL1`, `EEZL2 Manager`, `HelloWorldL2`), solid green arrows for calls, dashed mint arrows for returns.
This is a literal call-trace of real contracts, not a chain-topology diagram — the chain-node grid texture doesn't map cleanly onto individual contract actors the way it does onto phases or rollups. Recommend keeping this one close to its current box-and-arrow form (see §8's Mermaid-vs-hand-designed split — this is a "stays Mermaid" diagram), but: (a) apply real token colors instead of the current hand-guessed hex, (b) add a single small **proof-glyph** accent at the `EEZ Registry` node specifically where `postAndVerifyBatch` checks the proof — right now the proof-check is invisible, it's just one arrow among six, (c) resolve the Off-chain Sequencer / System Address question from §2 before finalizing — either split into two nodes with a shared "off-chain operator" grouping, or keep one node but relabel it to acknowledge both calls explicitly (e.g. two arrow labels into the same node rather than implying one undifferentiated role).

### 3.3 Cross-rollup flash loan (`docs/guides/flash-loans.mdx`)

**Reader's question:** "How can I borrow on L1, use funds on L2, and repay on L1, all atomically?"
**Today:** 3 Mermaid `subgraph`s (L1 / L2 / L1) with 7 sequential step-nodes threaded through them.
This is the other strong capsule candidate — arguably the strongest, because "borrow → bridge → act → bridge back → repay, same block" is structurally identical to the brand system's own **Use Case 1 — Bridging** ("finished in one block") from the marketing storyboards. Worth literally opening `~/Downloads/EEZ Design System/UC1 Bridging.html` in a browser before starting this one (see §4.3 for what it is and isn't) — it's a live 1920×1080 animated reference for almost exactly this concept, executed in the full grammar. Recommend a hand-designed static adaptation: two **chain-node** lanes (L1, L2 — note this diagram genuinely has two *chains*, not just phases, so the grid-texture panel is a literal fit here, more so than in 3.1), one **capsule** elongating from the L1 borrow point through L2 and back to the L1 repay point, **proof-glyph** marks at both bridge boundaries (bridge-out and bridge-back each involve a cross-chain proof), and — unlike the marketing use case — the developer-facing version needs to keep the exact function-call labels (`bridgeTokens`, `claimAndBridgeBack`, `receiveTokens`) visible, since builders need the real call sequence, not just the concept. This is the key adaptation the designer needs to make going from marketing grammar to developer-doc grammar: label density goes up, ambiguity goes down, the "beauty" budget goes toward layout and color, not toward hiding mechanism.

### 3.4 Building `ExecutionEntry` structs — the nested rolling-hash sequence (`docs/guides/build-execution-entries.mdx`)

**Reader's question:** "In what exact order do `CALL_BEGIN`/`CALL_END`/`NESTED_BEGIN`/`NESTED_END` events fire when a call reenters, and what does that do to the rolling hash?"
**Today:** 8 nodes, mostly linear with one visual "branch back" for the nested frame closing.
This is the single most content-volatile diagram in the set — it just needed two corrections in this very pass, and any future change to reentrancy handling touches it directly. **Stays Mermaid** (see §8). Redesign within Mermaid's limits: consistent node shapes for "call event" vs. "nesting boundary" (right now both look like generic rounded rects), token colors, and consider a light visual indent/nesting-box (Mermaid `subgraph`, borderless, just for grouping) around the `NESTED_BEGIN`→`NESTED_END` span so the reentrant frame reads as visually contained rather than just sequential — this directly supports the doc's own point that a reentrant call fires *between* the outer call's begin and end tags.

### 3.5 `postAndVerifyBatch` internal pipeline (`docs/guides/post-verify-batch.mdx`)

**Reader's question:** "What does `postAndVerifyBatch` actually do internally, in order?"
**Today:** 6 linear nodes: validate → verify proofs → mark verified → drain transient → meta hook → publish queues.
Content-volatile (tied to exact function internals) — **stays Mermaid**. This is the diagram where the **proof-glyph** belongs most naturally and isn't yet present at all: drop it on the "verify proofs" node specifically, since that's the literal on-chain proof-verification step this whole system hinges on. No revert/friction styling currently shown even though a proof-verification failure here is exactly when the whole batch reverts (see 3.6's multi-prover diagram, which does show this) — worth deciding whether to add a small revert branch here too for consistency, or to keep this diagram exclusively happy-path and let `multi-prover.mdx` own the revert story (current split is reasonable, just make it deliberate).

### 3.6 Multi-prover threshold / revert (`docs/concepts/multi-prover.mdx`)

**Reader's question:** "What happens if a rollup's proof-system threshold isn't met?"
**Today:** 2 rollup inputs → decision diamond → "queue" or "entire batch reverts," with the revert branch already styled in muted amber/`#8B7B55` and a matching amber `linkStyle`.
This is the one diagram already closest to brand-correct by accident — the amber revert convention is right, keep it exactly. This is a **stable structural concept, not a literal call trace** — a good hand-design candidate (see §8). If hand-designed: the two rollups become **chain-node** panels each showing their own accepted-proof-system set, the decision point becomes a clear fork (not necessarily a literal diamond — the marketing grammar doesn't use diamonds; consider a simple divergent capsule-path instead, one branch continuing in green to "queued," one branch breaking into the **friction-mark** motif and terminating), and this is the one diagram in the set that most needs the **friction-mark**'s dashed-line-plus-marker treatment (`assets/grammar/friction-mark.svg`) rather than solid-color-only amber, precisely because color-only failure encoding is the accessibility gap flagged in §5.

### 3.7 STATICCALL routing decision (`docs/guides/lookup-calls.mdx`)

**Reader's question:** "How does the proxy know whether to route to the execute path or the lookup path?"
**Today:** 1 decision diamond ("inside an active execution entry?"), 2 branches to `ExpectedLookup` (nested) or `LookupCall` (top-level).
Stable structural concept — **hand-design candidate**. This diagram and 3.8 (`cross-chain-proxy.mdx`) are close cousins (both are the same tstore-probe / execute-vs-lookup fork, one from the "inside an already-executing entry" angle, one from the "call just arrived at the proxy" angle) and should be designed as a visual pair so a reader who's seen one recognizes the grammar in the other immediately.

### 3.8 CrossChainProxy tstore probe (`docs/concepts/cross-chain-proxy.mdx`)

**Reader's question:** "How does a proxy distinguish a `STATICCALL` (read-only) from a regular `CALL` without a Solidity primitive for it?"
**Today:** decision diamond ("tstore probe: static call context?"), branching to "Execute path" or "Lookup path," with the lookup outcome already tinted mint (`#A8F3CE`) to signal "no state changes."
Pairs with 3.7 — **hand-design candidate**. This is the diagram where the state-changing-vs-read-only distinction flagged in §5 point 3 matters most: right now the only signal that the lookup path is different in kind (not just outcome) from the execute path is the mint tint on one downstream node. Recommend a persistent visual marker — e.g., a small "read-only" glyph or a dashed-vs-solid path style applied consistently — that travels with the *lookup path itself*, not just its terminal node, so the distinction reads immediately rather than only at the end.

## 4. The real brand system (source of truth, not vendored in this repo)

### 4.1 Files to open before starting, and what each one is

All under `~/Downloads/EEZ Design System/`:

| File | What it actually is |
|---|---|
| `README.md` | Brand context, voice rules, content fundamentals, named reviewers. Read this first. |
| `colors_and_type.css` | The literal CSS custom-property tokens — palette, type scale, spacing, radii, motion durations. Authoritative for hex values. |
| `uploads/EEZ-Creative-Brief-Use-Case-Animations.md` | The full motion-design spec this whole system was extracted from — palette, grammar, and a per-use-case beat sheet for 7 marketing animations. Built for motion, but §3 (Shared visual system) is the closest thing to a grammar rulebook and applies directly to static diagrams too. |
| `uploads/EEZ-Use-Case-Storyboards.html` | Static SVG rendering of each storyboard — per the system's own README, "the closest thing to a living style guide." Open this over the raw markdown brief if you want to *see* the grammar rather than read about it. |
| `UC1 Bridging.html` (repo root) | **Not a static reference** — a live, animated React component (1920×1080, 10s loop, uses `animations/uc1-scene.jsx`). Requires a browser to view. Directly relevant to §3.3 (flash-loans) since it's the same "atomic, same-block, there-and-back" concept. Treat as a feel/vocabulary reference, not something to screenshot-trace — the docs version needs real function-call labels the marketing version deliberately omits. |
| `preview/*.html` | Small single-concept HTML cards (`colors-accent.html`, `type-body.html`, `components-panels.html`, `spacing-radii.html`, etc.) — quick visual lookups for one token category at a time. `preview/brand-grammar.html` specifically previews the motion-grammar vocabulary. |
| `assets/grammar/*.svg` | **The literal, reusable grammar elements** — see §4.3. Use these files directly rather than redrawing the shapes from description. |
| `assets/logo/*.svg` | `eez-mark.svg` (the diamond mark used elsewhere in this repo as the favicon) and `eez-wordmark.svg`. Diagrams don't need a logo, but useful if any diagram gets a caption/attribution treatment. |
| `ui_kits/marketing/*.jsx` | React components (`Hero.jsx`, `UseCaseCard.jsx`, etc.) showing the grammar assembled into real page sections — useful for spacing/composition patterns, not diagram-specific. |

### 4.2 Palette, type, spacing (from `colors_and_type.css`)

**Palette:**
- Canvas: `#0A0A0A` (bg), `#121212` (card), `#161616` (raised panel inner fill)
- Ink: `#F2F2EC` (body text — never pure white); `#FFFFFF` reserved for strong emphasis only
- Accent green `#3BE57E` — active flows, calls, success (also has a dim/glow/deep variant: `rgba(59,229,126,.35/.12)`, `#1F8A4A` for pressed/focus)
- Mint `#A8F3CE` — settled state, proof glyphs, return values (dim variant `rgba(168,243,206,.45)`)
- Friction `#8B7B55` — **never red, never saturated, never "alarm."** This is a hard brand rule (README: "Friction in 'Today' comparisons is rendered as muted amber — never saturated red"), not a style preference open to reinterpretation.
- Rule/border: `rgba(242,242,236,.08)` default, `.16` strong, or `rgba(59,229,126,.25)` for a green-tinted rule

**Type:** Inter (sans) for labels/prose — **Light 300 is the default weight, this is deliberate** (the "keynote aesthetic"), Regular 400 for labels/running UI, Medium 500 only for emphasis, **never Bold**. JetBrains Mono for code/technical values (function names, hashes, addresses). Size scale relevant to diagram labels: `--eez-fs-micro: 9px` (barcode/meta), `--eez-fs-tiny: 11px` (eyebrow/label), `--eez-fs-small: 13px`, `--eez-fs-body: 15px`. Diagram node labels should almost certainly sit in the `tiny`–`small` range, not `body` — these are schematic annotations, not prose.

**Geometry:** rounded rectangles are the base motif (`--eez-radius: 6px` default, `--eez-radius-md: 8px` — matches `chain-node.svg`'s `rx="8"` exactly). Fully-round capsules (`--eez-radius-pill: 999px`) are **reserved specifically for transactions** — don't reach for a pill shape decoratively for something that isn't representing an actual transaction/call.

**Voice guardrails that touch diagram labels:** no "unlock / seamless / revolutionary / next-generation / effortless / magical"; sentence case, periods on declarative labels; middle-dot `·` as a lightweight separator (`concept · pre-mainnet`); specific numbers only when sourced from real code/tests (never round up or invent a duration/count).

### 4.3 The literal grammar assets — use these files, don't redraw them

`assets/grammar/*.svg` are small, self-contained SVGs, already at final token colors. Inspected directly so this brief can be precise about what each one is, not just what it's called:

- **`chain-node.svg`** — `viewBox="0 0 160 90"`, rounded rect (`rx="8"`, matches `--eez-radius-md`) with a faint internal grid (horizontal/vertical lines at `stroke-opacity:.06`) and a `stroke-opacity:.55` outer border in ink color. This is the base "chain/environment box" — use for L1/L2/rollup panels (3.3) and, adapted, for the phase-boxes in 3.1.
- **`capsule.svg`** — `viewBox="0 0 320 18"`, a pill (`rx="9"`) filled `#3BE57E` at 90% opacity. Native aspect ratio is very wide/flat (~17.7:1) — the "elongating" behavior in motion is literally this shape stretched between anchor points; in a static diagram, draw it as a tapered/stretched path between the chains it touches rather than a fixed-width pill.
- **`proof-glyph.svg`** — `viewBox="0 0 20 20"`, a small hexagon, mint fill (`#A8F3CE`) with a green stroke (`#3BE57E`). Small and secondary by design (README: "understated — not a hero element, because the proof is invisible infrastructure") — don't scale this up to a focal size even in a technical diagram where the proof matters a lot to the reader; its restraint *is* the point.
- **`friction-mark.svg`** — `viewBox="0 0 180 40"`, a dashed amber line with a small dot, leading into an amber-tinted rounded box. This is the answer to §5's accessibility gap: it encodes "friction" via **dash pattern + shape**, not color alone. Use this directly (or its pattern) anywhere a revert/failure path appears, instead of a solid amber stroke on an otherwise-identical line style.
- **`settlement-pulse.svg`** — `viewBox="0 0 200 200"`, concentric green rings fading outward (`stroke-opacity` .35/.22/…). Built for an animated pulse tied to L1's 12-second block cadence; in a static diagram this has no direct use unless a diagram specifically wants to call out "this settles on L1" — probably not needed for any of the 7 (none of them are about the passage of time), flag as available but likely unused.
- **`state-sweep.svg`** — `viewBox="0 0 160 90"`, a horizontal gradient sweep (transparent → `#3BE57E` at 35% → transparent). Motion-only element (an animated sweep across a chain node when its state changes); a static diagram would render this as a subtle inner glow rather than a sweep — most relevant to 3.5/3.6 where "state actually changed" is the payoff moment.

## 5. Accessibility: the color-only encoding gap

Right now, three separate distinctions in these diagrams are carried **by hue alone**, with no redundant shape/pattern signal:
1. Call (green, solid) vs. return (mint, dashed) — **this one is fine**, it already combines color with stroke-style.
2. Success/queue (green/mint) vs. revert/failure (amber) — **color-only** in every diagram except where amber already implies "different," e.g. `multi-prover.mdx`'s revert branch has no dash/shape distinction from its neighboring success branch beyond the fill color.
3. State-changing call vs. read-only/lookup call — **not distinguished at all** currently (flagged in §3.8), and this is arguably the most protocol-important distinction in the whole set.

For readers with red-green color-vision deficiency (~8% of men), green (`#3BE57E`) and amber (`#8B7B55`) sit close enough in some CVD simulations to blur together, especially at small diagram scale. The fix already exists in the brand system and doesn't require inventing anything: `friction-mark.svg` already encodes revert/failure via dash pattern *and* a small marker glyph, not fill color alone — adopt that pattern everywhere a revert path appears, and pick an equivalent redundant signal (a distinct stroke pattern, not just a color) for the read-only/lookup path in 3.7 and 3.8.

## 6. Layout & Docusaurus technical constraints

This repo has already hit one real rendering bug worth the designer knowing about before finalizing layouts: wide horizontal Mermaid diagrams silently shrink to illegibility inside Docusaurus's narrow content column (the SVG's `width="100%"` with no explicit height resolves against the container, not its own `viewBox`), and `max-width`/`width` CSS overrides alone don't fix it — this repo's actual fix was a `clientModules` script that sets each diagram's pixel width from its own `viewBox` (see the `docusaurus-expert` skill, "Mermaid Gotcha 3," for the exact code). Whatever ships next — restyled Mermaid or hand-designed static SVG — should be checked at the real content-column width (roughly 700–750px, not full-viewport) before considering the layout final, ideally via a real built-and-served page screenshot (`npx docusaurus build && npx docusaurus serve`, then headless Chrome at `--window-size=1000,1600`) rather than an isolated render, since isolated renders (e.g. `mermaid-cli`) use a different sizing path and won't reproduce a narrow-column shrink.

Separately: the site currently forces Mermaid diagrams into a fixed dark panel regardless of the site's own light/dark toggle (`docusaurus.config.js` comment + a `.docusaurus-mermaid-container` override in `custom.css`) — a deliberate choice made because Mermaid's `themeVariables` can't be split per color scheme. If any of the 7 diagrams move to hand-designed static SVG, confirm whether that same "always-dark-panel" constraint should carry over (probably yes, for visual consistency with the diagrams that stay Mermaid) or whether a hand-designed asset can afford to respect the site's light-mode toggle properly since it isn't bound by Mermaid's single-shared-theme limitation.

## 7. Gap between today's diagrams and the brand system

1. **No chain-node grid texture, no capsule, no proof-glyph iconography anywhere**, despite reusable assets for all three existing already (§4.3). Every node today is a plain Mermaid rounded-rect/stadium/diamond in one of three near-identical dark greens.
2. **Inconsistent node shapes across diagrams for the same semantic role** — actors are `("...")` rounded rects in some diagrams, `(["..."])` stadiums in others, `{"..."}` diamonds for decisions — not a deliberate system, just whatever each Mermaid author reached for in that session.
3. **Call vs. return is color+style coded (good); success vs. revert and state-changing vs. read-only are not** — see §5.
4. **No brand file vendored in this repo.** `docusaurus.config.js` and `custom.css` both comment-reference `~/Downloads/EEZ Design System/colors_and_type.css` as the source of truth, but nobody has copied real tokens in — the current hex values are hand-transcribed guesses that already drift (e.g. `#122018` as `primaryColor` isn't a token in `colors_and_type.css` at all).
5. **Mermaid itself is a real ceiling.** It cannot render inner-grid textures, hexagonal glyphs, or elongating capsules — the actual brand grammar requires custom SVG/illustration for at least some of these diagrams, not diagram-as-code. See §8.

## 8. The open decision: Mermaid-as-code vs. hand-designed static assets

Not a styling detail — a real trade-off with real consequences either way:

- **Keep Mermaid, restyle within its limits** (proper token colors, one consistent node-shape convention, targeted grammar accents like a proof-glyph icon dropped into an otherwise-Mermaid node) — diagrams stay auto-generated from text, trivially kept in sync with source (this audit just proved that matters: 3 content bugs were quietly living in these diagrams), full dark/light-mode compatibility for free, but will never fully match the brand's grid/capsule/glyph vocabulary.
- **Hand-design as static SVG/illustration** — full brand fidelity (grid-textured chain nodes, real capsule call-paths, hexagonal proof glyphs at verification boundaries), but every future protocol change requires a designer edit, not a text edit — a real risk given this repo has already needed a 29-issue accuracy fix once (commit `8915038`) and a 3-issue fix today.

**Per-diagram recommendation** (reasoning for each is in §3; this table is the summary to act on):

| Diagram | Recommendation | Why |
|---|---|---|
| 3.1 Execution flow overview | Hand-design | Simple, stable, highest-visibility (first diagram on the architecture page), ideal capsule-metaphor fit |
| 3.2 Full actor graph | Stay Mermaid | Literal call-trace tied to exact function names, most content-volatile of the actor diagrams |
| 3.3 Flash loan | Hand-design | Stable structural concept, direct marketing-grammar analog (UC1 Bridging), but needs real call labels added back in |
| 3.4 Execution-entries rolling hash | Stay Mermaid | Most content-volatile diagram in the set — needed 2 corrections this pass alone |
| 3.5 postAndVerifyBatch pipeline | Stay Mermaid | Tied to exact internal function steps |
| 3.6 Multi-prover threshold | Hand-design | Stable structural concept, needs the friction-mark treatment most |
| 3.7 Lookup-calls routing | Hand-design (paired with 3.8) | Stable structural concept |
| 3.8 CrossChainProxy tstore probe | Hand-design (paired with 3.7) | Stable structural concept |

Flag this table back to Armagan/the design owner for a final call before starting production — it's a strong recommendation, not a decision made on their behalf.

## 9. Deliverables requested from the design pass

For each of the 7 diagrams:
- A redesigned version using the real token values in §4.2 (not the current hand-guessed hex) and, where hand-designed, the literal grammar assets in §4.3 rather than redrawn approximations.
- One consistent node-shape convention across all diagrams for: chain/actor, process step, decision point, terminal/outcome state — documented once (see last bullet).
- Visual distinction between state-changing calls and read-only (STATICCALL/lookup) calls (§3.7, §3.8, §5) — currently invisible; this is a core protocol concept, not a cosmetic one.
- Friction/revert-path styling using the `friction-mark.svg` dash-plus-marker pattern (§4.3, §5), not solid amber fill alone — already directionally correct in `multi-prover.mdx`, should become the systematic convention everywhere a failure/revert path appears.
- Confirm both dark-mode (primary) and the site's light-mode toggle remain legible, per the constraint discussion in §6.
- Verify at real Docusaurus content-column width, per §6 — not just an isolated render.
- A short style-guide addendum (even half a page) showing the chosen node/arrow/decision conventions once, so future diagram additions — this repo has added diagrams in 3 separate sessions in the past week alone — don't drift again the way the current 7 did.

## 10. Review / sign-off routing

The Design System's own README names two reviewers for the brand generally: **Adrienne Youngman** (voice) and **Jordi Baylina** (technical). Those reviewers were named for brand-wide marketing material, not specifically for developer-doc diagrams — worth confirming with Armagan whether the same sign-off applies here, or whether technical review for these specific diagrams should route through whoever owns `eez-core-protocol` correctness instead (arguably more relevant given §2's findings were protocol-semantics bugs, not brand bugs). Either way, any diagram-label copy changes that fall out of the redesign should still respect the voice guardrails in §4.2 even if a formal voice-review pass isn't run.

## 11. Out of scope for this brief

- No new diagrams — this is a redesign of the existing 7.
- No changes to diagram *content/labels* beyond what's already fixed in commit `9881f99` — if the design pass surfaces further technical-accuracy questions (including the `architecture.mdx` missing-banner flag in §2), report them back rather than resolving them visually.
- No motion/animation. The source grammar (`assets/grammar/*.svg`, the UC1 Bridging reference) was built for animated marketing use; this pass is static docs diagrams only. Worth a separate note to Armagan as a possible future idea (an animated version of 3.1 or 3.3 on the architecture/flash-loan pages) but not part of this brief's scope or estimate.
- Vendoring the actual `colors_and_type.css` file (or an eez-docs-scoped subset of it) into this repo is a prerequisite someone should do before or alongside this pass, so token values stop being hand-copied guesses — flagged here, not solved here.

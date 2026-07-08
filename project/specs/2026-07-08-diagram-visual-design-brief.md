# EEZ Docs — Technical Diagram Visual Design Brief

**Date:** 2026-07-08
**Audience:** a designer (or Claude Design session) doing the visual pass — not an engineering brief.
**Status:** content is verified accurate as of this brief. This document is about *how these diagrams should look*, not what they say.

---

## 1. Why this brief exists

`eez-docs` has 7 technical Mermaid diagrams explaining EEZ's cross-rollup execution machinery to builders. They were styled ad hoc — inline Mermaid `style`/`linkStyle` hex codes chosen to loosely match EEZ green — not against the actual EEZ Design System. Before investing more in their look, we audited them for correctness (below), then wrote this brief so the next visual pass follows the real brand grammar instead of another round of engineer's-best-guess Mermaid theming.

## 2. Accuracy audit (completed, prerequisite to this brief)

All 7 diagrams were checked against the live source, `github.com/eez-association/eez-core-protocol` (not doc-vs-doc). 3 issues found and fixed in commit `9881f99`:

1. `_execution-flow-diagram.mdx` — an arrow was labeled with the wrong function name (`helloL2World` instead of `getWord`).
2. `guides/build-execution-entries.mdx` — the rolling-hash walkthrough had a wrong tag number (`CALL_END(1,...)` should read `CALL_END(3,...)`, because that tag reads the live shared cursor, not the number captured at `CALL_BEGIN`) — a subtle but real protocol-semantics error.
3. Same file — a `callCount` value (3) directly contradicted the doc's own arithmetic two sentences later (`2 + 2 == 4`); corrected to 2.

One item is flagged as a **judgment call, not a bug**, and is relevant to the redesign (see §5.3): the actor graph in `_execution-flow-diagram.mdx` collapses two different roles (`postAndVerifyBatch`, permissionless; `executeIncomingCrossChainCall`, gated by `onlySystemAddress`) into one "Off-chain Sequencer" node. Defensible as a simplification, but the redesign should decide deliberately whether to keep it collapsed.

All other content — the 6-step `postAndVerifyBatch` pipeline, the STATICCALL routing decision tree, the multi-prover threshold/revert branching, the CrossChainProxy tstore probe, and the flash-loan call sequence — matched source exactly.

## 3. What exists today (7 diagrams, all Mermaid `flowchart`)

| File | Diagram | Shape today |
|---|---|---|
| `docs/_execution-flow-diagram.mdx` | (a) 3-phase off-chain→L1→L2 overview | 3 boxes, LR |
| same file | (b) full actor call graph (`HelloWorldL1` → `HelloWorldL2`) | 6 nodes, solid/dashed arrows |
| `docs/guides/flash-loans.mdx` | cross-rollup flash loan, L1→L2→L1 | 3 subgraphs (L1/L2/L1), 7 steps |
| `docs/guides/build-execution-entries.mdx` | nested-call rolling-hash sequence | 8 nodes, linear w/ one branch-back |
| `docs/guides/post-verify-batch.mdx` | `postAndVerifyBatch` internal pipeline | 6 nodes, linear |
| `docs/guides/lookup-calls.mdx` | STATICCALL routing decision | 1 decision diamond, 2 branches |
| `docs/concepts/multi-prover.mdx` | per-rollup proof threshold → verify/revert | 2 inputs → decision → 2 outcomes |
| `docs/concepts/cross-chain-proxy.mdx` | tstore probe → execute vs. lookup | 1 decision diamond, 2 branches |

Every diagram is rendered client-side by Docusaurus's Mermaid plugin, themed via a single global `themeVariables` block in `docusaurus.config.js` (fixed dark panel, `primaryColor:#122018`, `primaryBorderColor/lineColor:#3BE57E`) — this is a comment-only pointer to the real brand file, not the brand file itself.

## 4. The actual brand system (source of truth, not vendored in this repo)

Location: `~/Downloads/EEZ Design System/` (`colors_and_type.css`, `uploads/EEZ-Creative-Brief-Use-Case-Animations.md`, `preview/*.html`). Key facts for this redesign:

**Palette** (from `colors_and_type.css`):
- Canvas: `#0A0A0A` (bg), `#121212`/`#161616` (elevated surfaces)
- Ink: `#F2F2EC` (never pure white; `#FFFFFF` reserved for strong emphasis)
- Accent green: `#3BE57E` (active flows, success, calls) / mint `#A8F3CE` (settled state, proof glyphs, returns)
- Friction: muted amber `#8B7B55` — **never red, never alarm-colored**, used only for "Today"/failure-path states
- Rule/border: `rgba(242,242,236,0.08–0.16)`

**Type:** Inter (sans, light 300 default weight) for labels/prose, JetBrains Mono for code/technical values. Never bold; medium (500) is the heaviest weight used.

**Motion/shape grammar** (from the creative brief — built for marketing animation but the vocabulary is exactly what these technical diagrams are informally reinventing):
- **Chain node** = rounded rectangle with a subtle inner grid texture, labeled, still unless active.
- **Transaction capsule** = a tight pill shape tracing a path; elongates across chains it touches rather than duplicating — visual metaphor for "one transaction, multiple chains."
- **Proof glyph** = small hexagonal mark at a chain node's boundary when a proof is generated/verified — understated, ~0.5s in animation, i.e. small and secondary in a static diagram too.
- **Settlement pulse** = soft green glow/pulse tied to the Ethereum L1 node (12s cadence in motion — not applicable to static diagrams, but signals "L1 is the heartbeat").
- **Friction marker** = dashed/dotted connectors, fading arrows, qualitative labels only (no invented time numbers) — reserved for failure/legacy-flow comparisons.
- Flat, front-on, no perspective/camera trick — diagrams read as infrastructure schematics, not marketing art.

**Voice guardrails that touch diagram labels:** no "unlock/seamless/revolutionary/effortless"; sentence case; middle-dot `·` as a lightweight separator (e.g. `concept · pre-mainnet`); specific numbers only when sourced (never round up).

## 5. Gap between today's diagrams and the brand system

1. **No chain-node grid texture, no capsule, no proof-glyph iconography anywhere.** Every node today is a plain Mermaid rounded-rect/stadium/diamond in one of three near-identical dark greens. The visual vocabulary that makes EEZ's own marketing material immediately recognizable is entirely absent from the docs.
2. **Inconsistent node shapes across diagrams for the same semantic role.** Actors are `("...")` rounded rects in some diagrams, `(["..."])` stadiums in others, `{"..."}` diamonds for decisions — not a deliberate system, just whatever each Mermaid author reached for.
3. **Call vs. return is currently color-only** (solid green vs. dashed mint) — matches the brand's "mint = settled" convention, which is good and worth keeping — but nothing distinguishes a *state-changing* call from a *read-only* one, which matters a lot in a protocol built around exactly that distinction (see `lookup-calls.mdx`, `cross-chain-proxy.mdx`).
4. **No brand file vendored in this repo.** `docusaurus.config.js` and `custom.css` both comment-reference `~/Downloads/EEZ Design System/colors_and_type.css` as the source of truth, but nobody has copied real tokens in — the current hex values are hand-transcribed guesses that already drift (e.g. `#122018` primaryColor isn't a token in `colors_and_type.css` at all).
5. **Mermaid itself is a real ceiling.** It cannot render inner-grid textures, hexagonal glyphs, or elongating capsules — the actual brand grammar requires custom SVG/illustration, not diagram-as-code.

## 6. The open decision this brief does not make for you

**Mermaid-as-code vs. hand-designed static assets** is a real trade-off, not a styling detail:

- **Keep Mermaid, restyle within its limits** (proper token colors, consistent node shapes, a documented decision-diamond/process-box/actor-node convention) — diagrams stay auto-generated from text, trivially kept in sync with source (as this very audit just proved matters — 3 content bugs were living in these diagrams), full dark/light-mode compatibility for free, but will never fully match the brand's grid/capsule/glyph vocabulary.
- **Hand-design as static SVG/illustration** — full brand fidelity (grid-textured chain nodes, capsule call-paths, hexagonal proof glyphs at verification boundaries), but every future protocol change requires a designer edit, not a text edit — a real risk given this repo has already needed a 29-issue accuracy fix once and a 3-issue fix today.

**Recommendation to hand to the designer:** split by volatility. The 3 diagrams tied tightly to exact function names/call sequences that change with the contracts (`build-execution-entries.mdx`, `post-verify-batch.mdx`, the `_execution-flow-diagram.mdx` actor graph) stay Mermaid, restyled to the token system. The 4 diagrams that illustrate a stable structural concept rather than a literal call trace (`multi-prover.mdx`, `cross-chain-proxy.mdx`, `lookup-calls.mdx`, and the flash-loan diagram) are good candidates for a hand-designed pass using the full grammar, since their content is unlikely to need frequent edits. Flag this split back to Armagan/the design owner for a final call before starting production.

## 7. Deliverables requested from the design pass

For each of the 7 diagrams:
- A redesigned version using the real token values in §4 (not the current hand-guessed hex).
- One consistent node-shape convention across all diagrams for: chain/actor, process step, decision point, terminal/outcome state.
- Visual distinction between state-changing calls and read-only (STATICCALL/lookup) calls — currently invisible; this is a core protocol concept in at least 3 of the 7 diagrams.
- Friction/revert-path styling in muted amber (`#8B7B55`), never red — already correct in 2 of the 7 diagrams (`multi-prover.mdx`'s revert branch), should be made the systematic convention everywhere a failure/revert path appears.
- Confirm both dark-mode (primary) and the site's light-mode toggle remain legible — the current fixed-dark-panel approach in `docusaurus.config.js` was a deliberate choice (see inline comment there); the redesign should confirm whether that constraint still holds or whether the new design bakes in its own container styling.
- A short style-guide addendum showing the chosen node/arrow/decision conventions once, so future diagram additions (this repo has added diagrams 3 times in the past week) don't drift again.

## 8. Out of scope for this brief

- No new diagrams — this is a redesign of the existing 7.
- No changes to diagram *content/labels* beyond what's already fixed in commit `9881f99` — if the design pass surfaces further technical-accuracy questions, flag them back rather than resolving them visually.
- Vendoring the actual `colors_and_type.css` file (or an eez-docs-scoped subset of it) into this repo is a prerequisite someone should do before or alongside this pass, so the token values stop being hand-copied guesses — flagged here, not solved here.

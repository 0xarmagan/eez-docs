# eez-docs Core-Protocol Sync Audit + Blob Spec Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring every eez-docs page back into accuracy with `eez-association/eez-core-protocol`'s current `main` (`60c184b`, 2026-08-04) — which rewrote `EEZ.sol`/`EEZL2.sol`/`EEZBase.sol` and all four spec docs since eez-docs was last audited at `08ae750` (2026-07-13) — and add coverage for the one wholly new feature (Blob Format).

**Architecture:** Doc-vs-real-source audit (never doc-vs-doc — see `[[doc-accuracy-audit-against-real-source]]`), one task per doc-page cluster mapped to the exact contract/spec files it claims to describe. Each task's "test" is: (a) every changed claim is re-derived by reading the cited source line directly, not taken from spec prose alone when the two might drift, and (b) `npm run build` succeeds with zero new broken-link warnings after the edit.

**Tech Stack:** Docusaurus 3.x (classic template, JS), MDX, Mermaid (see `future.faster: false` gotcha already in place). Real source lives in `eez-association/eez-core-protocol` (public) — clone fresh, do not rely on memory of past audits.

## Global Constraints

- Verify every factual fix against the real cloned source at commit `60c184b` (or later on `main` if re-cloned) — cite exact `file:line`. Never fix a doc based on another doc's claim alone.
- Keep the design-tense / not-live framing (`docs/_unaudited-warning.mdx`, `reference/security.mdx` §0 caveat) — proof system is still dev-grade ECDSA only; do not imply production ZK proving anywhere touched by this plan.
- Do not touch `docusaurus.config.js` mermaid theming, `custom.css` `.docusaurus-mermaid-container`, or the brand font setup — out of scope, already correct per prior passes.
- Preserve existing sidebar category structure (`sidebars.js` / `sidebarsContracts.js`) — add new entries, don't reorganize existing ones, unless a task explicitly says to.
- Run `npm run build` after every task's edits, from this worktree's root (`/Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit`), before committing that task. A failed build blocks the commit.
- All work happens on the isolated branch `docs/core-protocol-sync-audit-2026-08-13`, checked out in the git worktree above — **not** on `main` in the primary `eez-docs` checkout, which currently has unrelated pre-existing uncommitted changes (regenerated motion-loop assets) that must not be touched or mixed into this work. Commit per task (small, reviewable diffs) on this branch. **Do not push and do not merge to `main`** until the final review is clean and the user has explicitly confirmed (Push Permission Boundaries: direct push/merge to `main` needs explicit confirmation) — resolved via `superpowers:finishing-a-development-branch` at the end, not by any individual task.
- Source repo clone location for this session: `/private/tmp/claude-501/-Users-armagan/29fdf962-4e57-4d4a-8870-3b97dbee1cc3/scratchpad/eez-core-protocol` (already cloned at `60c184b`). Re-`git pull` it at the start of the work if picked up later than today.

---

## File Structure

**eez-docs pages touched** (all paths relative to `/Users/armagan/eez-docs`):
- `contracts/eez.mdx`, `contracts/rollup.mdx`, `contracts/interfaces/irollupcontract.mdx`
- `contracts/eezl2.mdx`
- `contracts/bridge.mdx`, `contracts/data-types.mdx`, `contracts/interfaces/imetacrosschainreceiver.mdx`, `contracts/interfaces/iproofsystem.mdx`
- `docs/architecture.mdx`, `docs/concepts/execution-model.mdx`, `docs/concepts/sync-composability.mdx`
- `docs/concepts/multi-prover.mdx`
- `docs/concepts/cross-chain-proxy.mdx`
- `docs/guides/build-execution-entries.mdx`, `docs/concepts/rolling-hash.mdx`
- `docs/guides/lookup-calls.mdx`
- `docs/guides/post-verify-batch.mdx`, `docs/guides/register-rollup.mdx`
- `docs/guides/flash-loans.mdx`, `docs/guides/bridge-tokens.mdx`
- `docs/reference/caveats.mdx`, `docs/reference/security.mdx`, `docs/reference/glossary.mdx`
- **New:** `docs/concepts/blob-format.mdx` (new page) + `sidebars.js` entry

**Real source consulted** (all paths relative to the cloned `eez-core-protocol` repo):
- `src/EEZ.sol`, `src/interfaces/IEEZ.sol`, `src/rollupContract/Rollup.sol`, `src/interfaces/IRollup.sol`
- `src/L2/EEZL2.sol`, `src/interfaces/IEEZL2.sol`
- `src/periphery/Bridge.sol`, `src/base/EEZBase.sol`, `src/interfaces/IMetaCrossChainReceiver.sol`
- `src/base/CrossChainProxy.sol`
- `script/flash-loan-test/ExecuteFlashLoan.s.sol`, `DeployFlashLoan.s.sol`, `DeployInfra.s.sol`
- `docs/CORE_PROTOCOL_SPEC.md`, `docs/EXECUTION_ENTRY_SPEC.md`, `docs/LOOKUP_SPEC.md`, `docs/MULTI_PROVER_SPEC.md`, `docs/CAVEATS.md`
- `docs/blobs/BLOB_FORMAT_SPEC.md` (new)

**Confirmed out of scope:** `visualizator/` and `trace-decoder/` directories have zero diff since `01462dc` (2026-07-13) — `docs/tools/visualizator.mdx` and `docs/tools/trace-decoder.mdx` need no source-driven changes; give them a 2-minute skim in Task 13 only.

---

### Task 1: L1 registry + rollup-manager contract pages

**Files:**
- Modify: `contracts/eez.mdx`, `contracts/rollup.mdx`, `contracts/interfaces/irollupcontract.mdx`
- Verify against: `src/EEZ.sol`, `src/interfaces/IEEZ.sol`, `src/rollupContract/Rollup.sol`, `src/interfaces/IRollup.sol`, `docs/CORE_PROTOCOL_SPEC.md` §B.1 (`registerRollup`, `postAndVerifyBatch`, `executeCrossChainCall`, `executeL2TX`, `staticCallLookup`, `createCrossChainProxy`, per-rollup ownership, internal helpers `_consumeAndExecute`/`_consumeNestedAction`/`_tryRevertedTopLevelLookup`/`_applyAndExecute`/`_processNCalls`/`_applyStateDeltas`/`_processNStaticCalls`)

- [ ] **Step 1: Read every function/struct `contracts/eez.mdx` and `contracts/rollup.mdx` currently document, list them out.**

- [ ] **Step 2: For each, open the matching real source function/struct at its current line number and diff its actual signature, revert conditions, and event emissions against what the doc claims.** Known anchor to check specifically: `RollupConfig` struct fields (doc previously said "owner / vkey / threshold live on `RollupConfig`" — current source at `CORE_PROTOCOL_SPEC.md:208` says those now live on the per-rollup `IRollupContract`-conforming manager, immutable after registration — confirm which model the doc pages currently describe and fix if stale).

- [ ] **Step 3: Fix every mismatch found, citing the exact `file:line` in the commit message or a PR-style note if helpful.** No speculative fixes — if source is ambiguous, flag it in your final report rather than guessing.

- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, no new broken-link warnings referencing these 3 files.

- [ ] **Step 5: Commit.**

```bash
git add contracts/eez.mdx contracts/rollup.mdx contracts/interfaces/irollupcontract.mdx
git commit -m "docs: sync L1 registry + rollup-manager pages to eez-core-protocol main"
```

---

### Task 2: L2 contract page

**Files:**
- Modify: `contracts/eezl2.mdx`
- Verify against: `src/L2/EEZL2.sol` (710-line diff since last audit), `src/interfaces/IEEZL2.sol` (207-line diff)

- [ ] **Step 1: List every function/struct `contracts/eezl2.mdx` documents.**
- [ ] **Step 2: Diff each against current `EEZL2.sol`/`IEEZL2.sol`.** Specific known naming convention to re-verify: L2 uses self-relative directional names (`CrossChainCall`/`incomingCalls`, `ExpectedOutgoingCrossChainCall`/`expectedOutgoingCalls`) — confirm the doc still uses these exact names, not the older L1-absolute names (`L2ToL1Call`/`ExpectedL1ToL2Call`) by mistake.
- [ ] **Step 3: Fix mismatches with source citations.**
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, no new broken-link warnings for `contracts/eezl2.mdx`.

- [ ] **Step 5: Commit.**

```bash
git add contracts/eezl2.mdx
git commit -m "docs: sync EEZL2 contract page to eez-core-protocol main"
```

---

### Task 3: Bridge / data-types / remaining interface pages

**Files:**
- Modify: `contracts/bridge.mdx`, `contracts/data-types.mdx`, `contracts/interfaces/imetacrosschainreceiver.mdx`, `contracts/interfaces/iproofsystem.mdx`
- Verify against: `src/periphery/Bridge.sol` (34-line diff), `src/base/EEZBase.sol` (226-line diff — this is where most shared structs/storage now live per `CORE_PROTOCOL_SPEC.md` §A.2 "EEZ.sol (L1) — inherits `EEZBase`"), `src/interfaces/IMetaCrossChainReceiver.sol` (8-line diff)

- [ ] **Step 1: Confirm which structs documented on `data-types.mdx` moved into `EEZBase.sol` vs stayed on `EEZ.sol`/`EEZL2.sol` directly** (the 226-line `EEZBase.sol` diff suggests shared-struct consolidation) — fix any page that still attributes a struct to the wrong contract.
- [ ] **Step 2: Diff `Bridge.sol`'s current functions against `contracts/bridge.mdx`.**
- [ ] **Step 3: Diff `IMetaCrossChainReceiver.sol` and `IProofSystem.sol` (check current interface, it wasn't in the top diff-stat — confirm no changes; if none, leave `iproofsystem.mdx` untouched and note that in your report) against their pages.**
- [ ] **Step 4: Fix mismatches with source citations.**
- [ ] **Step 5: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, no new broken-link warnings for these 4 files.

- [ ] **Step 6: Commit.**

```bash
git add contracts/bridge.mdx contracts/data-types.mdx contracts/interfaces/imetacrosschainreceiver.mdx contracts/interfaces/iproofsystem.mdx
git commit -m "docs: sync bridge/data-types/interface contract pages to eez-core-protocol main"
```

---

### Task 4: Architecture + execution-model + sync-composability overview pages

**Files:**
- Modify: `docs/architecture.mdx`, `docs/concepts/execution-model.mdx`, `docs/concepts/sync-composability.mdx`
- Verify against: `docs/CORE_PROTOCOL_SPEC.md` §A (Data Model) and §A.3 (Transient Variables and `_insideExecution`)

- [ ] **Step 1: Re-read `CORE_PROTOCOL_SPEC.md`'s opening summary (lines 1-20) and confirm the "flat sequential execution model" framing these 3 pages use is still exactly how the spec frames it** — the spec explicitly calls out this is the model "layered with the multi-prover / per-rollup-queue model from the `feature/flatten` refactor"; confirm the pages don't describe a stale pre-flatten or pre-multi-prover-queue model.
- [ ] **Step 2: Check the `docs/_execution-flow-diagram.mdx` Mermaid diagram embedded on `architecture.mdx` still matches current function names/order** (`postAndVerifyBatch` → `_consumeAndExecute` / `_consumeNestedAction`) — these exact internal helper names still exist in current `EEZ.sol` (confirmed via grep), so only check call *order* and *labels*, not existence.
- [ ] **Step 3: Fix mismatches with source citations.**
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, diagram still renders (spot-check via `npx docusaurus serve` + headless Chrome screenshot per prior methodology if any diagram label changed).

- [ ] **Step 5: Commit.**

```bash
git add docs/architecture.mdx docs/concepts/execution-model.mdx docs/concepts/sync-composability.mdx
git commit -m "docs: sync architecture/execution-model overview pages to eez-core-protocol main"
```

---

### Task 5: Multi-prover concept page

**Files:**
- Modify: `docs/concepts/multi-prover.mdx`
- Verify against: `docs/MULTI_PROVER_SPEC.md` (full rewrite, 300-line diff) — specifically §"Architecture overview", §"Deleted in this refactor", §"Multi-prover model" (`ProofSystemBatchPerVerificationEntries`, threshold-lives-on-manager, per-PS publicInputsHash two-stage), §"Manager registration (no handoff)", §"What's been removed (and why)"

- [ ] **Step 1: Read `MULTI_PROVER_SPEC.md` in full — it is a near-total rewrite, so treat this as authoring fresh from source rather than diffing paragraph-by-paragraph.**
- [ ] **Step 2: Specifically check whether `concepts/multi-prover.mdx` still describes a manager-handoff mechanism or anything listed under the spec's "What's been removed (and why)" section — remove/correct any doc content describing now-removed mechanisms.**
- [ ] **Step 3: Confirm the "threshold lives on the manager, not the registry" framing (spec §"Threshold lives on the manager") is reflected — this was flagged in the July audit as function-name-accurate but is worth re-confirming post-rewrite.**
- [ ] **Step 4: Fix mismatches with source citations.**
- [ ] **Step 5: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0.

- [ ] **Step 6: Commit.**

```bash
git add docs/concepts/multi-prover.mdx
git commit -m "docs: rewrite multi-prover concept page against rewritten MULTI_PROVER_SPEC"
```

---

### Task 6: Cross-chain-proxy concept page

**Files:**
- Modify: `docs/concepts/cross-chain-proxy.mdx`
- Verify against: `src/base/CrossChainProxy.sol` (18-line diff — small, likely no semantic change but confirm), `docs/CORE_PROTOCOL_SPEC.md` §`createCrossChainProxy` / `computeCrossChainProxyAddress`

- [ ] **Step 1: Diff the small `CrossChainProxy.sol` change directly — confirm it's cosmetic/non-breaking for doc purposes.**
- [ ] **Step 2: Re-check the CREATE2 addressing description against current `createCrossChainProxy`/`computeCrossChainProxyAddress` source.**
- [ ] **Step 3: Fix any mismatch found.**
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0.

- [ ] **Step 5: Commit** (only if a fix was needed — otherwise note "no change required" and skip the commit).

```bash
git add docs/concepts/cross-chain-proxy.mdx
git commit -m "docs: confirm cross-chain-proxy page against eez-core-protocol main"
```

---

### Task 7: Execution-entries guide + rolling-hash concept (gap now fillable)

**Files:**
- Modify: `docs/guides/build-execution-entries.mdx`
- Rewrite from stub/gap: `docs/concepts/rolling-hash.mdx` — **previously flagged (2026-07-08) as having no source anywhere; `docs/EXECUTION_ENTRY_SPEC.md` §"Rolling Hash" (line 298) and `docs/CORE_PROTOCOL_SPEC.md` §E now exist and cover it directly.**
- Verify against: `docs/EXECUTION_ENTRY_SPEC.md` §"Action Hash", §"L2ToL1Call", §"`revertSpan`: forced-revert context", §"ExpectedL1ToL2Call", §"callCount accounting", §"Rolling Hash", §"Flow Patterns" (all 4 L1↔L2 patterns)

- [ ] **Step 1: Diff `build-execution-entries.mdx`'s existing rolling-hash CALL_BEGIN/NESTED_BEGIN walkthrough against the rewritten `EXECUTION_ENTRY_SPEC.md` §"Rolling Hash" section** — the July pass already fixed a `CALL_END`/`_currentL2ToL1Call` cursor bug here; confirm that fix's underlying mechanism still matches post-rewrite (function/variable names may have shifted even if the bug fix concept holds).
- [ ] **Step 2: Check the `revertSpan` mechanism — this term appears in the current spec (§"`revertSpan`: forced-revert context", §"When `revertSpan` is the right tool") — confirm the guide already covers it; if not, add a short section using the spec's own framing.**
- [ ] **Step 3: Write `docs/concepts/rolling-hash.mdx` from scratch using `EXECUTION_ENTRY_SPEC.md` §"Rolling Hash" + `CORE_PROTOCOL_SPEC.md` §E as the sole source.** Keep it a concept page (what rolling hash is and why), not a duplicate of the guide's step-by-step walkthrough. Add it to `sidebars.js` under "Core Concepts" (it's already listed there — confirm the file just needs real content, not a new sidebar entry).
- [ ] **Step 4: Fix mismatches, cite sources.**
- [ ] **Step 5: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, `concepts/rolling-hash.mdx` no longer a stub/gap.

- [ ] **Step 6: Commit.**

```bash
git add docs/guides/build-execution-entries.mdx docs/concepts/rolling-hash.mdx
git commit -m "docs: sync execution-entries guide + write rolling-hash concept page from EXECUTION_ENTRY_SPEC"
```

---

### Task 8: Lookup-calls guide

**Files:**
- Modify: `docs/guides/lookup-calls.mdx`
- Verify against: `docs/LOOKUP_SPEC.md` (full rewrite, 433-line diff) — §"The two modes (static/failed)", §"Field reference", §"The `callCount` partition", §"Resolution mechanics" (`staticCallLookup` / `_executeRevertedNestedLookup` / `_executeRevertedTopLevelLookup`), §"Context binding: `executingLookupIndex`", §"State-root pins", §"L1/L2 differences"

- [ ] **Step 1: Treat as fresh authoring given the near-total rewrite — read the full current spec first, then read the current guide.**
- [ ] **Step 2: Specifically re-verify the `callCount == 0` explanation for static/failed lookups (spec §3, "Why `callCount == 0`...") — this is a subtle point worth double-checking word-for-word against spec, not paraphrased from memory of the old version.**
- [ ] **Step 3: Confirm `executingLookupIndex` is described as "enforced, not convention" per spec §5 — if the guide describes it as a soft convention, fix.**
- [ ] **Step 4: Fix mismatches, cite sources.**
- [ ] **Step 5: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0.

- [ ] **Step 6: Commit.**

```bash
git add docs/guides/lookup-calls.mdx
git commit -m "docs: rewrite lookup-calls guide against rewritten LOOKUP_SPEC"
```

---

### Task 9: Post-verify-batch guide + register-rollup guide (gap now fillable)

**Files:**
- Modify: `docs/guides/post-verify-batch.mdx`
- Rewrite from stub/gap: `docs/guides/register-rollup.mdx` — **previously flagged (2026-07-08) as having no source; `docs/CORE_PROTOCOL_SPEC.md` §B.1 `registerRollup` (line 295) now fully specifies it.**
- Verify against: `docs/CORE_PROTOCOL_SPEC.md` §`postAndVerifyBatch` (line 306), `docs/MULTI_PROVER_SPEC.md` §"`postAndVerifyBatch` flow (current)" + §"Reentrancy reasoning", §"registerRollup" (line 295-302), §"Manager registration (no handoff)"

- [ ] **Step 1: Diff `post-verify-batch.mdx`'s 8-step pipeline walkthrough against the current `postAndVerifyBatch` flow section in `MULTI_PROVER_SPEC.md` — step count/order may have shifted with the multi-prover rewrite.**
- [ ] **Step 2: Write `docs/guides/register-rollup.mdx` from scratch using `CORE_PROTOCOL_SPEC.md` §`registerRollup` as the sole source.** Cover: permissionless call, `rollupId = ++rollupCounter` (first id is 1, 0 is `MAINNET_ROLLUP_ID`), the `InvalidRollupContract` revert condition (zero address or the registry itself), the one-shot `rollupContractRegistered(rollupId)` callback, and that the caller must deploy their own `IRollupContract`-conforming manager (with proofSystems/vkeys/threshold/ownership baked in) *before* calling `registerRollup`. It's already listed in `sidebars.js` under "Guides" — confirm the file just needs real content.
- [ ] **Step 3: Fix mismatches on `post-verify-batch.mdx`, cite sources.**
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, `guides/register-rollup.mdx` no longer a stub/gap.

- [ ] **Step 5: Commit.**

```bash
git add docs/guides/post-verify-batch.mdx docs/guides/register-rollup.mdx
git commit -m "docs: sync post-verify-batch guide + write register-rollup guide from CORE_PROTOCOL_SPEC"
```

---

### Task 10: Flash-loans + bridge-tokens guides

**Files:**
- Modify: `docs/guides/flash-loans.mdx`, `docs/guides/bridge-tokens.mdx`
- Verify against: `script/flash-loan-test/ExecuteFlashLoan.s.sol` (275-line diff), `DeployFlashLoan.s.sol`, `DeployInfra.s.sol`, `src/periphery/Bridge.sol`, `src/periphery/defiMock/FlashLoanBridgeExecutor.sol` (6-line diff)

- [ ] **Step 1: Diff `flash-loans.mdx`'s L1/L2 swimlane diagram and prose against the current `ExecuteFlashLoan.s.sol` script flow — 275 lines changed is substantial, check whether the step sequence or contract call order shifted.**
- [ ] **Step 2: Diff `bridge-tokens.mdx` against current `Bridge.sol` (34-line diff — check for renamed functions or changed revert conditions).**
- [ ] **Step 3: Fix mismatches, cite sources.**
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0.

- [ ] **Step 5: Commit.**

```bash
git add docs/guides/flash-loans.mdx docs/guides/bridge-tokens.mdx
git commit -m "docs: sync flash-loans + bridge-tokens guides to eez-core-protocol main"
```

---

### Task 11: Reference pages — caveats (known critical fix), security, glossary

**Files:**
- Modify: `docs/reference/caveats.mdx`, `docs/reference/security.mdx`, `docs/reference/glossary.mdx`
- Verify against: `docs/CAVEATS.md` (small diff, but semantically critical — see Step 1), `docs/MULTI_PROVER_SPEC.md` §"Trust model"

- [ ] **Step 1: KNOWN FIX — apply this concrete correction to `reference/caveats.mdx` first.** The persistent-queue consumption model changed:
  - OLD (what the doc likely still says): match-time failures are *skipped* (forward-scan past non-matching candidates via `_findMatchingEntry`), so multiple alternative/candidate entries gated by different `StateDelta.currentState` values CAN be stacked in the *persistent* queues, and errors were named `ExecutionNotFound`/`RollingHashMismatch`/`EtherDeltaMismatch`; the immediate-prefix skip mechanism was `_attemptExecuteImmediateL2Txs` emitting `L2TxSkipped`, with `AllImmediateL2TxsFailed` as the all-fail case.
  - NEW (current source, `docs/CAVEATS.md`): there is now **one deterministic consumption order — no alternative/candidate entries in the persistent queues at all.** A persistent entry that reverts mid-execution (`StateRootMismatch`/`RollingHashMismatch`) blocks the queue rather than being skipped — it does NOT advance the cursor, and stacking alternatives in the persistent path does not work. Only the IMMEDIATE prefix still supports stacked alternatives, via `attemptApplyImmediate`, emitting `ImmediateEntrySkipped` on a reverting candidate.
  - Also update the transient-phase paragraph: `_transientEntries` → `_transientExecutions`; `_consumeAndExecuteEntry` → `_consumeAndExecute`; `staticCrossChainCall`/`_transientStaticEntries` → `staticCallLookup`/`_tryRevertedTopLevelLookup`.
  - Read the full current `docs/CAVEATS.md` for any other edge cases beyond these two paragraphs and apply the same doc-vs-doc-vs-source check to the rest of the file.
- [ ] **Step 2: Re-check `reference/security.mdx`'s trust-model section against `MULTI_PROVER_SPEC.md` §"Trust model" — confirm the "no production ZK verifier, dev-grade ECDSA only, no audit/bounty yet" framing is unchanged (per `[[eez-public-code-availability]]`, this is still true as of this plan's writing — confirm, don't assume).**
- [ ] **Step 3: Sweep `reference/glossary.mdx` for terms introduced or renamed by this whole audit pass** (`attemptApplyImmediate`, `ImmediateEntrySkipped`, `StateRootMismatch`, `revertSpan`, any Blob-format terms from Task 12) — add short entries for genuinely new terms used elsewhere on the site; don't pad with terms used only once.
- [ ] **Step 4: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0.

- [ ] **Step 5: Commit.**

```bash
git add docs/reference/caveats.mdx docs/reference/security.mdx docs/reference/glossary.mdx
git commit -m "docs: fix persistent-queue consumption model in caveats, confirm security trust model, sweep glossary"
```

---

### Task 12: New Blob Format concept page

**Files:**
- Create: `docs/concepts/blob-format.mdx`
- Modify: `sidebars.js` (add to "Core Concepts" category)
- Verify against: `docs/blobs/BLOB_FORMAT_SPEC.md` (457 lines, entirely new — sole source, this is new authoring not an audit)

- [ ] **Step 1: Read `docs/blobs/BLOB_FORMAT_SPEC.md` in full.** It defines a binary wire format for publishing chain activity as one message stream: reserved version byte (§6, hardcoded `00`), then a stream of messages each starting with a `message_type` byte selecting either a content-message shape (`message_type | …fields…`) or a marker-message shape (lone `message_type` byte). §1.1 "Wire encoding" specifies little-endian fixed-width scalars (`u8`/`u16`/`u32`/`u64`/`u128`/`u256`).
- [ ] **Step 2: Write `docs/concepts/blob-format.mdx` as a concept page** (why the format exists, the framing/message-type model, the two message shapes, the wire-encoding conventions) at the same depth/style as `concepts/multi-prover.mdx` — prose + one Mermaid diagram showing the version-byte-then-message-stream framing, styled per the existing site conventions (`future.faster: false`, EEZ green-on-black `themeVariables` already set globally, capsule/hexagon/friction-amber grammar from the design brief if a transaction-boundary or revert concept appears in the format). Do not invent message-type names or field layouts not in the spec — quote/cite the spec's own §2 per-type definitions if summarizing them.
- [ ] **Step 3: Add `'concepts/blob-format'` to `sidebars.js`'s "Core Concepts" category items array.**
- [ ] **Step 4: Cross-link from wherever it's relevant** (`architecture.mdx` if blobs are part of the top-level flow per the spec's own framing — confirm by re-reading how `BLOB_FORMAT_SPEC.md` positions itself relative to batches/entries before adding the link, don't assume).
- [ ] **Step 5: Run build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && npm run build`
Expected: exits 0, new page reachable from the sidebar.

- [ ] **Step 6: Commit.**

```bash
git add docs/concepts/blob-format.mdx sidebars.js
git commit -m "docs: add Blob Format concept page from BLOB_FORMAT_SPEC"
```

---

### Task 13: Final site-wide sweep (push/merge handled by finishing-a-development-branch, not this task)

**Files:**
- Spot-check only (no source changes expected): `docs/tools/visualizator.mdx`, `docs/tools/trace-decoder.mdx`, `docs/introduction.mdx`, `docs/quickstart.mdx`
- No new source to verify against — `visualizator/` and `trace-decoder/` dirs confirmed unchanged; `introduction.mdx`/`quickstart.mdx` are onboarding pages, lower technical-claim density.

- [ ] **Step 1: Skim the 4 spot-check pages for any cross-link to a page changed in Tasks 1-12 whose anchor/heading may have moved** (e.g. if Task 5 or 8 changed a heading `quickstart.mdx` links to).
- [ ] **Step 2: Full clean build.**

Run: `cd /Users/armagan/eez-docs/.worktrees/docs-core-protocol-sync-audit && rm -rf build .docusaurus && npm run build`
Expected: exits 0, zero broken-link warnings anywhere on the site (not just the touched files).

- [ ] **Step 3: Serve locally and screenshot the new Blob Format page + the fixed caveats page via headless Chrome, per the established verification method, to confirm they render correctly (not just build cleanly).**

Run: `npx docusaurus serve --port 3300 &` then `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --screenshot=/tmp/blob-format-check.png --window-size=1200,1600 http://localhost:3300/concepts/blob-format`

- [ ] **Step 4: Commit any Task 13 fixes on the branch, then stop.** Do not push, merge, or touch `main` — that decision belongs to `superpowers:finishing-a-development-branch`, run by the controller session after the final whole-branch review, not to this task.

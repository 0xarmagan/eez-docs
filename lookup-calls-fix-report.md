# lookup-calls.mdx Fix Report

Source verified at commit `60c184b` in `/private/tmp/claude-501/-Users-armagan/29fdf962-4e57-4d4a-8870-3b97dbee1cc3/scratchpad/eez-core-protocol` (`src/EEZ.sol`, `src/L2/EEZL2.sol`, `src/base/CrossChainProxy.sol`).

## Finding 1 (CRITICAL) — wrong resolver attributed to reverting try/catch calls

**Was wrong:** The page's intro said "Both static reads and reverting calls are resolved through the same lookup infrastructure," then the "Two Modes" and "Resolution Mechanics" sections presented `staticCallLookup` (untagged, `_processNStaticCalls`) as the resolver for both `failed==false` static reads AND `failed==true` reverting try/catch calls.

**Real mechanism:** `CrossChainProxy._fallback()` (`src/base/CrossChainProxy.sol:84-97`) detects the caller's opcode via a `tstore` probe in `staticCheck()` (write reverts under `STATICCALL`, succeeds under regular `CALL`). Dispatch is by opcode, not by the `failed` flag:
- `STATICCALL` → `EEZ.staticCallLookup` (`src/EEZ.sol:1300`), untagged hash via `_processNStaticCalls` (`src/EEZ.sol:1270`), real `STATICCALL`s only, cannot mutate state.
- Regular `CALL` (what a `try/catch`-wrapped external call compiles to) → `executeCrossChainCall` → `_consumeNestedAction` (nested, `src/EEZ.sol:882`) or `_consumeAndExecute` (top-level, `src/EEZ.sol:964`). Both try their primary (non-lookup) match first; only on a **miss** do they fall back to a `failed==true` lookup match:
  - Nested miss → `_executeRevertedNestedLookup` (`src/EEZ.sol:1201`)
  - Top-level miss → `_tryRevertedTopLevelLookup` (`src/EEZ.sol:1357`) → `_executeRevertedTopLevelLookup` (`src/EEZ.sol:1218`)
  - Both funnel into shared `_executeRevertedLookup` (`src/EEZ.sol:1235`): tagged hash schema, real sub-calls via `_processNCalls` (`src/EEZ.sol:1035`, genuine `CALL`/`STATICCALL` per sub-call — can mutate state).

A `failed==false` entry is only ever reachable via the `STATICCALL` route (confirmed by `_consumeNestedAction`'s doc comment at `src/EEZ.sol:876-881`: a successful reentrant CALL is expressed as an `ExpectedL1ToL2Call`, not a lookup). A `failed==true` entry is reachable via *either* route depending on the caller's opcode.

**Fix:** Rewrote the page intro, the "Two Modes" section (renamed "Two Modes, Two Possible Dispatch Routes"), and fully restructured "Resolution Mechanics" into "Path 1 — STATICCALL → `staticCallLookup`" and "Path 2 — regular CALL → `executeCrossChainCall`", naming all four required functions (`_consumeNestedAction`, `_executeRevertedNestedLookup`, `_tryRevertedTopLevelLookup`, `_executeRevertedTopLevelLookup`) plus their shared tail `_executeRevertedLookup`. Added a `:::info` box restating the opcode-vs-flag distinction. Also added a short note on the `tstore` detection mechanism in `CrossChainProxy._fallback()`.

## Finding 2 (IMPORTANT) — self-contradiction on "Failed mode"

**Was wrong:** Line 85 (old) said "a `failed` lookup matched during execution always runs through the reverted-lookup path; `staticCallLookup` always resolves statically" — directly contradicting the fact that `staticCallLookup` itself resolves `failed==true` entries reached via `STATICCALL` (confirmed by `_resolveStaticLookup`, `src/EEZ.sol:1185`, which reverts with `returnData` when `failed` is true, and by `staticCallLookup`'s call site at line 1326/1343 passing `el.failed`/`sc.failed` straight through with no branch).

**Fix:** Rewrote the "Why `callCount == 0`" section's split-criterion paragraph to state the split is by which opcode reached the match (not solely by `failed`), and that a `failed==true` entry can be resolved by either route. This resolved naturally once Finding 1's Resolution Mechanics rewrite was in place — same story now told consistently in the intro, "Two Modes" section, "Why callCount==0" section, "Resolution Mechanics," and the closing `:::info` box.

## Finding 3 (IMPORTANT) — Invariants Summary overclaims on-chain enforcement

**Was wrong:** "When building lookup entries, follow these rules or the batch will revert on-chain" was applied uniformly to all bullets, including `failed==false` requires `callCount==0`/`expectedL1ToL2Calls.length==0`/`expectedLookups.length==0` — but `_resolveStaticLookup(calls, rollingHash, failed, returnData)` (`src/EEZ.sol:1185-1197`) takes only those four parameters and never reads `callCount`, `expectedL1ToL2Calls`, or `expectedLookups` at all. This directly contradicted the page's own earlier correct statement (old line 81): "`callCount` is unused and must be `0` (a prover convention — the static resolvers never read it)."

**Fix:** Rewrote the Invariants Summary intro to distinguish "enforced on-chain when actually consumed" (verified against `_executeRevertedLookup`'s end-of-frame checks at `src/EEZ.sol:1255-1258`, which do check `callCount`/hash-schema/partition/`expectedL1ToL2Calls.length` — but only on the regular-CALL reverted-lookup route) from the one bullet that is genuinely a prover-only convention never read on-chain. Explicitly flagged that bullet.

## Finding 4 (IMPORTANT) — `destinationRollupId` mischaracterized as phase-conditional

**Was wrong:** The page said the on-chain match "adds a third term" (`destinationRollupId`) only during the mid-flight/transient phase, implying persistent-phase queue routing alone enforces it (no explicit check in the persistent branch).

**Real mechanism:** `staticCallLookup`'s top-level loop (`src/EEZ.sol:1333-1345`) checks `sc.crossChainCallHash == crossChainCallHash && sc.destinationRollupId == destRid && _stateRootsMatch(sc)` unconditionally — this same code runs against whichever table `_activeLookupCalls(destRid)` (`src/EEZ.sol:1378`) returns (transient or persistent), with no phase branch on the match condition. `_tryRevertedTopLevelLookup` (`src/EEZ.sol:1357-1371`) is identical. The persistent-phase check is redundant (the per-rollup queue only ever holds that rollup's entries) but is still literally evaluated every time.

**Fix:** Updated: (1) struct table's Match key cell for `LookupCall`, (2) the mid-flight paragraph in "LookupCall: Top-Level Lookups," (3) both branches of the Resolution Mechanics pseudocode (Path 1), (4) the L1/L2 differences table's "Match fields" row and the `destinationRollupId` row, and (5) added a note to the `expectedStateRoots` binding section — all now consistently state `destinationRollupId` is checked unconditionally in both phases.

## Build Verification

`npm run build` from worktree root: **exit 0**. No broken-link warnings; only an unrelated Node `ExperimentalWarning: localStorage is not available`. All new in-page anchor links (`#resolution-mechanics`, `#two-modes-two-possible-dispatch-routes`, `#how-crosschainproxy-routes-to-staticcalllookup`) resolved (Docusaurus would fail the build on a broken anchor).

## Self-Review

Re-read the whole page after editing. Confirmed no leftover contradictions:
- Intro, "Two Modes," "Why callCount==0," "Resolution Mechanics," and the closing `:::info`/Invariants bullet all now tell the same opcode-based dispatch story.
- All four named functions (`_consumeNestedAction`, `_executeRevertedNestedLookup`, `_tryRevertedTopLevelLookup`, `_executeRevertedTopLevelLookup`) appear with correct roles and are cross-referenced from at least two sections each.
- `destinationRollupId` is described identically (unconditional, both phases) everywhere it's mentioned: struct table, prose, pseudocode, L1/L2 table.
- Invariants Summary bullets are now individually annotated with their actual enforcement status, matching the earlier correct callCount==0 prover-convention framing rather than contradicting it.

This was a mechanism-level fix, not a wording patch: the previous page had exactly one resolver function (`staticCallLookup`) doing work that in the real contracts is split across five functions on two entirely different dispatch routes with different hash schemas and different state-mutation guarantees. The rewrite introduces that real two-path structure explicitly (Path 1 / Path 2) so a careful re-check against `src/EEZ.sol` should find matching names, matching hash-schema claims (untagged/no-mutation vs. tagged/can-mutate), and matching phase behavior for `destinationRollupId`.

## Concerns

- I did not exhaustively re-verify every pre-existing, unflagged sentence on the page against source (e.g. the `executingLookupIndex` section, the balance-read worked example) — only the sections implicated by the four findings and their immediate neighbors, since the task scoped "Resolution Mechanics" and its self-contradictions. A quick pass suggests the untouched sections were already accurate and consistent with the fixes.
- The `LOOKUP_SPEC.md` citation on line 101 ("Source: `LOOKUP_SPEC.md` §3...") was left as-is since it wasn't part of the flagged findings and I did not have that spec doc available to verify it independently.

---

## Follow-up Fix (post adversarial re-check): `expectedStateRoots` empty-array claim

**Was wrong:** State Root Binding section and the closing `:::note` both claimed an empty `expectedStateRoots` array "matches unconditionally" / "is valid."

**Real mechanism:** `postAndVerifyBatch`'s structural validation, `_validateStructure` (`src/EEZ.sol:562-583`), requires every `LookupCall`'s own `destinationRollupId` to appear among its `expectedStateRoots` pins:
```solidity
if (!_contains(verifiedRollups, lc.destinationRollupId)) {
    revert LookupDestinationNotPinned(lc.destinationRollupId);
}
```
where `verifiedRollups` is built solely from that `LookupCall`'s own `pins` (`expectedStateRoots`), strictly-increasing-by-rollupId and each required to be `_containsRollupInBatch`. An empty `expectedStateRoots` array yields an empty `verifiedRollups`, so the `_contains` check always fails — **every** `LookupCall` is rejected at publish time unless it pins at least its own `destinationRollupId`. This check is unconditional (not gated by `failed`) and runs at **publish time** (structural validation, before proof verification), distinct from the live-state-root equality check `staticCallLookup`/`_stateRootsMatch` runs at **resolution time**. The page's own worked example (pinning `rollupId: 1` for `destinationRollupId: 1`) was already consistent with the real rule — only the surrounding prose was wrong.

Exact requirement verified: `expectedStateRoots` must contain a pin for the lookup's own `destinationRollupId` (mandatory, minimum one entry); it may additionally carry pins for any other rollup covered by the batch (validated via `_containsRollupInBatch`), which is the mechanism for pinning a specific cross-rollup interleaving beyond just the destination.

**Fix:**
- Rewrote the "State Root Binding (L1)" section: removed the "empty array matches unconditionally" claim, replaced with the real `LookupDestinationNotPinned` publish-time requirement, and clarified additional pins are optional/allowed but the destination pin is mandatory.
- Rewrote the closing `:::note`: removed "empty array is valid," reframed around the prover choosing *additional* pins beyond the one mandatory destination pin.
- Added a new Invariants Summary bullet: `expectedStateRoots` must include the lookup's own `destinationRollupId`, enforced at publish time via `_validateStructure`/`LookupDestinationNotPinned`, for every `LookupCall` regardless of `failed`.

**Build:** `npm run build` — exit 0, no broken-link warnings.

**Self-review:** Confirmed no remaining "matches unconditionally" / "empty array is valid" language anywhere in the file (grep-verified). The three touched spots (State Root Binding prose, Invariants Summary, closing note) now tell one consistent story: `expectedStateRoots` is never legitimately empty for a published `LookupCall`; the mandatory content is the lookup's own destination pin, with room for additional pins layered on top.

# eezl2.mdx audit fix report

Verified against `eez-core-protocol` @ `60c184b` (`src/L2/EEZL2.sol`, `src/interfaces/IEEZL2.sol`, `src/base/EEZBase.sol`).

## Fixes applied

1. **`computeCrossChainCallHash`** — added a full function entry (inherited from `EEZBase`, `public pure`), with signature, parameters, and return value.
2. **`executeInContextAndRevert`** — added a full function entry: self-call-only (`NotSelf` gate), always reverts via `ContextResult`, documented as the mechanism behind `revertSpan`.
3. **`CrossChainProxyCreated`** — added to the Emits lists of both `executeCrossChainCall` (both top-level and nested branches) and `executeIncomingCrossChainCall`, noting it fires conditionally when `_processNCalls` auto-registers an unregistered source proxy via `_createCrossChainProxyInternal`. Also broadened the Events-table description for `CrossChainProxyCreated` itself.
4. **`EntryExecuted` ordering** — moved to the end of both functions' Emits lists (after `CallResult`/`OutgoingCallConsumed`/`RevertSpanExecuted`), matching real emission order confirmed in source (`_consumeAndExecute` / `executeIncomingCrossChainCall`).
5. **`executeCrossChainCall` nested branch** — split Emits/Returns into "Top-level call" vs "Nested (reentrant) call" sections; nested path never emits `ExecutionConsumed`/`EntryExecuted` and returns `nested.returnData`, not `entry.returnData`.
6. **Events table `indexed` qualifiers** — added `indexed` to `ExecutionConsumed`, `IncomingCrossChainCallExecuted`, `EntryExecuted`, `CallResult`, `OutgoingCallConsumed`, `RevertSpanExecuted` signatures, matching source.
7. **Inherited labels** — added "(inherited from EEZBase)" to `createCrossChainProxy` and `computeCrossChainProxyAddress` summaries.
8. **`authorizedProxies` description** — added the `_processNCalls` → `_createCrossChainProxyInternal` auto-registration path alongside the explicit `createCrossChainProxy` entry point.
9. **`uint64` truncation** — documented in the `authorizedProxies` Public State row and in `createCrossChainProxy`'s description (registration silently truncates `originalRollupId` above `type(uint64).max`).

Item 10 (SameNetworkProxy error-table row) was confirmed not a real issue per page-wide convention — left unchanged.

## Verification

- `npm run build` — exit 0, no new broken-link warnings.

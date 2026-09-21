# Devin cycle 05 — 2026-09-21T06:23Z (engine 2026.9.16.5, no drift)

Live: Richard #1 `7c370daf` 1903.2; relh #2 v159 `ce5bfbfa` 1768.9 (+35); Coach #3 `2bb94c84` 1670.5; Aaron #4 `61148477` 1661.2 (+1); Alex #5 `a30542cb` 1658.5; Jordan #6 `207ffaf9` 1618.2.
Ownership: single-writer retained (no foreign XP requests since 2026-09-20T22:14:20Z; 0 pending/submitted/running). Spend today 0/1600. No hosted spend, no deploy, no membership change.

## Head-to-head, exact current versions, all league-watch episodes (h2h-current-versions.txt)
- Aaron 20W 10L 2D; Coach 16W 12L 3D.
- **relh v159: 0W 9L vs us** (Aaron blue 0-3, red 0-1; Coach blue 0-4, red 0-1) — trigger sustained (3rd consecutive check).
- New watch: daveey-2 `gota-codex-side-aware-team-secondary-20260917:v1` 3W 0L vs us (Aaron red/blue, Coach red) — below us on the board, but needs ≥2 more checks.
- macromackie v4: Coach blue 0-2, red D-D; Aaron blue 0-1, red D-D (watch).
- Richard blue: Aaron 4-0, Coach 2-0; Richard red: Coach 0-1 (known).

## Local step: activation test of the H-ALLY-UNDER-ATTACK-01 predicate on hosted relh replays (no hosted spend)
Predicate (v2 form, public observations only): enemy hero ≤6 tiles whose public target is a living allied hero ≤6 tiles from self, while self's own target is a creep or none.
Evaluated offline over the hash-validated observer trajectories captured in cycle 03:
- Blue loss `ereq_ea546a70` (slot-5 view): fires for heroes 108 @tick 1418 (R104→105, self on creep, d²=26/0) and 107 @1436; total activation ticks 108:61, 107:59, 106:42, 109:105, 105:5 — i.e. exactly the diagnosed focus-fire window where two of ours kept hitting creeps while 105 died.
- Red loss `ereq_b551c346` (slot-0 view): 0 activation ticks in 220 ally-attacked ticks — the red loss is the 5-stack lane push (different mechanism; H-RED-TRANSIT-01 territory), not a retarget failure.
- `ereq_7fc140bc`: no observer trajectory captured (identical stream to ea546a70).
Conclusion: the belief is *observable and timely* in the blue loss; cycle-04's v2 failed only on runtime (extra 64-object scan → instruction-limit invalids and +2.1k instr). Zero activation vs Richard locally is consistent (Richard does not present this geometry to us).

Constraint found: the parent BASIC already uses exactly 256 scalar globals (GotA `maxGlobals = 256`), so any repair must be zero-new-globals (explains the cycle-04 global-cap failure).

## Next discriminating test (cycle 06)
v3: fold the assist detection into the parent's existing single object pass (R2 attack, main scan at policy.bas ~1313–1387) using the previous-tick nearest-ally id as the victim reference (scratch `mTD`), no second scan, no new globals. Gates: verify.py exact; both colours vs Richard v135 & parent — 0 invalid, max instr ≤ parent+600, no regression; then hosted A/B vs relh v159 via the durable journal (≤400 eps: candidate vs relh both colours + parent control), Coach first if it qualifies.

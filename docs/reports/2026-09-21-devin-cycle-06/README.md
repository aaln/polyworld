# Devin cycle 06 — 2026-09-21T08:23Z

Monitor 08:23:45Z (engine 2026.9.16.5, no drift): Richard #1 `7c370daf` v135 · relh #2 `ce5bfbfa` v159 · Coach #3 `2bb94c84` · Aaron #4 `61148477` · Alex #5 `a30542cb` · Jordan #6 `207ffaf9`.
H2H current versions vs relh v159 in window: Aaron blue 0-3, Coach blue 0-4 / red 0-1 → trigger sustained. Ownership unchanged (Aaron incumbent, Coach challenger, a-aron retired); single-writer held.

## H-ALLY-UNDER-ATTACK-01 v3 (single pass, zero new globals)
- source `d60f9626…`, policy IR `e170dea4…`, parent `c708970d…`; verify.py OK (79 compiler modules).
- Offline activation on hosted relh trajectories: blue loss fires (108 @1418, 107 @1496, victims 105/108, enemy 104, ordinary target = creep); red loss 0 fires.
- Local screen (pinned engine, seeds 54/101/202): vs Richard v135 red 0-3-0, blue 3-0-0, 0 INVALID, 3 streams each, max instr 19001/16660 (+591/+661 vs parent); vs parent red 0-2-1, blue 3-0-0. Parent mirror control red 0-2-1, blue 2-0-1. No regression, no invalid, instruction gate met.
- Hosted A/B (tools/gota_autoresearch/hosted_ab.py, frozen plan, idempotent keys, journaled before POST), fixed 5v5 seats vs relh v159, 40 platform-seeded episodes/arm:
  - candidate red 0W/40L/0D/0 INVALID · candidate blue 0W/40L/0D/0 INVALID · control (deployed Aaron source) red 0W/40L/0D/0 INVALID · control blue not purchased (candidate already below its absolute floor of 16/40; frozen request kept).
  - Mechanism: hosted candidate-blue observer trajectory (state hashes validated, 5706 ticks) is hero-state identical to the cycle-03 parent loss except one target field on hero 109 at tick 805; death timeline identical (105@1496, 107/108@1713, 106@2182, 109@2305). The v3 predicate is true at tick 1418 but the compiled attack branch produced no effective retarget → attempted ≠ effective. **Falsified; null result; incumbent retained; nothing deployed; no membership change.**
- Uploaded version `b507afaa` is inert (tagged unvalidated), not in any league.

Spend: 120 episodes this cycle (limits 400/cycle, 1600/day); active requests 0 at end. Next: see progress.json (H-RED-TRANSIT-01 red fork; scenario-vm single-tick trace of hero 108 @1418 to find why the retarget is not emitted).

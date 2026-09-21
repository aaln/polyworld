# Devin cycle 04 — 2026-09-21T04:23Z (engine 2026.9.16.5, no drift)

Live: Richard #1 `7c370daf` 1922.5; relh #2 v159 `ce5bfbfa` 1733.4; Coach #3 `2bb94c84` 1683.2 (+1); Alex #4 `a30542cb` 1674.6; Aaron #5 `61148477` 1648.8; Jordan #6 `207ffaf9` 1619.2.
Trigger (relh v159, from cycle 03) still active → one repair hypothesis tested locally. No hosted spend (0/1600), 0 pending requests, no deployment, no membership change. Aaron incumbent, Coach challenger, a-aron retired.

## H-ALLY-UNDER-ATTACK-01 — result: FALSIFIED (v1), NOT QUALIFIED (v2). Incumbent retained.
Parent: formation-adaptive-20260920 `c708970d…36a4`. Authentic Richard v135 `f48bb005…5a30`. Pinned engine f2ab959. Seeds 54/101/202, both colours, 5v5 same-source teams.

| arm | source sha256 | vs Richard red | vs Richard blue | vs parent red | vs parent blue | max instr | distinct streams | invalid |
|---|---|---|---|---|---|---|---|---|
| parent (control) | c708970d… | 0W 3L (1 stream) | 3W 0L (1 stream) | – | – | 18,410 | 2 | 0 |
| v1 `ally-under-attack-20260921` (any target, 8 tiles) | 28a33472… / bas 947ddfae… | 0W 3L | **0W 3L** (parent 3W) | killed (dir overwrite, see below) | 3W 0L (1 stream, 40 deaths/16k ticks) | 17,858 | 6 (Richard) | 0 |
| v2 `ally-under-attack-v2-20260921` (creep-only override, victim ≤6 tiles) | 5608d806… / bas 68a225c8… | 0W 3L | 3W 0L | **3 INVALID: VM "BASIC instruction limit exceeded" in slot 3** | 3W 0L (44–63 deaths) | 19,565 | – | 3 |

Mechanism evidence:
- v1: blue vs Richard turned 3W→0L with 20–32 candidate deaths per game (parent: 4). Override of `bestId` for any ally-targeting enemy within 8 tiles pulls heroes off structures/kite logic into Richard's stack → the repair is worse than the disease. Falsifier "regresses vs Richard controls" hit.
- v2: every v2-vs-Richard state hash equals the parent's (`A642C998/C7E34274/077F3B72` red, `D3D43335/8A91181B/2F9081DF` blue) → the narrowed predicate never fired vs Richard (zero activation), while costing +1,155 (red) / +2,101 (blue) instructions (>+1,500 falsifier budget on blue) and exceeding the VM instruction limit in red games vs the parent (invalid runs, preserved, not counted as losses).
- Neither variant was tested against relh v159 (no authentic relh source locally; hosted A/B not run because local gates failed).

Evidence handling: the v1 candidate JSON/replays were overwritten by a mis-pathed v2 run (harness path bug); the v1 harness summary was captured before overwrite (screen-v1-results.md). Raw v2 replays/JSON stay private under `.gota/cycles/20260921T0423Z-devin/`. First v1 build failed the BASIC global cap (new globals) — preserved in `screen-invalid-globals/`.

## Next discriminating test
Rewrite the assist predicate at the *belief* layer with per-tick memoised scan (avoid a second 64-object scan inside attack), and activation-test it against the hosted relh replay `ereq_ea546a70` tick 1470 via the semantic episode probe before any full-game screen. Also consider H-RED-TRANSIT-01 (red 1/2/2 dispersal) which is shared by the Richard and relh red losses.

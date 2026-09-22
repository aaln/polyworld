# Current-release ranged draft and microplay

Primary IR: `policy.py`. Generated BASIC retains exact practiced source **b82c3799**, registered as Aaron **f3f8baab-d02a-4f7f-8fc9-e1f050f967a7**. Engine **2026.9.21.5 / f776d5e**. This evidence bundle does not itself select a league champion.

The user episode ran old Coach compat, which chose Vanguard while Ranger was available. relh Ranger ended level 8 with 2,685 XP/no deaths; Coach level 2 with 209 XP/five deaths. Three teammates failed their VMs. Exact replay/draft/XP are verified, but that game is not clean strength evidence. Current real-host fixtures pick Ranger after Crossbowman and Arcanist when Ranger is taken, at tick 13.

The current pair keeps ranged-first drafting, explicit ability upgrades, practiced basic recovery/last hits/XP positioning, gear purchases and purposeful portals. Further reserve/attention changes were rejected after fresh responsive matched-color tests. Old IR assumptions and historical win-only gates no longer govern new experiments; the completed parent panel remains frozen.

Mixed comparison: 160 audited hosted games, one first-pick subject per team, exact matched rosters per color. Current score gate passed: **True**. An additional 160-game third-pick guardrail passed: **True**; its full results are in `evidence/current/middle-field`.

| Policy | Color | Mean score | Mean XP | Deaths | Level | W/L/D | Distinct streams |
|---|---|---:|---:|---:|---:|---|---:|
| candidate | red | 4081.61 | 7159.2 | 3.95 | 13.45 | 24/11/5 | 40 |
| candidate | blue | 2511.85 | 4525.3 | 2.62 | 10.53 | 39/0/1 | 40 |
| control | red | 0.00 | 362.7 | 3.83 | 2.62 | 0/40/0 | 37 |
| control | blue | 0.00 | 1162.5 | 8.85 | 4.92 | 29/3/8 | 40 |

XP-score comparison is per hero, with draft/world-time penalty. Fort outcomes are diagnostic. The two fixed rosters, repeated streams and first-pick seats limit generalization. No number-one rank or every-opponent/every-color score claim. Full original target evidence and all rejected refinements are preserved.

Run `python3 verify.py` for offline identity/result checks. Use `python3 convert.py compile --policy policy.py --out /tmp/new-current-pair` to regenerate edited IR, or `extract --source edited.bas` to reflect BASIC edits back into IR. Changed executable bytes invalidate prior beliefs. Raw replays/API inputs remain in `tmp/gota-targets-20260922`; historical coaching captures are unchanged.

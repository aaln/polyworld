# Druid lane recovery: qualified and deployed

The Druid stays in lane while safe, useful healing can recover a health-only
retreat. It resumes at 60% HP/20% mana, waits at most 12 seconds, and retains
returns for affordable missing core gear, unavailable healing or danger.
Other hero controllers retain blue-center behavior.

| Natural later-draft context | Baseline points | New points | Change |
|---|---:|---:|---:|
| Red | 71.10 | 106.11 | +49.24% |
| Blue | 475.58 | 682.06 | +43.42% |
| Pooled | 273.34 | 394.09 | +44.17% |

One frozen source, 400 fresh games, 100 per source/color. The 95% bootstrap
pooled gain interval is **+9.73% to +92.18%**. All source, VM, full-replay,
XP and integer-score checks pass; all four cells have 100 distinct streams.
Druid exposure is 175 control and 172 candidate games. The game and principal
champions remained stable. Both color floors and all prospective gates pass.
Scope is fixed natural later-draft rosters, not universal ranking or causality
of individual edits. Scores remain low, especially on red.

Blue improves hero XP 415.50→528.00 and creep XP 1879.84→2023.04, with slightly
shorter games. Deaths rise 5.10→5.30; this is not an overall survival claim.
In the 16-game descriptive diagnostic subset, recovered homeward ticks without
affordable missing core gear decline (red36.75→0,blue698.25→107.25 per game).
Classes/scenes differ and the subset does not establish a causal effect.

582 local checks pass; maximum14,962instructions/22,028work. Sixteen main native
cases include eight preserved deterministic local controls; four additional
Ranger/Crossbowman cases complete20native cases. Non-Druid command streams and
terminal states match exactly in these cases. No hosted controls were reused.

[Exact portable IR/policy pair](druid-lane/manifest.json), [full score report](evidence/report.json),
[effects](evidence/effects-summary.json), [plot](evidence/score-breakdown.png),
and [deployment readback](../druid-lane20260923-deployment/README.md) are preserved.
Run `python druid-lane/verify.py` for conversion, source and artifact equality.
Initial and local IR remain in the local capsule; reviewed hosted IR is
`d331ba094eae5ac56e4dbe8533b29b543df089a7720ca2b3d52943d02734e122`.
Source remains `29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36`.

Coaching session `2026-09-23t02-52-57-098ze03810`, verified episode
`ereq_7ad01f93-5ee5-4eca-ba01-a9b7ee9ea658`; all51captured files remain unchanged.
The earlier all-class320-game policy remains rejected and preserved separately.
Raw evidence: `polyworld/tmp/gota-druid-lane-20260923`.

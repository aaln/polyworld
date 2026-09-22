# New-week Gods of the Arena policy

Targets **2026.9.21.5**, upstream `f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. Primary semantic IR is `policy.py`; `policy.ir.json` and `policy.bas` are its verified generated pair.

The new league score is `max(0, lifetime XP - 200 * ticks / 1440)`, with draft ticks included. The policy drafts from public choices, spends ability points, farms separate lanes, buys permanent gear in its keep, uses recovery/portals, releases defense when the current threat clears, and avoids unsupported tower exposure.

Hosted frozen score gate: **passed**. Results are against an exact updated baseline opponent with candidate/compatibility control on each color. Repeated trajectories are correlated. No league champion was changed.

| Policy | Color | Mean score per hero | Wins / 40 | Invalid | Distinct command streams |
|---|---|---:|---:|---:|---:|
| candidate | red | 553.47 | 40 | 0 | 16 |
| candidate | blue | 584.76 | 34 | 0 | 17 |
| incumbent | red | 26.09 | 0 | 0 | 19 |
| incumbent | blue | 90.32 | 40 | 0 | 17 |

Mixed-team frozen score gate: **unqualified: insufficient clean games**. One subject seat, nine distinct frozen players, third pick on each team. Scores below use games with all ten VMs valid; tainted games remain in the evidence.

| Policy | Color | Clean mean score | Clean games | Subject errors | Distinct streams |
|---|---|---:|---:|---:|---:|
| candidate | red | N/A | 0 | 0 | 40 |
| candidate | blue | N/A | 0 | 0 | 40 |
| incumbent | red | N/A | 0 | 0 | 40 |
| incumbent | blue | N/A | 0 | 0 | 40 |

Other-policy VM failures and exact affected versions are recorded in `evidence/field-errors.json`; zero clean games provide no clean mixed-team score estimate.

These fixed rosters do not establish superiority over every current leader or a future rank. Native diagnostics: 8/8 candidate wins against the new baseline, 126 real-host scenario checks, maximum 11,960 instructions/18,684 work. Two prior hosted replays calibrated the engine and new score calculation. Six compiler tests passed. All captured earlier policies and coaching inputs remain unchanged.

Verify without network or a separate game checkout:

```sh
python3 verify.py
```

See `evidence/hosted-result.json`, `evidence/review.json`, and `tooling/README.md` for reproducibility, requests, budgets and limitations. Raw game tapes remain private under `tmp/gota-week-20260921`.

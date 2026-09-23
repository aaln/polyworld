# Richard v174 guarded siege: complete, not qualified

The coordinated source increased pooled mean individual score from **1,654.575 to1,779.945 (+7.58%)**, but failed the frozen10% threshold, the positive95% gain-bound requirement (interval **−8.65% to+27.05%**) and red later-draft preservation. It is **not deployed**. Both champions retain validated Druid lane recovery.

| Context | Baseline | Candidate | Change |
| --- | ---: | ---: | ---: |
| Red first pick | 2,945.18 | 3,040.86 | +3.25% |
| Blue first pick | 2,969.76 | 3,113.68 | +4.85% |
| Red later draft | 120.30 | 56.36 | −53.15% |
| Blue later draft | 583.06 | 908.88 | +55.88% |

All400 games pass ten-source/VM/full-replay/XP/integer-score audits. Each cell contains50games. The candidate blue-first cell has48distinct command streams; the other seven have50. Field versions were stable. All662 local checks and16native matches pass. The32-game mechanism subset reconstructs every subject command and world hash:149 covered-tower selections yield44 submitted tower attacks; two attacker selections yield two submitted attacks. Those are not landed-hit or causal score counts. Later-draft samples contain Druids; early samples differ in class mix.

The favorable blue-later result combines more heroXP (+138), creepXP (+458.74) and buildingXP (+38) with longer games (+1.177minutes, costing235.43points), plus god and clamp/rounding changes. Its gap against Richard improved, but its gap against khors worsened from−1,244.28 to−2,079.18. Higher personal points alone do not ensure league progress. No class or color slice qualifies the broad source.

[Reviewed portable IR/policy](guarded-siege/) keeps the tested BASIC unchanged while recording failed qualification in its beliefs. [Full report](evidence/report.json), [score/XP figure](evidence/score-breakdown.png), [prospective plan](evidence/plan.json) and [artifact index](evidence/artifact-index.json) preserve all results. Run `python guarded-siege/verify.py`; use its `convert.py` for compile/extract.

Source SHA256: `f7873bb2ec9ef14eb118639568144cadc75ad9a67f6b202a25a802890c85f143`.
Reviewed IR SHA256: `841b52731c7e39476727bb26a448cf5b6b5775ffa5a8aa6af4eff2feeb93f4bb`.

A separate blue-Druid-only source is a new hypothesis requiring fresh controls and unchanged red/other-class commands. The eight-game baseline home-navigation diagnostic found zero redundant home-navigation commands; it does not justify importing Richard's nearest-defender rule now. Original inputs and failed instrumentation versions are preserved.

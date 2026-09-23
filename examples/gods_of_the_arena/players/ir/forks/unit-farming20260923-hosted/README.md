# Unit-only targeting reduced score

The exact candidate `1238ec73` is **rejected**. Across 400 fresh games on replay59, average score fell **27.58%**, from 1,714.825 to 1,241.795; the 95% gain interval is −38.30% to −16.07%. All four color/draft contexts declined. Every game passed source, VM, replay-state, XP and integer-score checks; each cell has 50 distinct command streams.

| Metric | Incumbent | Candidate |
|---|---:|---:|
| Nonzero average | 2,834.42 | 2,459.00 |
| Nonzero frequency | 60.5% | 50.5% |
| Score ≥500 frequency | 54.5% | 38.0% |
| Hero XP per game | 1,575.75 | 1,422.00 |
| Creep XP per game | 2,271.86 | 2,421.71 |
| Building XP per game | 254.50 | 1.00 |
| God XP per game | 300.00 | 217.50 |
| Deaths per game | 7.525 | 9.115 |
| Elapsed minutes | 15.725 | 16.504 |

Extra creep XP did not compensate for lost hero/objective XP and elapsed-time cost. In the 32 preselected diagnostic games, building-target commands fell from 1,813 to zero, while unit-target commands fell from 4,481 to 4,366. This intervention does not establish productive replacement behavior. Incidental spell damage can still kill structures.

The natural draft differs slightly between independent arms; classes and all rival gaps are in the full report. Two ancillary log files returned404, but both games had complete mandatory artifacts and ten clean player exits. No games were excluded or replaced. The field stayed unchanged. The incumbent remains deployed.

[Reviewed semantic IR/policy pair](unit-farming/README.md), [all metrics and verdict](evidence/report.json), [mechanism subset](evidence/effects-summary.json), [missing-log receipts](evidence/missing-log-receipts.json). The IR reflects the failed qualification without changing the tested BASIC bytes. Original inputs remain in the raw capture folder.

A post-verdict check of the same32games found average dead time2.33→3.44minutes, while alive field time stayed10.78→10.82minutes. More elapsed time mainly failed to become more field time in this subset. [Supplemental downtime evidence](evidence/downtime-summary.json) is descriptive and did not alter the frozen verdict.

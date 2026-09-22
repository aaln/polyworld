# Individual XP opportunity candidate

Current game2026.9.22.3 /1b708944, replay58. **Hosted quality unvalidated; not
deployed.** Source f6a0dace is a fork of deployed portal source db71abb3.

Rank reachable finishing heroes against creep XP and routine structures, using
public health/distance/damage and final nearby force/tower context. Avoid
expensive chases; preserve critical recovery and portals. The new patch grants
500XP per teammate for god destruction, so an exposed god within basic reach
and four raw hits gets finishing priority. Utility scores are heuristics, not
calibrated expected XP; fog and armor can invalidate them. There is no hidden
opponent identity, private replay input, or invented live XP query.

The score remains max(0, XP*1440-200*world_ticks)//1440. Hero kill150XP,
shared creep pool15XP, building100XP, god500XP. Do not maximize game duration
unconditionally: every extra minute costs200XP.

All180 opportunity fixtures,84portal fixtures and126all-class/runtime checks
pass. Eight native games have exact replay/hash/XP/score checks, with four
matched score improvements: means3321→4166.75. Hero XP decreases on red and
increases on blue; the combined mean rises2325→2550. These native diagnostics
are not league evidence. Calibration matches a complete replay58 hosted game;
one other VM failed in that calibration game, so it proves decoder parity only.

A fresh160-game comparison is prepared against db71abb3, both colors, with
khors114/Jordan411/Richard167 opposing. No new games created. September22
budget1760/1760 is exhausted; additional games require user authorization or
the normal UTC reset. Promotion still requires the frozen score gate and
complete hosted audits. The deployed pair remains unchanged.

Edit policy.py and tooling/score20260922/score_binding.py, then use
`python3 convert.py compile --out <new-directory>` and
`python3 convert.py extract --source <BASIC> --out <new-directory>`.
`python3 verify.py` checks exact round-trip and evidence hashes. Changed
executable bytes invalidate inherited validation claims. Captured r1/r2 and
the initial fixture's automatic-acquisition ambiguity remain preserved.

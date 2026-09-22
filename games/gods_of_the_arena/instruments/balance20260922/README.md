# Published symmetry and balance adaptation

Exact engine: **2026.9.22.2**, `ffcedcd866c4d31924361ed4baff2b7a6d3aba67`,
`cow_2dd9158a-e22e-4000-9b2b-b060fffa7a9a`. Live API manifest and league captures
are in the raw study. Research uses a separate engine checkout; it does not run
the older engine files retained by the historical research branch. The user's
root `main` checkout and untracked work remain untouched.

The source audit confirms all three reported changes: Ranger HP growth 19,
Crossbowman base damage 69, and Warlock Dread Totem damage 87. Hero abilities,
costs, ranges, HP and damage still come from public host queries in the policy.
No old character stat table is carried into decisions. Faction draft bonuses
are removed. The four candidate preferences are experiments, not a claimed
new tier list.

`build.py` extends the existing IR conversion workflow with a new binding.
It normalizes public coordinates into the observer's team frame **before**
integer division, lane selection, fallback directions and quarter-tile attack
recovery steps. All movement and portal coordinates are converted back at the
host boundary. Reverse extraction verifies every generated executable region.
The frozen `current20260922` pair stays unchanged as the control.

The updated engine freezes one shared decision frame; accepted inventory and
skill operations remain live. Actors plan together, move together, then resolve
collected damage and deaths. The policy reads observed landed-hit counters and
does not assume that killing an enemy cancels its simultaneous attack. One full
movement tick before reacquisition still achieves a nine-tick Ranger interval
in fresh actual-engine practice. That is a controlled timing finding, not a
claim that Ranger remains the strongest hero.

Fresh validation:

- Four variants each pass 180 mirrored action scenarios, including exact tile
  boundaries and reversed equal-target storage order. The old source fails
  the farming mirror: canonical lane goal `(11,11)` versus `(104,104)`.
- Four variants each pass 126 real-host checks across ten heroes and both colors.
  Maximum 14,148 instructions / 21,092 work, under the frozen safety margins.
- Eight complete native episodes (four preferences × both colors) finish and
  reproduce every state hash; each preferred hero is actually drafted. These
  are runtime checks, not a hosted competitive verdict.
- Current hosted replay reconstruction matches every state hash, lifetime XP
  and official integer score. A first calibration replay had two failed rival
  VMs; it is preserved and excluded from clean strength evidence. A separate
  clean replay calibrates the admission gate.

`episode.nim` also corrects historical instrument output for simultaneous fort
destruction (`draw`) and emits actual integer XP scores. Original instrument
captures are preserved. Primary evaluation always compares official scores
with `max(0, xp*1440 - ticks*200) // 1440` for all ten heroes.

`hosted.py` freezes five versions and two mixed rosters, checks actual player-file
hashes from episode specs, and streams complete replay/runtime audits. Hosted
arms run sequentially; after an arm's games terminate, its local replay audit
may overlap the next hosted arm. The shared existing reservation journal remains
authoritative. No budget override or new journal is created. Eight local auditor
threads do not create extra hosted requests.

Roster health comes from current-engine co-participant listings. Some individual
version listings were dominated by later-created old-engine requests, and Games
Bond's listing returned HTTP 500. Those failures and original inputs remain in
the study. Pooled current-engine evidence gives 12–14 clean appearances for each
of the nine frozen background versions. This is a runtime-health filter only.

The preregistration is `../../experiments/2026-09-22-balance-heroes.md`.
Raw inputs and all rejected captures are under
`/Users/aaln/experiments/softmax/polyworld/tmp/gota-balance-20260922`.
The read-only dashboard serves local study data at `http://localhost:8850`.

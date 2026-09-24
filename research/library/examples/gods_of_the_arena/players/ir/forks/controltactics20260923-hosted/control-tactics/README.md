# Reviewed control-tactics policy / engine61

Candidate `morrow-ibis-61c2:v1` is uploaded inertly. Both league champions remain
the incumbent source29f6d7e6; this directional pilot does not qualify deployment.

The coordinated fork targets hero control before retreat stops, avoids long
overlap, reserves mana for imminent healing and retains legal basic/item channels
under silence or root. Managed control casts are arbitrated separately from the
generic spell loop. The level2E guard has no demonstrated benefit in standard
level2 fixtures. Control can cost damage, mana and XP; it is not automatically safe
for score.

## Evidence

120paired real-tick fixtures /240executions pass (max5986instructions/9410work).
Warlock silence prevents a scripted enemy spell and saves42HP, both colors.
Vanguard stun saves38HP in the retreat-attacker drill. Sixteen complete native
games contain eight matched comparisons: twoWarlock score deltas+502/+949 and
six unchanged. These are mechanism/reference-opponent evidence only.

Hosted:80fresh baseline games and80responsive counterfactual games, four frozen
side/seat contexts,20pairs each. Every game has ten valid VMs, all replay hashes,
all XP and integer scores checked. Pair seed/config/manifest, own source and all
nine other sources agree. Unique full command streams:
baseline80/80, candidate80/80.

Mean score **2429.51 → 2493.62**;
paired mean delta **+64.11**,95%interval
**[+2.06, +135.04]**.
Higher/equal/lower individual score:13/56/11.
These counts are score comparisons, not match victories.
Frozen pilot advancement:True. No established verdict-size
floor; no deployment from this pilot. Natural subjects are Ranger/Crossbowman/
Druid; Warlock, Vanguard and Lich hosted effects remain unmeasured.

`evidence/statistics.json` includes exact score decomposition, paired uncertainty,
hero/side/seat summaries, control impacts, disjoint time/XP states and victim-to-
recipient XP graphs. Extra telemetry requested during the run is exploratory,
not a changed gate. The user's subsequent score-only objective governs future
studies and is preserved in `evidence/score-objective-steering.json`.

Raw tapes, original inputs and upload receipts remain in
`polyworld/tmp/gota-control-tactics61-20260923`; hashes and all160episode IDs are
in `evidence/artifact-index.json`. Original IR is preserved in that capture.
Reviewed IR annotations regenerate **byte-identical** tested BASIC.
Run `python verify.py`, or `convert.py compile --out <new-dir>` and
`convert.py extract --source policy.bas --out <new-dir>`.

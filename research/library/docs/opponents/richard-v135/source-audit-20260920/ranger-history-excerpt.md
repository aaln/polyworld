# Historical Ranger research, pinned source excerpt

Extracted verbatim from `docs/gota-policy-handoff.md` at co-gas commit `93bd2aa1d79549960e88ea0f63ccf3a73273f198`. These are the source author’s reports about predecessors v115/v122/v123 and other matchups, not new v135 experiment results. The current audit independently measures v135 purchases, rewards and hit cadence.

### Red Kite combat deficit: quantified before another defense change

The logging-only spell overlay now also exposes `basicHeroHits`, emitted only
from the basic-attack branch against hero targets. Build it using
`players/users/relh/co-gas/polyworld-basic/tools/build_spell_impacts.py`; it
copies mechanics into its output overlay without editing canonical source.
Re-running the round497 Red Kite loss verifies all5846 hashes unchanged.
Artifacts: `.runtime/gota-round466-review-20260919/combat-trace/` and
`v115-round497-redkite-combat.json` in the same runtime parent.

Ranger106's last defensive life is not an unused-spell example. From5525 to5625
its spells register five damaging impacts on heroes101/102. Incoming Final
Measure and Siege Scarab do20+50 at5576. Then Crossbow101 hits for144 at5583,
Lich102 for128 at5589, and Crossbow101 for144 at5619:70 spell plus416 basic
damage takes434 HP to-52 exactly. Our Ranger's basic hits are61 at5582,5600
and5618. Its level is4 with dagger/sword/armor, versus level7 attackers with
dagger/sword/axe/armor/book. At5525 it has10 gold and no healing consumable;
both attackers carry a Vitality Elixir and over250 gold. This is observed
combat/economy evidence, not proof that swapping one purchase fixes the match.

The gap develops well before the final defense: at2000 enemy101/102 have
350/675 XP versus Ranger106's150; at4000 they have1300/1225 versus525.
Investigate reward acquisition and damage-item timing next. Simply moving more
underpowered heroes home has failed; do not infer that another recall threshold
addresses this deficit. No new policy has been uploaded from this diagnosis.

The follow-up `killRewards` overlay accounts for the XP gap exactly. By2000,
enemy101 has14 creep kills (350 XP), enemy102 has23 creeps plus one building
(675 XP), and Ranger106 has6 creeps (150 XP). Ranger's first reward is1899;
the enemy Lich's is774. At4000, enemy101 has30 creeps/one building/three hero
kills (1300 XP), enemy102 has39 creeps/one building/one hero (1225 XP), and
Ranger has21 creeps (525 XP). By5525 the attackers have seven and six hero
kills respectively. Farming precedes the combat snowball, not the reverse.
Lich's Bone Marionette hits at1829 produce five creep kills on that tick.

`tools/gota_idle_farm_audit.nim` checks each full-replay tick for a living hero
with no attack order and a visible enemy creep within exact basic range. There
are no such blue-team windows before2000, and Ranger106 has zero throughout
the replay. Thus a simple "attack in-range creeps while idle" patch does not
address this Ranger's delayed farm. Investigate early travel/engagement access
and wave-clear timing, not an unobserved idle-farm opportunity. This does not
rule out bad choices while already attacking, missed last hits, or better
routes. All5846 hashes verify for both instruments. Runtime artifacts:
`v115-round497-redkite-rewards.json` and `v115-round497-idle-farm.json` under
`.runtime/gota-round466-review-20260919/`; reward overlay is `reward-trace/`.

The opening trace identifies an actionable difference: Ranger106 at600 is
54,68 with visible creep1033 at57,58, but action2 has no objective/hero target
and sends it toward45,104. It reaches that rally near1100 and remains there
through1700. V122 engages a nearest visible creep within20 tiles in this
specific pre3500 fallback, retaining objective/hero priority and later routing.
A240-tick single-VM continuation from600 earns75 XP/45 gold versus zero for
v115, both at200 HP. The4000 decision control is identical and1000-tick smoke
passes. This is local behavior evidence only. V122
`ec3856dd-6c70-4872-9bbe-81caeba2a82e` is now retired. All14 native replays,
requested rosters, seeds and scores verify;114 text/log files show no inspected
error patterns. Hosted Red Kite blue confirms100 XP at1000 versus baseline0,
but by4000 the Ranger has425 versus baseline525, and home falls5286 rather
than5846. Red Kite red wins6403 without a v115 same-seed red control, so this
is not a verified added win. Aaron blue and v99 blue regress to losses6999
and7640. Preserve active v115/v154. Sustained farm and coordinated pressure
remain unresolved; the opening-only gain does not justify promotion.

### Axe-before-armor draft: no measured farm gain yet

The overlay now records accepted `purchases` (not merely attempted buy calls).
On the round497 Red Kite replay, enemy Lich102 buys sword1086, axe1697,
armor2139; enemy Crossbow101 buys sword1558, axe2476, armor2923. Ranger106
buys sword2599 and armor3803 with exactly160 gold. These timings confirm both
earlier income and a different item order; they do not isolate the cause of
Red Kite's wins. Full5846-tick hash verification still passes. Evidence:
`.runtime/gota-round466-review-20260919/v115-round497-redkite-purchases.json`;
logging overlay `purchase-trace/` in the same runtime directory.

Unuploaded source `gods_of_the_arena_neural_healthy_axe.bas` tests saving for
the axe before armor while at least75% healthy, preserving emergency armor
buying below that threshold. In a240-tick single-VM continuation from3802,
it holds160 gold rather than buying armor, then buys the axe by3984. However
both policies earn their next XP at exactly3814,3983,3993 and4002, ending at
550 XP. The draft ends with314 HP/40 gold versus434 HP/60 gold for v115,
reflecting foregone armor rather than an observed wound. No farming benefit
has been demonstrated; hold without upload. Its1000-tick compatibility smoke
passes. Files `healthy-axe-{nearest_defender,healthy_axe}-3802.json` and
`healthy-axe-smoke.json` preserve the bounded probe. Do not promote item-order
changes based solely on matching Kite's inventory.

### V123 observed-hit recovery test

Pinned mechanics expose `selfAttacksLanded` and reset swing state in the
no-target movement branch. A one-tick walk to the observed current tile after
a confirmed basic hit can shorten recovery without interrupting the preceding
windup. V123 initializes its persistent hit counter, then applies that action
after ordinary decisions. This is not a claim that Red Kite uses the technique.
In the exact prefix5580/Ranger106 single-VM120-tick probe, observed hits change
from5582/5600/5618 to5582/5591/5600/5609/5618/5627/5636/5645. Enemy Crossbow
ends at-40 HP rather than82; XP rises to800 versus650. The Ranger still dies,
ending-8 versus-52. A separate5550 probe gains75 XP on creeps, but neither
probe includes adaptive opponent scripts. The1000-tick smoke passes.

V123 `1a8c4ff2-9a80-478f-aada-864a5231768f` is now promoted for Richard.
Fourteen hosted comparisons cover the same seven opponents and seeds as v122:
13 wins, only Aaron red loses. Full Red Kite blue replay shows27 nine-tick
intervals between Ranger hero-target basic hits and a6673-tick win with own
fort400/enemy0. All five owned heroes survive. Current membership is
`lpm_06ab849a-dbb5-4ef8-9456-f0b9c1600e90`; relh v154 is unchanged and v115
is the source-backed rollback. Runtime evidence uses `attack-recovery-*` under
`.runtime/gota-round466-review-20260919/`; `gota_retreat_probe.nim` now includes
the attack counter in each sample so cadence claims are directly checkable.
Completed round496 contains two v115 wins;
standings remain relh fourth/Richard sixth, not goal completion.


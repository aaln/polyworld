# Prior hypotheses and limits

No mechanism is conclusively refuted by the completed small campaigns. A failed
superiority gate is not proof that an effect is absent. Preserve the reports;
do not silently retry an unchanged candidate on inspected validation seeds.

- Wave following alone: 28/60 discovery wins versus baseline 30/60. The older
  20-game validation was too small. No demonstrated superiority.
- Sustain-only center: 112/240 held-out wins versus baseline 115/240. Do not
  claim that removing poison alone improves wins.
- Duelist: 123/240 versus baseline 100/240, seed sign-test p=0.1796. Most net
  gains were on baseline timeout seeds. Stronger dueling is not established.

The new single-heal experiment changes a different purchase mechanism; it does
not repeat the poison-removal experiment. Recovery changes pursuit commitment;
structure pressure changes which object kind gets priority. All use Duelist as
the matched parent to isolate their respective changes.

Evidence: [completed campaign](campaign-20260910-result.json).

## Settings rejected by the 2026-09-10 hypothesis screen

These are configuration-level rejections, not statistically established broad
refutations. Do not rerun the same settings unchanged without new evidence.

- **72-tick stationary/HP pursuit exclusion:** 34/60 versus Duelist 35/60;
  activated once, with 59/60 identical complete tapes. Reopen only with evidence
  supporting a more informative progress signal or a distinct recovery action.
- **Structure weight 1:** 25/60 versus 35/60 despite structure-target share
  rising from 4.46% to 7.28%. Reopen with a concrete support/danger prerequisite,
  rather than assuming more objective attacks are inherently productive.
- **Single healing purchase:** 30/60 versus 35/60. The buy-return branch works,
  but an economy/strength advantage was not shown. Purchase attempts are not
  spending; future economy claims need accepted-purchase evidence.

Evidence: [hypothesis report](hypotheses-20260910-report.html), with complete
experiment records under [experiments/](experiments/).

## Four-equipment cap, 2026-09-10

27/60 versus Duelist 24/60 on six fresh discovery seeds; three extra wins missed the required four, so no confirmation. The capacity mechanism worked: healing purchases rejected for no space fell 55,580→99, accepted healing rose 588→884, and equipment fell 231→198. All 120 replay state sequences matched. This setting is not eligible for promotion; broader capacity improvements remain plausible. Do not rerun it unchanged to obtain another chance at the same gate. See [experiment](experiments/2026-09-10-reserve-consumables.md) and [report](reserve-20260910-report.html).

## Early HP investment, 2026-09-10

Below-half-HP missing helmet/buckler/amulet before consumables: **57/120 wins versus Duelist 62/120 and default 55/120** on 120 fresh independent seeds; both preregistered gain/significance gates failed (p=.831608 / .445962). The HP effect occurred: 113 investments across 89 games, adding 6,320 current HP. Healing purchases fell 1,208→701 and no-space rejections rose 47,499→122,862. All 360 replay state sequences matched; two interrupted candidate attempts completed on exact-input retry. Do not promote or rerun this setting unchanged. Reopen only with new evidence supporting a distinct gold/slot-aware purchase prerequisite; broader HP-equipment ideas are not conclusively refuted. See [experiment](experiments/2026-09-10-hp-investment.md) and [report](hp-investment-20260910-report.html). Seeds 67000–67119 are observed.

## Ordered five-item loadout, 2026-09-15

On published 2026.9.15.1: 14/40 versus v2 12/40 and default 10/40. Only two added wins versus v2 missed the four-win screen gate. 107 accepted planned purchases, all forty cases and ten classes; all 120 tapes verified. No confirmation or promotion. This setting is unqualified, not broadly refuted. Reopening on a changed balance release must explicitly account for the earlier failed gate and use fresh seeds. See [record](experiments/2026-09-15-ordered-loadout.md).

## Supported siege, announced balance simulation, 2026-09-15

Exposed fort/tower within8tiles of self, within5 of a living allied creep, selfHP>=60%:22/40 vs v2 21/40 and default22/40. Failed both +4-win gates. Overrides2891decisions across25cases/nine classes; structure-intent share6.66%→6.79%. All120 tapes match; no draws. Red/Blue split is small and exploratory, not a confirmed specialization. No promotion or validation. New settings need a new mechanistic reason and fresh seeds. See [record](experiments/2026-09-15-supported-siege.md).


## Wave-local R1, announced balance simulation, 2026-09-15

After passing the40-case screen, the same radius6 candidate completed120fresh
independent cases:68wins versus v2 57 and default60. Gain+9.17points/p=.110774
versusv2 and+6.67points/p=.174841 versusdefault failed the committed gates. All360
replays passed. Movement-share gain+58.33points occurred inall120cases/allclasses.
This setting has unconfirmed strength, not a broad mechanistic refutation. Keep
this failed gate intact; do not reclassify separately user-requested hosted field
batches as a passing local confirmation. [Record](experiments/2026-09-15-wave-local-balance.md).


## Timed18-tick kite on published2026.9.15.2, September15

2/40 fort wins versus v2 7/40 and default2/40; deaths92 versus78(+17.95%),
hits817 versus862. Only70/77 normal retreats had a hit in the preceding18ticks.
All120 tapes verified. Failed survival and parent-win gates; do not promote or
retry unchanged. Release2026.9.15.3 subsequently exposed a real hit counter,
which motivates a distinct confirmed-event controller on fresh seeds rather
than optimizing an uncertain stationary timer. See kiting-20260915-screen.json.


## Confirmed-hit kiting campaign on published2026.9.15.3

All candidates below completed40matched cases and full replay verification;
the same cohort was reused adaptively. Controls:v2 22wins/134deaths,
default18wins/154deaths. None qualified; do not rerun these settings unchanged
as another chance at the same screen. Timing was100% correct for normal
retreats, which is separate from competitive value.

| Setting | Wins /40 | Deaths | Basic hits |
| --- | ---: | ---: | ---: |
| Confirmed hit + emergency escape | 12 | 125 | 2153 |
| Confirmed hit, no emergency escape | 20 | 136 | 2403 |
| Target-aware, with emergency escape | 16 | 137 | 2147 |
| Earlier retreat | 17 | 124 | 2255 |
| Target-aware, no emergency escape | 20 | 137 | 2451 |
| Earlier target-aware retreat | 19 | 141 | 2596 |
| Short retreat + offensive spells | 17 | 115 | 2107 |
| Long retreat | 23 | 135 | 2447 |
| Long retreat + offensive spells | 20 | 138 | 2401 |

The spell matrix used an XP floor because it changed spell offense; no prior
failure was reclassified. Explicit casts during short/long retreats numbered39
and84, respectively. The longer bare retreat gained one win but did not reduce
raw deaths. No held-out confirmation, new XP upload or league promotion followed.
Broad kiting is not refuted. A distinct next hypothesis should measure threat
separation and incoming damage around chosen destinations; accepted movement
and displacement alone do not establish an effective escape. [Campaign](kiting-campaign-20260915.html).

## Replay diagnosis after the kiting campaign

New evidence supports a distinct motion-feedback hypothesis: short retreats
spend a median8/10 ticks turning, and only32/334 measured segments gain more
than0.25tiles against the tracked living enemy. Longer retreats improve that
mechanism but the existing32-tick candidate still failed the survival gate.
Do not reclassify it as qualified. Use fresh seeds for any new controller.

Simple nearby movement retries do not escape the reproduced friendly-tower
trap: all24 destinations fail at the verified Arcanist checkpoint. An engine-only
waypoint probe escapes; it is not a legal policy or evaluated engine release.
Reopen navigation with preventive clearance or a published engine correction,
not a target-ID timeout alone. [Evidence](replay-findings-20260915.md).

## Motion-feedback campaign, published2026.9.15.3

Ten IR cells plus v2/default completed480screen games on40fresh matched cases.
The selected motion+starting-dagger candidate then completed240untouched cases:
**125wins vs v2 116/default135**, paired one-sided p=.1642/.8384.
Death rate per alive minute fell.4580→.3879 (-15.3%) and XP rose323400→402550 (+24.5%).
All720confirmation tapes verified;4508/4508 normal retreats followed actual hits.
Thus survival/farming improved descriptively, but both frozen win gates failed.
Do not relabel this local qualification as passed. Retain the failed gate while
following the user's subsequent explicit request to test in40+game XP runs.
Artifacts: `tmp/gota-ir/motion-campaign-20260915/confirmation-result.json`.
The separate hosted study uses100episodes per arm, a fixed incumbent roster and
its own preregistered comparison; it does not erase these local results.

## Economy and target selection screen, 2026-09-16

40 fresh matched cases per arm on published 2026.9.15.3; all 520 full replay
sequences verified. Controls: waveguard 17/40, deployed motion 21/40, default 21/40.
These are selection results, not independent significance tests.

| Configuration | Wins / 40 | Deaths / alive minute | Status |
|---|---:|---:|---|
| center_motion | 24 | 0.4126 | Advanced to hosted discovery |
| center_loadout_motion | 23 | 0.4047 | Eligible, not selected under the two-candidate limit |
| center_loadout | 17 | 0.5173 | Failed local advancement gate |
| wave_loadout_motion | 20 | 0.3658 | Failed local advancement gate |
| center_poison_motion | 22 | 0.4109 | Failed local advancement gate |
| last_hit_motion | 21 | 0.4111 | Failed local advancement gate |
| farm_motion | 28 | 0.4158 | Advanced to hosted discovery |
| finish_motion | 21 | 0.4021 | Failed local advancement gate |
| farm_plain | 27 | 0.4929 | Failed local advancement gate |
| finish_plain | 17 | 0.5621 | Failed local advancement gate |

Retain every failed gate; do not rerun unchanged cells just for another chance.
Farm-plain improved discovery wins but exceeded the survival limit. Broad farming,
loadout, objective pressure and poison ideas are not universally refuted.
Evidence: `tmp/gota-ir/autoresearch-20260916/economy/screen-result.json`.

### Economy transfer failed against incumbents, 2026-09-16

After the 520-game local screen, both selected candidates failed the fixed hosted
discovery: farm-motion46/100, center-motion41/100, deployed motion54/100,
waveguard52/100. All400 full replay/VM/API audits passed; no failed episodes were
dropped. Both new policies had Death Knight0/10 versus motion8/10 and waveguard10/10,
a corrected adverse-class flag. Center movement is their shared changed behavior,
but this is not proof that it alone caused every loss. Do not promote or repeat
these configurations unchanged. Early farming/loadout gains against nine default
bots did not transfer to this incumbent roster. Evidence and IR feedback:
`tmp/gota-ir/autoresearch-20260916/hosted-discovery/result.json`.

## Cadence discovery screen, 2026-09-16

All360 complete local games and replay audits passed. Fresh40-case controls:
waveguard22, default23, deployed motion17. Ranged one-tick radius5:22wins;
radius7:21wins; one-tick all-class guard:24wins; wider-range long guard:21wins.
These four missed the required gain over both local controls and do not advance.
All-class one-tick recovery25wins and four-tick guarded recovery26wins advanced
to hosted discovery only. Mechanism or XP gains are not substitutes for wins.
Do not rerun unchanged failed cells simply to obtain another qualifying screen.
Evidence: `tmp/gota-ir/autoresearch-20260916/cadence-cycle/economy/screen-result.json`.

### Four-tick recovery plus danger escape: hosted transfer failed

Cadence4_guard36/100 versus waveguard46/motion37 on the new pinned roster.
Death rate fell to.4221, but win gates failed and Berserker0/10 versus
waveguard8/10 was an adverse-class flag. All400discovery tapes verified.
Do not promote or rerun this configuration unchanged; broad danger escapes
are not universally refuted. One-tick recovery without emergency retreat
qualified separately54/100 and requires fresh confirmation.
Evidence: `tmp/gota-ir/autoresearch-20260916/cadence-cycle/hosted-discovery/result.json`.

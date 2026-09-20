---
id: 2026-09-20-richard135-counter
policy: Aaron native IR
baseline: aaron-gota-ir-j268-redrace-0920-aaron:v1
candidate: critical40 / critical60 / weapon (separate attributable screens)
status: running
hypothesis: Near-core split pressure defeats remote recall cancellation; a critical recall exception can improve the matchup.
decision_rule: Fresh Richard135 >=30/40 per color and >=8 aggregate wins gained; Jordan268 >=38/40 per color; pinned field guard no aggregate regression.
evals: ["xreq_ec588afb-b51a-42ea-8d73-a29bc9008371", "xreq_ddd8c797-b23b-4756-9c78-70523473d3b0", "xreq_9e50f4d8-6b10-4e4c-b9dd-badb7036201b", "xreq_552b65bb-41fc-4e02-9538-e02de5ec9745", "xreq_6df54983-d6d2-46e8-a246-f716ab53b3cf", "xreq_f9304a60-ca10-4843-bb32-e91dd70fde89", "xreq_62315980-8e75-4052-a1a6-d8bd74fed7fe"]
---

# Richard v135 counter, Aaron player

User authorization: “richard's policy keep beating us. update Aaron player to policy that can beat him”.

Exact current Richard: 7c370daf-3c5f-42f8-870b-54b79c495a44. Current Aaron: 4cdbbf36-3d70-4ea3-8aed-c92ee0e024be, BASIC be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73. Published game .5, commit f2ab9598d8f8001b6beae3e66404e341770c803f. Both colors, five identical policies per team matches actual league layout. Own sources only; opponents evaluated remotely.

## Question and prospective design

The current distant-recall cancellation worked against Jordan but loses repeated league trajectories against Richard135 on both colors. First inspect complete losses and run fresh current baseline 40 per color. Candidate changes require a mechanism and individual preregistration below before source edits/upload. Initial candidate screen four games per color is only selection; finalist needs fresh 40 per color.

Promotion target: at least 30/40 wins on EACH color against Richard135 and at least eight wins gained overall over the fresh current control. Jordan268 guardrail at least 38/40 each color. Broad field screen current versus finalist: pinned head-to-head eight per color versus relh154, g002v1, black-kite16, macro4, red-kite34 and vanguard1; no more than two lost wins per rival/color, aggregate no regression. If a small field cohort is ambiguous, enlarge both arms before deciding. All episodes must complete and pass all ten VM exits, full replay hashes/actions, roster/config/build, score/XP checks. No candidate qualifies on small screening results alone.

## Critique

Game RNG produces repeated trajectories under fixed lineups, so N games is not N independent trials; report full command/audit signature diversity and no spurious inferential p-value. Generated seeds are not matched A/B. Fixed lineup competitive evidence does not imply superiority in arbitrary mixed teams. Recent league games are observational, not fresh controls. Reuse already completed comparable data only with explicit version/build matching and attribution. Closed levers checked: opening assembly and waveclear alone failed earlier; old unconditional defense releases/regrouping failures also retained. Missing local MIXIN bindings are bridged by the established published-build native compiler and complete replay/VM auditors.

## Result

Fresh exact deployed baseline: RED0W40L, BLUE0W40L. All80games complete and fullyaudited. Critical40 red directional screen:0W4L; no candidate qualifies for promotion. Other preregistered screens remain pending.

Native runtime: all6candidate/color games completed under VM limits and passed full replay/hash/action checks. Critical40 won both localdefault games; critical60red andweaponred lost theirs. These are one-game runtime smokes, not Richard/Jordan or broad-field qualification. Full observed critical40red command reconstruction matched36,961commands and all8,036statehashes; recall activated but did not avert loss. See tmp/gota-ir/richard-counter-20260920 for exact receipts and current-feedback/policy.py for executable-preserving IR feedback.

## Hypothesis 1: close two-hero pressure must override remote recall cancellation

Complete command reconstruction: red league ereq_86650a25 (8,517 ticks / 37,092 owned commands), blue ereq_979bc89a (5,803 ticks / 27,098 commands). Blue at 5,760 has all five distant, defCount=2, defAnchor=31, defActive=0; enemy Crossbowman/Berserker reach the blue god and destroy it at5,803. Richard is splitting threats instead of maintaining a four-hero cluster. The red loss includes repeated frontline deaths and eventual three-enemy god siege; improving recall may be insufficient there.

Proposed single mechanism: when the nearest visible enemy hero is within40 or60 tiles of the friendly god, at least2 enemies cluster around it, and a standing friendly defense anchor is present, accept a critical-defense commitment for1,200 ticks even when currently beyond28tiles. Other alarms still obey original nearby-only recall. Candidates critical40 and critical60 vary only the warning distance. No hidden opponent identity, private source, future replay state or seed enters the policy.

If true: representative near-core pressure activates remote defense and Richard screening wins improve over the control; a finalist passes fresh per-color thresholds while retaining Jordan. If false or direction reversed: same losses persist, defensive stalls replace them, or Jordan/field guards fail. Reject failing candidates; no threshold relaxation. Four/color screens only nominate, never justify deployment. Inspect actual winning/losing candidate replays before confirmation.

## Hypothesis 2: red frontline weapon progression

The fully audited red loss has DeathKnight eight deaths, only12 basic hits and level2 after8,517ticks; he begins with armor while Richard's heroes begin with CrimsonDagger and later SunsteelLongsword. This is association, not proof. Test the existing explicit `selective_loadout.red_loadout=1` on the deployed parent, keeping all targeting/recall unchanged: DeathKnight/Crossbowman/Berserker use the existing ordered weapon progression; red casters and all blue source stay exact. Candidate weapon. Predict improved red early combat/economy and screening outcomes if causal; reject if wins do not improve or guards fail. Blue cannot qualify from this change alone because execution is unchanged; a later combination with a separately supported recall component must be recorded and freshly confirmed as its own candidate.

# Convert surplus gold into effective combat healing

Status: complete; rejected from deployment. Checked closed_levers.md and the completed refreshed
reward-finisher rejection before choosing this distinct intervention.

Current engine2026.9.22.3/1b708944: cheap HealthPotion heals120 over240ticks,
interrupted by any damage (sim.applyDamage/recoverPotion). VitalityElixir costs75
and heals90 immediately (content.ItemSpecs, sim.applyUseItem). Health consumables
share240tick cooldown. Baseline correctly reserves interruptible potions for
quiet periods, but cannot heal under ongoing combat. Final inventories in80
clean controls retain1738mean gold; khors has same four core equipment items.
These facts motivate a coordinated item-choice/use/reserve hypothesis, not
proof that elixirs improve competitive score. No opponent source is available.

New source derives only from deployed portal db71abb3, through semantic IR:
replace the health-potion slot with Vitality Elixirs, use outside spawn at
missingHP>=70 even with nearby enemies/recent damage, and after four core items
stock up to6 while retaining200gold. Before core, at most2. Keep original
gear/portal purchasing priority and all timing, combat targeting, draft,
retreat and complete portal-channel ownership. No earlier failed pressure or
finisher changes are included. No hidden information enters the controller.

If true: actual engine scenes show immediate90HP even under damage, continued
combat, correct cooldown/spawn/reserve guards; hosted deaths/downtime may fall,
but only higher final XP-minus-time qualifies. If false: extra expenditure,
less healing per gold or altered survival lowers farming/score despite correct
local healing. Attacks, deaths, healing and XP are diagnostics, not substitute
objectives. We will measure all directly and disclose tradeoffs.

First practice exact commands and HP on both colors/all ten classes, preserve
84 portal/126 broader scenarios, and run8 complete ten-VM native games. Native
results establish execution only. Preserve all candidate IRs/failed fixtures.

Then one preselected source versus400 fresh current-roster controls,100 games
per source/color. One subject first team seat, fixed version-pinned mixed teams,
whole-team color rotation; khors114,Richard167,Jordan411 oppose both colors.
Use current Julia B5 source fingerprint from completed160-game refresh.
Freeze latest game/principal snapshots and all requests before spending.
No control reuse. Game and principal champions (ours,khors,Richard,Jordan,relh)
must stay fixed; background changes disclosed with exact tested-version scope.

Advance iff zero invalid/all10source and VM checks/full replay hashes/XP source
and integer-score checks pass, aggregate mean score gain>=10%, each color
>=95%control and lower95% side-stratified independent whole-game bootstrap gain
bound>0. Unmatched seeds, no pairing claim. Report duplicates. Fixed100/cell
may be underpowered for modest effects; fail/inconclusive means retain deployed.
No post-hoc gate changes or extra samples to rescue a near miss. The first4
lexical episode UUIDs per cell supply detailed diagnostic effects after all
finish; not an independent validation sample. This does not guarantee #1 or
late-draft strength. Successful gate permits previously authorized deployment
to both players, with exact source/owner/current-field verification and rollback.

Budget: one400game cycle interactive-combat-elixir-20260923, shared normal
1600/UTC day (160 already reserved September23), at most3active requests and
100games/request. The expired September22 override is not extended. Preserve
captures under polyworld/tmp/gota-combat-elixir-20260923. Prior worker paused.

## Local admission

Source aca1e7d147b84c69bd942d1d07f83751b1b37036b0969ff66aacb2c8f01f7b58,
initialIR15a88bf3d098961901bcd9be47e516f4b828299eba70c1845e0e1ad08a4d2805.
All240 actual-tick item/healing/economy checks,84portal and126broader checks
pass; maximum14936instructions/21996work. Baseline independently passes240
expectations for its original behavior: zero instant combat healing. All8
complete native matches pass VM/full replay hashes/XP/integer-score checks.
Native scores are not evidence of rival strength. Portable compile and extract
reproduce source and semantic IR exactly. Initial fixture compiler failure
from assigning a computed abilityPoints accessor is preserved; no policy change.

Initial submitted requests: xreq_a1eb6417-1590-4132-9aea-11770fb6a69a, xreq_8cb85b7a-3af8-48ce-85e8-f2754c6a0a23, xreq_3e89cd52-790c-459d-b11d-2a23e6aa8494.
The remaining blue candidate arm is admitted after an active slot frees.

## Completed result

All400 games completed with zero invalids and all ten sources/VM exits, full
replay hashes, XP sources and integer scores verified. Control cells and red
candidate each have100distinct streams; blue candidate has99/100, disclosed.
Mean score2447.32→2613.44 (+6.78783%), red2791.53→2899.93 (+3.88318%),
blue2103.11→2326.95 (+10.64329%).95%bootstrap gain interval
[−5.38795%,+20.87219%]. Aggregate10% and positive lower-bound gates fail.
Both portal champions remain deployed. Richard also changed167→174 during
the comparison, independently failing principal-field stability. No result
against167 is relabeled as174 evidence.

Hero XP rises on both colors (red2368.5→2575.5,blue1890→2014.5). Blue creep
XP2271.37→2600.04 rises; red2824.5→2822.39 is nearly unchanged. Mean deaths
rise5.45→5.60 red and5.18→5.51 blue. Longer games incur extra time cost.
The16-game diagnostic subset records more actual item healing with elixirs,
but different class/scene mixes prevent causal comparison of healing alone.
This does not establish reduced deaths or stronger overall survival.

Final request: xreq_cc069149-a53a-4767-ac00-19639b93c7c7. All400 reserved
September23UTC; shared total560/1600. Preserve original pair and all captures.
The directional gain is insufficient under the frozen rule; any future new
source must receive new controls and face current Richard174.

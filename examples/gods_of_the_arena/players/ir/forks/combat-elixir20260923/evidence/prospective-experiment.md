# Convert surplus gold into effective combat healing

Status: local development. Checked closed_levers.md and the completed refreshed
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

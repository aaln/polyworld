# Arcanist shopping return near tick 3,570

The hero turned home at **tick 3,530 because of shopping**. It had 250/250 HP, 28/210 mana, 590 gold, a dagger and one potion. The controller sets `restock=1` when fewer than four core items are owned, gold is at least 500 and no observed enemy unit is within 15 tiles. This also sets `retreat=1`; the walk-to-base rule then runs. Low mana was not the trigger.

The local enemy wave had just cleared. All 76 visible objects fit the scan; the remaining eight visible enemy creeps were distant. The screenshot's nearby allied creeps do not themselves offer XP. This particular trigger was not a missed-object scan bug.

| Event | Tick | Finding |
| --- | ---: | --- |
| Shopping return begins | 3,530 | Full HP, 590 gold, no portal scroll |
| Reaches shop | 4,682 | 48 seconds walking; buys armor, scroll, axe and potion for 470 gold |
| Spawn recovery releases retreat | 4,916 | Full HP and mana |
| Next XP | 5,114 | 66 seconds since return began; XP rises from 461 to 467 |
| Leaves keep area | 5,324 | Rune Crossbow also purchased at 5,264 after nearby XP income |

The 66-second gap adds **220 points of time penalty** before clamping. That is an observed cost, not proof that staying would have yielded 220 more final points. The upgrades were useful: armor increased maximum HP by 120. The hero eventually finished with 2,363 XP, score 861, five hero kills and no deaths. It gained 813 creep XP, 750 hero XP, 300 building XP and the 500-point god reward.

Mana Crystal remained locked throughout, including at level 8. The explicit-ability patch makes early unlock and useful manual restoration a concrete local improvement to test alongside better shopping timing. The separate survival candidate verifies restoration locally but failed its overall hosted score gate; none of its hosted subjects naturally drafted Arcanist or Warlock. It is not an approved caster replacement.

[Seven-layer coaching suggestions](suggestions.ir.json) propose an affordable upgrade basket, bounded wave-aware shopping deferral, early explicit mana restoration and a return plan. They preserve urgent survival escapes and useful shopping. The next comparison must measure complete-game scores and deaths together; this episode does not justify disabling all base returns.

[Episode](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_724a8b4c-122d-407d-b988-b80cd73548e8), [source reconstruction](source-audit-r5.json), [summary](summary.json), [screenshot](screenshot.png). The exact incumbent VM reproduced all 1,315 own commands and all 10,814 world-state hashes on replay60. Aaron's VM completed cleanly, but slots 2, 4 and 5 failed, so this is a controller diagnosis rather than competitive evidence. Original request/spec/results/replay and screenshot remain in the raw study; signed retrieval URLs are not republished.

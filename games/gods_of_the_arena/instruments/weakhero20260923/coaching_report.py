"""Seal the supplied Arcanist episode diagnosis without changing captured inputs."""
import hashlib
import json
from pathlib import Path
import shutil
from local import ROOT, RAW, HERE, write, sha

EPISODE = 'ereq_724a8b4c-122d-407d-b988-b80cd73548e8'
OUT = ROOT / 'docs/coaching/2026-09-23-arcanist-shopping'
read = lambda p: json.loads(p.read_text())


def main():
    raw = RAW / 'coaching-arcanist3570'
    audit = read(raw / 'source-audit-r5.json')
    replay = read(raw / 'episode-v2.json')
    economy = read(raw / 'economy.json')
    status = read(raw / 'player-status.json')
    assert audit['all_state_hashes_equal'] and audit['all_actions_consumed']
    assert audit['commands_matched'] == 1315 and replay['hash_mismatches'] == 0
    trigger = next(r for r in audit['rows'] if r['tick'] == 3530)
    arrival = next(r for r in audit['rows'] if r['tick'] == 4682)
    resume = next(r for r in audit['rows'] if r['tick'] > 3530 and r['xp'] > trigger['xp'])
    assert trigger['hp'] == trigger['max_hp'] == 250
    assert trigger['memory']['restock'] == trigger['memory']['retreat'] == 1
    assert trigger['memory']['objects'] == 76 and trigger['memory']['scanOffset'] == 0
    assert len(trigger['visible_enemy_creeps_at_trigger']) == 8
    assert min(x['distance_squared_tiles'] for x in trigger['visible_enemy_creeps_at_trigger']) > 36
    failed = [p['slot'] for p in status['players'] if p['exit_code'] != 0]
    assert 7 not in failed
    summary = {
        'episode': EPISODE, 'url': 'https://softmax.com/observatory/v2?tab=overview&detail=episode-request:' + EPISODE,
        'engine_commit': 'fd315c8fa30f8923c7a7709a577c40ac071b1c2a', 'game_version': '2026.9.23.2',
        'slot': 7, 'class': 'Arcanist', 'policy_version': '0c766ec9-131f-45d1-a207-ad75aea9ccc5',
        'source_sha256': sha(ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas'),
        'commands_matched': audit['commands_matched'], 'all_state_hashes_equal': True, 'all_actions_consumed': True,
        'other_vm_failure_slots': failed,
        'trigger': trigger, 'shop_arrival': arrival,
        'walk_to_shop_seconds': (arrival['tick'] - trigger['tick']) / 24,
        'first_xp_after_return_tick': resume['tick'],
        'xp_gap_seconds': (resume['tick'] - trigger['tick']) / 24,
        'time_charge_during_gap': (resume['tick'] - trigger['tick']) * 200 / 1440,
        'causal_limit': 'The time charge is exact; XP obtainable by staying and final-score improvement are unmeasured counterfactuals. Other three VMs failed, so this is a controller diagnosis, not a competitive evaluation.',
        'final_hero': replay['heroes'][7], 'xp_sources': economy['heroes'][7]['xp_sources'],
        'purchases': [p for p in economy['purchases'] if p['slot'] == 7],
        'diagnosis': 'R_economy sets restock after the local wave clears: fewer than4core items, gold>=500, observed enemy unit distance squared>225. Full-health return was not caused by low HP or low mana. No portal scroll was owned. R_walk_to_base walks to spawn and R_replenish clears retreat only in own spawn. Q remains rank0 through level8.'
    }
    write(raw / 'summary.json', summary)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ['summary.json', 'source-audit-r5.json', 'episode-v2.json', 'economy.json', 'downtime.json', 'player-status.json', 'screenshot.png']:
        shutil.copyfile(raw / name, OUT / name)
    suggestions = {
        'schema': 'semantic-coaching-hypotheses/1', 'id': 'arcanist_productive_restock60',
        'situation': {
            'healthy_undergeared_shopper': 'Outside keep, full or sustainable HP, incomplete item basket and enough gold to consider upgrades.',
            'recent_wave_cleared': 'Recent visible wave has died; distinguish a brief gap before the next wave from a persistently empty route.',
            'resource_sustain_available': 'Mana Crystal learned, charged and ready, outside spawn, with useful mana deficit.',
            'worthwhile_shop_basket': 'Explicit affordable next purchases and inventory space, plus legal return route, justify leaving now.',
            'safe_visible_wave': 'Visible enemy creep reachable on a safe route. Current BASIC exposes no direct object-layer or lifetime-XP field; validate same-floor reach using navigation, never private replay fields.'
        },
        'belief': {
            'observed_return': {'status': 'source_reconstructed', 'claim': 'Shopping latch at3530; full250HP,28mana,590gold,one core item. Full1315command and10814state-hash match. Local enemy wave had just cleared; all76visible objects fit the96object scan, so no partial-scan omission at this trigger.'},
            'measured_cost': {'status': 'observed', 'claim': '48seconds to shop;66seconds until next XP. Bought armor160,scroll100,axe180,potion30. The220point time charge is not a proven220point counterfactual score loss.'},
            'resource_gap': {'status': 'source_verified', 'claim': 'Mana Crystal never unlocked, even at level8. Current engine requires explicit casts; low mana itself did not trigger this return.'},
            'upgrade_value': {'status': 'unresolved', 'claim': 'Return bought meaningful upgrades, including120maxHP. Disabling shopping globally is not justified. Need a class-specific complete-game comparison of earlier sustain and return timing.'}
        },
        'goal': {'primary': 'Raise XP-minus-time score, conditional nonzero mean and productive frequency.', 'constraint': 'Preserve necessary survival escapes and item upgrades; never replace lane downtime with deaths.'},
        'skill': {
            'RestoreManaInLane': {'status': 'locally_verified_in_separate_unqualified_bundle', 'operation': 'Unlock Q from level2 after the normal level1 skill, explicitly cast useful ready Mana Crystal before target-dependent stops. No movement cancellation or portal interruption.', 'evidence': '../../../examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted/explicit-sustain/evidence/local-summary.json'},
            'PlanProductiveRestock': {'status': 'proposed', 'operation': 'Compute the next affordable class-specific item basket and travel commitment; use a safe wave gap for return. When healthy and a near-term wave can be farmed, briefly defer the shopping latch with bounded reevaluation. Treat urgent HP escape separately.'},
            'RetainReturnOptions': {'status': 'proposed', 'operation': 'Restock scrolls at actual shopping visits and preserve safe channel continuation. Do not assume a scroll exists at the first590gold return; the starting150gold was spent on dagger110 plus potion30.'},
            'ReconsiderShopCommitment': {'status': 'proposed', 'operation': 'Before irrevocable travel, reevaluate an already visible reachable wave and recent lane progress. Bound deferrals; once travel is committed avoid oscillation, and keep danger overrides.'}
        },
        'strategy': [
            {'when': 'resource_sustain_available', 'prefer': 'RestoreManaInLane', 'for': 'productive_lane_time'},
            {'when': 'healthy_undergeared_shopper and safe_visible_wave and no urgent upgrade or lethal threat', 'prefer': 'bounded wave farming then PlanProductiveRestock', 'over': 'gold-threshold-only immediate home latch'},
            {'when': 'worthwhile_shop_basket and a verified safe wave gap', 'prefer': 'useful shopping with return planning', 'for': 'future XP rate'}
        ],
        'execution': {'executable': False, 'deployed': False, 'evidence_scope': 'One supplied episode with three other-player VM failures. The separate400game survival bundle had no naturally drafted Arcanist/Warlock subjects, so it does not competitively validate caster changes.'},
        'update': {'origin': 'User screenshot and episode at~3570; captured inputs retained.', 'evidence': ['summary.json', 'source-audit-r5.json', 'screenshot.png'], 'next_test': 'Freeze Arcanist-specific mana/upgrade/return changes as a coordinated pair. Real-tick fixtures: ready/cooling/lockedQ, item basket, no-scroll return, safe wave present/absent, imminent danger, channel lock, bounded deferral. Complete responsive games with natural Arcanist exposure on both colors, source/VM/replay audits and fresh score/productivity gates; no fixed-opponent-action replay counterfactual as score proof.'}
    }
    write(OUT / 'suggestions.ir.json', suggestions)
    (OUT / 'README.md').write_text('''# Arcanist shopping return near tick 3,570

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
''')
    write(OUT / 'manifest.json', {'raw_root': str(raw), 'episode': EPISODE, 'source_probe_sha256': sha(HERE / 'coaching_probe.nim'), 'binary_sha256': sha(RAW / 'bin/coaching'), 'raw_inputs': {f.name: sha(f) for f in raw.iterdir() if f.is_file()}, 'artifacts': {f.name: sha(f) for f in OUT.iterdir() if f.is_file() and f.name != 'manifest.json'}})
    print(json.dumps({k: summary[k] for k in ['episode', 'walk_to_shop_seconds', 'xp_gap_seconds', 'time_charge_during_gap', 'commands_matched']}))


if __name__ == '__main__':
    main()

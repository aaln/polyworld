"""Descriptive khors IR from six existing replays, never an executable proxy."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import study

h = study.h
ROOT = study.ROOT
raw = h.STUDY / 'khors-discovery'
out = ROOT / 'docs/opponents/khors-v114/replay-audit-20260922'
read = h.read
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not out.exists(), 'Preserve the original descriptive model'
    data = read(raw / 'economy-v2-summary.json')
    rows = data['rows']
    assert len(rows) == 6 and {r['side'] for r in rows} == {0, 1}
    assert all(r['failed_other_slots'] for r in rows)
    sources = Counter()
    for r in rows:
        sources.update(r['xp_sources'])
        assert sum(r['xp_sources'].values()) == r['total_xp']
        assert sum(r['hero_xp_by_victim_slot']) == r['xp_sources'].get('hero', 0)
    failed_xp = sum(r['xp_from_failed_vms'] for r in rows)
    stats = {'episodes': 6, 'classes': dict(Counter(r['class'] for r in rows)),
             'xp_sources': dict(sources), 'total_xp': sum(sources.values()),
             'hero_kills': sum(r['hero_kills'] for r in rows),
             'creep_last_hits': sum(r['creep_last_hits'] for r in rows),
             'xp_from_failed_vms': failed_xp,
             'all_six_have_failed_other_vms': True,
             'scope': 'Retrospective behavior only; no clean score-comparison, forecast, mechanism identification or validated proxy.'}
    out.mkdir(parents=True)
    for name in ('economy-v2-summary.json', 'economy-v2-proof.json', 'six-game-audit.json', 'preflight.json', 'leaderboard-before.json'):
        shutil.copy2(raw / name, out / name)
    guide = ROOT / 'docs/guides/guide-opponent-model-ir.md'
    shutil.copy2(guide, out / 'guide-snapshot.md')
    model = {
        'schema': 'gota-opponent-descriptive-ir/1', 'id': 'khors_v114_replay_20260922',
        'situation': {'authority': 'retrospective full replay and typed events, not our live observation',
                      'game_version': h.VERSION, 'engine_commit': h.COMMIT,
                      'policy_version': '145c01e0-0cbf-4e1e-8120-11b437175b91',
                      'source_sha256_from_host_specs': rows[0]['source_sha256'],
                      'selection': 'First three completed current-engine episodes per color in the existing reverse-chronological API listing, frozen for VM preflight before economy measurements.',
                      'episodes': [r['episode'] for r in rows], 'guide_sha256': sha(guide)},
        'belief': {'observed': stats,
                   'claims': [
                       {'id': 'K_XP', 'status': 'observed', 'claim': 'This sample earns substantial XP from both creep proximity/last hits and hero kills; exact typed totals reconcile.'},
                       {'id': 'K_SHOP', 'status': 'observed', 'claim': 'All six start with item11 (dagger) plus item1 (health potion), and later acquire armor16, axe18 and spellbook19. Scroll21 purchases recur. Ordering and timing vary; the source priority graph is unknown.'},
                       {'id': 'K_FAILURES', 'status': 'observed', 'claim': 'Every sampled match has other failed VMs. XP earned from those hero slots is measured separately; scoring dominance in these games is not clean counter-policy evidence.'},
                       {'id': 'K_INTENT', 'status': 'unidentified', 'claim': 'Intentional farming of failed bots, exact target priority, timing, defensive transitions and draft priority cannot be identified from these aggregates.'}]},
        'goal': {'xp_accumulation': {'status': 'hypothesis', 'evidence': ['K_XP'], 'purpose': 'Accumulate XP through farming and kills; does not identify objective ordering.'}},
        'skill': {'ranged_combat': {'observed_classes': list(stats['classes']), 'initiation': 'unknown', 'termination': 'unknown'},
                  'restock_at_keep': {'observed': 'Accepted purchase event sequences in economy-v2-summary.json', 'priority': 'unknown'}},
        'strategy': [{'id': 'K_COUNTER_RECOVERY', 'when': 'Our publicly observed hero is low on health outside the keep and a safe home portal is available',
                      'skill': 'coached_field_recovery', 'for': ['deny_hero_kill_xp', 'return_to_productive_play'],
                      'status': 'counter_hypothesis; comparative result separate', 'priority_identified_for_opponent': False}],
        'execution': {'binding': 'retrospective-descriptive/1', 'proxy_usable': False,
                      'forecast_validated': False, 'heldout_forecast': None, 'source_available': False,
                      'public_policy_inputs_only': True,
                      'boundary': 'No policy UUID, future command tape, failed-VM identity or hidden replay position is supplied to our live controller.'},
        'update': {'at': h.research.now(), 'kind': 'Initial descriptive audit; not an observation-trained predictive model',
                   'next_discriminator': 'Use the exact hosted opponent responding in the frozen 160-game portal/control comparison. Do not replay future opponent commands after changing our actions.',
                   'evidence': ['economy-v2-summary.json', 'six-game-audit.json', 'preflight.json'],
                   'preserved_raw_root': str(raw)}}
    h.write(out / 'opponent.ir.json', model)
    h.write(out / 'summary.json', stats)
    (out / 'README.md').write_text(f'''# khors:v114: retrospective XP audit

Exact version `145c01e0-0cbf-4e1e-8120-11b437175b91`, engine **2026.9.22.2 / ffcedcd**.
The live snapshot ranks it first, ahead of Aaron and Coach. Six recent replays
were selected for VM preflight before reading their economy events.

The sample contains three Ranger, two Crossbowman and one Arcanist game.
Total XP is **{stats['total_xp']}**: **{sources['hero']} from hero kills**,
**{sources['creep']} from creeps**, and **{sources.get('structure_or_other', 0)} from structures**.
There are **{stats['hero_kills']} hero kills** and **{stats['creep_last_hits']} creep last hits**.
Of hero-kill XP, **{failed_xp}** came from slots whose VMs failed during the match.
That attribution does not establish whether each kill occurred before or after
the failure, or whether khors deliberately chose those targets.

All six khors VMs ran successfully, but every match contains failed other VMs.
Consequently these scores cannot establish clean competitive superiority.
All replay state hashes and event XP totals reconcile. Equipment observations
show dagger/potion openings and later armor, axe, spellbook and recurring scroll
purchases. They do not identify exact controller ordering or target priorities.

`opponent.ir.json` is a descriptive seven-layer record. It has no validated
forecast or executable proxy; it must not be compiled as the opponent's policy.
The proposed counter is to reduce avoidable hero-kill income through safe field
recovery, then return to XP-producing play. The exact responsive hosted A/B
evaluates that combined intervention separately. No hidden replay data enters
the live policy. Original artifacts remain in `{raw}`.
''')
    h.write(out / 'manifest.json', {'files': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps(stats))


if __name__ == '__main__':
    main()

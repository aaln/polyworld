"""Compare actual-tick traces and matched responsive games, not source strings."""
import json
from check import RAW, sha


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    read = lambda name: json.loads((RAW / name).read_text())
    base = read('baseline-practice.json')
    candidate = read('control-legality-practice.json')
    assert len(base['rows']) == len(candidate['rows']) == 104
    rows = []
    for a, b in zip(base['rows'], candidate['rows']):
        key = {k: a[k] for k in ['scenario', 'team', 'class', 'effect']}
        assert key == {k: b[k] for k in key}
        assert a['trace'] == b['trace'], key
        # Only silenced cast attempts may disappear. Preserve all other commands,
        # including their exact ticks, slots, targets and fractional coordinates.
        expected = [c for c in a['commands'] if not (
            a['effect'] == 'SilenceControl' and c['kind'] == 6 and c['tick'] < a['control_end'])]
        assert expected == b['commands'], key
        assert b['silenced_rejections'] == 0
        if a['effect'] == 'SilenceControl':
            assert b['cast_during'] == 0
        if a['effect'] == 'StunControl':
            assert b['cast_during'] == b['attacks_during'] == b['moves_during'] == b['items_during'] == 0
        if a['effect'] == 'RootControl':
            assert b['moves_during'] == 0
        if a['scenario'] == 'lane_heal':
            assert b['healing'] > 0
            if a['effect'] == 'SilenceControl':
                assert b['released_after'] > 0
            if a['effect'] == 'RootControl':
                assert b['released_during'] > 0
        if a['scenario'] == 'potion' and a['effect'] in ['RootControl', 'SilenceControl']:
            assert b['items_during'] > 0 and b['healing'] > 0
        if a['scenario'] == 'portal':
            assert (b['portal_after_control'] > 0) == (a['effect'] in ['NoControl', 'SilenceControl'])
            assert b['cast_during'] == 0
        rows.append({**key, 'passed': True, 'all120_gameplay_samples_equal': True,
                     'other_commands_equal': True,
                     'baseline': {k: v for k, v in a.items() if k not in [*key, 'trace', 'commands']},
                     'candidate': {k: v for k, v in b.items() if k not in [*key, 'trace', 'commands']}})
    removed = sum(a['silenced_rejections'] for a in base['rows'])
    assert removed > 0
    write(RAW / 'practice-comparison.json', {
        'passed': True, 'paired_fixtures': len(rows), 'executions': 208,
        'removed_silenced_casts': removed, 'candidate_silenced_casts': 0,
        'max_instructions': candidate['max_instructions'], 'max_work': candidate['max_work'],
        'raw_sha256': {name: sha(RAW / name) for name in ['baseline-practice.json', 'control-legality-practice.json']},
        'scope': 'Isolated48tick control windows; the four actual control abilities and every rank duration are separately covered by upstream controls tests. Gameplay samples omit diagnostic lastActionError, which correctly differs after omitted failed calls.',
        'rows': rows})
    native = read('native-result.json')
    pairs = []
    for a in native['rows']:
        if a['name'] != 'baseline': continue
        b = next(b for b in native['rows'] if b['name'] == 'control-legality' and
                 all(a[k] == b[k] for k in ['side', 'ordinal', 'seed']))
        stem = f"side{a['side']}-seat{a['ordinal']}-{a['seed']}"
        al = read('native/baseline/' + stem + '/live.json')
        bl = read('native/control-legality/' + stem + '/live.json')
        for k in ['ticks', 'battle_ticks', 'draft_ticks', 'winner', 'fort_hp']:
            assert al[k] == bl[k], (stem, k)
        for ah, bh in zip(al['heroes'], bl['heroes']):
            assert {k: v for k, v in ah.items() if not k.startswith('max_')} == {
                k: v for k, v in bh.items() if not k.startswith('max_')}, stem
        pairs.append({k: a[k] for k in ['side', 'ordinal', 'seed']} | {
            'subject_class': a['subject']['class'], 'baseline_score': a['subject']['score'],
            'candidate_score': b['subject']['score'], 'score_delta': b['subject']['score'] - a['subject']['score'],
            'all10_terminal_hero_fields_equal': True, 'replays_audited': True})
    write(RAW / 'native-comparison.json', {'passed': True, 'paired_games': 4, 'games': 8,
        'mean_paired_score_delta': sum(p['score_delta'] for p in pairs) / len(pairs),
        'scope': 'Local runtime/equivalence screen against nine responsive upstream VMs, not league rivals or a competitive confidence estimate.',
        'pairs': pairs})
    print(json.dumps({'paired_fixtures': len(rows), 'removed_silenced_casts': removed,
                      'paired_games': len(pairs), 'all_score_deltas': [p['score_delta'] for p in pairs]}))


if __name__ == '__main__':
    main()

"""Require observed recovery, escape, channel safety and unaffected-hero parity."""
import json
from local import RAW, sha, write


def main():
    read = lambda p: json.loads(p.read_text())
    before, after = [read(RAW / (label + '-practice.json')) for label in ['baseline', 'explicit-sustain']]
    key = lambda r: (r['scenario'], r['team'], r['class'])
    old = {key(r): r for r in before['rows']}
    assert len(after['rows']) == len(before['rows']) == 220
    checks = []
    for r in after['rows']:
        cls, scene = r['class'], r['scenario']
        baseline = old[key(r)]
        if cls not in ['VanguardKnight', 'DeathKnight', 'Arcanist', 'Warlock']:
            assert r == baseline, key(r)
        if scene in ['full', 'cooldown', 'empty', 'channel']:
            assert r['accepted_spell_releases'] == 0, key(r)
        if scene == 'channel':
            assert r['local_moves'] == r['home_walks'] == 0, key(r)
        if cls in ['VanguardKnight', 'DeathKnight']:
            if scene == 'heal':
                assert r['self_healing'] > 0 and baseline['self_healing'] == 0, key(r)
            if scene == 'danger':
                assert r['local_moves'] > 0 and r['retreat'] == 0 and r['hero_distance'] <= 25, key(r)
            if scene in ['outside_threat', 'last_hit']:
                assert r['local_moves'] == 0, key(r)
            if scene == 'last_hit':
                assert r['xp'] > 0 and r['final_mana'] >= baseline['final_mana'], key(r)
            if scene == 'shopping':
                assert r['retreat'] == 1 and r['local_moves'] == 0, key(r)
        if cls in ['Arcanist', 'Warlock'] and scene == 'mana':
            assert r['mana_restored'] > 0 and baseline['mana_restored'] == 0, key(r)
        if cls in ['VanguardKnight', 'DeathKnight', 'Arcanist', 'Warlock'] and scene == 'unlock':
            assert r['ranks'][0] == 1 and baseline['ranks'][0] == 0, key(r)
        checks.append({'scenario': scene, 'team': r['team'], 'class': cls, 'passed': True})
    assert after['max_instructions'] < 19000 and after['max_work'] < 50000
    native = read(RAW / 'native-result.json')
    assert native['passed'] and len(native['rows']) == 16
    carried = []
    for row in native['rows']:
        if row['name'] != 'explicit-sustain' or row['subject']['class'] in [0, 2, 5, 8]:
            continue
        leaf = f"side{row['side']}-seat{row['ordinal']}-{row['seed']}"
        control, changed = [read(RAW / 'native' / label / leaf / 'live.json') for label in ['baseline', 'explicit-sustain']]
        for field in ['ticks', 'state_hash', 'actions', 'commands', 'winner', 'fort_hp']:
            assert control[field] == changed[field], (leaf, field)
        carried.append({'case': leaf, 'class': row['subject']['class'], 'exact_commands_and_state': True})
    write(RAW / 'local-summary.json', {'passed': True, 'source_sha256': sha(RAW / 'explicit-sustain/policy.bas'), 'fixture_cases': len(checks), 'rows': checks, 'max_instructions': after['max_instructions'], 'max_work': after['max_work'], 'unchanged_complete_matches': carried, 'native_games': 16, 'scope': 'Normal vision for recovery; explicitly visible synthetic threats isolate the spacing guard. Current reference opponents for native checks; no league score qualification.'})
    print(json.dumps({'passed': True, 'cases': len(checks), 'unchanged_complete_matches': len(carried)}))


if __name__ == '__main__':
    main()

"""Frozen source-informed build and responsive native Richard comparisons."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import pprint
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5'
IR = CLEAN / 'examples/gods_of_the_arena/players/ir'
STUDY = ROOT / 'tmp/gota-ir/richard-growth-20260920'
CAMPAIGN = ROOT.parent / 'gota-autoresearch'
BIN = ROOT.parent / 'gota-research-20260916/r5/fast'
sys.path[:0] = [str(IR), str(ROOT)]
from policy_ir import read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_growth import contracts
from release_workspace import verify

PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/validated-blue-component'
DEPLOYED = ROOT / 'examples/gods_of_the_arena/players/ir/forks/jordan268'
RICHARD = STUDY / 'inputs/v135.bas'
NAMES = ('deployed', 'critical60', 'damage_recovery', 'productive')


def prepare():
    engine = verify()
    write(STUDY / 'engine.json', engine)
    assert digest(RICHARD.read_bytes()) == 'f48bb0057aeaf2ff939035324340183e34f8f9544e03226edfe62e78faad5a30'
    original = read(PARENT / 'policy.ir.json')
    for name in NAMES:
        p = deepcopy(read(DEPLOYED / 'policy.ir.json') if name == 'deployed' else original)
        if name not in ('deployed', 'critical60'):
            p['id'] = 'gota_richard_growth_' + name
            p['skill']['attack']['operator'] = contracts.ATTACK
            p['skill']['equipment']['operator'] = contracts.EQUIPMENT
            p['skill']['sustain']['operator'] = contracts.SUSTAIN
            if name == 'productive':
                p['skill']['observe']['operator'] = contracts.OBSERVER
                p['skill']['observe']['parameters']['growth_defenders'] = 1
            p['situation']['notes'] += (' Source-informed red damage-conversion study. Actual '
                'leveling follows credited kill rewards; there is no level-up command. Newly '
                'landed hits require consecutive living decisions. Current-distance defender '
                'rank uses public living ally geometry and actor-ID tie-breaks; unseen enemies '
                'remain unknown. No rival identity switch. Preserve critical60 blue as reference.')
            for claim in p['belief']['claims'].values():
                claim['claim'] = 'Inherited parent evidence; not validation of this new source. ' + claim['claim']
            p['belief']['claims']['ProductiveGrowth'] = {
                'claim': 'Hypothesis: from-start in-place hit recovery and damage/HP equipment '
                    'increase red rewarding attacks; current-distance recall allocation further '
                    'preserves productive pressure without fatal home exposure. Outcome applies '
                    'to the complete candidate. Individual component gains are not presumed.',
                'status': 'untested', 'evidence': [{'artifact': str(STUDY / 'inputs.json')},
                                                {'artifact': str(STUDY / 'prospective.md')}]}
            p['goal']['G_growth'] = {'preference': 'Earn kill rewards through effective basic '
                'hits, completed fights and structure pressure while denying repeated isolated '
                'hero deaths. Convert gold into damage and health without unnecessary mana '
                'purchases. Evaluate fixed-time XP and complete fort wins together.', 'provenance': 'authored'}
            for rule in p['strategy']:
                if rule['skill'] in ('observe', 'attack', 'equipment', 'sustain'):
                    rule['for'] = list(dict.fromkeys(rule['for'] + ['G_growth']))
            p['update'].update(revision=p['update']['revision'] + 1, parent=digest(original),
                change={'origin': 'User source-informed productive leveling integration', 'candidate': name},
                evidence=p['update']['evidence'] + [{'artifact': str(STUDY / 'inputs.json')}],
                needs_review=['belief/ProductiveGrowth'])
            refresh_grounding(p)
        d = STUDY / 'candidates' / name
        if not d.exists():
            d.parent.mkdir(parents=True, exist_ok=True)
            bundle(p, d)
            (d / 'policy.py').write_text('"""Source-informed semantic growth policy."""\n\nPOLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
        assert compile_policy(p).encode() == (d / 'policy.bas').read_bytes()
        assert extract((d / 'policy.bas').read_text(), p) == p
        print('BUILT', name, digest((d / 'policy.bas').read_bytes()), flush=True)
    write(STUDY / 'config.json', read(CAMPAIGN / 'config.json')['game_config'])
    if not (STUDY / 'plan.json').exists():
        plan = {'at': datetime.now(timezone.utc).isoformat(),
            'sources': {n: str(STUDY / 'candidates' / n / 'policy.bas') for n in NAMES},
            'opponents': {'richard135': str(RICHARD)},
            'cases': [{'seed': 9980000 + rep * 2 + side, 'side': side, 'opponent': 'richard135'}
                      for rep in range(2) for side in (0, 1)],
            'scope': '16 full responsive local diagnostics using authenticated Richard source; no hosted or promotion claim.',
            'prospective': str(STUDY / 'prospective.md')}
        paths = [Path(p) for p in plan['sources'].values()] + [RICHARD, STUDY / 'config.json', STUDY / 'prospective.md', Path(contracts.__file__)]
        plan['inputs_sha256'] = {str(p): digest(p.read_bytes()) for p in paths}
        write(STUDY / 'plan.json', plan)


def match(name, case, source, rival, out):
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'result.json').exists(): return read(out / 'result.json')
    command = [str(BIN / 'episode'), '--config', str(STUDY / 'config.json'), '--seed', str(case['seed']), '--record', str(out / 'replay.bin')]
    command += ['--bot:' + str(source if i // 5 == case['side'] else rival) for i in range(10)]
    try:
        with (out / 'stdout.log').open('w') as stdout, (out / 'stderr.log').open('w') as stderr:
            process = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=900)
        write(out / 'process.json', {'command': command, 'returncode': process.returncode})
        assert process.returncode == 0 and not (out / 'stderr.log').read_text().strip()
        actual = json.loads((out / 'stdout.log').read_text().splitlines()[-1])
        p = subprocess.run([str(BIN / 'audit-hosted'), '--replay', str(out / 'replay.bin')], capture_output=True, text=True, check=True, timeout=900)
        audit = json.loads(p.stdout); write(out / 'audit.json', audit)
        assert audit['hash_mismatches'] == 0
        assert actual['state_hash'] == audit['state_hash']
        assert actual['ticks'] == audit['recorded_ticks'] == audit['ticks']
        assert actual['actions'] == audit['recorded_actions'] == audit['actions_consumed']
        assert len(actual['heroes']) == len(audit['heroes']) == 10
        assert [h['score'] for h in actual['heroes']] == [h['score'] for h in audit['heroes']]
        assert all(h['max_instructions'] <= 20000 and h['max_work'] <= 50000 for h in actual['heroes'])
        ours = audit['heroes'][case['side'] * 5:case['side'] * 5 + 5]
        theirs = audit['heroes'][(1-case['side']) * 5:(1-case['side']) * 5 + 5]
        result = {'name': name, **case, 'valid': True, 'win': ours[0]['score'],
            'loss': theirs[0]['score'], 'draw': int(ours[0]['score'] == theirs[0]['score'] == 0),
            'ticks': audit['ticks'], 'deaths': sum(h['deaths'] for h in ours),
            'total_xp': sum(h['total_xp'] for h in ours), 'basic_hits': sum(h['basic_hits'] for h in ours),
            'gear_heroes': sum(h['first_gear_tick'] >= 0 for h in ours),
            'max_instructions': max(h['max_instructions'] for h in actual['heroes']),
            'max_work': max(h['max_work'] for h in actual['heroes']),
            'source_sha256': digest(Path(source).read_bytes()), 'replay_sha256': digest((out / 'replay.bin').read_bytes()),
            'audit_sha256': digest((out / 'audit.json').read_bytes())}
    except Exception as exc:
        result = {'name': name, **case, 'valid': False, 'error': repr(exc)}
    write(out / 'result.json', result)
    print(json.dumps(result), flush=True)
    return result


def calibrate():
    old = ROOT / 'tmp/gota-ir/richard-transition-20260920/cadence/hosted/coached_baseline'
    source = ROOT / 'examples/gods_of_the_arena/players/ir/forks/richard135-transition-20260920/coached-baseline/policy.bas'
    rows = []
    for side, color in enumerate(('red', 'blue')):
        d = old / color; original = read(d / 'arm-result.json')['rows'][0]
        out = STUDY / 'calibration' / color
        row = match('coached_baseline', {'seed': original['seed'], 'side': side, 'opponent': 'richard135'}, source, RICHARD, out)
        assert row['valid']
        hosted = read(d / 'artifacts' / original['episode'] / 'audit.json')
        native = read(out / 'audit.json')
        # Hosted collectors append artifact hashes; native audit stdout has only
        # gameplay fields. Replay container hashes differ with header metadata.
        gameplay = {k: v for k, v in hosted.items() if k not in ('binary_sha256', 'replay_sha256')}
        assert native == gameplay, 'Responsive local/hosted gameplay audit differs'
        stream = CAMPAIGN / 'cycles/20260919T101825Z-880d3c/replay-command-stream'
        command_hashes = []
        for tape in (out / 'replay.bin', d / 'artifacts' / original['episode'] / 'replay.bin'):
            dumped = subprocess.run([str(stream), str(tape)], capture_output=True, check=True)
            info = json.loads(dumped.stderr)
            assert info['ticks'] == native['ticks'] and info['actions_consumed'] == native['actions_consumed']
            command_hashes.append(digest(dumped.stdout))
        assert command_hashes[0] == command_hashes[1]
        rows.append({'color': color, 'episode': original['episode'], 'complete_native_audit_equal': True,
            'complete_all_ten_command_stream_equal': True, 'command_stream_sha256': command_hashes[0],
            'excluded_non_gameplay_fields': ['binary_sha256', 'replay_sha256'], **row})
    write(STUDY / 'calibration.json', {'passed': True, 'rows': rows,
        'scope': 'All ten authentic programs respond from initial state and reproduce the complete published audit on two held source/seed/config cases.'})


def screen():
    assert read(STUDY / 'calibration.json')['passed'] and read(STUDY / 'vm-proof.json')['passed']
    plan = read(STUDY / 'plan.json')
    for p, sha in plan['inputs_sha256'].items(): assert digest(Path(p).read_bytes()) == sha
    rows = []
    for case in plan['cases']:
        for name in NAMES:
            rows.append(match(name, case, Path(plan['sources'][name]), RICHARD, STUDY / 'local' / name / str(case['seed'])))
    write(STUDY / 'local-results.json', {'complete': len(rows) == 16, 'rows': rows})


if __name__ == '__main__':
    if '--prepare' in sys.argv: prepare()
    if '--calibrate' in sys.argv: calibrate()
    if '--screen' in sys.argv: screen()

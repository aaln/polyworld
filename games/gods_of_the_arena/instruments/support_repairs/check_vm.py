"""Real-VM activation, negative cases and actual-class dense-scene checks."""
from copy import deepcopy
import json
import subprocess

from prepare import CLEAN, STUDY, digest, write
import test_policy_ir as fixtures
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from hero_binding import class_ids, class_id

VM = CLEAN.parents[3] / 'tmp/gota-ir/scenario-vm'
MEMORY = ['bestId', 'defActive', 'defAnchor', 'aaCommitted']


def run(name, cases):
    memory = MEMORY if name != 'deployed' else MEMORY[:-1]
    proc = subprocess.run([str(VM), str(STUDY / 'candidates' / name / 'policy.bas')],
                          input=json.dumps({'decisions': cases, 'memory': memory}),
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def main():
    rows = []
    activation = []
    for hero in (2, 3):
        cases = [defense_case(hero, count=4), defense_case(hero)]
        cases[1]['self']['worldTick'] = 101
        for case in cases:
            case['self']['selfHp'] = 300
            case['objects'][3 + hero]['objectHp'] = 300
        cases[1]['objects'][3]['objectTarget'] = 106
        for name in ('anchored', 'unanchored'):
            actual = run(name, cases)
            baseline = run('deployed', cases)
            assert baseline[-1]['memory']['bestId'] == 0, baseline
            assert actual[-1]['memory']['bestId'] == 106, actual
            activation.append({'candidate': name, 'class': class_id(0, hero), 'target': 106,
                               'baseline_target': 0, 'committed': actual[-1]['memory']['aaCommitted']})
            rows.extend(actual)
            for variant in ('no_commitment', 'dead_ally', 'critical_hp'):
                negative = deepcopy(cases)
                if variant == 'no_commitment':
                    negative[1]['objects'][3]['objectTarget'] = 0
                elif variant == 'dead_ally':
                    negative[1]['objects'][3].update(objectAlive=0, objectHp=0)
                else:
                    negative[1]['self']['selfHp'] = 14
                assert run(name, negative)[-1]['memory']['bestId'] == run('deployed', negative)[-1]['memory']['bestId']
            unanchored = deepcopy(cases)
            unanchored[-1]['objects'][2]['objectHp'] = 0
            assert run(name, unanchored)[-1]['memory']['bestId'] == (0 if name == 'anchored' else 106)
    for name in ('anchored', 'unanchored'):
        for team in (0, 1):
            for density in (40, 160, 240):
                for slot, cls in enumerate(class_ids(team)):
                    case = defense_case(slot, count=4) if team == 0 else final_approach(team, 4, 100)
                    if team == 0:
                        case['objects'][3]['objectTarget'] = 106
                    else:
                        enemies = [o for o in case['objects'] if o['objectKind'] == 2]
                        for i, obj in enumerate(enemies):
                            obj.update(objectId=100+i, objectClass=class_id(0, i))
                        case['self'].update(selfClass=cls, selfId=105+slot)
                        own = fixtures.obj(105+slot, kind=2, team=1, x=case['self']['selfX'],
                                           y=case['self']['selfY'], hp=case['self']['selfHp'])
                        own['objectClass'] = cls
                        case['objects'].append(own)
                    case['objects'] += [fixtures.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                        for i in range(density-len(case['objects']))]
                    actual = run(name, [case])
                    rows.extend(actual)
                    if cls not in (7, 8):
                        assert actual[0]['actions'] == run('deployed', [case])[0]['actions']
    assert max(r['instructions'] for r in rows) <= 20000
    assert max(r['work'] for r in rows) <= 50000
    proof = {'passed': True, 'activation': activation, 'dense_decisions': 60,
             'negative_cases_per_caster_candidate': 4, 'blue_and_noncaster_action_parity': True,
             'max_instructions': max(r['instructions'] for r in rows),
             'max_fixture_work': max(r['work'] for r in rows), 'vm_sha256': digest(VM.read_bytes()),
             'scope': 'Native scenario VM correctness/budget check; full game budgets and outcomes still required.'}
    write(STUDY / 'vm-proof.json', proof)
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()

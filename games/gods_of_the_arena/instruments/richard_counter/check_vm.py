"""Exercise the recall exception in the real BASIC VM, including negative cases."""
from copy import deepcopy
import json
import subprocess
from prepare import CLEAN, PARENT, STUDY
import test_policy_ir as fixtures
from test_rush_defense import scene

VM = CLEAN.parents[3] / 'tmp/gota-ir/scenario-vm'


def run(source, cases, memory):
    result = subprocess.run([str(VM), str(source)], input=json.dumps(
        {'decisions': cases, 'memory': memory}), text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


def case(team):
    s = scene(team, count=2, worldTick=100)
    anchor = s['objects'][2 if team == 0 else 3]
    x, y = (85, 25) if team == 0 else (31, 91)
    anchor.update(objectX=x, objectY=y)
    for e in s['objects'][4:]:
        e.update(objectX=x+1, objectY=y+1)
    s['self'].update(selfX=50, selfY=60)
    return s


def main():
    proof = []
    for name in ('critical40', 'critical60'):
        source = STUDY / 'candidates' / name / 'policy.bas'
        for team in (0, 1):
            s = case(team)
            memory = ['defActive', 'defUntil', 'criticalUntil', 'bestId']
            rows = run(source, [s], memory)
            assert rows[0]['memory']['defActive'] == 1
            assert rows[0]['memory']['criticalUntil'] == 1300
            parent = run(PARENT / 'policy.bas', [s], ['defActive'])
            assert parent[0]['memory']['defActive'] == 0
            for variant in ('absent', 'dead', 'friendly', 'unanchored', 'far'):
                negative = deepcopy(s)
                for e in negative['objects'][4:]:
                    if variant == 'dead':
                        e.update(objectAlive=0, objectHp=0)
                    if variant == 'friendly':
                        e['objectTeam'] = team
                    if variant == 'far':
                        e.update(objectX=50, objectY=65)
                if variant == 'absent':
                    negative['objects'] = negative['objects'][:4]
                if variant == 'unanchored':
                    negative['objects'][2 if team == 0 else 3]['objectHp'] = 0
                row = run(source, [negative], memory)[0]
                assert row['memory']['criticalUntil'] == 0, (name, team, variant, row)
            cases = [s]
            for tick in range(101, 1301):
                gap = deepcopy(s)
                gap['self']['worldTick'] = tick
                gap['objects'] = gap['objects'][:4]
                cases.append(gap)
            rows = run(source, cases, memory)
            assert rows[-2]['memory']['defActive'] == 1
            assert rows[-1]['memory']['defActive'] == 0
            dense = deepcopy(s)
            dense['objects'] += [fixtures.obj(1000+i, team=i%2, x=i%116, y=i*7%116)
                                 for i in range(220)]
            rows += run(source, [dense], memory)
            assert max(r['instructions'] for r in rows) <= 20000
            assert max(r['work'] for r in rows) <= 50000
            proof.append({'candidate': name, 'team': team, 'activation': True,
                'negative_cases': 5, 'retention_ticks': 1200, 'expiry': True,
                'max_instructions': max(r['instructions'] for r in rows),
                'max_work': max(r['work'] for r in rows)})
    (STUDY / 'critical-vm-proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()

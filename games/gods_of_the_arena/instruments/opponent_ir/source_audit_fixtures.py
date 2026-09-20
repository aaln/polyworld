"""Source-reveal discriminators: exact v135 BASIC, synthetic public scenes.

Requests execute in the pinned BASIC VM. Command acceptance is scripted, so
these tests establish branch/command semantics, not combat efficacy or new
held-out forecast accuracy. No neural weights or private globals are patched.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from source_audit import ROOT, OUT, RUN, SOURCE_SHA, read, write, sha

MEMORY = ['decision', 'combatDecision', 'objectiveBuild', 'neuralActionCountdown',
          'bestId', 'objectiveId', 'objectiveKind', 'siegeThreatId', 'reserveNearest',
          'reserveTarget', 'reserveDirect', 'reserveGuards', 'reserveGuardCritical',
          'reserveFinish', 'groupDeparture', 'recoveryLastHit']


def obj(i, kind, team, x, y, hp=500, target=0):
    return dict(objectId=i, objectKind=kind, objectTeam=team, objectX=x, objectY=y,
                objectHp=hp, objectAlive=1, objectTarget=target)


def scene():
    return {'self': dict(selfId=100, selfTeam=0, selfClass=7, selfX=50, selfY=50,
        selfHp=800, selfMaxHp=800, selfMana=200, selfMaxMana=300, selfGold=0,
        selfLevel=5, worldTick=8000, selfAttackRange=600000, selfAttackDamage=40,
        selfAttacksLanded=0, mapWidth=116, mapHeight=116), 'inventory': [0] * 6,
        'objects': [obj(1, 1, 0, 105, 10, 400), obj(10, 4, 0, 105, 13, 1950),
            obj(11, 4, 0, 101, 10, 1950), obj(100, 2, 0, 50, 50, 800),
            obj(21, 4, 1, 55, 50, 1000), obj(201, 3, 1, 51, 50, 60),
            obj(200, 2, 1, 54, 50, 400)],
        'abilities': [{'abilityCharges': 1, 'abilityCooldown': 0} for _ in range(4)]}


def change(f, oid, **fields):
    next(o for o in f['objects'] if o['objectId'] == oid).update(fields)
    return f


def main():
    assert sha(OUT / 'v135.bas') == SOURCE_SHA
    results = []

    def run(name, frames):
        request = {'decisions': frames, 'memory': MEMORY}
        p = subprocess.run([str(RUN / 'fixture-vm'), str(OUT / 'v135.bas')],
            input=json.dumps(request), text=True, capture_output=True, check=True)
        actual = json.loads(p.stdout)
        results.append({'id': name, 'request': request, 'actual': actual})
        return actual

    def terminal(row):
        return [a for a in row['actions'] if a['command'] in ['attackTarget', 'walkTo']][-1]

    quiet = scene()
    attack = change(scene(), 200, objectTarget=100)
    ally = change(scene(), 200, objectTarget=101)
    a = run('siege_quiet', [quiet])[0]
    b = run('siege_attacker_targets_self', [attack])[0]
    c = run('siege_attacker_targets_other_ally', [ally])[0]
    assert [r['memory']['combatDecision'] for r in [a, b, c]] == [2, 2, 2]
    assert [terminal(r)['arguments'] for r in [a, b, c]] == [[21], [200], [21]]
    far = change(scene(), 200, objectX=61, objectTarget=100)
    r = run('siege_attacker_outside_range', [far])[0]
    assert r['memory']['siegeThreatId'] == 0 and terminal(r)['arguments'] == [21]
    god = change(deepcopy(attack), 21, objectKind=1)
    r = run('siege_god_is_not_tower', [god])[0]
    assert r['memory']['siegeThreatId'] == 200 and terminal(r)['arguments'] == [21]
    wounded = deepcopy(attack)
    wounded['objects'].append(obj(202, 2, 1, 55, 51, 100, 100))
    r = run('siege_lowest_hp_eligible_attacker', [wounded])[0]
    assert terminal(r)['arguments'] == [202]

    tower = scene()
    tower['objects'] = [o for o in tower['objects'] if o['objectId'] != 200]
    barracks = change(deepcopy(tower), 21, objectKind=5)
    a = run('structure_context_tower', [tower])[0]
    b = run('structure_context_barracks', [barracks])[0]
    assert a['memory']['combatDecision'] == b['memory']['combatDecision'] == 2
    assert terminal(a)['arguments'] == [21] and terminal(b)['command'] == 'walkTo'

    frames = [deepcopy(quiet) for _ in range(8)]
    for i, frame in enumerate(frames):
        frame['self']['worldTick'] += i
    r = run('neural_four_decision_clock', frames)
    assert [d['memory']['neuralActionCountdown'] for d in r] == [4, 3, 2, 1, 4, 3, 2, 1]
    frames = [deepcopy(quiet) for _ in range(3)]
    for i, frame in enumerate(frames):
        frame['self']['worldTick'] += i
        frame['self']['selfAttacksLanded'] = int(i > 0)
    r = run('one_decision_hit_recovery_pulse', frames)
    assert [terminal(d)['command'] for d in r] == ['attackTarget', 'walkTo', 'attackTarget']
    assert terminal(r[1])['arguments'] == [50, 50]

    defense = scene()
    change(defense, 1, objectX=60, objectY=50)
    defense['objects'] = [o for o in defense['objects'] if o['objectId'] not in [10, 11]]
    change(defense, 201, objectTarget=1)
    a = run('home_direct_creep_over_hero', [defense])[0]
    assert a['memory']['reserveNearest'] == 1 and a['memory']['reserveDirect'] == 201
    assert terminal(a)['arguments'] == [201]
    closer = deepcopy(defense)
    closer['objects'].append(obj(101, 2, 0, 59, 50, 800))
    b = run('home_closer_ally_removes_self_reservation', [closer])[0]
    assert b['memory']['reserveNearest'] == 0

    sys.path.insert(0, str(ROOT / 'examples/gods_of_the_arena/players/ir'))
    import opponent_ir
    model = opponent_ir.load(ROOT / 'examples/gods_of_the_arena/players/ir/opponents/richard_v135.py')
    # Forecast context deliberately matches the frozen, coarse abstraction.
    forecasts = {str(mask): opponent_ir.predict(model, {'opportunity_mask': mask, 'low_hp': False},
        ['hold', 'advance', 'withdraw', 'lateral', 'target_creep', 'target_structure'] +
        (['target_hero'] if mask == 7 else [])) for mask in [6, 7]}
    write(OUT / 'discriminating-fixtures.ir.json', {
        'schema': 'gota-source-reveal-discriminating-fixtures/1', 'source_sha256': SOURCE_SHA,
        'vm_binary_sha256': sha(RUN / 'fixture-vm'),
        'vm_source_sha256': sha(Path(__file__).with_name('source_fixture_vm.nim')),
        'scenes': len(results), 'executed_decisions': sum(len(r['actual']) for r in results),
        'all_assertions_passed': True, 'frozen_ir_forecasts': forecasts,
        'scope': 'Synthetic source-reveal branch tests with scripted acceptance. Counterexamples to identifying mechanisms from the old coarse context; not estimates of old-model forecast accuracy or real combat outcomes.',
        'private_state_injected': False, 'fixtures': results})
    print(f'{len(results)} discriminator scenes passed; {sum(len(r["actual"]) for r in results)} VM decisions')


if __name__ == '__main__':
    main()

"""Native command, boundary, dense-budget and unchanged-blue checks."""
from copy import deepcopy
import json
import subprocess
from study import CLEAN, STUDY, PARENT, NAMES, read, write, digest
from test_policy_ir import obj, fixture
from hero_binding import class_ids

VM = CLEAN / 'tmp/gota-ir/scenario-vm'
MEMORY = ['bestId', 'defActive', 'defUntil', 'criticalUntil', 'motionActive',
          'motionLastTick', 'motionLastHits', 'mAllies', 'coreRespond']


def case(team=0, slot=0, tick=100, x=60, y=50):
    objects = [obj(1, kind=1, team=0, x=105, y=11, hp=400),
        obj(2, kind=1, team=1, x=11, y=105, hp=400),
        obj(25, kind=4, team=0, x=101, y=18, hp=1950)]
    for i, cls in enumerate(class_ids(team)):
        actor = obj(100 + team * 5 + i, kind=2, team=team, x=x+i%2, y=y+i//2, hp=300)
        actor['objectClass'] = cls; objects.append(actor)
    c = fixture(objects, selfId=100+team*5+slot, selfTeam=team, selfClass=class_ids(team)[slot],
        selfX=x+slot%2, selfY=y+slot//2, selfHp=300, selfMaxHp=400, selfGold=150,
        selfAttackRange=360000, selfAttackDamage=30, selfAttackCooldown=5,
        selfAttacksLanded=20, worldTick=tick)
    c['returns'] = {'terrainWalkable': 1, 'walkTo': 1, 'attackTarget': 1}
    return c


def run(source, decisions):
    p = subprocess.run([str(VM), str(source)], input=json.dumps({'decisions': decisions, 'memory': MEMORY}),
        capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def main():
    rows, checks = [], []
    for name in NAMES[2:]:
        source = STUDY / 'candidates' / name / 'policy.bas'
        for slot in range(5):
            c = case(slot=slot)
            c['objects'].append(obj(105, kind=2, team=1, x=62, y=51, hp=300))
            a = run(source, [c])[0]; rows.append(a)
            assert any(x['command'] == 'attackTarget' for x in a['actions'])
            assert not any(x['command'] == 'walkTo' for x in a['actions']), 'cold hit memory'
            fresh = deepcopy(c); fresh['self'].update(worldTick=101, selfAttacksLanded=21)
            a = run(source, [c, fresh])[-1]; rows.append(a)
            assert any(x['command'] == 'walkTo' and x['arguments'] == [fresh['self']['selfX'], fresh['self']['selfY']] for x in a['actions'])
            assert a['memory']['motionActive'] == 1
            gap = deepcopy(fresh); gap['self']['worldTick'] = 150
            a = run(source, [c, gap])[-1]; rows.append(a)
            assert not any(x['command'] == 'walkTo' for x in a['actions']), 'gap hit memory'
            mana = deepcopy(c); mana['self']['selfMana'] = 0
            a = run(source, [mana])[0]; rows.append(a)
            purchases = [x['arguments'][0] for x in a['actions'] if x['command'] == 'buyItem']
            assert 3 not in purchases and purchases[:2] == [11, 13], purchases
        for team in (0, 1):
            for slot in range(5):
                for count in (10, 64, 80, 128, 240):
                    c = case(team=team, slot=slot, tick=6000)
                    c['objects'] += [obj(3000+i, team=i%2, x=i%116, y=i*7%116) for i in range(count-len(c['objects']))]
                    a = run(source, [c])[0]; rows.append(a)
                    if team == 1:
                        assert a['actions'] == run(PARENT / 'policy.bas', [c])[0]['actions']
        checks.append({'candidate': name, 'all_red_classes_fresh_recovery': True,
            'cold_and_gap_no_recovery': True, 'red_healing_before_damage_equipment_no_mana_purchase': True,
            'blue_fixture_actions_equal': True})
    c = case(tick=5000, x=75, y=40)
    for i, actor in enumerate(c['objects'][4:8]):
        actor['objectX'], actor['objectY'] = 103+i%2, 12+i//2
    c['objects'] += [obj(105+i, kind=2, team=1, x=96+i, y=22, hp=300) for i in range(2)]
    a = run(STUDY/'candidates/damage_recovery/policy.bas', [c])[0]; rows.append(a)
    b = run(STUDY/'candidates/productive/policy.bas', [c])[0]; rows.append(b)
    assert a['memory']['defActive'] == 1 and b['memory']['defActive'] == 0
    assert b['memory']['mAllies'] == 4 and b['memory']['defUntil'] == 0
    nearest = deepcopy(c); nearest['self'].update(selfX=105, selfY=11)
    nearest['objects'][3].update(objectX=105, objectY=11)
    a = run(STUDY/'candidates/productive/policy.bas', [nearest])[0]; rows.append(a)
    assert a['memory']['defActive'] == 1 and a['memory']['mAllies'] == 0
    # Equal-distance public IDs give one nearest role; dead actors never rank.
    tied = deepcopy(nearest)
    tied['self'].update(selfId=101, selfClass=6)
    for o in tied['objects'][3:8]: o.update(objectX=105, objectY=11)
    a = run(STUDY/'candidates/productive/policy.bas', [tied])[0]; rows.append(a)
    assert a['memory']['mAllies'] == 1
    tied['objects'][3].update(objectHp=0, objectAlive=0)
    a = run(STUDY/'candidates/productive/policy.bas', [tied])[0]; rows.append(a)
    assert a['memory']['mAllies'] == 0
    assert max(r['instructions'] for r in rows) <= 19000
    assert max(r['work'] for r in rows) <= 50000
    write(STUDY/'vm-proof.json', {'passed': True, 'checks': checks,
        'red_role_assignment_and_death_tie_checks': True,
        'max_instructions': max(r['instructions'] for r in rows),
        'max_work': max(r['work'] for r in rows), 'vm_sha256': digest(VM.read_bytes()),
        'rows': rows, 'scope': 'Scripted host acceptance proves command semantics, not combat success.'})
    print('Native scenarios passed', len(rows), flush=True)


if __name__ == '__main__': main()

import unittest
import test_policy_ir as f
import test_rush_unblock as u
from shared_engagement import make, VARIANTS, STUDY
from policy_ir import compile_policy, extract, write
from test_jordan_root import final_approach
from hero_binding import class_id, class_ids


def defense_case(hero=0, healthy=True, tower=False, count=2):
    positions = [(100, 15), (94, 7), (103, 9), (103, 9), (60, 12)]
    objects = [f.obj(1, kind=1, x=105, y=11, hp=4000, alive=0),
               f.obj(2, kind=1, team=1, x=11, y=105, hp=4000, alive=0),
               f.obj(29, kind=4, x=100, y=11, hp=1950)]
    for c, (x, y) in enumerate(positions):
        hp = 14 if c == 3 or (c in (1, 2) and not healthy) else 400
        obj = f.obj(100+c, kind=2, x=x, y=y, hp=hp)
        obj['objectClass'] = class_id(0, c)
        objects.append(obj)
    for c in range(count):
        e = f.obj(106+c, kind=2, team=1, x=97 if tower else 92,
                  y=14 if tower else 20+c, hp=400)
        e['objectTarget'] = 29 if tower else 0
        e['objectClass'] = class_id(1, (c+1) % 5)
        objects.append(e)
    hp = objects[3+hero]['objectHp']
    return f.fixture(objects, selfId=100+hero, selfClass=class_id(0, hero), selfX=positions[hero][0],
                     selfY=positions[hero][1], selfHp=hp, selfMaxHp=400, worldTick=100)


class SharedTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_shared_target_includes_healthy_casters_outside_old_self_radius(self):
        for hero in (0, 1, 2):
            row = self.play('shared_two', [defense_case(hero)], ('bestId', 'seFriends', 'seGo'))[0]
            self.assertEqual(row['memory']['bestId'], 106)
            self.assertEqual(row['memory']['seFriends'], 3)
        row = self.play('shared_two', [defense_case(3)], ('bestId', 'seGo'))[0]
        self.assertEqual(row['memory'], {'bestId': 0, 'seGo': 1})

    def test_captured_spacing_reproduces_parent_split_and_coordinates_candidate(self):
        old, new = [], []
        for hero in (0, 2):
            first = defense_case(hero, count=4)
            second = defense_case(hero)
            second['self']['worldTick'] = 101
            old.append(self.play('pressure_parent', [first, second], ('bestId',))[-1]['memory']['bestId'])
            new.append(self.play('shared_two', [first, second], ('bestId',))[-1]['memory']['bestId'])
        self.assertEqual(old, [106, 0])
        self.assertEqual(new, [106, 106])

    def test_tank_holds_when_healthy_support_is_missing(self):
        for name in VARIANTS[2:]:
            row = self.play(name, [defense_case(healthy=False)], ('bestId', 'seFriends', 'seGo'))[0]
            self.assertEqual(row['memory'], {'bestId': 0, 'seFriends': 1, 'seGo': 0})

    def test_tower_entry_allows_defense_without_full_squad(self):
        for name in VARIANTS[2:]:
            row = self.play(name, [defense_case(healthy=False, tower=True)], ('bestId', 'seTower'))[0]
            self.assertEqual(row['memory'], {'bestId': 106, 'seTower': 1})

    def test_absent_or_dead_enemy_does_not_trigger_local_recall(self):
        for alteration in ('absent', 'dead'):
            case = defense_case(count=0 if alteration == 'absent' else 2)
            if alteration == 'dead':
                for e in case['objects'][-2:]: e.update(objectAlive=0, objectHp=0)
            row = self.play('shared_two', [case], ('defActive', 'seLocal'))[0]
            self.assertEqual(row['memory'], {'defActive': 0, 'seLocal': 0})

    def test_roundtrip_and_dense_runtime_and_blue_parity(self):
        rows = []
        for name in VARIANTS[2:]:
            p = make(name)
            self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for density in (40, 160, 240):
                    case = defense_case() if team == 0 else final_approach(team, 4, 100)
                    case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                        for i in range(density-len(case['objects']))]
                    cases = [case | {'self': case['self'] | {'selfClass': c}} for c in class_ids(team)]
                    rr = self.play(name, cases)
                    rows += rr
                    if team == 1:
                        self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('pressure_parent', cases)])
        write(STUDY/'vm-stress-binding-corrected.json', {'passed': True, 'decisions': len(rows),
              'max_instructions': max(r['instructions'] for r in rows),
              'max_fixture_work': max(r['work'] for r in rows),
              'scope': 'Mixed40/160/240objects; exact blue action parity. Does not fix inherited extreme hostile-wave VM limit.'})
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)


if __name__ == '__main__': unittest.main()

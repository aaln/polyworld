import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from caster_assist import make, VARIANTS, STUDY
from policy_ir import compile_policy, extract, write
from hero_binding import class_ids


class CasterTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_legacy_caster_branch_is_inactive_for_actual_red_casters(self):
        for existing in (False, True):
            first = defense_case(2, count=4)
            case = defense_case(2); case['self']['worldTick'] = 101
            case['objects'][3]['objectTarget'] = 106
            if existing:
                blocker = f.obj(1500, kind=3, team=1, x=104, y=10)
                case['objects'].append(blocker)
            for name in VARIANTS[2:]:
                row = self.play(name, [first, case], ('bestId',))[-1]
                self.assertEqual(row['memory']['bestId'], 1500 if existing else 0)

    def test_other_roles_and_blue_commands_match_parent(self):
        rows = []
        for name in VARIANTS[2:]:
            p = make(name); self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for density in (40, 160, 240):
                    case = defense_case(count=4) if team == 0 else final_approach(team, 4, 100)
                    if team == 0: case['objects'][3]['objectTarget'] = 106
                    case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                        for i in range(density-len(case['objects']))]
                    for c in class_ids(team):
                        d = case | {'self': case['self'] | {'selfClass': c}}
                        new = self.play(name, [d]); rows += new
                        self.assertEqual(new[0]['actions'], self.play('pressure_parent', [d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        write(STUDY/'vm-stress-binding-corrected.json', {'passed': True, 'decisions': len(rows),
            'max_instructions': max(r['instructions'] for r in rows), 'max_fixture_work': max(r['work'] for r in rows),
            'scope': 'Mixed40/160/240objects; unchanged noncaster red and all blue commands. Inherited extreme hostile-wave VM limit remains.'})


if __name__ == '__main__': unittest.main()

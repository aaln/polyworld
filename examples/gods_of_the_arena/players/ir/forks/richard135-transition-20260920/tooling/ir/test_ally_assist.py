import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from ally_assist import make, VARIANTS, STUDY
from policy_ir import compile_policy, extract, write
from hero_binding import class_ids


class AssistTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_ally_attack_bridges_the_captured_self_radius_gap(self):
        for name in VARIANTS[2:]:
            cases = [defense_case(2, count=4), defense_case(2)]
            cases[1]['self']['worldTick'] = 101
            cases[1]['objects'][3]['objectTarget'] = 106
            old = self.play('pressure_parent', cases, ('bestId',))[-1]
            new = self.play(name, cases, ('bestId', 'aaCommitted'))[-1]
            self.assertEqual(old['memory']['bestId'], 0)
            self.assertEqual(new['memory'], {'bestId': 106, 'aaCommitted': 1})

    def test_no_ally_intent_or_critical_hp_preserves_parent_target(self):
        for critical in (False, True):
            cases = [defense_case(2, count=4), defense_case(2)]
            cases[1]['self']['worldTick'] = 101
            if critical:
                cases[1]['objects'][3]['objectTarget'] = 106
                cases[1]['self']['selfHp'] = 14
            for name in VARIANTS[2:]:
                row = self.play(name, cases, ('bestId',))[-1]
                self.assertEqual(row['memory']['bestId'], 0)

    def test_legacy_wait_gate_is_inactive_for_actual_red_death_knight(self):
        a = defense_case(0, healthy=False, count=4)
        b = defense_case(0, healthy=False); b['self']['worldTick'] = 101
        # Historical assist_wait used class0 (blue Vanguard), not red DK5.
        for name, expected in [('pressure_parent', 106), ('assist18', 106), ('assist_wait', 106)]:
            self.assertEqual(self.play(name, [a,b], ('bestId',))[-1]['memory']['bestId'], expected)

    def test_roundtrip_dense_runtime_and_inactive_blue(self):
        rows = []
        for name in VARIANTS[2:]:
            p = make(name); self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for density in (40, 160, 240):
                    case = defense_case(count=4) if team == 0 else final_approach(team, 4, 100)
                    case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                        for i in range(density-len(case['objects']))]
                    cases = [case | {'self': case['self'] | {'selfClass': c}} for c in class_ids(team)]
                    rr = self.play(name, cases); rows += rr
                    if team == 1:
                        self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('pressure_parent', cases)])
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        write(STUDY/'vm-stress-binding-corrected.json', {'passed': True, 'decisions': len(rows),
            'max_instructions': max(r['instructions'] for r in rows), 'max_fixture_work': max(r['work'] for r in rows),
            'scope': 'Active red defense, mixed40/160/240objects and unchanged blue actions. Inherited extreme hostile-wave limit not fixed.'})


if __name__ == '__main__': unittest.main()

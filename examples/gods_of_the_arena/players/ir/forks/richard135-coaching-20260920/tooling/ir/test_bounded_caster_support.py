import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from bounded_caster_support import make, VARIANTS, STUDY
from caster_assist import make as legacy
from hero_binding import CLASS_ID, class_id, class_ids, CONTENT
from policy_ir import compile_policy, extract, write


class BoundedCasterTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_engine_and_host_adapter_use_global_class_ordinals(self):
        self.assertEqual(class_ids(0), [5, 6, 7, 8, 9])
        self.assertEqual(class_ids(1), [0, 1, 2, 3, 4])
        self.assertIn('heroDataIds[DataSelfClass], int32(hero.class.ord)', CONTENT.with_name('bots.nim').read_text())
        self.assertEqual(defense_case(2)['self']['selfClass'], CLASS_ID['Lich'])
        self.assertEqual(defense_case(3)['self']['selfClass'], CLASS_ID['Warlock'])

    def test_real_red_casters_join_while_legacy_binding_is_inactive(self):
        for hero in (2, 3):
            first = defense_case(hero, count=4)
            case = defense_case(hero); case['self']['worldTick'] = 101
            for row in (first, case): row['self']['selfHp'] = 300
            case['objects'][3]['objectTarget'] = 106
            for name in VARIANTS[2:]:
                self.assertEqual(self.play(name, [first, case], ('bestId',))[-1]['memory']['bestId'], 106)
            saved = self.factory
            self.factory = legacy
            try: self.assertEqual(self.play('caster_focus', [first, case], ('bestId',))[-1]['memory']['bestId'], 0)
            finally: self.factory = saved

    def test_preserve_existing_wave_target(self):
        first=defense_case(2,count=4);case=defense_case(2)
        case['self']['worldTick']=101;case['objects'][3]['objectTarget']=106
        case['objects'].append(f.obj(1500,kind=3,team=1,x=104,y=10))
        for name in VARIANTS[2:]:
            self.assertEqual(self.play(name,[first,case],('bestId',))[-1]['memory']['bestId'],1500)

    def test_distant_support_excluded_but_parent_would_follow(self):
        first=defense_case(2,count=4);case=defense_case(2)
        case['self']['worldTick']=101;case['objects'][3]['objectTarget']=106
        for i,o in enumerate(o for o in case['objects'] if o['objectKind']==2 and o['objectTeam']==1):
            o.update(objectX=84,objectY=15+i)
        self.assertEqual(self.play('pressure_parent',[first,case],('bestId',))[-1]['memory']['bestId'],106)
        for name in VARIANTS[2:]:
            self.assertEqual(self.play(name,[first,case],('bestId',))[-1]['memory']['bestId'],0)

    def test_actual_noncasters_and_blue_unchanged_dense_and_roundtrip(self):
        rows = []
        for name in VARIANTS[2:]:
            p = make(name); self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for density in (40, 160, 240):
                    for slot, c in enumerate(class_ids(team)):
                        d = defense_case(slot, count=4) if team == 0 else final_approach(team, 4, 100)
                        if team == 0:
                            d['objects'][3]['objectTarget'] = 106
                        else:
                            enemies = [o for o in d['objects'] if o['objectKind'] == 2]
                            for i, o in enumerate(enemies):
                                o.update(objectId=100+i, objectClass=class_id(0, i))
                            d['self'].update(selfClass=c, selfId=105+slot)
                            own = f.obj(105+slot, kind=2, team=1, x=d['self']['selfX'], y=d['self']['selfY'], hp=d['self']['selfHp'])
                            own['objectClass'] = c
                            d['objects'].append(own)
                        d['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                         for i in range(density-len(d['objects']))]
                        own = next(o for o in d['objects'] if o['objectId'] == d['self']['selfId'])
                        self.assertEqual((own['objectClass'], own['objectTeam']), (c, team))
                        new = self.play(name, [d]); rows += new
                        if c not in (CLASS_ID['Lich'], CLASS_ID['Warlock']):
                            self.assertEqual(new[0]['actions'], self.play('pressure_parent', [d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        write(STUDY/'vm-stress.json', {'passed': True, 'decisions': len(rows), 'class_ids_from_engine': CLASS_ID,
            'max_instructions': max(r['instructions'] for r in rows), 'max_fixture_work': max(r['work'] for r in rows),
            'scope': 'Actual team/class pairs; mixed40/160/240objects. Noncaster red and all blue commands exact. Extreme hostile-wave inherited limit remains.'})


if __name__ == '__main__': unittest.main()

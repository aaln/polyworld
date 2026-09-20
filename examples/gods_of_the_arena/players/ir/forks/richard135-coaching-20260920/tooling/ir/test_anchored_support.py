import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from anchored_support import make, VARIANTS, STUDY
from hero_binding import CLASS_ID
from policy_ir import compile_policy, extract, write


class AnchoredSupportTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def cases(self, hero=2, anchor=True, committer=0):
        first=defense_case(hero,count=4); case=defense_case(hero)
        case['self']['worldTick']=101
        for row in (first,case): row['self']['selfHp']=300
        case['objects'][3+committer]['objectTarget']=106
        if not anchor:
            case['objects'][2]['objectHp']=0
        return [first,case]

    def test_frontline_engagement_under_friendly_perimeter_is_supported(self):
        for hero in (2,3):
            for name in VARIANTS[2:]:
                m=self.play(name,self.cases(hero),('bestId','defAnchor','aaCommitted'))[-1]['memory']
                self.assertEqual(m,{'bestId':106,'defAnchor':29,'aaCommitted':1})

    def test_no_anchor_excludes_expanded_support_only_when_required(self):
        expected={'pressure_parent':106,'anchor':0,'frontline':106,'anchored_frontline':0}
        for name,target in expected.items():
            m=self.play(name,self.cases(anchor=False),('bestId','defAnchor'))[-1]['memory']
            self.assertEqual(m,{'bestId':target,'defAnchor':0})

    def test_passing_carry_or_caster_cannot_impersonate_frontline(self):
        for committer in (1,3):
            cases=self.cases(committer=committer)
            cases[-1]['objects'][3+committer]['objectHp']=300
            for name,target in {'pressure_parent':106,'anchor':106,'frontline':0,'anchored_frontline':0}.items():
                self.assertEqual(self.play(name,cases,('bestId',))[-1]['memory']['bestId'],target)

    def test_ordinary_close_defense_and_existing_wave_targets_retained(self):
        for name in VARIANTS[2:]:
            cases=self.cases(anchor=False,committer=1)
            cases[-1]['objects'].append(f.obj(1500,kind=3,team=1,x=104,y=10))
            self.assertEqual(self.play(name,cases,('bestId',))[-1]['memory']['bestId'],1500)
            cases=self.cases(anchor=False,committer=1)
            for e in cases[-1]['objects']:
                if e['objectKind']==2 and e['objectTeam']==1:
                    e.update(objectX=100,objectY=14)
            self.assertNotEqual(self.play(name,cases,('bestId',))[-1]['memory']['bestId'],0)

    def test_roundtrip_and_inactive_role_parity_with_real_global_classes(self):
        # Reuse the full ten-role, 40/160/240-object VM budget/parity cases with
        # this study's variants rather than importing its unittest class.
        from test_jordan_root import final_approach
        from hero_binding import class_id,class_ids
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name); self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for density in (40,160,240):
                    for slot,c in enumerate(class_ids(team)):
                        d=defense_case(slot,count=4) if team==0 else final_approach(team,4,100)
                        if team==0: d['objects'][3]['objectTarget']=106
                        else:
                            enemies=[o for o in d['objects'] if o['objectKind']==2]
                            for i,o in enumerate(enemies): o.update(objectId=100+i,objectClass=class_id(0,i))
                            d['self'].update(selfClass=c,selfId=105+slot)
                            own=f.obj(105+slot,kind=2,team=1,x=d['self']['selfX'],y=d['self']['selfY'],hp=d['self']['selfHp'])
                            own['objectClass']=c; d['objects'].append(own)
                        d['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(d['objects']))]
                        own=next(o for o in d['objects'] if o['objectId']==d['self']['selfId'])
                        self.assertEqual((own['objectClass'],own['objectTeam']),(c,team))
                        new=self.play(name,[d]); rows+=new
                        if c not in (CLASS_ID['Lich'],CLASS_ID['Warlock']):
                            self.assertEqual(new[0]['actions'],self.play('pressure_parent',[d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'class_ids_from_engine':CLASS_ID,
            'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),
            'scope':'Actual team/class pairs; mixed40/160/240objects. Noncaster red and all blue commands exact. Inherited extreme hostile-wave limit unchanged.'})


if __name__=='__main__': unittest.main()

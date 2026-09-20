import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from hero_binding import class_id, class_ids
from supported_defense import make, VARIANTS, STUDY
from policy_ir import compile_policy, extract, write


class SupportedTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def states(self, hero=0, **kwargs):
        a=defense_case(hero,count=4,**kwargs)
        b=defense_case(hero,**kwargs);b['self']['worldTick']=101
        return [a,b]

    def test_actual_death_knight_waits_without_support(self):
        cases=self.states(healthy=False)
        self.assertEqual(cases[-1]['self']['selfClass'],5)
        self.assertEqual(self.play('pressure_parent',cases,('bestId',))[-1]['memory']['bestId'],106)
        for name in VARIANTS[2:]:
            self.assertEqual(self.play(name,cases,('bestId','dhHeld'))[-1]['memory'],{'bestId':0,'dhHeld':1})

    def test_healthy_support_or_tower_entry_allows_initiation(self):
        for kwargs in ({'healthy':True},{'healthy':False,'tower':True}):
            for name in VARIANTS[2:]:
                self.assertEqual(self.play(name,self.states(**kwargs),('bestId','dhHeld'))[-1]['memory'],{'bestId':106,'dhHeld':0})

    def test_casters_follow_committed_ally_and_do_not_wait(self):
        for slot in (2,3):
            cases=self.states(slot)
            for c in cases:
                c['self']['selfHp']=300;c['objects'][3+slot]['objectHp']=300
            cases[-1]['objects'][3]['objectTarget']=106
            for name in VARIANTS[2:]:
                self.assertEqual(self.play(name,cases,('bestId','dhHeld'))[-1]['memory'],{'bestId':106,'dhHeld':0})

    def test_roundtrip_dense_actual_team_classes_and_blue_parity(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for density in (40,160,240):
                    for slot,c in enumerate(class_ids(team)):
                        d=defense_case(slot,count=4,healthy=False) if team==0 else final_approach(team,4,100)
                        if team==0:d['objects'][3]['objectTarget']=106
                        else:
                            for i,o in enumerate(o for o in d['objects'] if o['objectKind']==2):
                                o.update(objectId=100+i,objectClass=class_id(0,i))
                            d['self'].update(selfClass=c,selfId=105+slot)
                            own=f.obj(105+slot,kind=2,team=1,x=d['self']['selfX'],y=d['self']['selfY'],hp=d['self']['selfHp'])
                            own['objectClass']=c;d['objects'].append(own)
                        d['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(d['objects']))]
                        own=next(o for o in d['objects'] if o['objectId']==d['self']['selfId'])
                        self.assertEqual((own['objectClass'],own['objectTeam']),(c,team))
                        new=self.play(name,[d]);rows+=new
                        if team==1 or c in (6,9):
                            self.assertEqual(new[0]['actions'],self.play('pressure_parent',[d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),
            'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),
            'scope':'Actual hero classes/IDs, mixed40/160/240objects; blue and red Crossbow/Berserker actions preserved. Inherited extreme-hostile-wave limit remains.'})


if __name__=='__main__':unittest.main()

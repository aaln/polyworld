"""Quiet starts after arrival; travelling and live tower threats are not idle."""
import unittest
from copy import deepcopy
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from g002_arrival import make,STUDY,VARIANTS
from policy_ir import compile_policy,extract,write


class ArrivalReleaseTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def cases(self,slot=2,tick=1000):
        a=defense_case(slot,count=4);b=defense_case(slot,count=0);b['self']['worldTick']=tick
        for c in (a,b):c['self']['selfHp']=400;c['objects'][3+slot]['objectHp']=400
        return [a,b]

    def test_cross_lane_travel_does_not_expire_as_quiet(self):
        for n in VARIANTS[2:]:
            cases=self.cases(tick=1800)
            for c in cases:
                c['self'].update(selfX=60,selfY=75);c['objects'][5].update(objectX=60,objectY=75)
            m=self.play(n,cases,('defActive','pdReleased','pdAtRally','pdLastProductive'))[-1]['memory']
            self.assertEqual(m,{'defActive':1,'pdReleased':0,'pdAtRally':0,'pdLastProductive':1800})

    def test_arrived_idle_defenders_eventually_resume_offense(self):
        for n in VARIANTS[2:]:
            p=make(n)['skill']['observe']['parameters']
            for slot in (0,2,3):
                threshold=p['redbranch_tank_quiet_ticks' if slot==0 else 'redbranch_quiet_ticks']
                m=self.play(n,self.cases(slot,100+threshold),('defActive','pdReleased','pdAtRally'))[-1]['memory']
                self.assertEqual(m,{'defActive':0,'pdReleased':1,'pdAtRally':1})

    def test_current_outer_tower_group_protects_defense_far_from_home(self):
        for n in VARIANTS[2:]:
            cases=self.cases(tick=1800);cases[-1]=deepcopy(cases[0]);cases[-1]['self']['worldTick']=1800
            for c in cases:
                c['objects'][2].update(objectX=67,objectY=41)
                c['self'].update(selfX=71,selfY=38);c['objects'][5].update(objectX=71,objectY=38)
                for o in c['objects']:
                    if o['objectKind']==2 and o['objectTeam']==1:o.update(objectX=65,objectY=44)
            m=self.play(n,cases,('defActive','pdReleased','pdVisibleThreat','defAnchor'))[-1]['memory']
            self.assertEqual(m,{'defActive':1,'pdReleased':0,'pdVisibleThreat':1,'defAnchor':29})

    def test_wider_guard_keeps_defense_for_visible_approaching_survivor(self):
        cases=self.cases(tick=1800);cases[-1]['objects'].append(f.obj(1900,kind=2,team=1,x=72,y=11))
        self.assertEqual(self.play('arrive30',cases,('pdReleased',))[-1]['memory']['pdReleased'],1)
        self.assertEqual(self.play('arrive30wide',cases,('pdReleased','pdVisibleThreat'))[-1]['memory'],{'pdReleased':0,'pdVisibleThreat':1})

    def test_roundtrip_blue_and_dense_budget(self):
        from test_jordan_root import final_approach
        from hero_binding import class_id,class_ids
        rows=[]
        for n in VARIANTS[2:]:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for density in (40,160,240):
                    for slot,c in enumerate(class_ids(team)):
                        d=defense_case(slot,count=4) if team==0 else final_approach(team,4,100)
                        if team==1:
                            for i,o in enumerate(o for o in d['objects'] if o['objectKind']==2):o.update(objectId=100+i,objectClass=class_id(0,i))
                            d['self'].update(selfClass=c,selfId=105+slot)
                            own=f.obj(105+slot,kind=2,team=1,x=d['self']['selfX'],y=d['self']['selfY'],hp=d['self']['selfHp']);own['objectClass']=c;d['objects'].append(own)
                        d['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(d['objects']))]
                        new=self.play(n,[d]);rows+=new
                        if team==1:self.assertEqual(new[0]['actions'],self.play('pressure_parent',[d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),'scope':'Actual team classes40/160/240mixedobjects and allblue action parity; inherited extreme hostile-wave limit unchanged.'})

if __name__=='__main__':unittest.main()

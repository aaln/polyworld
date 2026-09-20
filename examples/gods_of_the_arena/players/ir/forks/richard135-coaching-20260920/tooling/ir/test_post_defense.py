"""Execute post-defense transitions in the actual BASIC VM."""
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from test_jordan_root import final_approach
from hero_binding import class_id, class_ids
from g002_coordination import make, VARIANTS, STUDY
from policy_ir import compile_policy, extract, write


class PostDefenseTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def cases(self, slot=2, final_tick=400, threat=None):
        first=defense_case(slot,count=4)
        quiet=defense_case(slot,count=0)
        quiet['self']['worldTick']=final_tick
        for case in (first,quiet):
            case['self']['selfHp']=400
            case['objects'][3+slot]['objectHp']=400
        if threat is not None: quiet['objects'].append(threat)
        return [first,quiet]

    def test_quiet_casters_release_and_tank_covers_then_releases(self):
        for slot in (0,2,3):
            old=self.play('pressure_parent',self.cases(slot),('defActive',))[-1]
            self.assertEqual(old['memory']['defActive'],1)
            for name,threshold in [('release10',1080 if slot==0 else 240),('release20',1440 if slot==0 else 480),('release_all10',240)]:
                before=self.play(name,self.cases(slot,100+threshold-1),('defActive','pdReleased'))[-1]
                after=self.play(name,self.cases(slot,100+threshold),('defActive','pdReleased','defUntil'))[-1]
                self.assertEqual(before['memory'],{'defActive':1,'pdReleased':0})
                self.assertEqual(after['memory'],{'defActive':0,'pdReleased':1,'defUntil':0})
                self.assertTrue(any(a['command']=='walkTo' for a in after['actions']))
        self.assertEqual(self.play('rally',self.cases(2,1800),('defActive','pdReleased'))[-1]['memory'],{'defActive':1,'pdReleased':0})

    def test_visible_home_threat_keeps_defense_even_without_selected_target(self):
        for kind,x,y in [(2,84,11),(3,92,11)]:
            threat=f.obj(1800,kind=kind,team=1,x=x,y=y)
            for name in VARIANTS[3:]:
                row=self.play(name,self.cases(2,1800,threat),('defActive','pdReleased','pdVisibleThreat','bestId'))[-1]
                self.assertEqual(row['memory'],{'defActive':1,'pdReleased':0,'pdVisibleThreat':1,'bestId':0})
        for alteration in ('dead','friendly','far'):
            e=f.obj(1800,kind=2,team=1,x=84,y=11)
            if alteration=='dead':e.update(objectHp=0,objectAlive=0)
            if alteration=='friendly':e['objectTeam']=0
            if alteration=='far':e.update(objectX=60,objectY=50)
            self.assertEqual(self.play('release10',self.cases(2,1800,e),('pdReleased',))[-1]['memory']['pdReleased'],1)

    def test_rally_roles_get_distinct_walk_destinations(self):
        goals=[]
        for slot in (0,2,3):
            row=self.play('rally',self.cases(slot,101),('defActive','defGoalX','defGoalY'))[-1]
            self.assertEqual(row['memory']['defActive'],1)
            goals.append(tuple(a['arguments'] for a in row['actions'] if a['command']=='walkTo')[-1])
        self.assertEqual(len({tuple(g) for g in goals}),3)

    def test_destination_refresh_does_not_extend_attacker_lease(self):
        first=defense_case(1,count=4)
        second=defense_case(1,count=1);second['self']['worldTick']=101
        second['objects'][2].update(objectX=89,objectY=21)
        old=self.play('pressure_parent',[first,second],('defUntil','defPointX','defPointY'))
        new=self.play('rally',[first,second],('defUntil','defPointX','defPointY'))
        self.assertEqual(old[-1]['memory']['defUntil'],new[-1]['memory']['defUntil'])
        self.assertEqual(new[0]['memory']['defUntil'],new[-1]['memory']['defUntil'])
        self.assertNotEqual((old[-1]['memory']['defPointX'],old[-1]['memory']['defPointY']),
                            (new[-1]['memory']['defPointX'],new[-1]['memory']['defPointY']))

    def test_roundtrip_dense_actual_classes_and_blue_parity(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for density in (40,160,240):
                    for slot,c in enumerate(class_ids(team)):
                        d=defense_case(slot,count=4) if team==0 else final_approach(team,4,100)
                        if team==1:
                            for i,o in enumerate(o for o in d['objects'] if o['objectKind']==2):
                                o.update(objectId=100+i,objectClass=class_id(0,i))
                            d['self'].update(selfClass=c,selfId=105+slot)
                            own=f.obj(105+slot,kind=2,team=1,x=d['self']['selfX'],y=d['self']['selfY'],hp=d['self']['selfHp'])
                            own['objectClass']=c;d['objects'].append(own)
                        d['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(d['objects']))]
                        own=next(o for o in d['objects'] if o['objectId']==d['self']['selfId'])
                        self.assertEqual((own['objectClass'],own['objectTeam']),(c,team))
                        new=self.play(name,[d]);rows+=new
                        if team==1:self.assertEqual(new[0]['actions'],self.play('pressure_parent',[d])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),'scope':'Actual ten hero/team bindings with40/160/240mixed objects; all blue actions exact. Extreme hostile-wave inherited limit not repaired.'})


if __name__=='__main__':unittest.main()

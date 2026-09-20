import unittest
import subprocess
from copy import deepcopy
import test_policy_ir as f
import test_rush_unblock as u
from test_red_pressure import survivor_case
from test_jordan_root import final_approach
from victory_counterpush import make, STUDY, VARIANTS
from policy_ir import compile_policy,extract,write


def victory_case(tick=101,hero=2):
    c=survivor_case(tick,hero)
    c['self'].update(selfX=94,selfY=25)
    c['objects']=c['objects'][:4]
    c['objects'] += [f.obj(100+i,kind=2,team=0,x=93+i%2,y=25+i//2,hp=400) for i in range(4)]
    c['objects'] += [f.obj(105+i,kind=2,team=1,x=91,y=26+i,hp=-20,alive=0) for i in range(2)]
    return c


class VictoryTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_victory_releases_and_fresh_rush_recalls(self):
        for name in VARIANTS[2:]:
            for hero in range(5):
                a=survivor_case(100,hero);b=victory_case(hero=hero);c=survivor_case(102,hero)
                c['objects']=deepcopy(a['objects'])
                rows=self.play(name,[a,b,c])
                expect=1 if name=='victory_four' and hero==0 else 0
                self.assertEqual([r['memory']['defActive'] for r in rows],[1,expect,1])

    def test_missing_enemies_are_not_victory_and_live_threat_blocks_release(self):
        for mode in ['missing','one_dead','living_enemy','few_allies']:
            a=survivor_case(100,2);b=victory_case()
            if mode=='missing':b['objects']=b['objects'][:-2]
            if mode=='one_dead':b['objects']=b['objects'][:-1]
            if mode=='living_enemy':b['objects'].append(f.obj(109,kind=2,team=1,x=100,y=25,hp=200))
            if mode=='few_allies':b['objects']=[o for o in b['objects'] if o['objectId'] not in [100,101]]
            self.assertEqual(self.play('victory_all',[a,b])[-1]['memory']['defActive'],1,mode)

    def test_blue_parity_and_dense_runtime(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for size in (40,80,160,240):
                    c=final_approach(team,4,100)
                    c['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(size-len(c['objects']))]
                    cases=[c|{'self':c['self']|{'selfClass':k}} for k in range(team*5,team*5+5)]
                    rr=self.play(name,cases);rows+=rr
                    if team==1:self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('deployed',cases)])
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows)})

    def test_dense_hostile_matches_inherited_limit(self):
        rows=[];inherited=[]
        for name in VARIANTS[2:]:
            for hero in range(5):
                for near in (False,True):
                    first=final_approach(0,4,100);dense=final_approach(0,0,101)
                    dense['objects'] += [f.obj(3000+i,team=1,x=102+i%3 if near else 84+i%5,y=11) for i in range(238)]
                    cases=[c|{'self':c['self']|{'selfClass':hero,'selfX':105,'selfY':11}} for c in (first,dense)]
                    try:rows+=self.play(name,cases)
                    except subprocess.CalledProcessError as error:
                        with self.assertRaises(subprocess.CalledProcessError) as previous:
                            self.play('deployed',cases)
                        self.assertIn('instruction limit exceeded',error.stderr)
                        self.assertIn('instruction limit exceeded',previous.exception.stderr)
                        inherited.append({'candidate':name,'hero':hero,'near':near})
        write(STUDY/'dense-hostile.json',{'no_new_failure':True,'inherited_failures':inherited,
              'successful_decisions':len(rows),'max_successful_instructions':max(r['instructions'] for r in rows),
              'scope':'Shared pathological near-240 hostile fixture still exceeds the deployed and candidate instruction budgets. This test checks regression, not absolute runtime safety.'})


if __name__=='__main__':unittest.main()

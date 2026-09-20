import unittest
import test_policy_ir as f
from test_rush_unblock import UnblockTests
from test_mixed_backdoor import intruder
from test_mixed_backdoor_assigned import remote_case
from mixed_isolated import make,VARIANTS
from policy_ir import compile_policy,extract


class IsolatedTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_full_rush_retains_parent_actions(self):
        for team in (0,1):
            for remote in (False,True):
                case=intruder(team,remote=remote)
                enemy=case['objects'][-1]
                case['objects'] += [enemy|{'objectId':enemy['objectId']+i} for i in range(1,5)]
                for cls in range(team*5,team*5+5):
                    frame=case|{'self':case['self']|{'selfClass':cls}}
                    parent=self.play('fused_parent',[frame])[0]
                    for name in VARIANTS[2:]:
                        row=self.play(name,[frame])[0]
                        self.assertEqual(row['actions'],parent['actions'],(name,team,remote,cls))
                        self.assertEqual(row['memory']['bestId'],parent['memory']['bestId'])

    def test_visible_lone_guard_attacker_recalls_remote_backup(self):
        frames=[remote_case(t) for t in (100,101,150,195,196)]
        rows=self.play('isolated_assigned4',frames)
        self.assertEqual([r['memory']['defActive'] for r in rows],[0,0,0,0,1])
        self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[101] for a in rows[-1]['actions']))
        helping=[remote_case(t,101) for t in (100,101,150,195,196)]
        self.assertTrue(all(r['memory']['defActive']==0 for r in self.play('isolated_assigned4',helping)))

    def test_isolation_limit_and_nearby_scope(self):
        case=intruder(remote=True)
        self.assertEqual(self.play('isolated_all1',[case])[0]['memory']['defActive'],1)
        self.assertEqual(self.play('isolated_near1',[case])[0]['memory']['defActive'],0)
        case['objects'].append(case['objects'][-1]|{'objectId':102})
        self.assertEqual(self.play('isolated_all1',[case])[0]['memory']['defActive'],0)
        self.assertEqual(self.play('isolated_all2',[case])[0]['memory']['defActive'],1)

    def test_dense_budget_and_roundtrip(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for n in (40,80,160,240):
                    case=intruder(team,remote=True)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    rows+=self.play(name,[case|{'self':case['self']|{'selfClass':c}} for c in range(10)])
        print('Isolated-defense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

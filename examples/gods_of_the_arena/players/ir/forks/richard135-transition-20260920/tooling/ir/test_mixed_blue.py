import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_mixed_backdoor import intruder
from test_mixed_backdoor_assigned import remote_case
from mixed_blue import make
from mixed_isolated import make as isolated
from policy_ir import compile_policy,extract


class BlueTests(unittest.TestCase):
    factory=staticmethod(lambda name:isolated(name) if name=='isolated_assigned4' else make(name))
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_lineup_action_parity_and_dense_budget(self):
        p=make('blue_assigned');self.assertEqual(extract(compile_policy(p),p),p)
        rows=[]
        for team in (0,1):
            reference='fused_parent' if team==0 else 'isolated_assigned4'
            for remote in (False,True):
                for n in (40,80,160,240):
                    case=intruder(team,remote=remote)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    for cls in range(team*5,team*5+5):
                        frame=case|{'self':case['self']|{'selfClass':cls}}
                        row=self.play('blue_assigned',[frame])[0];parent=self.play(reference,[frame])[0]
                        self.assertEqual(row['actions'],parent['actions'],(team,remote,n,cls))
                        rows.append(row)
        print('Blue decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))

    def test_remote_blue_backup_and_no_blind_trust(self):
        frames=[remote_case(t) for t in (100,101,150,195,196)]
        rows=self.play('blue_assigned',frames)
        self.assertEqual([r['memory']['defActive'] for r in rows],[0,0,0,0,1])
        frames=[remote_case(t,101) for t in (100,101,150,195,196)]
        self.assertTrue(all(r['memory']['defActive']==0 for r in self.play('blue_assigned',frames)))


if __name__=='__main__':unittest.main()

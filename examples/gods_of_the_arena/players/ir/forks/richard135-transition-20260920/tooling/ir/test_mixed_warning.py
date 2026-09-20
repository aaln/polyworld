import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_mixed_backdoor_assigned import remote_case
from mixed_warning import make
from policy_ir import compile_policy,extract


class WarningTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_brief_target_switch_does_not_restart_backup_forever(self):
        frames=[remote_case(t) for t in (100,101,197,198)]
        self.assertEqual([r['memory']['defActive'] for r in self.play('blue_assigned',frames)],[0,0,0,0])
        self.assertEqual([r['memory']['defActive'] for r in self.play('blue_warning20',frames)],[0,0,1,1])

    def test_no_recall_from_memory_without_current_attack(self):
        first=remote_case(100);later=remote_case(197);later['objects'][-2]['objectTarget']=0
        self.assertEqual([r['memory']['defActive'] for r in self.play('blue_warning20',[first,later])],[0,0])
        frames=[remote_case(t) for t in (100,101,700)]
        self.assertTrue(all(r['memory']['defActive']==0 for r in self.play('blue_warning20',frames)))

    def test_parity_and_dense_budget(self):
        p=make('blue_warning20');self.assertEqual(extract(compile_policy(p),p),p)
        rows=[]
        for n in (40,80,160,240):
            case=remote_case(100)
            case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
            rows+=self.play('blue_warning20',[case|{'self':case['self']|{'selfClass':c}} for c in range(5,10)])
        print('Warning decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

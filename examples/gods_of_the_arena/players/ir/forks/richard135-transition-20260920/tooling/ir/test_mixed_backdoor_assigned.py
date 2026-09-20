import unittest
import test_policy_ir as f
from test_rush_unblock import UnblockTests
from test_mixed_backdoor import intruder
from mixed_backdoor_assigned import make
from policy_ir import compile_policy,extract


def remote_case(tick,helper_target=0):
    p=intruder(tick=tick,remote=True);p['self']['selfId']=107
    ally=f.obj(106,kind=2,team=1,x=8,y=107,hp=352);ally['objectTarget']=helper_target
    p['objects'].append(ally);return p


class AssignedTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_nearby_ranger_handles_visible_guard_attacker(self):
        for team in (0,1):
            row=self.play('assigned_4',[intruder(team)])[0]
            self.assertEqual(row['memory']['defActive'],1)
            self.assertEqual(row['memory']['bestId'],101 if team else 106)

    def test_far_hero_stays_on_offense_when_ally_actually_engages(self):
        cases=[remote_case(t,101) for t in (100,101,150,196,240)]
        self.assertTrue(all(r['memory']['defActive']==0 for r in self.play('assigned_4',cases)))

    def test_ignored_threat_gets_delayed_backup_not_blind_trust(self):
        rows=self.play('assigned_4',[remote_case(t) for t in (100,101,150,195,196)])
        self.assertEqual([r['memory']['defActive'] for r in rows],[0,0,0,0,1])
        self.assertEqual(rows[-1]['memory']['bestId'],101)

    def test_reset_and_dense_budget(self):
        rows=[]
        for name in ('assigned_4','assigned_8'):
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for n in (40,80,160,240):
                for team in (0,1):
                    case=intruder(team,remote=True)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    rows+=self.play(name,[case|{'self':case['self']|{'selfClass':c}} for c in range(10)])
        print('Assigned-defense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))
        row=self.play('assigned_4',[remote_case(100),remote_case(1)])[1]
        self.assertEqual(row['memory']['defActive'],0)


if __name__=='__main__':unittest.main()

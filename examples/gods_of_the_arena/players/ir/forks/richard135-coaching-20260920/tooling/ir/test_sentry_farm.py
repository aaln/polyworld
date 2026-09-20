import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_jordan_root import final_approach
from sentry_farm import make,VARIANTS
from policy_ir import compile_policy,extract


class SentryFarmTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_quiet_sentry_farms_but_hero_threat_blocks_fallback(self):
        first=final_approach(0,4,100)
        first['self'].update(selfClass=0,selfX=105,selfY=11)
        quiet=final_approach(0,0,101)
        quiet['self'].update(selfClass=0,selfX=105,selfY=11)
        quiet['objects'].append(f.obj(1000,kind=3,team=1,x=84,y=11,hp=60))
        self.assertEqual(self.play('core_parent',[first,quiet])[-1]['memory']['bestId'],0)
        unsafe=quiet|{'objects':quiet['objects'][:2]+[f.obj(106,kind=2,team=1,x=95,y=35,hp=500)]+quiet['objects'][2:]}
        for name in VARIANTS[3:]:
            self.assertEqual(self.play(name,[first,quiet])[-1]['memory']['bestId'],1000)
            self.assertEqual(self.play(name,[first,unsafe])[-1]['memory']['bestId'],0)
            attacker=[c|{'self':c['self']|{'selfClass':1}} for c in (first,quiet)]
            self.assertEqual(self.play(name,attacker)[-1]['memory']['bestId'],0)

    def test_dense_quiet_and_active_budget_blue_parity(self):
        rows=[]
        for name in VARIANTS[3:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for size in (64,160,240):
                    for cls in range(team*5,team*5+5):
                        first=final_approach(team,4,100)
                        quiet=final_approach(team,0,101)
                        quiet['objects'] += [f.obj(3000+i,team=1-team,x=84+i%5 if team==0 else 32-i%5,
                            y=11 if team==0 else 105) for i in range(size-len(quiet['objects']))]
                        cases=[c|{'self':c['self']|{'selfClass':cls,'selfX':105 if team==0 else 11,'selfY':11 if team==0 else 105}} for c in (first,quiet)]
                        rr=self.play(name,cases);rows+=rr
                        if team==1:self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('core_parent',cases)])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        print('Farm dense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

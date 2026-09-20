import unittest
from policy_ir import compile_policy, extract
import test_policy_ir as f
from test_rush_defense import scene
from test_rush_unblock import UnblockTests, core_scene
from rush_unblock_refine import make, VARIANTS


class RefinedTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = UnblockTests.play

    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    def test_only_nearby_heroes_respond_to_core_emergency(self):
        for team in (0, 1):
            near = core_scene(team)
            far = core_scene(team); far['self'].update(selfX=60, selfY=60)
            for name in ('near_core', 'near_release_20', 'near_release_60'):
                self.assertEqual(self.play(name,[near])[0]['memory']['defActive'],1)
                self.assertEqual(self.play(name,[far])[0]['memory']['defActive'],0)
            harmless = core_scene(team)
            for o in harmless['objects'][4:]:
                o.update(objectX=95 if team==0 else 21,objectY=11 if team==0 else 105,objectTarget=0)
            self.assertEqual(self.play('near_core',[harmless])[0]['memory']['defActive'],0)

    def test_quiet_only_releases_and_does_not_recall_for_single_creep(self):
        for name,wait in (('quiet_20',480),('quiet_30',720),('quiet_60',1440)):
            a=scene(worldTick=100); b=scene(count=0,worldTick=100+wait)
            for case in (a,b): case['self']['selfClass']=2
            self.assertEqual([r['memory']['defActive'] for r in self.play(name,[a,b])],[1,0])
            self.assertEqual(self.play(name,[core_scene()])[0]['memory']['defActive'],0)

    def test_parity_budget_and_inactive_items(self):
        rows=[]
        for name in VARIANTS:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                empty=scene(team,count=0,selfGold=150)
                self.assertEqual(self.play(name,[empty])[0]['actions'],self.play('deployed_parent',[empty])[0]['actions'])
                for density in (40,80,160):
                    case=core_scene(team)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(case['objects']))]
                    rows+=self.play(name,[case|{'self':case['self']|{'selfClass':c}} for c in range(10)])
        print('Refinement decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

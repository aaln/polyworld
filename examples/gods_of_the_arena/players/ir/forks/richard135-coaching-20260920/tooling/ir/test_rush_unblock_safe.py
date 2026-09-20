import unittest
import test_policy_ir as f
from policy_ir import compile_policy,extract
from test_rush_defense import scene
from test_rush_unblock import UnblockTests,core_scene
from rush_unblock_safe import make


class FusedTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_stale_sentry_changes_target_and_rally_to_visible_core_wave(self):
        for team in (0,1):
            start=scene(team,worldTick=100)
            end=core_scene(team);end['self']['worldTick']=101
            for case in (start,end):case['self']['selfClass']=2 if team==0 else 7
            old=self.play('deployed_parent',[start,end])[-1]
            new=self.play('fused_core',[start,end])[-1]
            self.assertNotIn(old['memory']['bestId'],range(2149,2155))
            self.assertIn(new['memory']['bestId'],range(2149,2155))
            self.assertNotEqual(old['memory']['defPointX'],new['memory']['defPointX'])
            self.assertTrue(any(a['command']=='attackTarget' for a in new['actions']))

    def test_inactive_and_far_behavior_preserved(self):
        for team in (0,1):
            case=core_scene(team)
            self.assertEqual(self.play('fused_core',[case])[0]['actions'],self.play('spread',[case])[0]['actions'])
            first=scene(team,worldTick=100);case['self'].update(worldTick=101,selfX=60,selfY=60)
            self.assertEqual(self.play('fused_core',[first,case])[-1]['actions'],self.play('spread',[first,case])[-1]['actions'])

    def test_parity_and_240_object_dense_budget(self):
        p=make('fused_core');self.assertEqual(extract(compile_policy(p),p),p)
        rows=[]
        for team in (0,1):
            for n in (40,80,160,192,240):
                for c in range(10):
                    a=scene(team,worldTick=100);a['self']['selfClass']=c
                    b=core_scene(team);b['self'].update(worldTick=101,selfClass=c,selfGold=150)
                    b['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(b['objects']))]
                    rows+=self.play('fused_core',[a,b])
        print('Fused decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

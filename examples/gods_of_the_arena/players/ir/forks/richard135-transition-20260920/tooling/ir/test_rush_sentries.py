import tempfile
import unittest
from pathlib import Path

import test_policy_ir as f
from test_rush_defense import scene
from policy_ir import compile_policy, extract
from rush_sentries import make, VARIANTS


class SentryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases):
        with tempfile.TemporaryDirectory() as directory:
            p = make(name)
            source = Path(directory)/'policy.bas'
            source.write_text(compile_policy(p))
            memory = ['defActive','defUntil','bestId']
            if name != 'defense_parent': memory.append('defSentry')
            return self.run_vm(source, cases, memory)

    def test_role_split_memory_expiry_and_new_episode_reset(self):
        for team, classes in [(0,range(5,10)),(1,range(5))]:
            for c in classes:
                cases = [scene(team,worldTick=100),scene(team,count=0,worldTick=2000),
                         scene(team,count=0,worldTick=3700),scene(team,count=0,worldTick=1)]
                for case in cases: case['self']['selfClass'] = c
                rows = self.play('three', cases)
                sentry = c in (0,2,3,5,7,8)
                self.assertEqual([r['memory']['defActive'] for r in rows], [1,int(sentry),0,0])
                self.assertEqual(rows[0]['memory']['defSentry'], int(sentry))
                self.assertEqual(rows[0]['memory']['defUntil'], 3700 if sentry else 100+(1200 if team else 1440))

    def test_no_unseen_rush_prediction_or_inactive_action_changes(self):
        for team in (0,1):
            cases = [scene(team,count=0,worldTick=1,selfGold=150),scene(team,count=2,worldTick=2)]
            new,old = self.play('three',cases),self.play('defense_parent',cases)
            self.assertEqual([r['actions'] for r in new],[r['actions'] for r in old])
            self.assertTrue(all(r['memory']['defActive']==0 for r in new))

    def test_roundtrip_and_runtime_boundaries(self):
        rows=[]
        for name in VARIANTS:
            p=make(name)
            self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for n in (39,40,41,79,80,81,160):
                    case=scene(team,selfGold=150)
                    case['objects'] += [f.obj(1000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    rows += self.play(name,[case | {'self':case['self'] | {'selfClass':c}} for c in range(10)])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        print('Sentry VM decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__ == '__main__': unittest.main()

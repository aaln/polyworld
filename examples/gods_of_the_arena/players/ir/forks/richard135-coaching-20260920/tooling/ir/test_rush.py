import tempfile
from pathlib import Path
import unittest
import test_policy_ir as f
from policy_ir import compile_policy, extract
from rush_candidates import make, VARIANTS


class RushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm = f.RealVmTests.run_vm

    def run_policy(self, name, cases):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'policy.bas'; path.write_text(compile_policy(make(name)))
            return self.run_vm(path, cases, ['bestId', 'rushStage'])

    def test_shared_target_ignores_barracks_wrong_lane_and_protected_fort(self):
        targets = [f.obj(2, kind=1, team=1, alive=0), f.obj(25, kind=4, team=1, x=95, y=104),
                   f.obj(26, kind=4, team=1, alive=0), f.obj(19, kind=4, team=1),
                   f.obj(44, kind=5, team=1), f.obj(109, kind=2, team=1)]
        rows = self.run_policy('outer', [f.fixture(targets, selfId=100+s, selfClass=s) for s in range(5)])
        self.assertEqual([r['memory']['bestId'] for r in rows], [25] * 5)

    def test_exposed_fort_overrides_everything_on_both_sides(self):
        for team in [0, 1]:
            enemies = [f.obj(2-team, kind=1, team=1-team), f.obj(25 if team==0 else 10, kind=4, team=1-team),
                       f.obj(101, kind=2, team=1-team,x=21)]
            row = self.run_policy('clear', [f.fixture(enemies, selfTeam=team)])[0]
            self.assertEqual(row['memory']['bestId'], 2-team)

    def test_identical_route_all_classes_and_mirrored_teams(self):
        for team in [0, 1]:
            x,y=(105,11) if team==0 else (11,105)
            rows=self.run_policy('outer',[f.fixture(selfId=100+s+5*team,selfClass=s+5*team,selfTeam=team,selfX=x,selfY=y) for s in range(5)])
            expected=[108,44] if team==0 else [8,72]
            for r in rows:
                self.assertEqual([a['arguments'] for a in r['actions'] if a['command']=='walkTo'],[expected])

    def test_dense_observations_and_roundtrip(self):
        objects=[f.obj(1000+i,team=i%2,x=i%116,y=(i*7)%116) for i in range(160)]
        for name in VARIANTS:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for r in self.run_policy(name,[f.fixture(objects,selfClass=c,selfGold=150) for c in range(10)]):
                self.assertLessEqual(r['work'],50000)
                self.assertLessEqual(r['instructions'],20000)


if __name__ == '__main__': unittest.main()

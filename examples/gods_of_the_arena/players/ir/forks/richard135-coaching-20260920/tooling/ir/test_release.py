from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from policy_ir import compile_policy, extract
from release_candidates import make, rebase


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def test_rebase_keeps_deployed_bytes_and_round_trip(self):
        for filename in ['cadence_all.evaluated.ir.json', 'waveguard_xp.evaluated.ir.json']:
            p = rebase(filename)
            self.assertEqual(extract(compile_policy(p), p), p)
        for name in ['footprint', 'siege', 'short_step', 'wave_spacing']:
            p = make(name)
            self.assertEqual(extract(compile_policy(p), p), p)

    def test_exposed_barracks_and_towers_use_edge_distance(self):
        hero = f.obj(100, team=1, kind=2, x=23)
        for kind in [4, 5]:
            structure = f.obj(42, team=1, kind=kind, x=24)
            cases = [f.fixture([hero, structure]),
                     f.fixture([hero, structure | {'objectAlive': 0}]),
                     f.fixture([hero, structure | {'objectHp': 0}])]
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / 'policy.bas'
                path.write_text(compile_policy(make('footprint')))
                rows = self.run_vm(path, cases, ['bestId'])
                self.assertEqual([r['memory']['bestId'] for r in rows], [42, 100, 100])


if __name__ == '__main__':
    unittest.main()

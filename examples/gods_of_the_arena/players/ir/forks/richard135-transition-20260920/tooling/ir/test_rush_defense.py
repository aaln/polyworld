"""Real VM evidence for shared-vision defense and its absence-of-threat branch."""
import tempfile
import unittest
from pathlib import Path

import test_policy_ir as f
from policy_ir import compile_policy, extract, read
from release_workspace import RUN
from rush_defense import make, VARIANTS, STUDY


def scene(team=0, count=5, **changes):
    objects = [f.obj(1, kind=1, team=0, x=105, y=11, hp=400, alive=0),
               f.obj(2, kind=1, team=1, x=11, y=105, hp=400, alive=0),
               f.obj(16, kind=4, team=0, x=67, y=43, hp=950),
               f.obj(19, kind=4, team=1, x=43, y=67, hp=950)]
    for i in range(count):
        enemy = f.obj(105+i, kind=2, team=1-team,
                      x=63+i%2 if team == 0 else 47-i%2,
                      y=46+i%2 if team == 0 else 64-i%2)
        enemy['objectTarget'] = 16 if team == 0 else 19
        objects.append(enemy)
    return f.fixture(objects, selfTeam=team, selfClass=5 if team == 0 else 0,
                     selfId=100 if team == 0 else 105,
                     selfX=70 if team == 0 else 40, selfY=70 if team == 0 else 40,
                     **changes)


class RushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, cases, name='rally', ir=None):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)/'policy.bas'
            src.write_text(compile_policy(ir or make(name)))
            memory = ['bestId'] if ir and not ir['skill']['observe']['operator'].startswith('rush_defense') else [
                'defActive', 'defUntil', 'bestId', 'defPointX', 'defPointY', 'defCount']
            return self.run_vm(src, cases, memory)

    def test_remote_rush_overrides_split_push_on_both_colors(self):
        for team in (0, 1):
            row = self.play([scene(team)])[0]
            self.assertEqual(row['memory']['defActive'], 1)
            self.assertEqual(row['memory']['bestId'], 0)
            moves = [a for a in row['actions'] if a['command'] == 'walkTo']
            self.assertEqual(moves[-1]['arguments'], [row['memory']['defPointX'], row['memory']['defPointY']])
            self.assertGreater(row['memory']['defPointX'], 67) if team == 0 else self.assertLess(row['memory']['defPointX'], 43)

    def test_requires_group_and_standing_friendly_anchor(self):
        cases = [scene(count=2), scene(count=3)]
        gone = scene(); gone['objects'][2]['objectHp'] = -1
        cases.append(gone)
        # A protected but standing tower remains a valid defense anchor.
        protected = scene(); protected['objects'][2]['objectAlive'] = 0
        cases.append(protected)
        rows = [self.play([case])[0] for case in cases]
        self.assertEqual([r['memory']['defActive'] for r in rows], [0, 1, 0, 1])

    def test_memory_covers_visibility_gap_but_expires_and_resets(self):
        first = scene(worldTick=100)
        gap = scene(count=0, worldTick=101)
        rows = self.play([first, gap])
        self.assertEqual([r['memory']['defActive'] for r in rows], [1, 1])
        rows = self.play([first, scene(count=0, worldTick=103)])
        self.assertEqual(rows[-1]['memory']['defActive'], 0)
        short = make('rally'); short['skill']['observe']['parameters']['hold_ticks'] = 120
        rows = self.play([first] + [scene(count=0, worldTick=t) for t in range(101, 221)], ir=short)
        self.assertEqual(rows[-2]['memory']['defActive'], 1)
        self.assertEqual(rows[-1]['memory']['defActive'], 0)

    def test_focus_config_switches_hero_vs_creep_cover(self):
        case = scene(); case['self'].update(selfX=67, selfY=46)
        case['objects'].append(f.obj(1000, kind=3, team=1, x=65, y=46))
        hero = self.play([case])[0]
        creep = self.play([case], 'clear_wave')[0]
        self.assertIn(hero['memory']['bestId'], range(105, 110))
        self.assertEqual(creep['memory']['bestId'], 1000)

    def test_inactive_commands_match_parent_and_gear_is_preserved(self):
        parent = read(RUN/'coached-lanes/r5-asymmetric/hosted/blue_damage/team-feedback/policy.ir.json')
        cases = [f.fixture([f.obj(1000, team=1-c//5, x=23)], selfClass=c,
                           selfTeam=c//5, selfGold=150, worldTick=1) for c in range(10)]
        old = self.play(cases, ir=parent)
        new = self.play(cases)
        self.assertEqual([r['actions'] for r in old], [r['actions'] for r in new])
        for team in (0, 1):
            row = self.play([scene(team, selfGold=150)])[0]
            self.assertTrue(any(a['command'] == 'buyItem' and a['arguments'][0] > 4 for a in row['actions']))

    def test_parity_and_dense_runtime_budget(self):
        rows = []
        for name in VARIANTS:
            ir = make(name)
            self.assertEqual(extract(compile_policy(ir), ir), ir)
            for active in (False, True):
                for density in (39, 40, 41, 64, 79, 80, 81, 160):
                    case = scene(count=5 if active else 0, selfGold=150)
                    case['objects'] += [f.obj(1000+i, team=i%2, x=i%116, y=i*7%116) for i in range(density-len(case['objects']))]
                    rows.extend(self.play([case | {'self': case['self'] | {'selfClass': c}} for c in range(10)], name))
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        print('Rush defense VM maxima:', max(r['instructions'] for r in rows), max(r['work'] for r in rows))


if __name__ == '__main__':
    unittest.main()

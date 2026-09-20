"""Replay-derived core defense and rally separation, executed in the BASIC VM."""
import tempfile
import unittest
from pathlib import Path

import test_policy_ir as f
from test_rush_defense import scene
from policy_ir import compile_policy, extract
from rush_unblock import make, VARIANTS


def core_scene(team=0):
    case = scene(team, count=0, worldTick=17280)
    case['self'].update(selfX=90 if team == 0 else 26,
                        selfY=5 if team == 0 else 111,
                        selfClass=2 if team == 0 else 7)
    for i in range(6):
        enemy = f.obj(2149+i, kind=3, team=1-team,
                      x=102+i%2 if team == 0 else 14-i%2,
                      y=13 if team == 0 else 103, hp=60)
        enemy['objectTarget'] = 1 if team == 0 else 2
        case['objects'].append(enemy)
    return case


class UnblockTests(unittest.TestCase):
    factory = staticmethod(make)
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases, memory=('bestId', 'defActive', 'defPointX', 'defPointY')):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'policy.bas'
            source.write_text(compile_policy(self.factory(name)))
            return self.run_vm(source, cases, memory)

    def test_redirects_remote_sentry_to_visible_core_creeps_on_both_colors(self):
        for team in (0, 1):
            case = core_scene(team)
            parent = self.play('deployed_parent', [case])[0]
            self.assertNotIn(parent['memory']['bestId'], range(2149, 2155))
            for name in ('core_wave', 'combined', 'wide_combined'):
                row = self.play(name, [case])[0]
                self.assertEqual(row['memory']['defActive'], 1)
                self.assertIn(row['memory']['bestId'], range(2149, 2155))
                self.assertTrue(any(a['command'] == 'attackTarget' and
                                    a['arguments'][0] in range(2149, 2155) for a in row['actions']))

    def test_target_priority_and_no_invented_threats(self):
        for team in (0, 1):
            case = core_scene(team)
            for enemy in case['objects'][4:]:
                enemy['objectTarget'] = 0
            case['objects'][-1]['objectTarget'] = 1 if team == 0 else 2
            case['objects'][-1]['objectHp'] = 900
            row = self.play('combined', [case])[0]
            self.assertEqual(row['memory']['bestId'], 2154)
            for alteration in ('absent', 'dead', 'friendly', 'far'):
                case = core_scene(team)
                if alteration == 'absent': case['objects'] = case['objects'][:4]
                for enemy in case['objects'][4:]:
                    if alteration == 'dead': enemy.update(objectAlive=0, objectHp=0)
                    if alteration == 'friendly': enemy['objectTeam'] = team
                    if alteration == 'far': enemy.update(objectX=60, objectY=60)
                row = self.play('combined', [case])[0]
                self.assertEqual(row['memory']['defActive'], 0, alteration)

    def test_distinct_rally_destinations_and_terrain_fallback(self):
        for team, classes in ((0, range(5)), (1, range(5, 10))):
            moves = []
            for hero_class in classes:
                case = scene(team); case['self']['selfClass'] = hero_class
                row = self.play('combined', [case])[0]
                goal = [a['arguments'] for a in row['actions'] if a['command'] == 'walkTo'][-1]
                moves.append(tuple(goal))
                case['blocked'] = [goal]
                fallback = self.play('combined', [case])[0]
                other = [a['arguments'] for a in fallback['actions'] if a['command'] == 'walkTo'][-1]
                self.assertNotEqual(goal, other)
            self.assertEqual(len(set(moves)), 5)

    def test_inactive_commands_and_item_purchases_preserved(self):
        for team in (0, 1):
            cases = [scene(team, count=0, worldTick=1, selfGold=150)]
            parent = self.play('deployed_parent', cases)
            for name in VARIANTS[1:]:
                new = self.play(name, cases)
                self.assertEqual([r['actions'] for r in parent], [r['actions'] for r in new])
                self.assertTrue(any(a['command'] == 'buyItem' and a['arguments'][0] > 4
                                    for a in new[0]['actions']))

    def test_release_requires_quiet_and_fresh_core_wave_reactivates(self):
        for team in (0, 1):
            for name, wait in (('release_20', 480), ('release_30', 720), ('release_60', 1440)):
                first = scene(team, worldTick=100)
                first['self']['selfClass'] = 2 if team == 0 else 7
                before = scene(team, count=0, worldTick=100+wait-1)
                after = scene(team, count=0, worldTick=100+wait)
                for case in (before, after): case['self']['selfClass'] = first['self']['selfClass']
                fresh = core_scene(team); fresh['self']['worldTick'] = 101+wait
                rows = self.play(name, [first, before, after, fresh])
                self.assertEqual([r['memory']['defActive'] for r in rows], [1, 1, 0, 1])
                self.assertTrue(any(a['command']=='attackTarget' for a in rows[-1]['actions']))

    def test_nearby_nonattacking_survivor_does_not_extend_duty(self):
        for targeting, expected in ((False, 0), (True, 1)):
            cases = [scene(worldTick=100)]
            cases[0]['self']['selfClass'] = 2
            last = scene(count=1, worldTick=820)
            last['self']['selfClass'] = 2
            last['objects'][-1].update(objectX=70, objectY=43)
            last['objects'][-1]['objectTarget'] = 16 if targeting else 0
            cases.append(last)
            self.assertEqual(self.play('release_30', cases)[-1]['memory']['defActive'], expected)

    def test_parity_and_dense_budget(self):
        rows = []
        for name in VARIANTS:
            p = make(name)
            self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for density in (39, 40, 41, 79, 80, 81, 160):
                    for active in (False, True):
                        case = core_scene(team) if active else scene(team, count=0, selfGold=150)
                        case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116)
                                            for i in range(density-len(case['objects']))]
                        rows += self.play(name, [case | {'self':case['self'] | {'selfClass':c}}
                                                for c in range(10)])
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        print('Unblock VM decisions', len(rows), 'max instructions/work',
              max(r['instructions'] for r in rows), max(r['work'] for r in rows))


if __name__ == '__main__': unittest.main()

import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_rush_defense import scene
from test_jordan_root import final_approach
from policy_ir import compile_policy, extract
from ranger_guard import make, VARIANTS


def travel(tick, count=0, arrived=False):
    case = scene(1, count=count, worldTick=tick)
    case['self'].update(selfClass=6, selfX=40 if arrived else 90, selfY=70 if arrived else 10)
    return case


class ArrivalTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_remote_recall_completes_before_quiet_release(self):
        # Non-sentry death/resume detection intentionally clears duty on skipped
        # ticks. Feed every decision so this tests quiet release, not respawn.
        cases = [travel(tick, 5 if tick == 100 else 0, arrived=tick >= 600) for tick in range(100, 1083)]
        old = self.play('deployed', cases)
        self.assertEqual(old[581-100]['memory']['defActive'], 0)
        new = self.play('arrival18', cases)
        self.assertEqual([new[t-100]['memory']['defActive'] for t in (100, 101, 581, 600, 1082)], [1, 1, 1, 1, 0])

    def test_red_commands_and_dense_budget(self):
        rows = []
        for n in VARIANTS:
            p = make(n); self.assertEqual(extract(compile_policy(p), p), p)
            for team in (0, 1):
                for size in (40, 160, 240):
                    a = final_approach(team, 4, 100)
                    a['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116) for i in range(size-len(a['objects']))]
                    cases = [a | {'self': a['self'] | {'selfClass': c}} for c in range(team*5, team*5+5)]
                    rr = self.play(n, cases); rows += rr
                    if team == 0:
                        self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('deployed', cases)])
        print('Arrival dense decisions', len(rows), 'max instructions/work', max(r['instructions'] for r in rows), max(r['work'] for r in rows))


if __name__ == '__main__': unittest.main()

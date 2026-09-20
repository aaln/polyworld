import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_victory_counterpush import victory_case
from test_red_pressure import survivor_case
from counterwatch import make


class CounterwatchTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_leave_position_retain_watch_and_recall_single_base_attacker(self):
        for name in ('watch_all','watch_four'):
            for hero in (1,2,3,4):
                a=survivor_case(100,hero);b=victory_case(hero=hero)
                c=victory_case(102,hero);c['objects']=c['objects'][:-2]
                d=victory_case(103,hero);d['objects']=d['objects'][:-2]
                enemy=f.obj(105,kind=2,team=1,x=104,y=15,hp=400);enemy['objectTarget']=1
                d['objects'].append(enemy)
                rows=self.play(name,[a,b,c,d],('bestId','defActive','defUntil','cwPush'))
                self.assertEqual([r['memory']['defActive'] for r in rows],[1,0,0,1])
                self.assertEqual([r['memory']['cwPush'] for r in rows],[0,1,1,0])
                self.assertGreater(rows[1]['memory']['defUntil'],101)

    def test_missing_enemy_never_starts_counterattack(self):
        a=survivor_case(100,2);b=victory_case();b['objects']=b['objects'][:-2]
        r=self.play('watch_all',[a,b],('bestId','defActive','cwPush'))[-1]
        self.assertEqual(r['memory']['cwPush'],0)
        self.assertEqual(r['memory']['defActive'],1)

if __name__=='__main__':unittest.main()

import unittest
import test_policy_ir as f
from test_rush_unblock import UnblockTests
from test_rush_defense import scene
from policy_ir import compile_policy,extract
from mixed_backdoor import make


def intruder(team=1, tick=100, remote=False):
    case=scene(team,count=0,worldTick=tick,selfGold=150)
    x,y=(16,107) if team==1 else (100,9)
    guard=31 if team==1 else 29
    case['objects'].append(f.obj(guard,kind=4,team=team,x=x,y=y,hp=1254))
    enemy=f.obj(101 if team==1 else 106,kind=2,team=1-team,x=x+8 if team==1 else x-8,y=y+2 if team==1 else y-2,hp=458)
    enemy['objectTarget']=guard;case['objects'].append(enemy)
    case['self'].update(selfX=85 if remote else (8 if team==1 else 108),
                        selfY=8 if remote else (107 if team==1 else 9),
                        selfClass=7 if remote else (6 if team==1 else 1))
    return case


class BackdoorTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_ranger_at_home_and_remote_sieger_target_single_guard_attacker(self):
        for team in (0,1):
            for remote in (False,True):
                case=intruder(team,remote=remote);enemy=case['objects'][-1]['objectId']
                old=self.play('fused_parent',[case])[0]
                new=self.play('solo_20',[case])[0]
                self.assertEqual(old['memory']['defActive'],0)
                self.assertEqual(new['memory']['defActive'],1)
                self.assertEqual(new['memory']['bestId'],enemy)
                self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[enemy] for a in new['actions']))

    def test_requires_actual_visible_own_core_structure_attack(self):
        for target in (0,100,19):
            case=intruder();case['objects'][-1]['objectTarget']=target
            self.assertEqual(self.play('solo_20',[case])[0]['memory']['defActive'],0)
        case=intruder();case['objects']=case['objects'][:-1]
        self.assertEqual(self.play('solo_20',[case])[0]['memory']['defActive'],0)
        case=intruder();case['objects'][-2]['objectHp']=0
        self.assertEqual(self.play('solo_20',[case])[0]['memory']['defActive'],0)

    def test_sentry_lone_duty_expires_but_full_group_keeps_long_memory(self):
        first=intruder(remote=True)
        gap=intruder(tick=101,remote=True);gap['objects']=gap['objects'][:-1]
        late=intruder(tick=580,remote=True);late['objects']=late['objects'][:-1]
        self.assertEqual([r['memory']['defActive'] for r in self.play('solo_20',[first,gap,late])],[1,1,0])
        group=scene(1,worldTick=101);group['self']['selfClass']=7
        self.assertEqual(self.play('solo_20',[first,group,late])[-1]['memory']['defActive'],1)

    def test_dense_budget_and_exact_ir_roundtrip(self):
        rows=[]
        for name in ('solo_20','solo_40'):
            ir=make(name);self.assertEqual(extract(compile_policy(ir),ir),ir)
            for team in (0,1):
                for density in (40,80,160,240):
                    case=intruder(team,remote=True)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(density-len(case['objects']))]
                    rows+=self.play(name,[case|{'self':case['self']|{'selfClass':c}} for c in range(10)])
        print('Solo-defense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()

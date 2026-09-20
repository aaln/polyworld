"""Native two-color rally geometry, public liveness, scope and VM work checks."""
from copy import deepcopy
from pathlib import Path
import unittest
import test_policy_ir as f
from hero_binding import class_id
from policy_ir import read, write
from autoresearch_inward_rally import STUDY as S, VARIANTS


def scene(team=0, slot=0, dense=240):
    xy = lambda x, y: (x, y) if team == 0 else (116-x, 116-y)
    home, anchor, inward = xy(105, 10), xy(20, 11), xy(69, 11)
    own = 1 + team
    objs = [f.obj(1, kind=1, team=0, x=105, y=10, hp=400, alive=0),
            f.obj(2, kind=1, team=1, x=11, y=106, hp=400, alive=0),
            f.obj(10 if team == 0 else 25, kind=4, team=team, x=anchor[0], y=anchor[1], hp=500),
            f.obj(11 if team == 0 else 26, kind=4, team=team, x=inward[0], y=inward[1], hp=1300, alive=0)]
    for i in range(4):
        x, y = xy(16+i%2, 12+i//2)
        e = f.obj(200+i, kind=2, team=1-team, x=x, y=y, hp=300)
        e['objectTarget'] = 10 if team == 0 else 25
        objs.append(e)
    for i in range(dense-len(objs)):
        objs.append(f.obj(1000+i, kind=3, team=team, x=50, y=50, hp=60))
    x, y = xy(104, 93)
    return f.fixture(objs, selfId=100+team*5+slot, selfTeam=team, selfClass=class_id(team, slot),
        selfX=x, selfY=y, selfLevel=2, worldTick=100, selfGold=150,
        selfAttackCooldown=12, selfAttackRange=330000)


class InwardRallyTests(unittest.TestCase):
    captures = []
    @classmethod
    def setUpClass(cls):
        cls.vm = Path('/Users/aaln/experiments/softmax/gota-autoresearch/cycles/20260920T033342Z-b4ca5b/scenario-vm-public-target')
    @classmethod
    def tearDownClass(cls):
        write(S/'native-captures.json', cls.captures)
    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases):
        memory = ['defPointX','defPointY','defAnchor','defActive','bestId','defSentry','perimeterAnchor']
        if name.startswith('relay_'):
            memory += ['relayActive','relayId']
        rows = self.run_vm(S/'candidates'/name/'policy.bas', cases, memory)
        self.captures.append(dict(name=name, inputs=cases, outputs=rows))
        return rows

    def test_distant_geometry_roles_both_colors_every_class(self):
        for team in (0,1):
            for slot in range(5):
                c=scene(team,slot)
                ref=self.play('suppression_reference',[c])[0]
                for name in ('relay_all','relay_sentries'):
                    row=self.play(name,[c])[0];m=row['memory']
                    active=name=='relay_all' or bool(m['defSentry'])
                    self.assertEqual(m['relayActive'],int(active))
                    self.assertEqual(m['defAnchor'],ref['memory']['defAnchor'])
                    self.assertEqual(m['bestId'],ref['memory']['bestId'])
                    self.assertEqual(m['perimeterAnchor'],ref['memory']['perimeterAnchor'])
                    if active:
                        self.assertEqual([m['defPointX'],m['defPointY']],[73,11] if team==0 else [43,105])
                    else:
                        self.assertEqual(row['actions'],ref['actions'])

    def test_nearby_and_no_distance_saving_retain_reference(self):
        for team in (0,1):
            for mode in ('near','no_saving','no_alarm'):
                c=scene(team, dense=32 if mode=='no_alarm' else 240)
                if mode=='near':
                    c['self'].update(selfX=25 if team==0 else 91,selfY=15 if team==0 else 101)
                elif mode=='no_saving':
                    c['self'].update(selfX=20 if team==0 else 96,selfY=80 if team==0 else 36)
                else:
                    c['objects']=[o for o in c['objects'] if o['objectKind']!=2]
                ref=self.play('suppression_reference',[c])[0]
                for name in ('relay_all','relay_sentries'):
                    row=self.play(name,[c])[0]
                    self.assertEqual(row['memory']['relayActive'],0)
                    self.assertEqual(row['actions'],ref['actions'])

    def test_dead_inward_structure_is_not_selected(self):
        for team in (0,1):
            c=scene(team);c['objects'][3]['objectHp']=0
            row=self.play('relay_all',[c])[0]
            self.assertNotEqual(row['memory']['relayId'],11 if team==0 else 26)
            # The fort has zero homeward vector; its fallback remains unchanged.
            self.assertEqual(row['memory']['relayActive'],0)

    def test_closest_inward_structure_prevents_skipping_to_fort(self):
        for team in (0,1):
            row=self.play('relay_all',[scene(team)])[0]
            self.assertEqual(row['memory']['relayId'],11 if team==0 else 26)

    def test_no_stale_active_flag_after_refresh_ends(self):
        c=scene();second=deepcopy(c);second['self']['worldTick']=101
        second['objects']=[o for o in second['objects'] if o['objectKind']!=2]
        rows=self.play('relay_all',[c,second])
        self.assertEqual([r['memory']['relayActive'] for r in rows],[1,0])

    def test_native_budget_equipment_both_colors_all_classes(self):
        rows=[]
        for name in ('relay_all','relay_sentries'):
            for team in (0,1):
                for slot in range(5):
                    rr=self.play(name,[scene(team,slot)]);rows+=rr
                    self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in rr[0]['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(S/'vm-budget.json',dict(decisions=len(rows),max_instructions=max(r['instructions'] for r in rows),max_work=max(r['work'] for r in rows),native_compile_enforces=True,limits=dict(globals=256,source_bytes=65536,instructions=20000,work=50000)))


if __name__=='__main__':
    unittest.main()

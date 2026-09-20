"""Public-target handoff, readiness boundaries, native limits and exact parity."""
from pathlib import Path
import json, subprocess, unittest
import test_policy_ir as f
from test_autoresearch_target_geometry import scene
from hero_binding import class_id
from policy_ir import compile_policy, extract, write
from autoresearch_target_handoff import make, STUDY, VARIANTS

D=Path('/Users/aaln/experiments/softmax/gota-autoresearch/cycles/20260920T033342Z-b4ca5b')

class HandoffTests(unittest.TestCase):
    captures=[]
    vm=D/'scenario-vm-public-target'
    run_vm=f.RealVmTests.run_vm

    @classmethod
    def tearDownClass(cls):
        write(STUDY/'native-captures.json',cls.captures)

    def play(self,name,cc):
        memory=('bestId','motionActive','defActive')
        if name!='parent':memory+=('denseSteps',)
        if name.startswith('handoff'):memory+=('handoffSkips',)
        rows=self.run_vm(STUDY/'candidates'/name/'policy.bas',cc,memory)
        self.captures.append(dict(name=name,inputs=cc,outputs=rows))
        return rows

    def cases(self,team=0,slot=0,kind=3,target=200,level=2,hits=(0,1,1),count=240):
        cc=[scene(team,slot,100+i,h,direction='away',kind=kind,count=count) for i,h in enumerate(hits)]
        for c in cc:c['self'].update(selfTarget=target,selfLevel=level)
        return cc

    def test_public_target_harness_reproducer(self):
        p=STUDY/'native-harness'
        rr=subprocess.run([str(self.vm),str(p/'target_readback.bas')],input=(p/'request.json').read_text(),text=True,capture_output=True,check=True)
        write(p/'new-output.json',json.loads(rr.stdout))
        self.assertEqual(json.loads(rr.stdout)[0]['memory']['targetEcho'],105)

    def test_nonhero_handoff_all_classes_both_colors(self):
        for team in (0,1):
            for slot in range(5):
                eligible=class_id(team,slot) in (0,1,4,5,6)
                for kind in (3,4):
                    cc=self.cases(team,slot,kind,target=199)
                    ref=self.play('suppression_reference',cc)
                    self.assertEqual(ref[1]['memory']['motionActive'],int(eligible))
                    for name in ('handoff','handoff_hits8'):
                        rows=self.play(name,cc)
                        self.assertEqual([r['memory']['motionActive'] for r in rows],[0,0,0])
                        self.assertEqual(rows[1]['memory']['handoffSkips'],int(eligible))
                        self.assertEqual(rows[1]['actions'][0],{'command':'attackTarget','arguments':[200],'accepted':1})

    def test_same_target_and_hero_transition_preserve_reference(self):
        for team in (0,1):
            for slot in range(5):
                for kind,target in ((2,199),(2,200),(3,200),(4,200)):
                    cc=self.cases(team,slot,kind,target)
                    expected=[r['actions'] for r in self.play('suppression_reference',cc)]
                    for name in ('handoff','handoff_hits8'):
                        rr=self.play(name,cc)
                        self.assertEqual([r['actions'] for r in rr],expected)
                        self.assertEqual(rr[-1]['memory']['handoffSkips'],0)

    def test_level1_verified_hit_boundary_and_scope(self):
        for team in (0,1):
            for slot in range(5):
                for last in (7,8):
                    cc=self.cases(team,slot,2,200,1,(last-1,last,last))
                    for name in ('suppression_reference','handoff','handoff_hits8'):
                        expected=int(name=='handoff_hits8' and last==8 and class_id(team,slot) in (0,1,4,5,6))
                        self.assertEqual(self.play(name,cc)[1]['memory']['motionActive'],expected)

    def test_gaps_no_hit_cooldown_sparse_terrain_rejection(self):
        for name in ('handoff','handoff_hits8'):
            for mode in ('gap','same_tick','no_hit','no_cooldown','sparse','blocked','failed'):
                cc=self.cases(slot=1,count=30 if mode=='sparse' else 240)[:2]
                if mode=='gap':cc[1]['self']['worldTick']=103
                if mode=='same_tick':cc[1]['self']['worldTick']=100
                if mode=='no_hit':cc[1]['self']['selfAttacksLanded']=0
                if mode=='no_cooldown':cc[1]['self']['selfAttackCooldown']=0
                if mode=='blocked':cc[1]['blocked']=[[100,14]]
                if mode=='failed':cc[1]['returns']={'walkTo':0}
                row=self.play(name,cc)[1]
                if mode=='sparse':
                    self.assertEqual(row['actions'],self.play('suppression_reference',cc)[1]['actions'])
                    self.assertEqual(row['memory']['handoffSkips'],0)
                    continue
                self.assertEqual(row['memory']['motionActive'],0,mode)
                self.assertTrue(any(a['command']=='attackTarget' for a in row['actions']))

    def test_limits_equipment_both_colors_all_classes(self):
        rows=[]
        for name in ('handoff','handoff_hits8'):
            for team in (0,1):
                for slot in range(5):
                    for active in (False,True):
                        cc=[scene(team,slot,t,h,direction='away',active=active) for t,h in ((100,0),(101,1))]
                        for c in cc:
                            c['self']['selfTarget']=199
                            if not active:
                                enemy=c['objects'].pop(2);enemy['objectKind']=3;c['objects'].append(enemy)
                        rr=self.play(name,cc);rows+=rr
                        for r in rr:self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',dict(decisions=len(rows),max_instructions=max(r['instructions'] for r in rows),max_work=max(r['work'] for r in rows),limits=dict(globals=256,source_bytes=65536,instructions=20000,work=50000),native_compile_enforces=True))

    def test_exact_compile_reverse_and_old_binding_prefix(self):
        for name in VARIANTS:
            p=make(name);source=compile_policy(p)
            self.assertEqual(extract(source,p),p)
            self.assertEqual(source,(STUDY/'candidates'/name/'policy.bas').read_text())
        self.assertTrue((Path(__file__).parent/'binding.py').read_bytes().startswith((STUDY/'binding-before.py').read_bytes()))

if __name__=='__main__':unittest.main()

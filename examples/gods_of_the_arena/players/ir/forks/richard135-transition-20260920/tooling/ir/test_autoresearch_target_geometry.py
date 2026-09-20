"""Native public-target direction, scope, fallback, memory and budget checks."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from test_autoresearch_dense_cadence import case
from hero_binding import class_id
from policy_ir import compile_policy, write
from autoresearch_target_geometry import make, STUDY


def scene(team=0, slot=0, tick=100, hits=0, direction='toward', kind=2, count=240, active=False):
    c = case(team, slot, tick, hits, count, active)
    c['self']['selfLevel'] = 2
    x,y=c['self']['selfX'],c['self']['selfY']
    sign=1 if team==0 else -1
    if direction=='away':sign=-sign
    for o in c['objects']:
        if o['objectTeam']!=team and o['objectKind']==2:
            o.update(objectX=x+2*sign,objectY=y,objectKind=kind,objectTarget=0)
    return c


class GeometryTests(unittest.TestCase):
    captures=[]
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):write(STUDY/'native-captures.json',cls.captures)
    run_vm=f.RealVmTests.run_vm

    def play(self,name,cc):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            memory=('bestId','motionActive','defActive')
            if name!='parent':memory+=('denseSteps',)
            rr=self.run_vm(p,cc,memory)
        self.captures.append({'name':name,'inputs':cc,'outputs':rr})
        return rr

    def test_toward_step_suppressed_or_reversed_then_attack_resumes(self):
        for team in (0,1):
            for slot in range(5):
                eligible=class_id(team,slot) in (0,1,4,5,6)
                cc=[scene(team,slot,t,h) for t,h in [(100,0),(101,1),(102,1)]]
                for name in ('suppress_toward','reverse_toward'):
                    rr=self.play(name,cc)
                    self.assertEqual([r['memory']['motionActive'] for r in rr],[0,int(eligible and name=='reverse_toward'),0])
                    if eligible and name=='reverse_toward':
                        self.assertEqual(rr[1]['actions'][0]['arguments'],[98,15] if team==0 else [16,99])
                    self.assertEqual(rr[-1]['actions'][0]['command'],'attackTarget')

    def test_away_structure_sparse_and_level1_preserve_reference(self):
        for team in (0,1):
            for slot in range(5):
                for mode in ('away','structure','sparse','level1'):
                    cc=[scene(team,slot,t,h,direction='away' if mode=='away' else 'toward',kind=4 if mode=='structure' else 2,count=30 if mode=='sparse' else 240) for t,h in [(100,0),(101,1),(102,1)]]
                    if mode=='level1':
                        for c in cc:c['self']['selfLevel']=1
                    expected=[r['actions'] for r in self.play('readiness_reference',cc)]
                    for name in ('suppress_toward','reverse_toward'):
                        self.assertEqual([r['actions'] for r in self.play(name,cc)],expected,(team,slot,mode,name))

    def test_creep_geometry_and_blocked_or_rejected_step(self):
        for team in (0,1):
            for mode in ('creep','blocked','failed'):
                cc=[scene(team,1,t,h,kind=3 if mode=='creep' else 2) for t,h in [(100,0),(101,1)]]
                if mode=='blocked':cc[-1]['blocked']=[[98,15] if team==0 else [16,99]]
                if mode=='failed':cc[-1]['returns']={'walkTo':0}
                rr=self.play('reverse_toward',cc)
                self.assertEqual(rr[-1]['memory']['motionActive'],int(mode=='creep'))
                if mode!='creep':self.assertTrue(any(a['command']=='attackTarget' for a in rr[-1]['actions']))

    def test_gaps_and_no_new_hit_do_not_recover(self):
        for name in ('suppress_toward','reverse_toward'):
            for mode in ('gap','same_tick','no_hit','no_cooldown'):
                cc=[scene(tick=100),scene(tick=101,hits=1)]
                if mode=='gap':cc[1]['self']['worldTick']=103
                if mode=='same_tick':cc[1]['self']['worldTick']=100
                if mode=='no_hit':cc[1]['self']['selfAttacksLanded']=0
                if mode=='no_cooldown':cc[1]['self']['selfAttackCooldown']=0
                self.assertEqual(self.play(name,cc)[-1]['memory']['motionActive'],0)

    def test_native_limits_equipment_both_teams_all_classes_dense_worst_position(self):
        rows=[]
        for name in ('suppress_toward','reverse_toward'):
            for team in (0,1):
                for slot in range(5):
                    for active in (False,True):
                        cc=[scene(team,slot,t,h,active=active) for t,h in [(100,0),(101,1)]]
                        # Keep legal object ordering; a selected final enemy creep
                        # tests the full added pass when mobile objects are dense.
                        if not active:
                            for c in cc:
                                enemy=c['objects'].pop(2);enemy['objectKind']=3;c['objects'].append(enemy)
                        rr=self.play(name,cc);rows.extend(rr)
                        self.assertTrue(all(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']) for r in rr))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})


if __name__=='__main__':unittest.main()

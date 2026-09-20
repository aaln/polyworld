"""Native physical-class scope, reset, fallback, sparse parity, gear and VM limits."""
from pathlib import Path
import tempfile,unittest,re
import test_policy_ir as f
from test_autoresearch_dense_cadence import case
from hero_binding import class_id,NAMES,CONTENT
from policy_ir import compile_policy,write
from autoresearch_weapon_dense import make,STUDY

class WeaponDenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm
    def play(self,name,cases):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'policy.bas';source.write_text(compile_policy(make(name)));return self.run_vm(source,cases,('bestId','motionActive') if name=='parent' else ('bestId','motionActive','denseSteps'))
    def test_class_membership_matches_published_attack_styles(self):
        source=CONTENT.read_text()
        styles=re.findall(r'HeroSpec\(\s+name: "[^"]+",\s+role: "[^"]+",\s+attackStyle: (\w+),',source)
        self.assertEqual(len(styles),len(NAMES))
        for index,style in enumerate(styles):
            self.assertEqual(style=='RangedAttack',index in (1,6))
            self.assertEqual(style=='MagicAttack',index in (2,3,7,8))
    def test_new_hit_then_resume_all_classes_and_colors(self):
        for name in ('weapon_ranged','weapon_all'):
            for team in (0,1):
                for slot in range(5):
                    cls=class_id(team,slot);eligible=cls in ((0,1,4,5,6) if name=='weapon_all' else (1,6))
                    rows=self.play(name,[case(team,slot,t,h) for t,h in [(100,0),(101,1),(102,1)]])
                    self.assertEqual([r['memory']['motionActive'] for r in rows],[0,int(eligible),0])
                    if eligible:self.assertEqual(rows[1]['actions'][0]['command'],'walkTo')
                    self.assertEqual(rows[-1]['actions'][0]['command'],'attackTarget')
    def test_excluded_classes_exact_parent_commands_after_hits(self):
        for name in ('weapon_ranged','weapon_all'):
            for team in (0,1):
                for slot in range(5):
                    cls=class_id(team,slot)
                    if cls in ((0,1,4,5,6) if name=='weapon_all' else (1,6)):continue
                    for active in (False,True):
                        cc=[case(team,slot,t,h,240,active) for t,h in [(100,0),(101,1),(102,2)]]
                        self.assertEqual([r['actions'] for r in self.play(name,cc)],[r['actions'] for r in self.play('parent',cc)])
    def test_sparse_and_no_new_hit_exact_parent_commands(self):
        for n in ('weapon_ranged','weapon_all'):
            for team in (0,1):
                for slot in range(5):
                    for count in (30,240):
                        cc=[case(team,slot,t,0,count) for t in (100,101)]
                        self.assertEqual([r['actions'] for r in self.play(n,cc)],[r['actions'] for r in self.play('parent',cc)])
    def test_gaps_cooldown_and_failed_terrain_fallback(self):
        for n in ('weapon_ranged','weapon_all'):
            for mode in ('gap','same_tick','no_cooldown','blocked','failed'):
                first=case(team=0,slot=1);second=case(team=0,slot=1,tick=101,hits=1)
                if mode=='gap':second['self']['worldTick']=103
                elif mode=='same_tick':second['self']['worldTick']=100
                elif mode=='no_cooldown':second['self']['selfAttackCooldown']=0
                elif mode=='blocked':second['blocked']=[[100,14]]
                elif mode=='failed':second['returns']={'walkTo':0}
                row=self.play(n,[first,second])[-1];self.assertEqual(row['memory']['motionActive'],0);self.assertEqual([a['arguments'] for a in row['actions'] if a['command']=='attackTarget'],[[row['memory']['bestId']]])
    def test_limits_and_equipment_every_class(self):
        rows=[]
        for n in ('weapon_ranged','weapon_all'):
            for team in (0,1):
                for slot in range(5):
                    for active in (False,True):
                        rows+=self.play(n,[case(team,slot,t,h,240,active) for t,h in [(100,0),(101,1)]])
        for r in rows:
            self.assertLessEqual(r['instructions'],20000);self.assertLessEqual(r['work'],50000)
            self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']))
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})
if __name__=='__main__':unittest.main()

"""Native reservation thresholds, public inventory guards, parity and limits."""
from pathlib import Path
import tempfile, unittest
import test_policy_ir as f
from test_autoresearch_readiness import fixture
from autoresearch_last_slot_axe import make, STUDY
from policy_ir import compile_policy, write


class AxeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm

    def play(self,name,cases):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            return self.run_vm(p,cases)

    def test_melee_final_slot_price_boundary(self):
        for name in ('axe_only','readiness_axe'):
            for cls in (0,4,5,9):
                for gold in (149,150,179,180,500):
                    c=f.fixture(selfClass=cls,selfGold=gold)
                    c['inventory']=[7,5,6,9,11,0]
                    row=self.play(name,[c])[0]
                    purchases=[a['arguments'][0] for a in row['actions'] if a['command']=='buyItem']
                    self.assertEqual(purchases,[18] if gold>=180 else [])

    def test_nonmatching_inventory_and_classes_exact_reference(self):
        for name,ref in [('axe_only','parent'),('readiness_axe','readiness_reference')]:
            for cls in range(10):
                inventories=[[7,5,6,11,0,0],[7,5,6,9,13,0],[7,5,6,9,18,0],
                             [7,5,6,9,11,13],[11,13,18,19,16,0],[7,5,6,9,2,0]]
                if cls not in (0,4,5,9):inventories.append([7,5,6,9,11,0])
                for inventory in inventories:
                    c=f.fixture(selfClass=cls,selfGold=200);c['inventory']=inventory
                    self.assertEqual(self.play(name,[c])[0]['actions'],self.play(ref,[c])[0]['actions'])

    def test_sustain_precedence_retained(self):
        for name in ('axe_only','readiness_axe'):
            c=f.fixture(selfClass=5,selfGold=180,selfHp=30);c['inventory']=[7,5,6,9,11,0]
            actions=self.play(name,[c])[0]['actions']
            purchases=[a['arguments'][0] for a in actions if a['command']=='buyItem']
            self.assertEqual(purchases,[2,1,18])
            # Fixture returns do not spend gold. Complete engine games must verify
            # actual accepted inventory changes; these calls prove ordering only.

    def test_equipment_failure_does_not_change_combat(self):
        for name in ('axe_only','readiness_axe'):
            c=f.fixture(selfClass=5,selfGold=180);c['inventory']=[7,5,6,9,11,0]
            c['returns']={'buyItem':0}
            row=self.play(name,[c])[0]
            self.assertTrue(all(a['accepted']==0 for a in row['actions'] if a['command']=='buyItem'))

    def test_all_classes_dense_sparse_limits(self):
        rows=[]
        for name in ('axe_only','readiness_axe'):
            for team in (0,1):
                for slot in range(5):
                    for count in (30,240):
                        cc=[fixture(team,slot,t,h,2,True,count) for t,h in [(100,0),(101,1)]]
                        rows+=self.play(name,cc)
        for row in rows:
            self.assertLessEqual(row['instructions'],20000)
            self.assertLessEqual(row['work'],50000)
            self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})

if __name__=='__main__':unittest.main()

import tempfile,unittest
from pathlib import Path
import test_policy_ir as f
from test_jordan_root import final_approach
from jordan_lineup import make
from jordan_root import make as parent
from policy_ir import compile_policy,extract

class LineupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm
    def test_exact_parent_commands_and_dense_budget(self):
        p=make();self.assertEqual(extract(compile_policy(p),p),p)
        with tempfile.TemporaryDirectory() as temp:
            new=Path(temp)/'new.bas';new.write_text(compile_policy(p));rows=[]
            for team in (0,1):
                old=Path(temp)/'old.bas';old.write_text(compile_policy(parent('deployed_parent' if team==0 else 'release20')))
                for size in (40,80,160,240):
                    cases=[]
                    for c in range(team*5,team*5+5):
                        a=final_approach(team,4,100);a['self']['selfClass']=c
                        a['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(size-len(a['objects']))]
                        cases.append(a)
                    before=self.run_vm(old,cases,['bestId','defActive']);after=self.run_vm(new,cases,['bestId','defActive'])
                    self.assertEqual([r['actions'] for r in before],[r['actions'] for r in after]);rows+=after
            print('Lineup dense decisions',len(rows),'max',max(r['instructions'] for r in rows),max(r['work'] for r in rows))
if __name__=='__main__':unittest.main()

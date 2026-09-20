from bounded_core import STUDY,CANDIDATES,make
from core_pressure_eval import main
from policy_ir import read

if __name__=='__main__':
    if not read(STUDY/'vm-stress.json')['passed']:raise ValueError('Dense runtime proof required')
    main(study=STUDY,variants=['deployed','pressure_parent']+CANDIDATES,factory=make,seed=779000)

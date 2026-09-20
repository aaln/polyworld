import time
from warlock_cadence import STUDY,VARIANTS,make
from mage_reserve import STUDY as RESERVE
from core_pressure_eval import main
from ranger_guard_queue import alive
from policy_ir import read

if __name__=='__main__':
    while alive(read(RESERVE/'local-process.json')['pid']):time.sleep(15)
    main(study=STUDY,variants=VARIANTS,factory=make,seed=781000)

"""Reuse the frozen threat/preservation/field design for versioned bounded skills."""
import core_pressure_hosted as hosted
import core_pressure_queue as queue
import time
from bounded_core import STUDY
from policy_ir import read
from ranger_guard_queue import alive
from threat_coverage import STUDY as COVERAGE

if __name__=='__main__':
    if not read(STUDY/'vm-stress.json')['passed']:raise ValueError('Bounded runtime proof required')
    # The already selected coverage cohort owns the serial queue; retain it.
    if (COVERAGE/'hosted-selection.json').exists():
        while alive(read(COVERAGE/'process.json')['pid']):time.sleep(15)
        if not (COVERAGE/'hosted-comparison.json').exists():
            raise RuntimeError('Coverage queue stopped without reconciled result')
    hosted.STUDY=STUDY
    queue.STUDY=STUDY
    queue.main()

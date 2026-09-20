"""Run the measured-cadence refinement through the same frozen target gate."""
import importlib.util
from cadence import ROOT,STUDY,NAMES,read

if __name__=='__main__':
    assert read(STUDY/'focus-proof.json')['passed']
    spec=importlib.util.spec_from_file_location('transition_hosted_runner',ROOT/'games/gods_of_the_arena/instruments/richard_transition/hosted.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    runner.STUDY=STUDY;runner.NAMES=NAMES;runner.main()

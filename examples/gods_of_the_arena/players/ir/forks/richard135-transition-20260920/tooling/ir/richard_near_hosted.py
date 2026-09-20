"""Evaluate the already local-qualified pressure20_near behavior against Richard."""
import counterpush_hosted as runner
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-richard-near'

if __name__=='__main__':
    runner.STUDY=STUDY
    runner.PREFIX='aaron-gota-ir-near-pressure'
    runner.CHANGE='Release Crossbowman and Berserker after20seconds unless an observed survivor within16tiles of the god renews duty; retain three sentries, original rally and exact blue branch.'
    runner.RED_KITE_FLOOR=24
    runner.main()

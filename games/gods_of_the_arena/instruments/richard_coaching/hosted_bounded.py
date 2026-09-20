"""Final80of the follow-up400cycle, gated by the measured runtime margin."""
from bounded_cohort import STUDY
from prepare import read
from hosted_followups import main

if __name__=='__main__':
    assert read(STUDY/'runtime-margin.json')['passed']
    main('bounded_cohort')

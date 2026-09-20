"""Final80of follow-up400, after the coupled observation/combat margin gate."""
from bounded_combat import STUDY
from prepare import read
from hosted_followups import main

if __name__=='__main__':
    assert read(STUDY/'runtime-margin.json')['passed']
    main('bounded_combat')

from rolling_core import STUDY,VARIANTS,make
from core_pressure_eval import main

if __name__=='__main__':main(study=STUDY,variants=['deployed','pressure_parent','scan8'],factory=make,seed=783000)

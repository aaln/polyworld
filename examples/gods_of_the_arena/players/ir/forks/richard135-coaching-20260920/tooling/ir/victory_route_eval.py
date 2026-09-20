from victory_route import STUDY, VARIANTS, make
from core_pressure_eval import main
from rush_defense_eval import evaluate
from ranger_guard_hosted import freeze
from policy_ir import read,write
from release_workspace import RUN


if __name__=='__main__':
    freeze(STUDY/'screen-prospective.json',{'cases':12,'seed':787000,'variants':VARIANTS,
        'gate':'Candidate wins per color/opponent at least deployed, all gear/runtime/replays. Screen only; require60 fresh games afterward.'})
    evaluate('screen',VARIANTS,12,787000,make,STUDY,RUN/'r5/fast/audit-local')
    m=read(STUDY/'screen/result.json')['metrics'];b=m['deployed']
    qualified=[n for n in VARIANTS[1:] if m[n]['all_gear'] and m[n]['wins']>=b['wins'] and
        all(m[n]['colors'][c]>=b['colors'][c] for c in b['colors']) and
        all(m[n]['opponents'][o]>=b['opponents'][o] for o in b['opponents'])]
    write(STUDY/'screen/comparison.json',{'qualified':qualified,'metrics':m})
    if qualified:main(study=STUDY,variants=['deployed','pressure_parent',*qualified],factory=make,seed=788000)
    else:
        (STUDY/'local').mkdir(exist_ok=True)
        write(STUDY/'local/comparison.json',{'qualified':[],'selected':None,'stage':'screen','metrics':m})

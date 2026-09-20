from counterwatch import STUDY,VARIANTS,make
from core_pressure_eval import main
from rush_defense_eval import evaluate
from ranger_guard_hosted import freeze
from policy_ir import read,write
from release_workspace import RUN

if __name__=='__main__':
    freeze(STUDY/'screen-prospective.json',{'cases':12,'seed':789000,'variants':VARIANTS,
        'gate':'At least deployed wins for each color/opponent and all gear/runtime/replays. Then60 fresh games for each passing candidate.'})
    evaluate('screen',VARIANTS,12,789000,make,STUDY,RUN/'r5/fast/audit-local')
    m=read(STUDY/'screen/result.json')['metrics'];b=m['deployed']
    q=[n for n in VARIANTS[1:] if m[n]['all_gear'] and m[n]['wins']>=b['wins'] and
        all(m[n]['colors'][c]>=b['colors'][c] for c in b['colors']) and
        all(m[n]['opponents'][o]>=b['opponents'][o] for o in b['opponents'])]
    write(STUDY/'screen/comparison.json',{'qualified':q,'metrics':m})
    if q:main(study=STUDY,variants=['deployed','pressure_parent',*q],factory=make,seed=790000)
    else:
        (STUDY/'local').mkdir(exist_ok=True)
        write(STUDY/'local/comparison.json',{'qualified':[],'selected':None,'stage':'screen','metrics':m})

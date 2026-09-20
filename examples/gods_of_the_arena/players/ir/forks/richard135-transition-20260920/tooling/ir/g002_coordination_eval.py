from g002_coordination import STUDY, VARIANTS, make
from core_pressure_eval import main
from rush_defense_eval import evaluate
from ranger_guard_hosted import freeze
from policy_ir import read, write
from release_workspace import RUN

if __name__ == '__main__':
    freeze(STUDY/'screen-prospective.json', {'cases':12, 'seed':809000, 'variants':VARIANTS,
        'parent':'Exact anchor candidate that won blue40 but red4 against g002.',
        'gate':'No opponent/color win regression versus parent, full runtime/replay/gear checks. Fresh60cases per qualifier with full blue gameplay parity. G002 is the first hosted target; original rejected studies remain rejected.'})
    evaluate('screen',VARIANTS,12,809000,make,STUDY,RUN/'r5/fast/audit-local')
    m=read(STUDY/'screen/result.json')['metrics']; b=m['pressure_parent']
    q=[n for n in VARIANTS[2:] if m[n]['all_gear'] and m[n]['wins']>=b['wins'] and
       all(m[n]['colors'][c]>=b['colors'][c] for c in b['colors']) and
       all(m[n]['opponents'][o]>=b['opponents'][o] for o in b['opponents'])]
    write(STUDY/'screen/comparison.json',{'qualified':q,'metrics':m})
    if q: main(study=STUDY,variants=['deployed','pressure_parent',*q],factory=make,seed=810000)
    else:
        (STUDY/'local').mkdir(exist_ok=True)
        write(STUDY/'local/comparison.json',{'qualified':[],'selected':None,'stage':'screen','metrics':m})

"""Separate, frozen repair hypotheses for the replay-proven stale tower duty."""
from copy import deepcopy
from pathlib import Path

from binding import CONTRACTS
from jordan254_followup import STUDY as PREVIOUS
from jordan254_research import STUDY as BASE
from policy_ir import read,digest,refresh_grounding,bundle,write
from ranger_guard_hosted import freeze

STUDY=BASE/'stale-anchor-repair'
VARIANTS=['warning100','retire','retire_core']


def make(name):
    parent=read(PREVIOUS/'final-feedback/policy.ir.json')
    if name=='warning100':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='gota_stale_anchor_'+name
    op='lineup_live_anchor_core' if name=='retire_core' else 'lineup_live_anchor'
    p['skill']['observe']['operator']=op
    params=p['skill']['observe']['parameters']
    p['skill']['observe']['parameters']={k:params.get(k,v[0]) for k,v in CONTRACTS[op].parameters.items()}
    p['goal']['G_defense']['preference']+=' A defensive assignment ends when its saved friendly structure is destroyed; reassess visible pressure or resume ordinary wave objectives immediately.'
    if name=='retire_core':
        p['goal']['G_defense']['preference']+=' Independently respond from within40tiles to visible living enemy creeps within8tiles of our god, using a bounded rotating observation scan.'
    evidence=BASE/'user-stall-77d700dd/diagnosis.json'
    p['belief']['claims']['B_anchor_repair']={'status':'untested',
        'claim':'Canceling dead-anchor duty may release sentries from the demonstrated wait; a separate creep alarm may prevent the uncovered god loss. Full-match improvement and rival nonregression are not yet established.',
        'evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
        change='New stale-anchor repair experiment: '+name,needs_review=['belief/B_anchor_repair','goal/G_defense'])
    refresh_grounding(p);return p


def prepare():
    STUDY.mkdir(exist_ok=True)
    freeze(STUDY/'prospective.json',{'variants':VARIANTS,'baseline':str(PREVIOUS/'final-feedback'),
        'hypotheses':['Remember and retire missing own anchor without shortening any standing-anchor duty.',
                      'Add bounded creep-only core alarm within40tiles response radius.'],
        'mechanism_gate':'Actual red DK/Lich/Warlock retire absent/dead own anchor; fog alone preserves it; replacement group can reanchor. Independent visible core-creep response must fire from the replay rally. Blue branch exact. Dense240object decisions remain within VM budget.',
        'local_gate':'Reproduce the public baseline loss with exactseed2026/config, verify same gameplay; then test each frozen repair full episode. Counterfactual win is diagnostic only, not league qualification.',
        'promotion':'No promotion of these repairs without fresh40/color Jordan254/g002/black16/macromackie4/relh154 preservation checks. warning100 promotion is independent.'})
    for n in VARIANTS:
        p=make(n);dest=STUDY/'candidates'/n
        if dest.exists():assert read(dest/'policy.ir.json')==p
        else:bundle(p,dest)
    write(STUDY/'config.json',read(BASE/'user-stall-77d700dd/episode-request.json')['game_config'])


if __name__=='__main__':prepare()

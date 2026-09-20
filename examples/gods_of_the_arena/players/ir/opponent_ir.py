"""Python dictionary opponent IR using the primary policy's seven-layer layout.

The observation binding predicts visible motifs. It is deliberately not accepted
by the BASIC compiler: observational similarity does not prove executable parity.
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

SCHEMA='gota-semantic-opponent/1'
LAYERS=('situation','belief','goal','skill','strategy','execution','update')
SKILLS=('target_hero','target_creep','target_structure','advance','withdraw','lateral','hold')

def validate(model):
    if set(model)!={'schema','id',*LAYERS} or model['schema']!=SCHEMA:
        raise ValueError('Opponent IR requires the primary seven-layer dictionary layout')
    if model['execution']!={'binding':'gota-observer-model/1','game_version':'2026.9.16.5','language':'Python'}:
        raise ValueError('Unsupported observation binding')
    for skill,spec in model['skill'].items():
        if skill not in SKILLS or set(spec)!={'operator','parameters'} or spec['operator']!='observed_'+skill:
            raise ValueError('Unknown observational skill')
    seen=set()
    for rule in model['strategy']:
        if set(rule)!={'id','when','skill','for'} or rule['id'] in seen:
            raise ValueError('Invalid or duplicate strategy rule')
        seen.add(rule['id'])
        if rule['when'] not in model['situation']['grounded']['predicates'] or rule['skill'] not in model['skill']:
            raise ValueError('Unbound observational rule')
        if not rule['for'] or any(g not in model['goal'] for g in rule['for']):
            raise ValueError('Missing goal hypothesis')
        claim=model['belief']['claims'][rule['id']]
        if set(claim)!={'claim','status','evidence'}:raise ValueError('Incompatible belief claim layout')
        evidence=claim['evidence'][0]
        for field in ('confidence','n','base_rate','level','opponent','last_observed','predictions','over','status'):
            if field not in evidence:raise ValueError(f'Missing preference evidence: {field}')
        if not 0<=evidence['confidence']<=1 or evidence['n']<0:raise ValueError('Invalid confidence/count')
        if evidence['status']=='supported' and (evidence['n']<8 or evidence['predictions']['n']==0 or evidence['predictions']['accuracy']<=evidence['predictions']['population_accuracy']):
            raise ValueError('Unsupported promotion')
    if model['belief']['grounded']['proxy']['usable']:raise ValueError('This binding has no validated rollout controller')
    return model

def predict(model, situation, affordances):
    """Predict a motif at an inferred boundary from the PRIOR visible snapshot.

    This predicts neither boundary timing nor action arguments. It never emits
    simulator actions and is not a counterfactual rollout opponent.
    """
    if not affordances or any(s not in model['skill'] for s in affordances):raise ValueError('Invalid affordances')
    key=f"mask_{situation['opportunity_mask']}_low_{int(situation['low_hp'])}"
    predictor=model['belief']['grounded']['predictor'];counts=predictor['contexts'].get(key,predictor['global'])
    if sum(counts.values())<8:counts=predictor['global']
    weights={s:counts.get(s,0)+1 for s in set(affordances)};total=sum(weights.values())
    distribution={s:v/total for s,v in sorted(weights.items())}
    chosen=max(distribution,key=lambda s:(distribution[s],s))
    rules=[r['id'] for r in model['strategy'] if r['when']==key]
    return {'skill':chosen,'probabilities':distribution,'preference_id':rules[0] if rules else None,'context':key,'usable_for_rollout':False}

def belief_patch(model):
    """Return reviewable primary-IR claim entries; never mutate the live policy."""
    validate(model)
    return deepcopy(model['belief']['claims'])

def load(path):
    spec=importlib.util.spec_from_file_location('opponent_model',Path(path));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return validate(module.MODEL)

if __name__=='__main__':
    model=load(sys.argv[1]);print(f"Valid {model['id']}: {len(model['skill'])} skills, {len(model['strategy'])} evidence-backed hypotheses; rollout disabled")

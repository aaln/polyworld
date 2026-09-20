"""Coordinate threat-group coverage with measured recall and pressure mechanisms."""
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-threat-coverage'
PARENT = RUN / 'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS = ['deployed', 'blue_coverage', 'red_coverage', 'both_coverage']


def make(name):
    parent = read(PARENT / 'policy.ir.json')
    if name == 'deployed': return parent
    if name not in VARIANTS: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_' + name
    blue, red = name != 'red_coverage', name != 'blue_coverage'
    operator = 'lineup_coverage_observe' if blue and red else 'lineup_arrival_observe' if blue else 'lineup_pressure_observe'
    parameters = p['skill']['observe']['parameters'].copy()
    if blue: parameters.update(arrival_tiles=12, blue_group=3, isolated_max=2)
    if red: parameters.update(redbranch_pressure_hold=480, redbranch_pressure_continue=0, redbranch_group_size=3)
    p['skill']['observe'] = {'operator': operator, 'parameters': parameters}
    if red:
        p['goal']['G_defense']['preference'] += (' On red, three observed clustered enemy heroes near a standing friendly structure trigger group recall. '
            'Keep three sentries on long duty, but retain Crossbowman/Berserker for20seconds after the last group; isolated survivors do not renew their duty.')
    if blue:
        p['goal']['G_defense']['preference'] += (' On blue, three observed clustered enemy heroes trigger group recall; the assigned core-intrusion response admits groups of up to two. '
            'Quiet release can count down only after reaching within12tiles of the remembered protected structure. Existing responder assignment and combat priority remain.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_threat_coverage'] = {'claim': (
        'Actual league round377 red loss to red-kite27 ereq_9b1b365d shows three surviving attackers '
        'advancing while group_size4 does not initiate fresh recall of the absent attackers. '
        'The failed arrival12 mixed test44/80vs42/80 repaired transit but a reconstructed loss '
        'still releases Ranger before a two/three-hero wave; blue_group4 and isolated_max1 leave '
        'those sizes without an independent trigger. Test coordinated coverage and duty changes. '
        'Neither a selected replay nor the failed arrival-only candidate establishes improvement.'),
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Coordinated observed threat coverage: ' + name)
    refresh_grounding(p)
    return p

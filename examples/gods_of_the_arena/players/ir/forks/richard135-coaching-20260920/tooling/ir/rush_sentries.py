"""Test second-wave coverage after repelling an observed five-hero rush."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from rush_defense import STUDY as PARENT

STUDY = PARENT.parent/'r5-rush-sentries'
VARIANTS = {
    'defense_parent': {},
    'blue_three': {'red_sentry': 0},
    'three': {},
    'two': {'red_sentry': 2, 'blue_sentry': 2, 'sentry_hold': 4800},
    'long_three': {'sentry_hold': 7200},
}


def make(name):
    parent = read(PARENT/'hosted/blue_memory/final-feedback/policy.ir.json')
    if name == 'defense_parent': return parent
    p = deepcopy(parent)
    p['id'] = 'gota_second_rush_'+name
    p['skill']['observe'] = {'operator': 'rush_sentries', 'parameters':
        CONTRACTS['rush_sentries'].defaults() | parent['skill']['observe']['parameters'] | VARIANTS[name]}
    paths = [PARENT/'candidate-red-kite-review/loss.review.json',
             PARENT/'candidate-red-kite-review/win.review.json',
             PARENT/'hosted/blue_memory/result.json']
    p['belief']['claims']['B_second_wave'] = {
        'claim': 'In a fully decoded blue loss to red-kite20, the first rush was repelled but '
                 'all five defenders left after their short commitment expired. At220seconds '
                 'the next five-hero wave attacked the surviving gate while every defender was '
                 'far away; the god fell at242.7seconds. In the sampled win, three defenders '
                 'occupied the attackers while Ranger and Demon finished the enemy base. '
                 'Test retaining two or three sentries after observed rushes while the other '
                 'heroes resume pressure. These are two selected replay examples, not causal '
                 'proof or a prediction of unseen enemies. Overdefending may reduce wins.',
        'status': 'untested', 'evidence': [{'artifact': str(x), 'sha256': digest(x.read_bytes())} for x in paths]}
    p['goal']['G_defense']['preference'] += ' After repelling a concentrated rush, retain the configured defensive roles through its likely return window; let remaining roles restore objective pressure.'
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                        change='Second-wave sentry experiment: '+name,
                        needs_review=['belief/B_second_wave','goal/G_defense','goal/G_wave','goal/G_survival'])
    refresh_grounding(p)
    return p

"""Session-bound coordinated center push; complete local and hosted comparisons."""
from copy import deepcopy
import sys
import g002_watch as workflow
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN/'coached-lanes/r5-coach-split-0918'
PARENT = workflow.PARENT
VARIANTS = ('deployed', 'supports', 'tankheal')


def make(name):
    parent = read(PARENT/'policy.ir.json')
    if name == 'deployed': return parent
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'gota_coached_split_' + name
    for key, operator in [('observe', 'lineup_coached_split'), ('fallback', 'lineup_coached_center')]:
        s = p['skill'][key]
        s['operator'] = operator
        s['parameters'] = {k: s['parameters'].get(k, v[0]) for k, v in CONTRACTS[operator].parameters.items()}
    p['skill']['observe']['parameters']['redbranch_split_guard'] = 7 if name == 'supports' else 5
    p['skill']['fallback']['parameters']['redbranch_lane'] = 1
    p['goal']['G_defense']['preference'] = (
        'Red: defend an immediate observed rush together. After nearby pressure clears, '
        'retain at most two assigned rear guards and send the other three roles down '
        'center to create offensive pressure. Keep threat memory and recall for a fresh '
        'group or god damage. Preserve initial combat and exact deployed blue behavior. '
        'Two rear guards are Lich/Warlock for supports, DeathKnight/Warlock for tankheal; '
        'death can reduce the living rear guard count. Neither fog nor silence proves enemy death.')
    p['goal']['G_wave']['preference'] = ('In red post-defense split, the three offensive roles '
        'advance common center waypoints when they have no combat or recovery action. '
        'Other phases retain original allied-wave routing; preserve purchases and kiting.')
    p['situation']['notes'] = ('Session 2026-09-18t23-13-38-249zf154ac shows current relh154-legacy '
        'RED vs gota-g002:v1 in ereq_0806a449-3d7c-4160-868a-3e157634ebbc, verified by API '
        'and recording. Captured input IR/source were blank. Published .5 clean source used. '
        'Quiet means no observed living hero near the protected objective for120ticks; '
        'red/blue use observed own god coordinates. Fixed lineups differ in hero capabilities.')
    p['belief']['claims']['B_coached_split'] = {'status':'untested',
        'claim':'Two rear guards plus coordinated three-hero center pressure may avoid '
        'three-sentry five-minute waiting without exposing the base as all-release did. '
        'Behavior and competitive superiority require separate validation.',
        'evidence':[{'artifact':str(STUDY/'prospective.json'),
                     'sha256':digest((STUDY/'prospective.json').read_bytes())},
                    {'artifact':str(STUDY/'captured-input/notes.md'),
                     'sha256':digest((STUDY/'captured-input/notes.md').read_bytes())}]}
    for rule in p['strategy']:
        if rule['skill'] == 'fallback': rule['for'] = ['G_wave', 'G_defense', 'G_fort']
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Coaching-guided two-defender/three-center-pusher allocation: '+name)
    p['update']['evidence'] += p['belief']['claims']['B_coached_split']['evidence']
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    workflow.STUDY = STUDY
    workflow.VARIANTS = VARIANTS
    workflow.make = make
    workflow.local(819500) if sys.argv[1] == 'local' else workflow.remote()

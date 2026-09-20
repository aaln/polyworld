"""Prospective tests of the exact support contexts seen in complete replays."""
from copy import deepcopy
from caster_binding_repair import make as caster
from policy_ir import digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN/'coached-lanes/r5-anchored-support'
VARIANTS = ['deployed', 'pressure_parent', 'anchor', 'frontline', 'anchored_frontline']


def make(name):
    if name == 'deployed': return caster('deployed')
    parent = caster('bound_idle')
    if name == 'pressure_parent': return parent
    if name not in VARIANTS[2:]: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_support_' + name
    p['skill']['observe']['operator'] = 'lineup_anchored_support'
    p['skill']['observe']['parameters'].update(
        redbranch_frontline_only=int(name in ('frontline', 'anchored_frontline')),
        redbranch_anchor_required=int(name in ('anchor', 'anchored_frontline')))
    p['goal']['G_defense']['preference'] += (
        ' Coordinate idle casters around an actual frontline attack and/or a current '
        'standing friendly structure perimeter; a passing carry or another caster '
        'target is insufficient evidence of a coordinated defensive engagement.')
    e = STUDY/'diagnosis.json'
    p['belief']['claims']['B_anchored_support'] = {'status': 'untested', 'claim': (
        'Exact public context at expanded assistance distinguishes observed outcomes: '
        'Richard winning replay joins at5537/5910/5948/9741 have a friendly anchor '
        'and DeathKnight commitment. Jordan loss joins4173/6721 have no friendly '
        'anchor and the commitment comes from Warlock/Crossbowman while DK has '
        'no target. At8281 actual core defense has DK commitment. Hypothesis: '
        'qualify expanded support by anchor, frontline commitment, or both, keeping '
        '22tile reach and idle-only targeting. These are contextual observations, '
        'not proof those decisions caused either full-game outcome.'),
        'evidence': [{'artifact': str(e), 'sha256': digest(e.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Context-qualified coordinated caster defense: '+name)
    refresh_grounding(p); return p

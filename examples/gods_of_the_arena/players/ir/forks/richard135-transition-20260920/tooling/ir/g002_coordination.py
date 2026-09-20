"""Coaching-grounded joint repair of red rally and quiet-defense transitions."""
from copy import deepcopy
from anchored_support import make as anchored
from policy_ir import digest, refresh_grounding
from g002_review import STUDY

VARIANTS = ['deployed', 'pressure_parent', 'rally', 'release10', 'release20', 'release_all10']


def make(name):
    if name == 'deployed': return anchored('deployed')
    parent = anchored('anchor')
    if name == 'pressure_parent': return parent
    if name not in VARIANTS[2:]: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_g002_' + name
    p['skill']['observe']['operator'] = 'lineup_post_defense'
    p['skill']['observe']['parameters'].update(
        redbranch_refresh_rally=1, redbranch_release_enabled=int(name != 'rally'),
        redbranch_quiet_ticks=480 if name == 'release20' else 240,
        redbranch_tank_quiet_ticks=240 if name == 'release_all10' else (1440 if name == 'release20' else 1080),
        redbranch_hero_home_tiles=24, redbranch_creep_home_tiles=16)
    p['skill']['fallback']['operator'] = 'lineup_counterpush_route'
    p['skill']['fallback']['parameters']['redbranch_rally_spacing'] = 2
    p['goal']['G_defense']['preference'] += (
        ' Defense must end after a bounded period without combat targets or visible '
        'near-base threats. Update active recall destinations separately from duration; '
        'spread role destinations. Preserve rear cover for the declared tank interval.')
    p['goal']['G_wave']['preference'] += (
        ' After a quiet defense, resume the existing creep-backed lane objective '
        'selection instead of indefinitely repeating the old home rally command.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_g002_post_defense'] = {
        'status': 'untested', 'claim': (
            'Exact coached red loss ereq_4d7cce70 contains two consecutive20second '
            'windows with DK/Lich/Warlock repeating walkTo(103,9), no target, '
            'no new basic hits and under0.42tile displacement. At2880 defense '
            'expiry9710 persists despite no visible enemy hero. This is an explicit '
            'shared waiting order, not evidence of a failed outward path. '
            'Hypothesis: spread destinations and separate the current rally point '
            'from lease renewal; add bounded quiet release with nearby threat '
            'protection, then measure actual exit, objective pressure and wins. '
            'The session captured an unrelated Pudge policy; only human GotA '
            'coaching and exact native GotA evidence ground this change.'),
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='G002 coached post-defense transition and rally repair: ' + name)
    refresh_grounding(p); return p

"""Match item spending to sustained structure damage and the committed push."""
from copy import deepcopy
from coached_strike import make as strike_make
from policy_ir import HERE, read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-loadout'
VARIANTS = {
    'damage': ('current', [11, 13, 18, 19, 16]),
    'armor': ('current', [11, 16, 18, 19, 20]),
    'sword': ('current', [13, 11, 18, 19, 16]),
    'boots': ('current', [8, 11, 13, 16, 18]),
    'focus_damage': ('focus6', [11, 13, 18, 19, 16]),
    'focus_armor': ('focus6', [11, 16, 18, 19, 20]),
}


def make(name):
    base, items = VARIANTS[name]
    parent = read(HERE / 'win_bounded_0916.r5.evaluated.ir.json') if base == 'current' else strike_make(base)
    p = deepcopy(parent)
    p['id'] = 'gota_coached_loadout_' + name
    p['skill']['equipment'] = {'operator': 'buy_ordered_loadout', 'parameters':
                              {slot + '_item': item for slot, item in
                               zip(['first', 'second', 'third', 'fourth', 'fifth'], items)}}
    p['goal']['G_fort']['preference'] += (
        ' Spend on the explicit ordered loadout to increase sustained structure damage, '
        'with configured armor timing. Preserve consumables and evaluate wins, gear purchases, '
        'and survival jointly; items have no hero-class purchase restriction.')
    ref = RUN / 'coached-lanes/r5-pressure/screen/result.json'
    p['belief']['claims']['B_loadout_coaching'] = {
        'claim': 'The lane-focused combat variant beat bounded in all four local matches but '
                 'lost one of four default matchups and suffered many deaths. None qualified. '
                 'Test an explicit damage/armor progression with both the successful deployed '
                 'navigation and the coached center push; changing item and macro components '
                 'jointly may alter the tower race. Current source item stats ground the proposal, '
                 'but this candidate has no validated competitive improvement.',
        'status': 'untested', 'evidence': [{'artifact': str(ref), 'sha256': digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                        change='Coached structure race and ordered equipment: '+name,
                        needs_review=['belief/B_loadout_coaching', 'goal/G_fort', 'goal/G_survival'])
    refresh_grounding(p)
    return p

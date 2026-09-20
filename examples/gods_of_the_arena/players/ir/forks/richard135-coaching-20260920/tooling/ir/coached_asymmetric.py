"""Keep red's validated equipment while improving blue's structure damage."""
from coached_loadout import make as loadout_make
from policy_ir import digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-asymmetric'
VARIANTS = {'blue_damage': 0, 'preserve_red_magic': 1}


def make(name):
    parent = loadout_make('damage')
    p = loadout_make('damage')
    p['id'] = 'gota_coached_asymmetric_' + name
    p['skill']['equipment']['operator'] = 'selective_loadout'
    p['skill']['equipment']['parameters']['red_loadout'] = VARIANTS[name]
    p['goal']['G_fort']['preference'] = (
        'Preserve bounded pursuit, existing wave escort, and class combat. Blue heroes use '
        'Crimson Dagger, Sunsteel Longsword, Battle Axe, Rune Crossbow, then Knight Armor. '
        'Red heroes use the validated class loadout except the explicitly configured non-magic '
        'red branch. Preserve purchasing and consumables while winning the structure race.')
    ref = RUN / 'coached-lanes/r5-loadout/local/result.json'
    p['belief']['claims']['B_asymmetric'] = {
        'claim': 'The universal damage plan won37/40 versus deployed29/40, including20/20 '
                 'direct matches, but failed the unchanged default gate with17/20 versuscontrol19/20. '
                 'Red accounts for all three default losses; blue won every matchup. '
                 'Reject universal deployment. Test preserving red equipment while applying the '
                 'ordered plan to blue, optionally extending to red non-magic heroes. This is '
                 'a new hypothesis requiring fresh cases, not a relaxed gate.',
        'status': 'untested', 'evidence': [{'artifact': str(ref), 'sha256': digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                        change='Lineup-specific damage loadout: '+name,
                        needs_review=['belief/B_asymmetric', 'goal/G_fort'])
    refresh_grounding(p)
    return p

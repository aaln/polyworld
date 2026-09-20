"""Replay-guided defense repair without changing the deployed/frozen XP policy."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,read,refresh_grounding
from release_workspace import RUN
from rush_sentries import STUDY as PARENT

STUDY=RUN/'coached-lanes/r5-richard-unblock'
VARIANTS=['deployed_parent','spread','core_wave','combined','wide_combined',
          'release_20','release_30','release_60']


def make(name):
    parent=read(PARENT/'deployment-requested/policy/policy.ir.json')
    if name=='deployed_parent':return parent
    p=deepcopy(parent);p['id']='gota_defense_unblock_'+name
    if name in ['core_wave','combined','wide_combined'] or name.startswith('release_'):
        p['skill']['observe']={'operator':'core_wave_defense','parameters':
            CONTRACTS['core_wave_defense'].defaults() | parent['skill']['observe']['parameters']}
        if name=='wide_combined':p['skill']['observe']['parameters']['core_radius']=18
        if name.startswith('release_'):
            p['skill']['observe']={'operator':'released_defense','parameters':
                CONTRACTS['released_defense'].defaults() | p['skill']['observe']['parameters'] |
                {'quiet_ticks':int(name.split('_')[1])*24}}
    if name in ['spread','combined','wide_combined'] or name.startswith('release_'):
        p['skill']['fallback']={'operator':'spread_defense','parameters':
            CONTRACTS['spread_defense'].defaults() | parent['skill']['fallback']['parameters']}
    evidence=STUDY/'analysis.json'
    p['belief']['claims']['B_rally_and_core']={
        'claim':'User-reported league loss ereq_6226f76f is actually against relh133, on '
                'the latest deployed sentry policy. Full source-matched replay shows repeated '
                'identical walk destinations for multiple defenders; at720seconds three '
                'sentries remain near(90,5), while six visible enemy creeps near(102,13) '
                'attack the own god, which has52HP. It dies at721.17seconds. This shows '
                'stale rally/target selection; the screenshot alone cannot establish collision '
                'physics as sole cause. Test separate hero rally points and a visible core-wave '
                'emergency override together and separately. Keep current deployed tests frozen. '
                'Richard69 and relh133 are prioritized named-opponent tests; no claim of improvement yet.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Protect the actual god from observed creep waves even when the remembered hero rush was elsewhere; spread defensive rally destinations across heroes.'
    if name.startswith('release_'):
        p['goal']['G_defense']['preference']+=' Release stale defensive duty after a bounded interval without observed pressure; resume wave offense and reacquire future threats from shared vision.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                        change='Replay-guided rally/core-defense repair: '+name,
                        needs_review=['belief/B_rally_and_core','goal/G_defense','goal/G_wave'])
    refresh_grounding(p);return p

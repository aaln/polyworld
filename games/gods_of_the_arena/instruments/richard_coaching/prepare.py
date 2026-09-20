"""Build the complete coached behavior through native compile/extract parity."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import pprint
import sys

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent/'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CLEAN))
from policy_ir import read, write, digest, refresh_grounding, bundle, compile_policy, extract
from games.gods_of_the_arena.instruments.richard_coaching import contracts

STUDY = ROOT/'tmp/gota-ir/richard-coaching-20260920'
CAMPAIGN = ROOT.parent/'gota-autoresearch'
PARENT = ROOT/'examples/gods_of_the_arena/players/ir/forks/jordan268'
CRITICAL = ROOT/'tmp/gota-ir/richard-counter-20260920/candidates/critical60'
NAMES = ('deployed','formation2400','formation3600','formation2400_weapon')


def make(name):
    baseline = read(PARENT/'policy.ir.json')
    assert compile_policy(baseline).encode() == (PARENT/'policy.bas').read_bytes()
    if name == 'deployed':
        return baseline
    p = deepcopy(read(CRITICAL/'policy.ir.json'))
    assert compile_policy(p).encode() == (CRITICAL/'policy.bas').read_bytes()
    p['id'] = 'gota_richard_coaching_' + name
    p['skill']['observe']['operator'] = contracts.NAME
    p['skill']['observe']['parameters'].update(phase_tick=3600 if name=='formation3600' else 2400,
        group_radius=14, tether_radius=20, ready_hp=120, probe_ticks=480, home_radius=50)
    p['skill']['attack']['operator'] = 'richard_formation_combat_v1'
    p['skill']['fallback']['operator'] = 'richard_formation_route_v1'
    if name == 'formation2400_weapon':
        p['skill']['equipment']['parameters']['red_loadout'] = 1
    p['situation']['notes'] += (
        ' Coaching2026-09-20t17-21-56-307zf4f7b3 is bound to audited episode '
        'ereq_15e13437-273d-4c4f-84cc-162b01b602b4: historical bound_idle red '
        'against exact Richard135 blue. New comparison baseline is current deployed '
        'be6aff, not an empty captured input. Late red phase begins at the authored '
        'phase_tick, not a claimed inferred Richard threshold. Allies_concentrated '
        'means four living allies with HP>=120 within14integer tiles of living-team '
        'centroid. Near_base_perimeter means that centroid within60tiles of the '
        'enemy god; enemy_spread_out requires at least3currently visible enemies '
        'and their bounding-box diagonal>=32tiles. Hidden enemies remain unknown.')
    p['goal']['G_group_siege'] = {'preference':
        'During coached red phase, prioritize a coherent four/five-hero objective '
        'group over separate wave escorts and solo base dives. Gather, probe the '
        'enemy perimeter, update the breach entry, then focus a shared visible '
        'hero or exposed structure. Regroup after loss of readiness. Gathered home '
        'defense supersedes siege under observed critical pressure. Preserve blue '
        'critical60 behavior and validate actual fort wins separately.', 'provenance':'authored'}
    p['belief']['claims']['CoachedFormation'] = {'claim':
        'The coach hypothesizes that Richard wins by concentrating4–5heroes while '
        'ours disperse. The combined readiness, tether, entry selection, probing '
        'and assault controller may counter that numerical disadvantage. No '
        'individual edit is required to improve independently. This hypothesis '
        'is not competitive validation or recovered opponent source.',
        'status':'untested','evidence':[{'artifact':str(STUDY/'session-inputs/notes.md')},
            {'artifact':str(STUDY/'session-binding.json')}]}
    p['belief']['claims']['RichardBlueComponent'] = {'claim':
        'Exact critical60 won40/40fresh blue versus Richard135 with all ten VMs '
        'and full replay audits. Retaining its blue execution in this new '
        'combined executable still requires parity and fresh confirmation.',
        'status':'supported','evidence':[{'artifact':str(CAMPAIGN/'adaptive-opponent-20260920/critical-blue-confirmation/critical60/arm-result.json')}]}
    for rule in p['strategy']:
        if rule['skill'] in ('observe','attack','fallback'):
            rule['for'].append('G_group_siege')
    p['update'].update(revision=baseline['update']['revision']+1,parent=digest(baseline),
        change={'origin':'User coaching session2026-09-20t17-21-56-307zf4f7b3',
                'coordinated_behavior':'GroupProbeAndCircleBase + SynchronizedTeamAssault',
                'candidate':name,'blue_component':str(CRITICAL),
                'session_references':str(STUDY/'captured-inputs.json')},
        needs_review=['belief/CoachedFormation','goal/G_group_siege'])
    refresh_grounding(p)
    return p


def prepare():
    STUDY.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        dest=STUDY/'candidates'/name
        p=make(name)
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True)
            bundle(p,dest)
            (dest/'policy.py').write_text('"""Primary IR: combined coached team behavior."""\n\nPOLICY = '
                +pprint.pformat(p,width=110,sort_dicts=False)+'\n')
        assert compile_policy(p).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(p),p)==p
    c=read(CAMPAIGN/'config.json')
    if not (STUDY/'plan.json').exists():
        write(STUDY/'config.json',c['game_config'])
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in NAMES}
        opponents={'default':str(ROOT.parent/'gota-research-20260916/r5/default.bas'),
            'deployed':sources['deployed'],
            'historical_bound':str(CAMPAIGN/'historical-richard-review-20260920/references/bound_idle/policy.bas')}
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts.__file__),Path(__file__),STUDY/'config.json',STUDY/'captured-inputs.json']
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9870000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'game_version':c['game_version'],'engine_commit':c['engine_commit'],
            'gate':{'fidelity':'Native scenarios prove early/blue parity, four-person readiness, dispersion unknown handling, tether, home override and combined assault.',
                'runtime':'All local games and dense scenarios within native budgets; complete replay/audit/equipment validation.',
                'local_comparison':'Report every candidate/control cell and deaths. Local play is a mechanism/regression diagnostic, not a Richard proxy or proof of field preservation.',
                'Richard_discovery':'Each eligible executable fresh40games bothcolors versus exact135; >=30/40EACH and >=8aggregate wins over fresh deployed control. Rank candidates first by minimum side wins, then aggregate, then fewer deaths. All failures retained.',
                'promotion':'Existing all-target/field/survival requirements retained. No promotion from local or Richard-only win.'},
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'48 complete local games, then hosted combined-behavior diagnostic only after fidelity/runtime checks. No component-alone gain requirement.'})
    print(json.dumps({'study':str(STUDY),'sources':{n:digest((STUDY/'candidates'/n/'policy.bas').read_bytes()) for n in NAMES}},indent=2))


if __name__=='__main__':prepare()

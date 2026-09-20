"""Prospective mixed-team guardrail for a policy that first beats all rush rivals."""
import argparse
import random
import shutil
from pathlib import Path

from campaign_hosted_compare import cohort
from coached_league_live import arm_plan, AARON, OPTIMIZER, CONTROL
from command_diversity import inventory
from economy_feedback import record
from hosted_queue import run as run_queue
from hosted_wave import client, get, create
from hosted_batch import batch_body
from policy_ir import read, write, digest
from release_deploy_pair import clone_for_aaron
from release_hosted import summarize
from release_workspace import RUN
from rush_defense import STUDY
from win_hosted import live

ROOT = STUDY/'paired-guardrail'
NAME = 'blue_memory'
EXPLORATORY = False
DIAGNOSTIC_ONLY = False
GATES = {'minimum_allied_gain': -.05, 'maximum_roster_regression': .10,
         'maximum_allied_class_regression': .30, 'no_additional_opposed_draws': True,
         'minimum_field_allied_win_rate': .70}


def freeze():
    game = live()
    ROOT.mkdir(parents=True, exist_ok=True)
    if (ROOT/'plan.json').exists():
        plan = read(ROOT/'plan.json')
        if game['id'] != plan['target']['coworld_id']:
            raise ValueError('Live release changed')
        return plan
    candidate = STUDY/'hosted'/NAME
    gate = read(candidate/'gate.json') if (candidate/'gate.json').exists() else None
    if not EXPLORATORY and (not gate or not gate['passed']):
        raise ValueError('Candidate must first pass the complete named-rival rush benchmark')
    meta, version = read(candidate/'upload-request.json'), read(candidate/'uploaded-version.json')
    source = (STUDY/'local/candidates'/NAME/'policy.bas').read_bytes()
    with client() as c:
        champions = get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
        write(ROOT/'champions.json', champions)
        clone = clone_for_aaron(c, ROOT, meta, source,
                               'Experimental defense clone for user-requested ten-player tests; local60cases complete, named-rival results may be pending. No champion selection.'
                               if EXPLORATORY else 'Experimental defense clone for mixed-team guardrail; passed local60cases and named-rival240games. No champion selection.')
    parent = read(STUDY/'hosted-plan.json')
    core = parent['rivals']
    if EXPLORATORY:
        active = {r['player']['id']:r for r in champions if r['status']=='competing' and r['substatus']=='active'}
        core = [{'id':active[r['player_id']]['policy_version']['id'],
                 'label':active[r['player_id']]['policy_version']['label'],
                 'player_id':r['player_id']} for r in core]
    excluded = {AARON, OPTIMIZER} | {r['player_id'] for r in core}
    others = sorted([{'id': r['policy_version']['id'], 'label': r['policy_version']['label'],
                      'player_id': r['player']['id']} for r in champions if r['player']['id'] not in excluded
                     and r['status'] == 'competing' and r['substatus'] == 'active'], key=lambda r:r['label'])
    if len(others) < 5:
        raise ValueError('Need eight other distinct players per lineup')
    random.Random(7590916).shuffle(others)
    lineups = [{'partner_slot': slot, 'other_players': core+[others[(5*i+j)%len(others)] for j in range(5)]}
               for i, slot in enumerate([1, 9])]
    plan = {k: parent[k] for k in ['target', 'game_version', 'game_source', 'config']}
    plan.update(control_versions=CONTROL, candidate_versions=[version['id'], clone['id']],
                lineups=lineups, gates=GATES,
                exploratory=EXPLORATORY,
                diagnostic_only=DIAGNOSTIC_ONLY,
                rush_gate_sha256=digest((candidate/'gate.json').read_bytes()) if gate else None,
                basic_sha256=digest(source),
                design='Fresh400games: two fixed100episode rosters per arm, both owned players plus '
                       'eight other distinct players. Reverse adjacent partner placement across rosters '
                       'so every focal hero class appears in allied games. Perarm160allied+40opposed. '
                       'Primarypurpose is mixed-team nonregression after measured two-player rush '
                       'improvement, not a claim of mixed-team superiority. Frozen observed guardrail: '
                       'pooled allied loss<=5pp, each roster loss<=10pp, each allied focal class '
                       'loss<=30pp, no additional opposed draws, allgear andfulltenVM/replay checks. '
                       'Report combat deaths/alivemin as a separate tradeoff: defense engages fights '
                       'that the baseline ignored. Do not tune between arms. This new candidate and '
                       'guardrail do not reinterpret the rejected gear-only800game experiment. '
                       'Then100sampled paired-player fieldgames with>=70%alliedwins. No league '
                       'selection until all rush, mixed andfield evidence is complete.')
    if EXPLORATORY:
        plan['design'] += (' User explicitly requested ten-player XP matches alongside all-leader tests. '
                          'Run this diagnostic comparison before the rush verdict if needed; this '
                          'does not bypass any deployment criteria. Pin current champion versions '
                          'for the three rush players as well as the remaining roster.')
    if DIAGNOSTIC_ONLY:
        plan['design'] = ('User requested200ten-playergames with the latest iteration. Run only '
                          'the candidate in two pinned100episode rosters, bothownedplayers plus '
                          'eight otherdistinctplayers. Reverseadjacent partnerplacement covers '
                          'everyclass allied:160allied+40opposed total. This is a diagnostic '
                          'performance sweep without a fresh matchedbaseline; do not claim '
                          'improvement from its win rate. Allreplay/source/tenVM/ownership/gear '
                          'checks retained. The earlier400game comparison design is deferred, '
                          'not passed. No champion selection.')
    write(ROOT/'plan.json', plan)
    return plan


def run():
    plan = freeze()
    for i in range(2):
        for arm in ['control', 'candidate']:
            out = ROOT/arm/f'part-{i}'
            out.mkdir(parents=True, exist_ok=True)
            p = arm_plan(plan, arm, i)
            if (out/'plan.json').exists() and read(out/'plan.json') != p:
                raise ValueError('Frozen mixed guardrail changed')
            write(out/'plan.json', p)
            shutil.copy2(RUN/'r5/audit', out/'audit')
            if (out/'audit-progress.json').exists() and read(out/'audit-progress.json')['verified'] == 100:
                continue
            live()
            with client() as c:
                create(c, batch_body(p, 100), out/'batch', dry_run=True)
            run_queue([out])
    report()


def report():
    plan = freeze()
    parts, arms, seen = {}, {}, set()
    for arm in ['control', 'candidate']:
        parts[arm] = []
        for i in range(2):
            out = ROOT/arm/f'part-{i}'
            if read(out/'plan.json') != arm_plan(plan, arm, i):
                raise ValueError('Arm differs from frozen design')
            part = cohort(out, 2)
            for row in part['rows']:
                if row['seed'] in seen:
                    raise ValueError('Seed reused across arms')
                seen.add(row['seed'])
                ep, audit = [read(out/'artifacts'/row['episode']/n) for n in ['episode.json','audit.json']]
                expected = {r['id']:r['player_id'] for r in arm_plan(plan, arm, i)['opponents']}
                expected[plan[arm+'_versions'][0]] = OPTIMIZER
                if {p['position']:p['player_id'] for p in ep['participants']} != {
                        s:expected[v] for s,v in enumerate(ep['policy_version_ids'])}:
                    raise ValueError('Actual owners differ from both-player plan')
                partner = ep['policy_version_ids'].index(plan[arm+'_versions'][1])
                buddy = audit['heroes'][partner]
                row.update(roster_index=i, partner_slot=partner, allied=partner//5 == row['slot']//5,
                           partner_win=buddy['score'], partner_deaths=buddy['deaths'],
                           partner_alive_ticks=buddy['alive_ticks'], partner_gear=buddy['first_gear_tick'] >= 0)
            parts[arm].append(part)
        total = summarize(parts[arm]); rr = total['rows']
        allied, opposed = [r for r in rr if r['allied']], [r for r in rr if not r['allied']]
        if len(allied) != 160 or len(opposed) != 40:
            raise ValueError('Allied/opposed coverage mismatch')
        total.update(allied_wins=sum(r['win'] for r in allied),
                     opposed_draws=sum(not r['win'] and not r['partner_win'] for r in opposed),
                     both_bought_equipment=sum(r['first_gear_tick'] >= 0 and r['partner_gear'] for r in rr),
                     pair_death_rate=sum(r['deaths']+r['partner_deaths'] for r in rr)*1440/
                                     sum(r['alive_ticks']+r['partner_alive_ticks'] for r in rr),
                     allied_classes={c: {'games':len(cr := [r for r in allied if r['class'] == c]),
                                         'wins':sum(r['win'] for r in cr)} for c in {r['class'] for r in rr}})
        arms[arm] = total
    a,b = arms['candidate'],arms['control']
    gains = [(sum(r['win'] for r in parts['candidate'][i]['rows'] if r['allied'])-
              sum(r['win'] for r in parts['control'][i]['rows'] if r['allied']))/80 for i in range(2)]
    gates = plan['gates']
    checks = {'allied_nonregression': (a['allied_wins']-b['allied_wins'])/160 >= gates['minimum_allied_gain'],
              'roster_nonregression': all(g >= -gates['maximum_roster_regression'] for g in gains),
              'allied_classes': all(v['games'] >= 10 and v['games'] == b['allied_classes'][c]['games'] and
                                   (v['wins']-b['allied_classes'][c]['wins'])/v['games'] >=
                                   -gates['maximum_allied_class_regression'] for c,v in a['allied_classes'].items()),
              'opposed_draws': a['opposed_draws'] <= b['opposed_draws'],
              'equipment': a['both_bought_equipment'] == 200}
    result = {'arms':arms, 'checks':checks, 'passed':all(checks.values()),
              'allied_roster_gains':gains, 'design':plan['design'],
              'interpretation':'Observed fixed-roster guardrail; not a formal independent-trial noninferiority claim. Field evidence still required.'}
    write(ROOT/'result.json', result)
    inventory(ROOT)
    if not (ROOT/'feedback').exists():
        parent = STUDY/'hosted'/NAME/'feedback'
        record(parent/'policy.ir.json',parent/'policy.bas',
               f'New defense mixed guardrail400games: allied {a["allied_wins"]}/160 vs{b["allied_wins"]}/160; '
               f'checks{checks}; pair deaths/alivemin {a["pair_death_rate"]} vs{b["pair_death_rate"]}. '
               +result['interpretation'], ROOT/'result.json', ROOT/'feedback')
    print(checks, flush=True)


def report_diagnostic():
    plan=freeze()
    if not plan.get('diagnostic_only'):raise ValueError('Not a candidate-only diagnostic plan')
    parts=[];seen=set()
    for i in range(2):
        out=ROOT/'candidate'/f'part-{i}'
        part=cohort(out,2)
        for row in part['rows']:
            if row['seed'] in seen:raise ValueError('Repeated diagnostic seed')
            seen.add(row['seed'])
            ep,audit=[read(out/'artifacts'/row['episode']/n) for n in ['episode.json','audit.json']]
            expected={r['id']:r['player_id'] for r in arm_plan(plan,'candidate',i)['opponents']}
            expected[plan['candidate_versions'][0]]=OPTIMIZER
            if {p['position']:p['player_id'] for p in ep['participants']}!={s:expected[v] for s,v in enumerate(ep['policy_version_ids'])}:
                raise ValueError('Wrong actual owners')
            partner=ep['policy_version_ids'].index(plan['candidate_versions'][1])
            buddy=audit['heroes'][partner]
            row.update(roster_index=i,partner_slot=partner,allied=partner//5==row['slot']//5,
                       partner_win=buddy['score'],partner_gear=buddy['first_gear_tick']>=0)
        parts.append(part)
    total=summarize(parts);rows=total['rows']
    allied=[r for r in rows if r['allied']];opposed=[r for r in rows if not r['allied']]
    if len(allied)!=160 or len(opposed)!=40:raise ValueError('Wrong paired coverage')
    result={'games':200,'allied_games':160,'allied_wins':sum(r['win'] for r in allied),
            'opposed_games':40,'opposed_optimizer_wins':sum(r['win'] for r in opposed),
            'opposed_aaron_wins':sum(r['partner_win'] for r in opposed),
            'both_equipment_games':sum(r['first_gear_tick']>=0 and r['partner_gear'] for r in rows),
            'passed':False,'verdict':'Diagnostic only; a matched improvement/promotion gate was not run.',
            'design':plan['design'],'rows':rows}
    write(ROOT/'result.json',result);inventory(ROOT)
    if not (ROOT/'feedback').exists():
        parent=STUDY/'local/context-feedback'/NAME
        record(parent/'policy.ir.json',parent/'policy.bas',
               f'Latestiteration tenplayerdiagnostic200games: allied{result["allied_wins"]}/160; '
               f'bothgear{result["both_equipment_games"]}/200. No matchedbaseline, no improvement claim. '
               'Fortwin remains primary; glory uses200XP/minute. Separate opposed results retained.',
               ROOT/'result.json',ROOT/'feedback')
    print({k:v for k,v in result.items() if k!='rows'},flush=True)


def field():
    import coached_pair_field
    coached_pair_field.STUDY = ROOT
    coached_pair_field.ROOT = ROOT/'field'
    coached_pair_field.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['freeze','run','report','field'])
    parser.add_argument('--study', type=Path)
    parser.add_argument('--candidate', default=NAME)
    parser.add_argument('--exploratory', action='store_true')
    args=parser.parse_args()
    if args.study:
        STUDY=args.study.resolve()
        ROOT=STUDY/'paired-guardrail'
    NAME=args.candidate
    EXPLORATORY=args.exploratory
    globals()[args.command]()

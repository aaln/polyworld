"""Frozen user-requested relh154/Jordan228 side-swapped candidate guardrails."""
from datetime import datetime, timezone
import httpx

from economy_feedback import record
from hosted_wave import client, create, episodes
from jordan_lineup_guardrails import pin_auditor
from macromackie_middle_rush import STUDY
from policy_ir import digest, read, write, compile_policy, extract
from ranger_guard_hosted import freeze
from red_pressure_hosted import result
from win_hosted import live

ROOT = STUDY / 'tournament-guards'
RIVALS = [('relh154', 'relh-gods-of-the-arena:v154'),
          ('jordan228', 'Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v228')]
DESIGN = ('User-requested exact new tournament opponents relh154 andJordan228. '
          'Same immutable middle-rush candidate; five heroes per policy,40episodes '
          'each color per rival. Normal policy_ref label resolution then exact '
          'UUID/name/version/roster validation. Full runtime/replay/gear audits. '
          'Per-rival guard passes only>=38wins/40 on both colors; no interim tuning. '
          'Repeated trajectories, directional matchup evidence; no automatic promotion.')


def one(key, label, version):
    live()
    root = ROOT/key
    root.mkdir(parents=True, exist_ok=True)
    ref = read(STUDY/'hosted/blue_three/macromackie-v4/plan.json')
    folder = root/'named/red'
    folder.mkdir(parents=True, exist_ok=True)
    body = {'idempotency_key': 'gota-middle-guard-'+digest({'study':str(ROOT),'label':label,'own':version['id']})[:20],
            'target': ref['target'], 'game_config_overrides': ref['config'], 'num_episodes':40,
            'roster': [{'slot':s,'player':{'policy_ref':version['id'] if s<5 else label}} for s in range(10)],
            'notes': DESIGN+' Candidate red versus '+label}
    with client() as c:
        create(c,body,folder/'batch',dry_run=True)
        try:
            request = create(c,body,folder/'batch')
        except httpx.HTTPStatusError as error:
            write(root/'unavailable.json', {'label':label,'status':error.response.status_code,
                  'detail':error.response.json(),'time':datetime.now(timezone.utc).isoformat()})
            if error.response.status_code not in (400,403,404):
                raise
            print('UNAVAILABLE',label,error.response.status_code,flush=True)
            return None
        eps = read(folder/'batch/created.json').get('episodes') or episodes(c,request)
    if not eps:
        raise ValueError('No resolved episode roster')
    rivals = {p['policy_version_id']:p for e in eps for p in e['participants'] if p['position']>=5}
    if len(rivals)!=1:
        raise ValueError('Ambiguous rival resolution')
    rid, rival = next(iter(rivals.items()))
    name, n = label.rsplit(':v',1)
    if rival['policy_name']!=name or rival['version']!=int(n):
        raise ValueError('Named rival mismatch')
    if key=='jordan228' and rival['player_id']!='ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb':
        raise ValueError('Jordan owner mismatch')
    if any(e['policy_version_ids']!=[version['id']]*5+[rid]*5 for e in eps):
        raise ValueError('Unexpected resolved roster')
    freeze(root/'resolved-target.json', {'label':label,'id':rid,'player_id':rival['player_id'],
           'player_name':rival['player_name'],'resolved_from_xreq':request})
    print('RESOLVED',label,rid,request,flush=True)
    plan = {k:ref[k] for k in ('target','game_version','game_source','config','episodes_per_color','interpretation')}
    plan.update(policy_version=version['id'],policy_label=version['name']+':v'+str(version['version']),
                rival=label,rival_version=rid,rival_key='named',design=DESIGN)
    freeze(root/'plan.json',plan)
    for color in ('red','blue'):
        arm = root/'named'/color
        arm.mkdir(parents=True,exist_ok=True)
        slots = list(range(5)) if color=='red' else list(range(5,10))
        roster = [version['id'] if s in slots else rid for s in range(10)]
        freeze(arm/'plan.json',plan|{'color':color,'own_slots':slots,'roster':roster})
        pin_auditor(arm)
        if color=='blue':
            blue = body|{'idempotency_key':body['idempotency_key']+'-blue',
                   'roster':[{'slot':s,'player':{'policy_ref':v}} for s,v in enumerate(roster)],
                   'notes':DESIGN+' Candidate blue versus '+label}
            with client() as c:
                create(c,blue,arm/'batch',dry_run=True)
    cohort = result(root)
    passed = all(cohort['colors'][color]['win']>=38 for color in ('red','blue'))
    write(root/'guard-verdict.json', {'passed':passed,'result':cohort,'promotion_performed':False})
    return {'passed':passed,'result':cohort,'resolved_target':read(root/'resolved-target.json')}


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    version = read(STUDY/'hosted/blue_three/uploaded-version.json')
    source = STUDY/'hosted/blue_three/reviewed-feedback'
    ir, basic = read(source/'policy.ir.json'), (source/'policy.bas').read_bytes()
    assert compile_policy(ir).encode()==basic and extract(basic.decode(),ir)==ir
    freeze(ROOT/'prospective.json', {'design':DESIGN,'rivals':RIVALS,'policy':version['id'],
           'basic_sha256':digest(basic),'games_per_rival':80,'maximum_games':160,
           'minimum_wins_per_color':38,'promotion':False})
    results = {}
    for key,label in RIVALS:
        results[key] = one(key,label,version)
        write(ROOT/'progress.json', {'results':results})
    passed = all(r is not None and r['passed'] for r in results.values())
    write(ROOT/'result.json', {'passed':passed,'results':results,'scope':DESIGN,'promotion_performed':False})
    if not (ROOT/'evaluated-feedback').exists():
        record(source/'policy.ir.json',source/'policy.bas',
            'Completed named tournament guardrails: '+str({n:None if r is None else r['result']['colors'] for n,r in results.items()})+
            f'. Both guards pass={passed}. Original macromackie80/80 preserved as distinct evidence. '
            'No automatic promotion; broad mixed-player field still untested.',
            ROOT/'result.json',ROOT/'evaluated-feedback')
    print('FINAL GUARDS',passed,{n:None if r is None else r['result']['colors'] for n,r in results.items()},flush=True)


if __name__=='__main__':
    main()

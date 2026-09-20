"""Frozen multi-candidate screen, followed by one fresh 240-case confirmation.

Usage: python motion_campaign.py DIRECTORY --stage screen --workers 12
       python motion_campaign.py DIRECTORY --stage confirmation --workers 12
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import shutil
import subprocess
from hypothesis_study import sign_p
from policy_ir import HERE, ROOT, digest, read, write
from motion_candidates import VARIANTS


def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--stage',choices=['screen','confirmation'],default='screen')
    parser.add_argument('--workers',type=int,default=12)
    args=parser.parse_args();d=args.directory.resolve()
    if not (d/'plan.json').exists():
        shutil.copy2(ROOT/'tmp/gota-ir/hit-kite-20260915/config.json',d/'config.json')
        shutil.copy2(ROOT/'tmp/gota-ir/hit-kite-20260915/audit',d/'audit')
        shutil.copy2(HERE/'waveguard_xp.evaluated.bas',d/'v2.bas')
        shutil.copy2(ROOT/'tmp/gota-ir/runtime-2026.9.15.3/examples/gods_of_the_arena/players/base.bas',d/'default.bas')
        sources={'v2':d/'v2.bas','default':d/'default.bas'} | {n:d/'candidates'/n/'policy.bas' for n in VARIANTS}
        rng=random.Random(2026091518)
        def cases(start,n):
            slots=list(range(10))*(n//10);rng.shuffle(slots)
            return [{'seed':start+i,'slot':s} for i,s in enumerate(slots)]
        inputs=[d/'episode',d/'audit',d/'config.json',*sources.values()]
        instruments=['motion_campaign.py','motion_candidates.py','motion_contract.py','episode_motion.nim',
                     'binding.py','policy_ir.py','basic_syntax.py','independent_ir.py','kiting_contract.py','hypothesis_study.py','audit_current.nim']
        frozen=d/'frozen-instruments';frozen.mkdir()
        for n in instruments:shutil.copy2(HERE/n,frozen/n)
        plan={'created_at':datetime.now(timezone.utc).isoformat(),'game_version':'2026.9.15.3',
              'source':'e1279894d10a7684f303e7a9f1ea2f84c1d14253','variants':VARIANTS,
              'sources':{k:str(p) for k,p in sources.items()},
              'inputs':{str(p):digest(p.read_bytes()) for p in inputs},
              'instruments':{n:digest((frozen/n).read_bytes()) for n in instruments},
              'screen':cases(723000,40),'confirmation':cases(724000,240),
              'screen_rule':'Finish every arm/case and replay audit. Eligible shortlist: >=2 added fort wins against BOTH v2 and default, deaths per alive minute <=110% of v2, XP>=80% of v2. Choose ONE by win count, then lower death rate, then greater XP, then name. Mechanism counters must activate and no normal retreat may precede an actual hit. Discovery only; no significance claim after selecting among ten variants.',
              'confirmation_rule':'240 fresh independent seeds, balanced24/class, selected candidate plus exact v2 and default. Require >=5 percentage-point win gain and one-sided exact paired discordance p<.025 against EACH control, death rate <=110% of v2, XP>=80% of v2, no class-specific adverse win flag at .05/10. Full tape parity and real-host budget/loading checks required. One candidate only; failed seeds may not become a fresh confirmation of a revised policy.',
              'hosted_rule':'Only a local qualifier advances. Freeze nine incumbent versions and the current published game. Independent hosted seed cohorts, one100-episode XP request per arm; require >=10pp gain and one-sided Fisher exact p<.05 for candidate vs v2. Any incomplete/invalid artifacts block the comparison. Inspect survival/replays. A separate40-episode field guardrail precedes league promotion. If underpowered, retain the negative/inconclusive result; no promotion from local scores alone.',
              'stop_rule':'No optional stopping, dropped seeds, changed arms or thresholds after observing results. Failed/incomplete runs retained and recovered with identical frozen inputs. User explicitly authorizes multiple hypotheses/combinations; their selection is separated from fresh confirmation.'}
        write(d/'plan.json',plan)
    plan=read(d/'plan.json')
    for path,sha in plan['inputs'].items():
        if digest(Path(path).read_bytes())!=sha:raise ValueError('Frozen input changed: '+path)
    for name,sha in plan['instruments'].items():
        if digest((d/'frozen-instruments'/name).read_bytes())!=sha:raise ValueError('Frozen instrument changed')
    names=list(plan['sources'])
    if args.stage=='confirmation':
        screen=read(d/'screen-result.json')
        if not screen['selected']:raise ValueError('No candidate qualified for fresh confirmation')
        names=['v2','default',screen['selected']]
        selection={'candidate':screen['selected'],'screen_sha256':digest((d/'screen-result.json').read_bytes()),
                   'cases':plan['confirmation'],'sources':{n:plan['inputs'][plan['sources'][n]] for n in names}}
        p=d/'confirmation-selection.json'
        if p.exists() and read(p)!=selection:raise ValueError('Confirmation selection changed')
        write(p,selection)
    cases=plan[args.stage]

    def episode(name,case):
        folder=d/args.stage/name/f"seed-{case['seed']}-slot-{case['slot']}"
        source=plan['sources'][name]
        folder.mkdir(parents=True,exist_ok=True)
        result_path=folder/'result.json'
        if not result_path.exists():
            command=[str(d/'episode'),'--config',str(d/'config.json'),'--seed',str(case['seed']),
                     '--record',str(folder/'episode.replay')]
            command += ['--bot:'+str(source if slot==case['slot'] else d/'default.bas') for slot in range(10)]
            with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
                subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=300,check=True)
            result=json.loads((folder/'stdout.log').read_text().splitlines()[-1])
            result.update(subject_slot=case['slot'],source_sha256=plan['inputs'][source],
                          replay_sha256=digest((folder/'episode.replay').read_bytes()),
                          binary_sha256=plan['inputs'][str(d/'episode')],
                          config_sha256=plan['inputs'][str(d/'config.json')])
            write(result_path,result)
        result=read(result_path)
        if result['seed']!=case['seed'] or result['subject_slot']!=case['slot'] or result['source_sha256']!=plan['inputs'][source]:
            raise ValueError('Cached episode inputs disagree')
        if result['binary_sha256']!=plan['inputs'][str(d/'episode')] or result['config_sha256']!=plan['inputs'][str(d/'config.json')]:
            raise ValueError('Cached engine inputs disagree')
        if result['replay_sha256']!=digest((folder/'episode.replay').read_bytes()):raise ValueError('Replay changed')
        if not (folder/'audit.json').exists():
            process=subprocess.run([str(d/'audit'),'--replay',str(folder/'episode.replay')],cwd=ROOT,
                                   capture_output=True,text=True,timeout=300,check=True)
            audit=json.loads(process.stdout.splitlines()[-1])
            audit.update(replay_sha256=result['replay_sha256'],auditor_sha256=plan['inputs'][str(d/'audit')])
            write(folder/'audit.json',audit)
        audit=read(folder/'audit.json')
        if audit['hash_mismatches'] or audit['ticks']!=result['ticks'] or audit['actions_consumed']!=result['actions'] or audit['state_hash']!=result['state_hash']:
            raise ValueError('Full replay verification failed')
        if audit['replay_sha256']!=result['replay_sha256'] or audit['auditor_sha256']!=plan['inputs'][str(d/'audit')]:
            raise ValueError('Cached audit inputs disagree')
        hero=result['heroes'][case['slot']]
        if hero['deaths']!=audit['heroes'][case['slot']]['deaths']:raise ValueError('Death counter disagrees')
        return {'name':name,'seed':case['seed'],'slot':case['slot'],'ticks':result['ticks'],
                'timeout':result['timeout'],'alive_ticks':audit['heroes'][case['slot']]['alive_ticks'],**hero}

    rows=[]
    jobs=[(name,case) for case in cases for name in names]
    with ThreadPoolExecutor(args.workers) as pool:
        futures=[pool.submit(episode,*job) for job in jobs]
        for f in as_completed(futures):
            rows.append(f.result())
            if len(rows)%12==0:print(f'{args.stage}: {len(rows)}/{len(jobs)} games AND full replay audits complete',flush=True)
    rows.sort(key=lambda x:(x['name'],x['seed']))
    write(d/(args.stage+'-rows.json'),rows)
    metrics={}
    for name in names:
        rr=[r for r in rows if r['name']==name]
        metrics[name]={'games':len(rr),'wins':sum(r['score'] for r in rr),'deaths':sum(r['deaths'] for r in rr),
                       'death_rate':sum(r['deaths'] for r in rr)*1440/sum(r['alive_ticks'] for r in rr),
                       'xp':sum(r['total_xp'] for r in rr),'normal_retreats':sum(r['verified_bursts'] for r in rr),
                       'unverified_retreats':sum(r['unverified_bursts'] for r in rr),
                       'moved_kite_ticks':sum(r['moved_kite_ticks'] for r in rr),
                       'spells':sum(r['kite_spell_casts'] or 0 for r in rr),
                       'motion_completions':sum(r['motion_completions'] or 0 for r in rr),
                       'tower_detours':sum(r['tower_detours'] or 0 for r in rr),
                       'weapon_starts':sum(r['weapon_starts'] or 0 for r in rr),
                       'max_work':max(r['max_work'] for r in rr),'max_instructions':max(r['max_instructions'] for r in rr)}
    def mechanisms(name):
        m=metrics[name];v=plan['variants'][name]
        return (not m['unverified_retreats'] and
                ('motion' not in v or (m['moved_kite_ticks']>0 and (not v['motion'].get('normal',1) or m['normal_retreats']>0))) and
                (not v.get('tower') or m['tower_detours']>0) and (not v.get('weapon') or m['weapon_starts']>0))
    if args.stage=='screen':
        eligible=[n for n in names if n not in ('v2','default') and
                  all(metrics[n]['wins']>=metrics[c]['wins']+2 for c in ('v2','default')) and
                  metrics[n]['death_rate']<=1.1*metrics['v2']['death_rate'] and metrics[n]['xp']>=.8*metrics['v2']['xp'] and mechanisms(n)]
        eligible.sort(key=lambda n:(-metrics[n]['wins'],metrics[n]['death_rate'],-metrics[n]['xp'],n))
        report={'stage':args.stage,'metrics':metrics,'eligible':eligible,'selected':eligible[0] if eligible else None,
                'verified_games':len(rows),'design':'Multi-candidate discovery; no independent superiority claim.'}
    else:
        name=names[-1];comparisons={}
        for control in ('v2','default'):
            cc={r['seed']:r for r in rows if r['name']==control};vv=[r for r in rows if r['name']==name]
            gained=sum(r['score']>cc[r['seed']]['score'] for r in vv)
            lost=sum(r['score']<cc[r['seed']]['score'] for r in vv)
            p=sign_p(gained,lost);delta=(metrics[name]['wins']-metrics[control]['wins'])/len(cases)
            regressions=[]
            for cls in range(10):
                cr=[r for r in vv if r['class']==cls]
                win=sum(r['score']>cc[r['seed']]['score'] for r in cr);loss=sum(r['score']<cc[r['seed']]['score'] for r in cr)
                if sign_p(loss,win)<.05/10:regressions.append(cls)
            comparisons[control]={'gain':delta,'gained_pairs':gained,'lost_pairs':lost,'p':p,'adverse_classes':regressions,
                                  'passed':delta>=.05 and p<.025 and not regressions}
        passed=all(c['passed'] for c in comparisons.values()) and metrics[name]['death_rate']<=1.1*metrics['v2']['death_rate'] and metrics[name]['xp']>=.8*metrics['v2']['xp'] and mechanisms(name)
        report={'stage':args.stage,'candidate':name,'metrics':metrics,'comparisons':comparisons,'passed':passed,'verified_games':len(rows)}
    write(d/(args.stage+'-result.json'),report)
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':run()

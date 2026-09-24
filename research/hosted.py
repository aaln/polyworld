"""Current-engine three-arm recovery comparison across every side/team seat."""
from pathlib import Path
import argparse, importlib.util, json, sys, time
from concurrent.futures import ThreadPoolExecutor
import httpx, jsonschema

ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT/'research/vendor'
spec=importlib.util.spec_from_file_location('recovery_platform',VENDOR/'games/gods_of_the_arena/instruments/neutralfarm20260923/hosted.py')
platform=importlib.util.module_from_spec(spec);spec.loader.exec_module(platform)
h,cc,panel=platform.h,platform.cc,platform.panel
h.ROOT=h.ENGINE=ROOT
h.CAMPAIGN=ROOT.parent/'gota-autoresearch'

def shared_budget_config(campaign):
    """Read shared limits without importing the paused worker's old tooling."""
    cfg=h.read(campaign/'config.json')
    override=cfg.get('daily_episode_limit_override')
    if override and h.research.now()[:10]!=override['utc_day']:
        cfg['daily_episode_limit']=override['normal_limit']
    return cfg

h.research.config=shared_budget_config
RAW=ROOT.parent/'polyworld/tmp/gota-weak-neutral62-20260924'
platform.RAW=cc.RAW=h.STUDY=panel.STUDY=RAW
h.CYCLE='interactive-score-recovery62-20260924'
SOURCES={k:ROOT/'research/policies'/k/'policy.bas' for k in ['deployed','previous','weak-neutral']}
platform.SOURCES=SOURCES

def prepare():
    assert h.read(RAW/'practice.json')['passed'] and h.read(RAW/'native-comparison.json')['passed']
    with h.client() as c:
        game=h.live(c);h.freeze(RAW/'canonical-game.json',game)
        schema=h.get(c,'/openapi.json');h.freeze(RAW/'openapi-preparation.json',schema)
        members=h.get(c,'/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&active_only=true&limit=1000')
        h.freeze(RAW/'memberships-preparation.json',members)
        field={m['player']['name']:m['policy_version'] for m in members}
        versions={k:platform.upload(c,k,n,schema) for k,n in [('deployed','moss-tern-24a1'),('previous','plum-otter-24a1'),('weak-neutral','cinder-finch-24a1')]}
        log=ROOT/'research/VERSION_LOG.md'
        if not log.exists():log.write_text('# Recovery study versions\n\n'+''.join('- '+k+': '+v+'; source '+h.sha(SOURCES[k].read_bytes())+'; runtime verified, score unvalidated, inert upload.\n' for k,v in versions.items()))
        # Named pool excludes the two observed crashing opponents. Rotation
        # changes allies/opponents and natural draft competition across slots.
        names=['Andre von Auto','richard','relh','Alex Smith','BeWellBot','Rohit Mukherjee','juliajerome','Scott Smith','macromackie']
        rivals=[field[n]['id'] for n in names]
        config={k:v for k,v in game['manifest']['variants'][0]['game_config'].items() if k not in ['players','tokens','seed']}
        arms=[]
        for slot in range(10):
            shift=(slot*4)%9;roster=rivals[shift:]+rivals[:shift];roster.insert(slot,versions['deployed'])
            cell=f'side{slot//5}-seat{slot%5}'
            body={'idempotency_key':'gota-recovery62a1-'+cell,'target':{'coworld_id':h.GAME,'variant_id':'competition'},
                  'game_config_overrides':config,'num_episodes':6,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                  'notes':'Current-release score recovery: every side/team seat, responsive matched previous and weak-neutral counterfactuals.'}
            folder=RAW/'hosted'/cell;h.freeze(folder/'request.json',body);h.create(c,body,folder/'batch',dry_run=True)
            arms.append({'slot':slot,'side':slot//5,'ordinal':slot%5,'cell':cell,'roster':roster,'games':6})
        h.freeze(RAW/'hosted-plan.json',{'at':h.research.now(),'arms':arms,'versions':versions,'source_hashes':{k:h.sha(v.read_bytes()) for k,v in SOURCES.items()},
            'game':h.VERSION,'engine':h.COMMIT,'field':{n:field[n] for n in names},'games':180,'pairs_per_contrast':60,
            'selection':'60fresh baseline games:6per side/team seat, fixed rotating nine-opponent panel. Both candidates reuse exact60seed/roster/slot controls; all ten policies respond. No outcome filtering.',
            'rule':'Expected individual score only. Two baseline contrasts with97.5percent whole-pair bootstrap intervals stratified by side/seat; candidate advances only if mean gain>0 and adjusted lower>0. Full ten-VM/hash/score/source/seed/config validity. Failed episodes invalidate qualification, never become zero scores. Neutral kills/XP, class, time, deaths are diagnostics, not substitute score gates. Independent fresh confirmation required before claiming a reliable repair.',
            'weak_hero_test':'Classes other than Ranger/Crossbowman; report actual observed class coverage, neutral XP and kills, alive time and net score. No claim for absent classes.'})
        print(json.dumps({'prepared':True,'versions':versions,'games':180}),flush=True)

def run():
    plan=h.read(RAW/'hosted-plan.json')
    with h.client() as c,ThreadPoolExecutor(4) as pool:
        baseline=[]
        for offset in range(0,len(plan['arms']),3):
            group=plan['arms'][offset:offset+3];requests={};seen={a['cell']:{} for a in group}
            for arm in group:
                folder=RAW/'hosted'/arm['cell'];receipt=panel.reserve(c,h.read(folder/'request.json'),folder/'batch')
                ident=receipt['id'] if isinstance(receipt,dict) else receipt;requests[arm['cell']]=ident
                print(json.dumps({'request':ident,'cell':arm['cell']}),flush=True)
            while any(len(seen[a['cell']])<a['games'] for a in group):
                for arm in group:
                    folder=RAW/'hosted'/arm['cell'];ident=requests[arm['cell']];cell=seen[arm['cell']]
                    if len(cell)==arm['games']:continue
                    eps=h.episodes(c,ident);h.write(folder/'episodes.json',eps)
                    ready=[e for e in eps if e['status']=='completed' and e['id'] not in cell]
                    assert all(e['status'] not in ['failed','error','cancelled'] for e in eps)
                    for e,r in zip(ready,pool.map(lambda e:cc.collect(c,e['id'],arm['roster'],arm['slot'],plan['source_hashes']['deployed']),ready)):
                        cell[e['id']]=r|{'cell':arm['cell'],'roster':arm['roster']}
                    h.write(folder/'result.json',list(cell.values()))
                if any(len(seen[a['cell']])<a['games'] for a in group):time.sleep(10)
            for arm in group:baseline.extend(seen[arm['cell']].values())
        assert len(baseline)==60 and all(r['valid'] for r in baseline)
        baseline_path=RAW/'baseline-pool.json'
        if baseline_path.exists():
            frozen=h.read(baseline_path)
            # Completion order can differ on resume. Keep the captured order
            # after checking every episode's full audited record is unchanged.
            assert {r['episode']:r for r in baseline}=={r['episode']:r for r in frozen}
            baseline=frozen
        else:
            h.freeze(baseline_path,baseline)
        indexed={r['episode']:r for r in baseline}
        ready={'baseline_version':plan['versions']['deployed'],'coworld_id':h.GAME,'complete':True,'episode_ids':list(indexed)}
        for label in ['previous','weak-neutral']:
            body={'candidate_policy_version_id':plan['versions'][label],'baseline_policy_version_id':plan['versions']['deployed'],
                  'source':'experience_request','n':60,'idempotency_key':'gota-recovery62a1-cf-'+label}
            out=RAW/'counterfactual'/label
            ev=cc.counterfactual_journal.create(c,h,body,out,h.read(RAW/'openapi-preparation.json'),ready)
            seen={}
            while True:
                ev=h.get(c,'/v2/counterfactual-evals/'+ev['id']);h.write(out/'status.json',ev)
                pairs=ev.get('pairs',[]);selected={p['baseline_episode_request_id'] for p in pairs}
                assert selected<=set(indexed) and len(selected)==len(pairs)
                pending=[p for p in pairs if p['candidate_episode_request_id'] and p['candidate_score'] is not None and p['candidate_episode_request_id'] not in seen]
                def one(p):
                    b=indexed[p['baseline_episode_request_id']];roster=list(b['roster']);roster[b['slot']]=plan['versions'][label]
                    return cc.collect(c,p['candidate_episode_request_id'],roster,b['slot'],plan['source_hashes'][label])
                for p,r in zip(pending,pool.map(one,pending)):
                    b=indexed[p['baseline_episode_request_id']]
                    assert p['seed']==b['seed']==r['seed'] and p['probe_slot']==b['slot']==r['slot'] and p['coworld_id']==h.GAME
                    assert p['opponent_policy_version_ids']==[v for i,v in enumerate(b['roster']) if i!=b['slot']]
                    assert all(x==y for i,(x,y) in enumerate(zip(b['content_hashes'],r['content_hashes'])) if i!=b['slot'])
                    assert p['baseline_score']==b['score'] and p['candidate_score']==r['score']
                    seen[r['episode']]={'pair':p,'baseline':b,'candidate':r}
                h.write(out/'paired-results.json',{'complete':len(seen)==60,'pairs':list(seen.values())})
                print(json.dumps({'arm':label,'pairs':len(seen),'status':ev['status']}),flush=True)
                if ev['status'] in ['completed','failed','cancelled','skipped']:
                    assert ev['status']=='completed' and len(seen)==60 and selected==set(indexed);break
                time.sleep(10)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true')
    if p.parse_args().prepare:prepare()
    else:run()

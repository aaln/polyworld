"""Fresh release62 baseline and two matched forty-pair responsive treatments."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import time
import httpx
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT.parent / 'polyworld/tmp/gota-lane-neutral62-20260923'
spec = importlib.util.spec_from_file_location('neutral_previous_hosted', HERE.parent/'controltactics20260923/hosted.py')
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
h, panel = cc.h, cc.panel
cc.RAW = h.STUDY = panel.STUDY = RAW
h.GAME = 'cow_a472c872-2b97-4b81-9961-e171304e5d63'
h.COMMIT = '2c8db6ebe1dc785ce1eea87496505d1244ee4c44'
h.VERSION = '2026.9.23.4'
SOURCES = {
    'baseline': ROOT/'examples/gods_of_the_arena/players/ir/forks/controltactics20260923-hosted/control-tactics/policy.bas',
    'lane-only': ROOT/'examples/gods_of_the_arena/players/ir/forks/lanefarm20260923-hosted/lane-occupancy/policy.bas',
    'lane-neutral': RAW/'lane-neutral/policy.bas',
}


def upload(c, label, name, schema):
    data = SOURCES[label].read_bytes(); out = RAW/'uploads'/label
    body = {'name':name, 'content_hash':h.sha(data), 'size_bytes':len(data),
            'player_id':h.PLAYER, 'attributes':{}, 'tags':{'game':'gods_of_the_arena'}}
    h.freeze(out/'request.json',body)
    jsonschema.validate(body,schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out/'version.json').exists():
        r = c.post('/stats/policies/files/upload',json=body)
        if r.status_code == 409:
            r=c.post('/stats/policies/files/complete',json=body);r.raise_for_status();v=r.json()
        else:
            r.raise_for_status();payload=r.json();v=payload.get('existing_policy_version')
            if v is None:
                r=httpx.put(payload['upload_url'],content=data,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=body);r.raise_for_status();v=r.json()
        h.write(out/'version.json',v)
    version=h.read(out/'version.json')
    meta=h.get(c,'/stats/policy-versions/'+version['id']);assert meta['name']==name
    h.write(out/'metadata.json',meta)
    return version['id']


def prepare():
    assert h.read(RAW/'practice-comparison.json')['passed']
    assert h.read(RAW/'native-comparison.json')['passed']
    with h.client() as c:
        game=h.live(c);h.freeze(RAW/'canonical-game.json',game)
        schema=h.get(c,'/openapi.json');h.freeze(RAW/'openapi-preparation.json',schema)
        members=h.get(c,'/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&active_only=true&limit=1000')
        h.freeze(RAW/'memberships-preparation.json',members)
        field={m['player']['name']:m['policy_version'] for m in members}
        versions={'baseline':upload(c,'baseline','brume-linnet-62f5',schema),
                  'lane-only':'4d55ef4d-cfa2-485d-a048-a81c35b8acd3',
                  'lane-neutral':upload(c,'lane-neutral','quartz-marten-62e4',schema)}
        config={k:v for k,v in game['manifest']['variants'][0]['game_config'].items() if k not in ['players','tokens','seed']}
        allies=[field[n]['id'] for n in ['relh','Alex Smith','macromackie','Scott Smith']]
        enemies=[field[n]['id'] for n in ['Andre von Auto','richard','BeWellBot','Andre von Houck','daveey']]
        arms=[]
        for side in [0,1]:
            for ordinal in [0,3]:
                team=list(allies);team.insert(ordinal,versions['baseline'])
                roster=team+enemies if side==0 else enemies+team
                arm={'side':side,'ordinal':ordinal,'slot':side*5+ordinal,'roster':roster,'cell':f'side{side}-seat{ordinal}','games':10}
                body={'idempotency_key':'gota-neutral62f5-base-'+arm['cell'],
                      'target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':config,'num_episodes':10,
                      'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                      'notes':'Fresh release62 controls for lane-only and lane-neutral responsive counterfactuals; individual score only.'}
                folder=RAW/'hosted-f5'/arm['cell'];h.freeze(folder/'request.json',body)
                h.create(c,body,folder/'batch',dry_run=True);arms.append(arm)
        h.freeze(RAW/'hosted-plan.json',{'game':h.VERSION,'engine':h.COMMIT,'versions':versions,
            'source_hashes':{k:h.sha(v.read_bytes()) for k,v in SOURCES.items()},'arms':arms,'pairs_per_candidate':40,'new_games':120,
            'field':{n:field[n] for n in ['relh','Alex Smith','macromackie','Scott Smith','Andre von Auto','richard','BeWellBot','Andre von Houck','daveey']},
            'selection':'All40new baseline episodes from unique version history, ten per color/seat. Both treatments reuse exact same40baseline seeds, slots, resolved rosters and config; allotherpolicies respond. Never compare to replay61 outcomes as current-release controls.',
            'rule':'Two directional contrasts versus baseline, plus paired lane-neutral versus lane-only. All games,tenVMs,replayhashes,XP,scores,seed/config/source identity must validate. Primary expectedindividualscore. Report stratified paired10000resample percentile95%intervals(seed9236102) and97.5%intervals for two baseline contrasts(Bonferroni). Advance a candidate only if mean>0 and97.5%lower>=0. No independent win/death/nonzero gate; all secondary slices descriptive. No deployment from directional pilot or unestablished verdict floor.'})
        log=ROOT/'games/gods_of_the_arena/players/neutralfarm20260923/VERSION_LOG.md';log.parent.mkdir(parents=True,exist_ok=True)
        if not log.exists():log.write_text('# Release62 research versions\n\n'+''.join('- '+k+': `'+v+'`, source `'+h.sha(SOURCES[k].read_bytes())+'`; inert, no league selection.\n' for k,v in versions.items()))
        print(json.dumps({'prepared':True,'new_games':120,'versions':versions}),flush=True)


def run():
    plan=h.read(RAW/'hosted-plan.json')
    assert plan['source_hashes']=={k:h.sha(v.read_bytes()) for k,v in SOURCES.items()}
    with h.client() as c, ThreadPoolExecutor(4) as pool:
        baseline=[]
        for arm in plan['arms']:
            folder=RAW/'hosted-f5'/arm['cell'];ident=panel.reserve(c,h.read(folder/'request.json'),folder/'batch')
            if isinstance(ident,dict):ident=ident['id']
            print(json.dumps({'baseline_request':ident,'cell':arm['cell']}),flush=True)
            seen={}
            while len(seen)<10:
                eps=h.episodes(c,ident);h.write(folder/'episodes.json',eps)
                ready=[e for e in eps if e['status'] in ['completed','failed','cancelled','error'] and e['id'] not in seen]
                assert all(e['status']=='completed' for e in ready)
                for e,row in zip(ready,pool.map(lambda e:cc.collect(c,e['id'],arm['roster'],arm['slot'],plan['source_hashes']['baseline']),ready)):
                    seen[e['id']]=row|{'cell':arm['cell'],'roster':arm['roster']}
                h.write(folder/'result.json',list(seen.values()))
                if len(seen)<10:time.sleep(10)
            baseline.extend(seen.values())
        assert len(baseline)==40 and all(r['valid'] for r in baseline)
        indexed={r['episode']:r for r in baseline}
        h.freeze(RAW/'baseline-pool.json',baseline)
        ready={'baseline_version':plan['versions']['baseline'],'coworld_id':h.GAME,'complete':True,'episode_ids':list(indexed)}
        for label in ['lane-only','lane-neutral']:
            body={'candidate_policy_version_id':plan['versions'][label],'baseline_policy_version_id':plan['versions']['baseline'],
                  'source':'experience_request','n':40,'idempotency_key':'gota-neutral62f5-cf-'+label+'-'+plan['source_hashes'][label][:8]}
            out=RAW/'counterfactual'/label
            evaluation=cc.counterfactual_journal.create(c,h,body,out,h.read(RAW/'openapi-preparation.json'),ready)
            print(json.dumps({'candidate':label,'evaluation':evaluation['id']}),flush=True)
            seen={}
            while True:
                evaluation=h.get(c,'/v2/counterfactual-evals/'+evaluation['id']);h.write(out/'status.json',evaluation)
                pairs=evaluation.get('pairs',[]);selected={p['baseline_episode_request_id'] for p in pairs}
                assert selected<=set(indexed) and len(selected)==len(pairs)
                pending=[p for p in pairs if p['candidate_episode_request_id'] and p['candidate_episode_request_id'] not in seen and p['candidate_score'] is not None]
                def collect(pair):
                    base=indexed[pair['baseline_episode_request_id']];roster=list(base['roster']);roster[base['slot']]=plan['versions'][label]
                    return cc.collect(c,pair['candidate_episode_request_id'],roster,base['slot'],plan['source_hashes'][label])
                for pair,result in zip(pending,pool.map(collect,pending)):
                    base=indexed[pair['baseline_episode_request_id']]
                    assert pair['coworld_id']==h.GAME and pair['seed']==base['seed'] and pair['probe_slot']==base['slot']
                    assert pair['opponent_policy_version_ids']==[v for i,v in enumerate(base['roster']) if i!=base['slot']]
                    assert all(x==y for i,(x,y) in enumerate(zip(base['content_hashes'],result['content_hashes'])) if i!=base['slot'])
                    assert pair['baseline_score']==base['score'] and pair['candidate_score']==result['score']
                    seen[result['episode']]={'pair':pair,'baseline':base,'candidate':result}
                h.write(out/'paired-results.json',{'complete':len(seen)==40,'pairs':list(seen.values())})
                print(json.dumps({'candidate':label,'audited_pairs':len(seen),'status':evaluation['status']}),flush=True)
                if evaluation['status'] in ['completed','failed','cancelled','skipped']:
                    assert evaluation['status']=='completed' and len(seen)==40 and selected==set(indexed)
                    break
                time.sleep(10)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true')
    if parser.parse_args().prepare:prepare()
    else:run()

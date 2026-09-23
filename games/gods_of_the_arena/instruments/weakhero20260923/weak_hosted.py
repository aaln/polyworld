"""Frozen replay60 sustain/survival comparison against the deployed policy."""
import argparse,json,sys,time
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import httpx,jsonschema
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'adaptive20260922'))
import adaptive_hosted as base
h,field,panel,audit=base.h,base.field,base.panel,base.audit
ROOT=base.ROOT
STUDY=ROOT.parent/'polyworld/tmp/gota-weakhero60-20260923'
base.STUDY=h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-weakhero60-20260923'
h.GAME='cow_f2dcdbcd-f984-445b-af5b-ee9481a7f362'
h.VERSION=audit.VERSION='2026.9.23.2'
h.COMMIT='fd315c8fa30f8923c7a7709a577c40ac071b1c2a'
h.ENGINE=ROOT.parent/'polyworld-gota-explicit60-20260923'
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'productive20260923'))
import unit_audit
unit_audit.h=h;unit_audit.STUDY=STUDY;unit_audit.VERSION=h.VERSION
audit=unit_audit

# Use the saved owning user credential for own uploads/XP, without changing
# the CLI's selected player or requesting elevated privileges.
from softmax.auth import load_user_token, get_api_server
from hosted_wave import ResilientClient, API

def user_client():
    token=load_user_token(server=get_api_server())
    assert token, 'Saved user credential required for own research'
    return ResilientClient(base_url=API,headers={'Authorization':'Bearer '+token},timeout=120,follow_redirects=True)
h.client=user_client

BASELINE='0c766ec9-131f-45d1-a207-ad75aea9ccc5'
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
CRITICAL={'ply_630a768f-d623-44b2-80fa-36968d6fa75a','ply_594ec24d-d7f3-4370-a000-468354ec41c9','ply_3d22435e-30a2-4f2a-b037-a5c249583788','ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83','ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb','ply_18302115-9fc9-482d-a2f3-f4c592bf9e57','ply_607f17a2-3acf-405b-91fe-d12ef1001c00','ply_74ab20ef-cdf2-4250-b995-2b4f2cc96fc0','ply_176e1e1a-7af8-40f7-9ee3-a67b96690ad6','ply_ac95b848-2475-4901-9344-95c88f33f8e6'}
RULE='400 fresh games,50/source/context: red lead,blue lead,red late,blue late; ordinals0/3. Zero10source/VM/full-replay/XP/integer failures;>=10percent pooled mean score gain,eachcontext>=95percentcontrol,positive lower95percent context-stratified independent whole-game bootstrap gain. Nonzero mean>=105percentcontrol, nonzero frequency>=control, score>=500 frequency strictly higher. Stable game/principal champions. One frozen combined source; no prior hosted controls or posthoc class filtering.'
RULE += ' Late-draft pooled deaths per minute must not increase, and pooled XP per minute must not decrease. Fewer deaths alone is insufficient.'
def source(label):return (PARENT if label=='baseline' else STUDY/label)/'policy.bas'
def folder(arm):return STUDY/'trial'/arm['name']/arm['cell']
def upload(c):
    data=source('explicit-sustain').read_bytes();out=STUDY/'uploads/explicit-sustain'
    meta={'name':'opal-sable-4e91','content_hash':h.sha(data),'size_bytes':len(data),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena'}}
    h.freeze(out/'request.json',meta);jsonschema.validate(meta,h.read(STUDY/'openapi-current.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out/'version.json').exists():
        r=c.post('/stats/policies/files/upload',json=meta)
        if r.status_code==409:r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();v=r.json()
        else:
            r.raise_for_status();payload=r.json();v=payload.get('existing_policy_version')
            if v is None:
                r=httpx.put(payload['upload_url'],content=data,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();v=r.json()
        h.write(out/'version.json',v)
    v=h.read(out/'version.json');assert h.get(c,'/stats/policy-versions/'+v['id'])['name']==meta['name'];return v['id']
def prepare():
    assert h.read(STUDY/'local-summary.json')['passed'] and h.read(STUDY/'native-result.json')['passed']
    assert h.sha(source('explicit-sustain').read_bytes())==h.read(STUDY/'explicit-sustain/manifest.json')['source_sha256']
    assert h.read(STUDY/'preflight.json')['identity_verified']
    out=STUDY/'trial'
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        game=h.live(c);snap=field.snapshot(c,out/'field-before')
        start=h.read(STUDY/'field-before/snapshot.json')
        for owner in CRITICAL:assert snap['champions'][owner]['version']==start['champions'][owner]['version'], 'Principal changed before source freeze'
        assert snap['champions']['ply_630a768f-d623-44b2-80fa-36968d6fa75a']['version']==BASELINE
        cfg=lambda g:{k:v for k,v in g['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
        assert cfg(game)==cfg(h.read(STUDY/'canonical-game.json'))
        # Preserve the retrieved schema separately; old snapshots remain immutable.
        schema=h.get(c,'/openapi.json');h.freeze(STUDY/'openapi-preparation.json',schema)
        versions={'baseline':BASELINE,'explicit-sustain':upload(c)}
        template=h.read(STUDY/'roster-template-v2.json');arms=[]
        for label,version in versions.items():
            for cell,side,ordinal in [('red-lead',0,0),('blue-lead',1,0),('red-late',0,3),('blue-late',1,3)]:
                roster=list(template)
                if ordinal==3:roster[:5]=[BASELINE,template[1],BASELINE,version,template[2]]
                else:roster[0]=version
                if side:roster=roster[5:]+roster[:5]
                digest=h.sha(source(label).read_bytes())
                arm={'name':label,'cell':cell,'side':side,'ordinal':ordinal,'version':version,'source_sha256':digest,'own_slots':[side*5+ordinal],'roster':roster,'games':50}
                body={'idempotency_key':f'gota-opal-4e91-{label}-{cell}-{digest[:10]}','target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg(game),'num_episodes':50,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],'notes':'Controlled policy evaluation.'}
                h.freeze(folder(arm)/'arm.json',arm);h.freeze(folder(arm)/'request.json',body);h.create(c,body,folder(arm)/'batch',dry_run=True);arms.append(arm)
        plan={'stage':'trial','games':400,'engine_commit':h.COMMIT,'game_version':h.VERSION,'cycle':h.CYCLE,'arms':arms,'rule':RULE,'budget':'Permanent100000/day authorized;400new in8x50, separate cycle, maximum3active; shared ledger retained.','source_evidence':'games/gods_of_the_arena/release-audits/2026-09-23-explicit-abilities','source_freeze':'Combined early resource unlock, explicit heal/restore, bounded melee lane recovery and short spacing under enemy pressure. Current deployed baseline; fresh replay60 controls; natural draft. Deaths, XP/minute and late-draft scores are prospective diagnostics; all-context score and productivity gates unchanged.'}
        h.freeze(out/'plan.json',plan)
        print(json.dumps({'prepared':True,'games':400,'new_requests':0}),flush=True)
def run():
    out=STUDY/'trial';plan=h.read(out/'plan.json')
    for arm in plan['arms']:assert h.sha(source(arm['name']).read_bytes())==arm['source_sha256']
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        h.live(c)
        submitted=field.snapshot(c,out/'field-submit')
        changes=field.compare(h.read(out/'field-before/snapshot.json'),submitted)
        assert not changes['game_changed'] and not any(x['player_id'] in CRITICAL for x in changes['champion_changes']), 'Field changed: review and freeze a new plan before spend'
        journal=h.read(h.CAMPAIGN/'xp-ledger.json');today=h.research.now()[:10]
        used=sum(v['episodes'] for v in journal.values() if v['day']==today)
        needed=sum(a['games'] for a in plan['arms'] if h.read(folder(a)/'request.json')['idempotency_key'] not in journal)
        assert used+needed<=h.research.config(h.CAMPAIGN)['daily_episode_limit'], 'Complete comparison exceeds current authorized allowance; no requests submitted'
        pending=sorted(plan['arms'],key=lambda a:(a['cell'],a['name']!='baseline'));active=[]
        while pending or active:
            while pending and len(active)<3:
                arm=pending.pop(0);f=folder(arm)
                if (f/'result.json').exists():continue
                receipt=f/'batch/created.json';ident=h.read(receipt)['id'] if receipt.exists() else panel.reserve(c,h.read(f/'request.json'),f/'batch')
                active.append((arm,f,ident));print(json.dumps({'name':arm['name'],'cell':arm['cell'],'request':ident}),flush=True)
            remaining=[]
            for arm,f,ident in active:
                episodes=h.episodes(c,ident);h.write(f/'episodes.json',episodes)
                done=[e for e in episodes if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(6) as pool:rows=list(pool.map(lambda e:audit.collect(c,arm,f,e),done))
                h.write(f/'progress.json',{'audited':len(rows),'total':arm['games'],'rows':rows})
                if len(rows)<arm['games']:remaining.append((arm,f,ident));continue
                cell={'name':arm['name'],'cell':arm['cell'],'side':arm['side'],'invalid':sum(not r['valid'] for r in rows),'score':sum(r.get('score',0) for r in rows)/arm['games'],'picks':dict(Counter(r.get('class') for r in rows)),'distinct_streams':len({r.get('canonical_commands_sha1') for r in rows}),'rows':rows}
                h.write(f/'result.json',cell);print(json.dumps({k:v for k,v in cell.items() if k!='rows'}),flush=True)
            active=remaining
            if active:time.sleep(10)
        h.write(out/'result.json',{'complete':True,'cells':[h.read(folder(a)/'result.json') for a in plan['arms']]})
        snap=field.snapshot(c,out/'field-after');h.freeze(out/'field-changes.json',field.compare(h.read(out/'field-before/snapshot.json'),snap))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    else:run()

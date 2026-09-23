"""Prospective two-candidate screen, then independent roster confirmation if qualified."""
import argparse,json,sys,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import httpx,jsonschema
import field
h=field.h
old=field.old
panel,audit=old.panel,old.audit
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-adaptive-score-20260922'
h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-adaptive-score-20260922'
BASELINE=old.BASELINE
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted'
LABELS=['spell-targeting','spell-pressure']
CONFIRM_SUBJECT=2
GAMES=40
REQUEST_PREFIX='gota-adaptive0922'
RULE_OVERRIDE=BUDGET_OVERRIDE=NOTES_OVERRIDE=None
PINNED_RIVALS=None

def source(label):return (PARENT if label=='baseline' else STUDY/label)/'policy.bas'
def upload(c,label):
    data=source(label).read_bytes();digest=h.sha(data)
    meta={'name':'aaron-gota-adaptive0922-'+label,'content_hash':digest,'size_bytes':len(data),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'44 spell+84 portal+126 broad host fixtures;12 complete native games. Inert research upload; competitive score unvalidated.'}}
    out=STUDY/'uploads'/label;h.freeze(out/'request.json',meta)
    jsonschema.validate(meta,h.read(STUDY/'openapi-current.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out/'version.json').exists():
        r=c.post('/stats/policies/files/upload',json=meta)
        if r.status_code==409:
            r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        else:
            r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
            if version is None:
                r=httpx.put(payload['upload_url'],content=data,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        h.write(out/'version.json',version)
    v=h.read(out/'version.json');assert h.get(c,'/stats/policy-versions/'+v['id'])['name']==meta['name']
    return v['id']

def prepare(stage,candidate=None):
    labels=LABELS if stage=='screen' else [candidate]
    if stage=='confirmation':
        screen=h.read(STUDY/'screen/report.json');assert candidate==screen['selected']
    for label in labels:
        for n in ['practice','portals']:
            assert all(r['passed'] for r in h.read(STUDY/(label+'-'+n+'.json'))['rows'])
        assert h.read(STUDY/(label+'-scenarios.json'))['passed']
        assert h.sha(source(label).read_bytes())==h.read(STUDY/label/'manifest.json')['source_sha256']
    assert h.read(STUDY/'native-result.json')['passed']
    assert h.read(STUDY/'preflight.json')['passed'] and h.read(STUDY/'runtime-provenance.json')['reuse_verified']
    out=STUDY/stage
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        game=h.live(c)
        snap=field.snapshot(c,out/'field-before')
        h.freeze(STUDY/'openapi-current.json',h.get(c,'/openapi.json'))
        original=h.read(STUDY/'canonical-game.json')
        cfg=lambda g:{k:v for k,v in g['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
        assert cfg(game)==cfg(original)
        template=h.read(STUDY/'roster-template-v2.json')
        # Active named rivals must still match the pinned research targets.
        for owner,version in (PINNED_RIVALS if PINNED_RIVALS is not None else [('ply_3d22435e-30a2-4f2a-b037-a5c249583788','145c01e0-0cbf-4e1e-8120-11b437175b91'),('ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83','e811221e-c419-4f7b-9629-01f8722ab9f7')]):
            assert snap['champions'][owner]['version']==version,'Named rival updated: prepare new cohort instead of silently substituting.'
        for row in h.read(STUDY/'preflight.json')['rows']:
            path=out/'versions'/(row['version']+'.json')
            if not path.exists():h.freeze(path,{'version':row['version'],'source_sha256':row['source_sha256'],'source_evidence':row,'current_memberships':[m for m in h.read(out/'field-before/memberships.json') if m['policy_version']['id']==row['version']],'scope':'Exact source verified in prior clean current-engine games; dry-run resolves pinned UUID. The stats metadata route is owner-scoped and404 for rivals.'})
        versions={'baseline':BASELINE,**{n:upload(c,n) for n in labels}}
        if stage=='confirmation':
            # Different allied lane/order and a third subject team seat. Keep
            # khors, Richard, Jordan opposing; exchange two background players.
            template[1],template[8]=template[8],template[1]
            if CONFIRM_SUBJECT==2:template[0],template[2]=template[2],template[0]
        subject=0 if stage=='screen' else CONFIRM_SUBJECT
        arms=[]
        for label,ident in versions.items():
            for side in (0,1):
                roster=list(template);roster[subject]=ident
                if side:roster=roster[5:]+roster[:5]
                digest=h.sha(source(label).read_bytes())
                arm={'name':label,'side':side,'version':ident,'source_sha256':digest,'own_slots':[side*5+subject],'roster':roster,'games':GAMES}
                body={'idempotency_key':f'{REQUEST_PREFIX}-{stage}-{label}-{side}-{digest[:10]}','target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg(game),'num_episodes':GAMES,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],'notes':'Adaptive individual-score research. Exact Richard167 and khors114 opposing both colors; public-only spell-targeting variants. Frozen>=10% aggregate score gain and>=95% each color, zero invalid/source/VM/replay/XP/integer failures. Screen selection requires fresh separate roster confirmation before deployment. No automatic league selection.'}
                if NOTES_OVERRIDE:body['notes']=NOTES_OVERRIDE
                folder=out/label/str(side);h.freeze(folder/'arm.json',arm);h.freeze(folder/'request.json',body);h.create(c,body,folder/'batch',dry_run=True);arms.append(arm)
        plan={'stage':stage,'games':len(arms)*GAMES,'engine_commit':h.COMMIT,'game_version':h.VERSION,'cycle':h.CYCLE,'arms':arms,'rule':'Zero invalid; strict aggregate mean score improvement>=10%; each color>=95% control. Screen choose highest qualifying aggregate (ties lexical), then independent160-game different-roster confirmation before deployment. No confirm if no candidate qualifies. Full10source/VM/replay/XP audits; independent per-color whole-game bootstrap, duplicates reported. Fixed opponent versions, no universal rank claim.','budget':f'Authorized Sep22 UTC10000; shared ledger/cycle400/parallel3/batch40 preserved.{(len(LABELS)+1)*80}screen+160conditionalconfirmation.'}
        if RULE_OVERRIDE:plan['rule']=RULE_OVERRIDE
        if BUDGET_OVERRIDE:plan['budget']=BUDGET_OVERRIDE
        h.freeze(out/'plan.json',plan)
        print(json.dumps({'prepared':stage,'games':plan['games'],'new_requests':0}),flush=True)

def run(stage):
    out=STUDY/stage;plan=h.read(out/'plan.json')
    for arm in plan['arms']:assert h.sha(source(arm['name']).read_bytes())==arm['source_sha256']
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        # Interleave both colors and candidates. All requests frozen before spend.
        pending=sorted(plan['arms'],key=lambda a:(a['side'],a['name']!='baseline',a['name']))
        active=[]
        while pending or active:
            while pending and len(active)<3:
                arm=pending.pop(0);folder=out/arm['name']/str(arm['side'])
                if (folder/'result.json').exists():continue
                receipt=folder/'batch/created.json'
                ident=h.read(receipt)['id'] if receipt.exists() else panel.reserve(c,h.read(folder/'request.json'),folder/'batch')
                active.append((arm,folder,ident));print(json.dumps({'stage':stage,'name':arm['name'],'side':arm['side'],'request':ident}),flush=True)
            remaining=[]
            for arm,folder,ident in active:
                episodes=h.episodes(c,ident);h.write(folder/'episodes.json',episodes)
                done=[e for e in episodes if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(6) as pool:rows=list(pool.map(lambda e:audit.collect(c,arm,folder,e),done))
                h.write(folder/'progress.json',{'audited':len(rows),'total':arm['games'],'rows':rows})
                if len(rows)<arm['games']:remaining.append((arm,folder,ident));continue
                cell={'name':arm['name'],'side':arm['side'],'invalid':sum(not r['valid'] for r in rows),'score':sum(r.get('score',0) for r in rows)/arm['games'],'picks':dict(Counter(r.get('class') for r in rows)),'distinct_streams':len({r.get('canonical_commands_sha1') for r in rows}),'rows':rows}
                h.write(folder/'result.json',cell);print(json.dumps({k:v for k,v in cell.items() if k!='rows'}),flush=True)
            active=remaining
            if active:time.sleep(10)
        cells=[h.read(out/a['name']/str(a['side'])/'result.json') for a in plan['arms']]
        h.write(out/'result.json',{'complete':True,'cells':cells,'review_required':True})
        snap=field.snapshot(c,out/'field-after')
        h.freeze(out/'field-changes.json',field.compare(h.read(out/'field-before/snapshot.json'),snap))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['screen','confirmation'],default='screen');p.add_argument('--prepare',action='store_true');p.add_argument('--candidate',choices=LABELS);a=p.parse_args()
    if a.prepare:prepare(a.stage,a.candidate)
    else:run(a.stage)

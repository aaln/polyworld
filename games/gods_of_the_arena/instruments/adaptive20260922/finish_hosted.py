"""One preselected reward-finisher versus 400 fresh held-out games."""
import argparse,json
import httpx,jsonschema
import adaptive_hosted as base
h,panel,audit=base.h,base.panel,base.audit
ROOT=base.ROOT
STUDY=ROOT.parent/'polyworld/tmp/gota-finish-score-20260922'
base.STUDY=h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-reward-finish-20260922'
base.LABELS=['reward-finisher'];base.CONFIRM_SUBJECT=0;base.GAMES=100;base.REQUEST_PREFIX='gota-finish0922'
base.RULE_OVERRIDE='One preselected source;400fresh games,100/source/color. Zero invalid and all10source/VM/replay/XP/integer audits; aggregate mean gain>=10%, each color>=95% control, positive lower95% side-stratified whole-game bootstrap gain bound. No screening/control reuse. Field must remain unchanged. Fixed first-seat mixed roster; no universal rank or late-draft claim.'
base.BUDGET_OVERRIDE='Authorized Sep22UTC10000; shared ledger,one400-game cycle,parallel3,batch100. No additional stage.'
base.NOTES_OVERRIDE=base.RULE_OVERRIDE+' Exact Richard167 and khors114 opposing both colors. Public-only immediately reachable one-hit reward priorities. No automatic league selection.'
source=base.source

def upload(c,label):
    data=source(label).read_bytes();digest=h.sha(data);out=STUDY/'uploads'/label
    meta={'name':'aaron-gota-finish0922-'+label,'content_hash':digest,'size_bytes':len(data),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'140 actual-tick target/reward cases;84portal+126broad cases;8complete native games;portable IR equality. Inert; competitive score unvalidated.'}}
    h.freeze(out/'request.json',meta);jsonschema.validate(meta,h.read(STUDY/'openapi-current.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out/'version.json').exists():
        r=c.post('/stats/policies/files/upload',json=meta)
        if r.status_code==409:r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        else:
            r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
            if version is None:
                r=httpx.put(payload['upload_url'],content=data,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        h.write(out/'version.json',version)
    version=h.read(out/'version.json');assert h.get(c,'/stats/policy-versions/'+version['id'])['name']==meta['name'];return version['id']
base.upload=upload

def prepare(stage):
    assert stage=='trial' and h.read(STUDY/'local-summary.json')['passed']
    base.prepare(stage,'reward-finisher')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['trial'],default='trial');p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.stage)
    else:base.run(a.stage)

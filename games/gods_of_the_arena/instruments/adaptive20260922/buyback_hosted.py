"""One preselected core-buyback versus 400 fresh held-out games."""
import argparse,json
import httpx,jsonschema
import adaptive_hosted as base
h,panel,audit=base.h,base.panel,base.audit
ROOT=base.ROOT
STUDY=ROOT.parent/'polyworld/tmp/gota-core-buyback-20260923'
base.STUDY=h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-core-buyback-20260923'
base.LABELS=['core-buyback'];base.CONFIRM_SUBJECT=0;base.GAMES=100;base.REQUEST_PREFIX='gota-buyback0923'
base.RULE_OVERRIDE='One preselected source;400fresh games,100/source/color. Zero invalid and all10source/VM/replay/XP/integer audits; aggregate mean gain>=10%, each color>=95% control, positive lower95% side-stratified whole-game bootstrap gain bound. No screening/control reuse. Game and principal champion versions must remain unchanged; background changes disclosed. Fixed first-seat mixed roster; no universal rank or late-draft claim.'
base.BUDGET_OVERRIDE='Normal Sep23UTC1600; shared ledger,one400-game cycle,parallel3,batch100. No additional stage.'
base.NOTES_OVERRIDE=base.RULE_OVERRIDE+' Exact Richard174 and khors114 opposing both colors. Public post-core buyback with time and gold guards. No automatic league selection.'
CRITICAL={'ply_630a768f-d623-44b2-80fa-36968d6fa75a','ply_594ec24d-d7f3-4370-a000-468354ec41c9','ply_3d22435e-30a2-4f2a-b037-a5c249583788','ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83','ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb','ply_18302115-9fc9-482d-a2f3-f4c592bf9e57'}
base.PINNED_RIVALS=[('ply_3d22435e-30a2-4f2a-b037-a5c249583788','145c01e0-0cbf-4e1e-8120-11b437175b91'),('ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83','5b854825-446a-4864-8dfc-bb3404d4fe81')]
source=base.source

def upload(c,label):
    data=source(label).read_bytes();digest=h.sha(data);out=STUDY/'uploads'/label
    meta={'name':'aaron-gota-buyback0923-'+label,'content_hash':digest,'size_bytes':len(data),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'180 actual-tick buyback/resource/guard cases;84portal+126broad cases;8complete native games;portable IR equality. Inert; competitive score unvalidated.'}}
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
    base.prepare(stage,'core-buyback')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['trial'],default='trial');p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.stage)
    else:base.run(a.stage)

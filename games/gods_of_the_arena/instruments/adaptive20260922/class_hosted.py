"""Fresh tests of the complete Crossbow-only controller; no reused controls."""
import argparse,json
import httpx,jsonschema
import adaptive_hosted as base
h,panel,audit=base.h,base.panel,base.audit
ROOT=base.ROOT
STUDY=ROOT.parent/'polyworld/tmp/gota-class-score-20260922'
base.STUDY=h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-class-score-20260922'
base.LABELS=['crossbow-only'];base.CONFIRM_SUBJECT=0;base.REQUEST_PREFIX='gota-class0922'
source=base.source

def upload(c,label):
    data=source(label).read_bytes();digest=h.sha(data);out=STUDY/'uploads'/label
    meta={'name':'aaron-gota-class0922-'+label,'content_hash':digest,'size_bytes':len(data),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'160 real-tick conformance cases: Crossbow matches intervention,9other classes match deployed controller.84portal+126broad cases;12full native games and trajectory equivalence. Inert; competitive full-policy score unvalidated.'}}
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
    assert h.read(STUDY/'conformance.json')['passed']
    assert h.read(STUDY/'native-equivalence.json')['passed']
    base.prepare(stage,'crossbow-only' if stage=='confirmation' else None)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['screen','confirmation'],default='screen');p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.stage)
    else:base.run(a.stage)

"""Select an independently confirmed exact source for both authorized players."""
import importlib.util,json,subprocess,sys
from pathlib import Path
import httpx,jsonschema
import siege_hosted as study
h,ROOT,STUDY=study.h,study.ROOT,study.STUDY
loader=importlib.util.spec_from_file_location('prior_score_deployer',Path(__file__).resolve().parent.parent/'score20260922/deploy.py')
placement=importlib.util.module_from_spec(loader);loader.loader.exec_module(placement)
OUT=STUDY/'deployment'
placement.h=h;placement.OUT=OUT
PLAYERS=placement.PLAYERS
PRIOR={'aaron':'0c766ec9-131f-45d1-a207-ad75aea9ccc5','coach':'d75ff766-e78f-4aa5-b656-55eb29248208'}
placement.PRIOR=PRIOR

NAMES={'aaron':'cairn-orchid-d8e1','coach':'sable-cipher-40b9'}

def upload_named(c,label,source,schema):
    out=OUT/label;meta={'name':NAMES[label],'content_hash':h.sha(source),'size_bytes':len(source),'player_id':PLAYERS[label],'attributes':{},'tags':{'game':'gods_of_the_arena'}}
    h.freeze(out/'upload-request.json',meta);jsonschema.validate(meta,schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    if not (out/'uploaded-version.json').exists():
        r=c.post('/stats/policies/files/upload',json=meta)
        if r.status_code==409:r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        else:
            r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
            if version is None:
                r=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        h.write(out/'uploaded-version.json',version)
    return h.read(out/'uploaded-version.json')

def main():
    confirmation=h.read(STUDY/'trial/report.json')
    assert confirmation['complete'] and confirmation['deployment_qualified']
    selected=confirmation['selected'];assert selected=='guarded-siege' and confirmation['games']==400
    result=confirmation['candidates'][0];assert result['score_gate_passed']
    pair=ROOT/'examples/gods_of_the_arena/players/ir/forks/richard17420260923-hosted'/selected
    manifest=h.read(pair/'manifest.json');source=(pair/'policy.bas').read_bytes()
    assert manifest['deployment_qualified'] and h.sha(source)==manifest['source_sha256']==result['source_sha256']
    check=subprocess.run([sys.executable,str(pair/'verify.py')],capture_output=True,text=True,check=True);h.write(OUT/'conversion-proof.json',{'stdout':check.stdout,'returncode':check.returncode})
    note=f"Coordinated guarded structure pressure and siege attacker response, generated from current semantic IR. One preselected source,400fresh games,50/source/context across red/blue lead/later drafts: gain{result['aggregate_gain_percent']:.3f}%, contexts{result['per_context_gain_percent']},95% interval{result['gain_ci95_percent']}. All10source/VM/fullreplay/XP/integer audits pass;32-game source reconstruction verifies mechanism. Fixed roster, no universal ranking or component causality. Prior user authorization for both players."
    placement.NOTE='Validated release; user-directed deployment.'
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.research.lock(h.CAMPAIGN/'league-deployment.lock',blocking=False),h.client() as c:
        h.live(c);assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        before=placement.members(c);schema=h.get(c,'/openapi.json')
        if not (OUT/'before.json').exists():
            for label,player in PLAYERS.items():
                current=[m for m in before if m['player']['id']==player and m['is_champion'] and m['end_time'] is None]
                assert len(current)==1 and current[0]['policy_version']['id']==PRIOR[label],'Concurrent champion change must be reconciled.'
            latest=study.base.field.snapshot(c,OUT/'field-before')
            changes=study.base.field.compare(h.read(STUDY/'trial/field-after/snapshot.json'),latest)
            h.freeze(OUT/'field-comparison.json',changes)
            assert not changes['game_changed'] and not any(c['player_id'] in study.CRITICAL for c in changes['champion_changes']),'Current field differs from confirmation; retain champion pending revalidation.'
            h.freeze(OUT/'before.json',before)
            h.freeze(OUT/'decision.json',{'at':h.research.now(),'authorization':'Existing user authorization to deploy validated latest policy to both Aaron and Coach; unsigned research commits permitted.','source_sha256':h.sha(source),'ir_sha256':manifest['ir_sha256'],'trial_report':result,'validation_note':note,'naming_authorization':'do it. use bespoke hidden policy names','opaque_names':NAMES,'visibility':'Upload/submission API has no policy visibility setting; opaque names and neutral public notes only.','rollback_versions':PRIOR,'rollback_source_sha256':'29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36','engine_commit':h.COMMIT,'game_version':h.VERSION})
        versions={label:upload_named(c,label,source,schema) for label in PLAYERS}
        chosen={}
        for label,version in versions.items():
            meta=h.get(c,'/stats/policy-versions/'+version['id'])
            assert meta['name']==version['name'] and meta['user_id']==h.get(c,'/stats/policy-versions/'+PRIOR['aaron'])['user_id']
            if meta['player_file_content_hash'] is not None:assert meta['player_file_content_hash']==h.sha(source)
            chosen[label]=placement.select(c,label,version,schema)
        after=placement.members(c);h.write(OUT/'after.json',after)
        for label,version in versions.items():
            assert any(m['player']['id']==PLAYERS[label] and m['policy_version']['id']==version['id'] and m['is_champion'] and m['status']=='competing' and m['substatus']=='active' and m['end_time'] is None for m in after)
        h.write(OUT/'result.json',{'complete':True,'source_sha256':h.sha(source),'ir_sha256':manifest['ir_sha256'],'pair':str(pair.relative_to(ROOT)),'versions':versions,'memberships':{k:v['id'] for k,v in chosen.items()},'at':h.research.now(),'scope':'Placement verified; future league round score remains unmeasured.'})
        print(json.dumps({'deployed':True,'source_sha256':h.sha(source),'versions':{k:v['id'] for k,v in versions.items()}}))
if __name__=='__main__':main()

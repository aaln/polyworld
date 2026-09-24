"""User-directed publication of the audited release62 pilot, preserving its scope."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import httpx
import jsonschema

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('neutral_deploy_hosted',HERE/'hosted.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
h,ROOT,RAW=study.h,study.ROOT,study.RAW
spec=importlib.util.spec_from_file_location('neutral_placement',HERE.parent/'score20260922/deploy.py')
placement=importlib.util.module_from_spec(spec);spec.loader.exec_module(placement)
OUT=RAW/'deployment'
PAIR=ROOT/'examples/gods_of_the_arena/players/ir/forks/neutralfarm20260923-hosted/lane-neutral'
PRIOR={'aaron':'0c766ec9-131f-45d1-a207-ad75aea9ccc5','coach':'d75ff766-e78f-4aa5-b656-55eb29248208'}
placement.h=h;placement.OUT=OUT;placement.PRIOR=PRIOR
placement.NOTE='User-directed release; validated runtime and score pilot.'


def coach_upload(c,source,schema):
    body={'name':'linen-kestrel-62f5','content_hash':h.sha(source),'size_bytes':len(source),
          'player_id':placement.PLAYERS['coach'],'attributes':{},'tags':{'game':'gods_of_the_arena'}}
    h.freeze(OUT/'coach/upload-request.json',body)
    jsonschema.validate(body,schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    p=OUT/'coach/uploaded-version.json'
    if not p.exists():
        r=c.post('/stats/policies/files/upload',json=body)
        if r.status_code==409:
            r=c.post('/stats/policies/files/complete',json=body);r.raise_for_status();v=r.json()
        else:
            r.raise_for_status();payload=r.json();v=payload.get('existing_policy_version')
            if v is None:
                r=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=body);r.raise_for_status();v=r.json()
        h.write(p,v)
    return h.read(p)


def main():
    stats=h.read(RAW/'statistics.json');manifest=h.read(PAIR/'manifest.json');source=(PAIR/'policy.bas').read_bytes()
    assert stats['complete'] and stats['all_120_games_10_vms_valid'] and stats['full_hash_xp_score_config_pair_audits']
    assert stats['contrasts']['lane-neutral']['pilot_advance'] and manifest['pilot_score_gate_passed']
    assert h.sha(source)==manifest['source_sha256']=='2fbd789b0d9b9f25df3c41b24c31be665ddc0a7e6a9482b79ad80d52dcabe83c'
    proof=subprocess.run([sys.executable,str(PAIR/'verify.py')],capture_output=True,text=True,check=True)
    h.write(OUT/'conversion-proof.json',{'returncode':proof.returncode,'stdout':proof.stdout})
    owner=h.read(h.CAMPAIGN/'ownership.json')
    # The root session holds runner.lock continuously in its dedicated holder.
    assert owner['active_writer'] and owner['cycle']==h.CYCLE and owner['worktree']==str(ROOT)
    with h.research.lock(h.CAMPAIGN/'league-deployment.lock',blocking=False),h.client() as c:
        h.live(c);assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        schema=h.get(c,'/openapi.json');h.write(OUT/'live-openapi.json',schema)
        before=placement.members(c)
        if not (OUT/'before.json').exists():
            for label,player in placement.PLAYERS.items():
                current=[m for m in before if m['player']['id']==player and m['is_champion'] and m['end_time'] is None]
                assert len(current)==1 and current[0]['policy_version']['id']==PRIOR[label],'Reconcile concurrent champion change'
            h.freeze(OUT/'before.json',before)
            h.freeze(OUT/'decision.json',{'at':h.research.now(),'authorization_verbatim':'publish the better policy',
                'scope':'Publish the best completed lane/camp pilot to both players, consistent with prior both-player publication scope.',
                'source_sha256':h.sha(source),'ir_sha256':manifest['ir_sha256'],'engine':h.COMMIT,'game_version':h.VERSION,
                'research_evidence':stats['contrasts']['lane-neutral']['overall'],'scientific_status':'Successful directional score pilot versus research parent b3f0c124; not independent incumbent confirmation or broad-field qualification. User explicitly requested publication after seeing that limitation.',
                'user_authorized_pilot_deployment':True,'blue_druid_caution':'Redseat3delta+659.5,blueseat3-664.3; pooledDruidflat. Diagnostic slices, not confirmed effects.',
                'rollback_versions':PRIOR,'rollback_source_sha256':'29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36',
                'rollback_plan':'On confirmed own-runtime invalidity or disqualification, immediately reselect the corresponding prior version. Investigate persistent score regression with fresh paired controls; do not churn on one league result.',
                'submission_skill':'/Users/aaln/.codex/skills/submit/SKILL.md','visibility':'Opaque names; API has no privacy setting.','league_writes':'Both selected players only; no messages to others.'})
        versions={'aaron':h.read(RAW/'uploads/lane-neutral/version.json'),'coach':coach_upload(c,source,schema)}
        owner_id=h.get(c,'/stats/policy-versions/'+PRIOR['aaron'])['user_id']
        for label,v in versions.items():
            metadata=h.get(c,'/stats/policy-versions/'+v['id']);h.write(OUT/label/'metadata.json',metadata)
            assert metadata['user_id']==owner_id and metadata['name']==v['name']
            upload=h.read(RAW/'uploads/lane-neutral/request.json' if label=='aaron' else OUT/'coach/upload-request.json')
            assert upload['player_id']==placement.PLAYERS[label] and upload['content_hash']==h.sha(source)
            if metadata.get('player_file_content_hash') is not None:assert metadata['player_file_content_hash']==h.sha(source)
        chosen={}
        for label in ['coach','aaron']:
            chosen[label]=placement.select(c,label,versions[label],schema)
        after=placement.members(c);h.write(OUT/'after.json',after)
        for label,v in versions.items():
            assert any(m['player']['id']==placement.PLAYERS[label] and m['policy_version']['id']==v['id'] and m['is_champion'] and m['status']=='competing' and m['substatus']=='active' and m['end_time'] is None for m in after)
        result={'complete':True,'at':h.research.now(),'source_sha256':h.sha(source),'ir_sha256':manifest['ir_sha256'],
                'pair':str(PAIR.relative_to(ROOT)),'versions':versions,'memberships':{k:v['id'] for k,v in chosen.items()},
                'user_authorized_pilot_deployment':True,'independent_confirmation':False,'scope':'Both active competing champions verified. Future league score impact unmeasured.'}
        h.write(OUT/'result.json',result)
        print(json.dumps({'deployed':True,'versions':{k:v['id'] for k,v in versions.items()}}),flush=True)


if __name__=='__main__':main()

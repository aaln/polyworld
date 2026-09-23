"""One preselected reward-finisher versus 160 fresh field-refresh confirmation games."""
import argparse,json
import httpx,jsonschema
import adaptive_hosted as base
h,panel,audit=base.h,base.panel,base.audit
ROOT=base.ROOT
PRIOR_STUDY=ROOT.parent/'polyworld/tmp/gota-finish-score-20260922'
STUDY=ROOT.parent/'polyworld/tmp/gota-finish-refresh-20260922'
base.STUDY=h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-reward-refresh-20260922'
base.LABELS=['reward-finisher'];base.CONFIRM_SUBJECT=0;base.GAMES=40;base.REQUEST_PREFIX='gota-refresh0922'
base.RULE_OVERRIDE='Initial400game exact-source score gate must pass; fresh160games,40/source/color, latest Julia frozen at preparation. Zero invalid and all10source/VM/replay/XP/integer audits; aggregate gain>=10%, each color>=95%control, unchanged game and principal champion versions; background changes reported. No control reuse. Report separate bootstrap interval and duplicate streams. No universal rank claim.'
base.BUDGET_OVERRIDE='One160game cycle; shared existing UTC ledger,Sep22dated10000 thennormal1600,parallel3,batch40.'
base.NOTES_OVERRIDE=base.RULE_OVERRIDE+' New Julia has no completed public episode at preparation; fingerprint first control job before score review and require all160specs to match.'
CRITICAL={'ply_630a768f-d623-44b2-80fa-36968d6fa75a','ply_594ec24d-d7f3-4370-a000-468354ec41c9','ply_3d22435e-30a2-4f2a-b037-a5c249583788','ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83','ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb','ply_18302115-9fc9-482d-a2f3-f4c592bf9e57'}
source=base.source

def upload(c,label):
    version=h.read(PRIOR_STUDY/'uploads'/label/'version.json')
    assert h.sha(source(label).read_bytes())==h.read(PRIOR_STUDY/label/'manifest.json')['source_sha256']
    meta=h.get(c,'/stats/policy-versions/'+version['id'])
    request=h.read(PRIOR_STUDY/'uploads'/label/'request.json')
    assert request['player_id']==h.PLAYER and meta['name']==request['name']
    assert meta['user_id']==h.get(c,'/stats/policy-versions/'+base.BASELINE)['user_id']
    digest=h.sha(source(label).read_bytes())
    arm=next(a for a in h.read(PRIOR_STUDY/'trial/plan.json')['arms'] if a['name']==label)
    assert arm['version']==version['id'] and arm['source_sha256']==digest
    if meta['player_file_content_hash'] is not None:assert meta['player_file_content_hash']==digest
    h.freeze(STUDY/'metadata-reuse-proof.json',{'version':version['id'],'source_sha256':digest,'metadata_file_hash':meta['player_file_content_hash'],'ownership':'Same authenticated owner as deployed control; original upload names authorized Aaron player.','source_evidence':'Completed400game report verifies exact specs for this immutable UUID; optional stats hash field is null.'})
    h.freeze(STUDY/'uploads'/label/'version.json',version)
    return version['id']
base.upload=upload

def prepare(stage):
    assert stage=='refresh' and h.read(STUDY/'local-summary.json')['passed']
    prior=h.read(PRIOR_STUDY/'trial/report.json')
    assert prior['complete'] and prior['candidates'][0]['score_gate_passed']
    h.freeze(STUDY/'prior-trial-report.json',prior)
    with h.client() as c:
        snap=base.field.snapshot(c,STUDY/stage/'field-before')
    new=snap['champions']['ply_74ab20ef-cdf2-4250-b995-2b4f2cc96fc0']
    h.freeze(STUDY/'new-version-admission.json',new)
    roster=h.read(PRIOR_STUDY/'roster-template-v2.json')
    roster[roster.index('94a17c5a-480f-478e-ba25-60a5ecd70286')]=new['version']
    h.freeze(STUDY/'roster-template-v2.json',roster)
    base.prepare(stage,'reward-finisher')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['refresh'],default='refresh');p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.stage)
    else:base.run(a.stage)

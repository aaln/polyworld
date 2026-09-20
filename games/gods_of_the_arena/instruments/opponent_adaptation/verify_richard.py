"""Finite, journaled Richard135 verification; no policy or league mutations."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY = ROOT/'adaptive-opponent-20260920'
ORIGINAL = Path('/Users/aaln/experiments/softmax/polyworld')
PYTHON = '/Users/aaln/experiments/softmax/metta/.venv/bin/python'
CYCLE = 'interactive-richard-historical-20260920'
sys.path.insert(0,str(ORIGINAL/'tools/gota_autoresearch'))
import researcher as r
CONFIG = r.config(ROOT)
sys.path.insert(0,CONFIG['tooling'])
from hosted_wave import client, get
from win_hosted import live

COLLECTOR = Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/instruments/autoresearch_collect.py')
ARCHIVE = Path('/Users/aaln/experiments/softmax/gota-research-20260916/coached-lanes')


def checkpoint(phase, **extra):
    result = {'at':r.now(),'phase':phase,'pid':os.getpid(),'cycle':CYCLE,**extra}
    r.write(STUDY/'verification-progress.json',result)
    print(json.dumps(result),flush=True)


def verify_sources():
    inputs = [
        ('anchor','9cedf3ff-c7ce-4cff-897f-d48b44e049ad',ARCHIVE/'r5-anchored-support/hosted/anchor/upload-request.json'),
        ('bound_idle','7fe0a72b-f420-4ec3-81a1-61222ccb3036',ARCHIVE/'r5-caster-binding-repair/hosted/bound_idle/upload-request.json'),
        ('assist22','ecd056dd-49d2-44fc-838f-6c49daea8a14',ARCHIVE/'r5-ally-assist/hosted/assist22/upload-request.json'),
    ]
    proofs=[]
    with client() as api:
        for name,version,path in inputs:
            metadata=r.read(path)
            local=ROOT/'historical-richard-review-20260920/references'/name/'policy.bas'
            assert r.sha(local)==metadata['content_hash']
            proof=r.verify_remote_source(api,metadata,version)
            proofs.append({'name':name,**proof})
        remote=get(api,'/stats/policy-versions/00cd9483-0309-4613-bf61-89f3f4a33d01')
        if remote.get('player_file_content_hash') is not None:
            assert remote['player_file_content_hash']=='be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73'
        proofs.append({'name':'deployed','version':'00cd9483-0309-4613-bf61-89f3f4a33d01',
                       'remote_readback':remote,'local_source_sha256':r.sha(ORIGINAL/'examples/gods_of_the_arena/players/ir/forks/jordan268/policy.bas')})
    r.write(STUDY/'source-identity.json',proofs)


def summarize(plan):
    cells=[]
    for arm in plan['arms']:
        path=Path(arm['directory'])/'arm-result.json'
        if path.exists():
            result=r.read(path)
            cells.append({'key':arm['key'],'policy_version':arm['policy_version'],'color':arm['color'],
                          **{k:v for k,v in result.items() if k!='rows'}})
    r.write(STUDY/'verification-result.json',{'complete':len(cells)==len(plan['arms']),
        'completed_cells':len(cells),'expected_cells':len(plan['arms']),
        'games':sum(x['games'] for x in cells),'cells':cells,'promotion_eligible':False,
        'interpretation':'Fresh Richard135 fort outcomes. Detector/controller switching not tested. Full per-episode rows remain in arm-result.json; no binomial independence claim.'})
    return cells


def main():
    with r.lock(STUDY/'verification-runner.lock',blocking=False):
        assert r.sha(STUDY/'verification-plan.json')==r.read(STUDY/'verification-plan.sha256.json')['sha256']
        plan=r.read(STUDY/'verification-plan.json')
        assert len(plan['arms'])==8 and sum(a['games'] for a in plan['arms'])==320
        assert all(a['rival_version']=='7c370daf-3c5f-42f8-870b-54b79c495a44' for a in plan['arms'])
        live();verify_sources()
        # The interactive Codex coordinator supervises this finite evaluation
        # cycle. It owns no candidate source edits, snapshots or memberships.
        os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        r.write(STUDY/'verification-owner.json',{'pid':os.getpid(),'supervisor':'interactive Codex coordinator',
            'cycle':CYCLE,'authorized_games':320,'source_writer':False,'started_at':r.now(),
            'command':[PYTHON,str(Path(__file__).resolve())],'user_priority':'Richard135 only'})
        for arm in plan['arms']:
            directory=Path(arm['directory'])
            if (directory/'arm-result.json').exists():
                continue
            assert r.sha(STUDY/'verification-plan.json')==r.read(STUDY/'verification-plan.sha256.json')['sha256']
            checkpoint('waiting_or_creating',arm=arm['key'],completed=len(summarize(plan)))
            while not (directory/'batch/created.json').exists():
                try:
                    r.xp_create(ROOT,directory/'request.json',directory/'batch')
                except ValueError as exc:
                    if 'Three XP batches already active' in str(exc):
                        checkpoint('waiting_for_shared_concurrency',arm=arm['key'])
                        time.sleep(30)
                        continue
                    raise
            ident=r.read(directory/'batch/created.json')['id']
            checkpoint('harvesting',arm=arm['key'],request=ident,
                url='https://softmax.com/observatory/v2?tab=experience-requests&detail=experience-request:'+ident)
            with (directory/'harvest.log').open('a') as log:
                subprocess.run([PYTHON,str(COLLECTOR),str(directory)],stdout=log,stderr=subprocess.STDOUT,check=True)
            cells=summarize(plan)
            checkpoint('cell_complete',arm=arm['key'],result=cells[-1],completed=len(cells))
        checkpoint('complete',completed=len(summarize(plan)),games=320)


if __name__=='__main__':
    main()

"""Finish every purchased episode after a runtime quarantine; never count it as a win."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import subprocess
import time
from prepare import ROOT, STUDY, CAMPAIGN, read, write, digest
from hosted import COLLECTOR


def main():
    d=STUDY/'late-cohort/hosted/formation4800_cohort/red'
    spec=importlib.util.spec_from_file_location('original_collector',COLLECTOR)
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    plan=read(d/'plan.json');request=read(d/'batch/created.json')['id']
    body=read(d/'batch/request.json');ledger=read(CAMPAIGN/'xp-ledger.json')[body['idempotency_key']]
    assert ledger['body_sha256']==digest(body) and ledger['output']==str(d/'batch')
    config=c.CONFIG;binary=Path(config['auditor']);assert digest(binary.read_bytes())==config['auditor_sha256']
    rows={}

    def one(ep):
        p=d/'artifacts'/ep['id'];dest=p/'quarantine-review.json'
        if dest.exists():return read(dest)
        with c.client() as api:
            c.fetch(api,ep,d/'artifacts',plan['policy_version'],allow_repeated_subject=True)
            if not (p/'player-status.json').exists():write(p/'player-status.json',c.get(api,f'/v2/episode-requests/{ep["id"]}/artifacts/player-status'))
        status=read(p/'player-status.json')
        failures=[v for v in status['players'] if v.get('state')!='exited' or v.get('exit_code')!=0 or v.get('reason')!='Completed']
        if not (p/'audit.json').exists():
            result=subprocess.run([str(binary),'--replay',str(p/'replay.bin')],capture_output=True,text=True,check=True,timeout=900)
            audit=json.loads(result.stdout);audit.update(binary_sha256=config['auditor_sha256'],replay_sha256=digest((p/'replay.bin').read_bytes()))
            write(p/'audit.json',audit)
        audit=read(p/'audit.json');result=read(p/'results.json')
        assert audit['hash_mismatches']==0 and audit['ticks']==audit['recorded_ticks']==result['ticks']
        assert audit['actions_consumed']==audit['recorded_actions']
        assert audit['replay_sha256']==digest((p/'replay.bin').read_bytes())
        verified=c.validate_episode(plan,ep,result,audit,config)
        valid=not failures
        if valid:c.successful_status(status);c.verify(p,binary,config['auditor_sha256'])
        row={'episode':ep['id'],'valid':valid,'failed_players':failures,'ticks':result['ticks'],
             'reported_scores_for_diagnosis_only':result['scores'],
             'replay_reconstructed_completely':True,'replay_sha256':audit['replay_sha256'],
             'player_status_sha256':digest((p/'player-status.json').read_bytes()),
             'valid_game_outcome':verified if valid else None}
        write(dest,row);return row

    with c.client() as api,ThreadPoolExecutor(2) as pool:
        while len(rows)<40:
            es=c.episodes(api,request);write(d/'batch/episodes.json',es)
            assert len(es)<=40 and len({x['id'] for x in es})==len(es)
            ready=[e for e in es if e['status'] in c.TERMINAL and e['id'] not in rows]
            for row in pool.map(one,ready):rows[row['episode']]=row
            write(d/'quarantine-progress.json',{'request':request,'reviewed':len(rows),
                'expected':40,'invalid':sum(not r['valid'] for r in rows.values()),
                'statuses':dict(Counter(e['status'] for e in es))})
            print('REVIEWED',len(rows),'INVALID',sum(not r['valid'] for r in rows.values()),flush=True)
            if len(rows)<40:time.sleep(20)
    values=sorted(rows.values(),key=lambda r:r['episode']);valid=[r['valid_game_outcome'] for r in values if r['valid']]
    write(d/'arm-invalid-result.json',{'complete':True,'games':40,'valid_games':len(valid),
        'invalid_games':40-len(valid),'valid_wins':sum(r['win'] for r in valid),
        'valid_losses':sum(r['loss'] for r in valid),'valid_draws':sum(r['draw'] for r in valid),
        'rows':values,'cohort_eligible':False,'all_replays_reconstructed':True,
        'all_full_audits_passed':False,'reason':'BASIC instruction limit disabled an owned VM. '
            'Reject candidate and cohort; invalid episodes are neither wins nor losses. '
            'Every purchased episode is preserved and separately reviewed.'})
    plan=read(STUDY/'late-cohort/hosted-plan.json');cells=[]
    for arm in plan['arms']:
        p=Path(arm['directory']);f=p/'arm-result.json'
        if not f.exists():f=p/'arm-invalid-result.json'
        result=read(f);cells.append({'key':arm['key'],**{k:v for k,v in result.items() if k!='rows'}})
    write(STUDY/'late-cohort/hosted-result.json',{'complete':True,'games':160,'cells':cells,
        'promotion_eligible':False,'runtime_rejection':True,'decision_rule':plan['decision_rule']})


if __name__=='__main__':main()

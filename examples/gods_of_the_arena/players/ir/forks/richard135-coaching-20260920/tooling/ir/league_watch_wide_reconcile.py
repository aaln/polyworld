"""Preserve monitored beliefs when the already-authorized broad suite finishes."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import time
from hosted_wave import client,get
from jordan_lineup_wide import ROOT as WIDE
from league_threat_watch import ROOT as WATCH
from policy_ir import HERE,read,write,digest,bundle,compile_policy,extract,refresh_grounding
from ranger_guard_queue import alive
from release_deploy import champions
from release_deploy_pair import check_champions


def main():
    while True:
        stage=read(WIDE/'queue-state.json')['stage']
        if stage=='postdeployment_evaluation_complete':break
        if not alive(read(WIDE/'process.json')['pid']):
            raise RuntimeError('Broad queue stopped before completing; retain all receipts for resumption')
        time.sleep(30)
    monitor=read(WATCH/'final-report/deployed-feedback/policy.ir.json')
    parent=read(WIDE/'postdeployment-feedback/policy.ir.json');p=deepcopy(parent)
    p['belief']['claims']['B_league_monitoring']=deepcopy(monitor['belief']['claims']['B_candidate'])
    p['belief']['claims']['B_current_field_evaluation']=deepcopy(read(WIDE/'feedback/policy.ir.json')['belief']['claims']['B_candidate'])
    ev={'artifact':str(WATCH/'final-report/report.json'),'sha256':digest((WATCH/'final-report/report.json').read_bytes())}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
        change='Preserve actual league monitoring alongside completed broad XP evidence; executable unchanged',
        evidence=parent['update']['evidence']+[ev])
    refresh_grounding(p)
    source=(WIDE/'postdeployment-feedback/policy.bas').read_bytes()
    if compile_policy(p).encode()!=source or extract(source.decode(),p)!=p:
        raise ValueError('Evidence reconciliation changed policy behavior')
    if source!=(WATCH/'final-report/deployed-feedback/policy.bas').read_bytes():
        raise ValueError('Broad and monitored policies differ')
    out=WIDE/'reconciled-monitoring-feedback'
    if not out.exists():bundle(p,out)
    elif read(out/'policy.ir.json')!=p:raise ValueError('Existing immutable reconciliation differs')
    expected=read(WATCH/'final-report/metadata-readback.json')['versions']
    active=read(HERE/'active_policy.json')
    if {r['player']:r['version'] for r in active['players']}!=expected:
        write(out/'not-applied.json',{'reason':'Current player versions changed; historical pair retained'});return
    tags={'semantic_ir_sha256':digest(p),'symbolic_policy_sha256':digest(source),'ir_revision':str(p['update']['revision']),
          'monitoring_report_sha256':ev['sha256'],'broad_evaluation_sha256':digest((WIDE/'result.json').read_bytes()),
          'broad_evaluation_passed':str(read(WIDE/'result.json')['passed']).lower(),
          'feedback_parity':'Completed league monitoring and broad XP evidence; exact BASIC compile/reverse parity.'}
    with client() as c:
        check_champions(champions(c),expected,expected)
        for version in expected.values():
            remote=get(c,'/stats/policy-versions/'+version)
            response=c.put('/stats/policy-versions/'+version+'/tags',json=(remote.get('tags') or {})|tags)
            response.raise_for_status();saved=get(c,'/stats/policy-versions/'+version)['tags']
            if any(saved.get(k)!=v for k,v in tags.items()):raise ValueError('Evidence metadata did not persist')
        check_champions(champions(c),expected,expected)
    active.update(policy=str(out/'policy.bas'),semantic_ir=str(out/'policy.ir.json'),
                  latest_evaluation=str(WIDE/'result.json'),monitoring_feedback_sha256=digest(p))
    write(HERE/'active_policy.json',active)
    write(out/'verified.json',{'at':datetime.now(timezone.utc).isoformat(),'versions':expected,'tags':tags,
                             'league_selection_changed':False,'exact_ir_policy_parity':True})
    print('Broad/monitoring IR evidence reconciled for unchanged active pair',flush=True)


if __name__=='__main__':main()

"""Close failed red-watch trials without changing either live champion."""
from copy import deepcopy
from pathlib import Path
import json
import re
from policy_ir import HERE,read,write,digest,bundle,compile_policy,extract,refresh_grounding
from g002_watch import STUDY
from hosted_wave import client,get


def feedback(root,name,claim,key,evidence_path):
    out=root/'rejected-feedback'/name
    if out.exists():return
    src=root/'local/candidates'/name;p=read(src/'policy.ir.json');parent=deepcopy(p)
    evidence=[{'artifact':str(evidence_path),'sha256':digest(evidence_path.read_bytes())}]
    for k in ('B_candidate',key):p['belief']['claims'][k]={'status':'supported','claim':claim,'evidence':evidence}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Completed failed qualification; exact measured BASIC preserved.')
    p['update']['evidence']+=evidence;refresh_grounding(p)
    source=(src/'policy.bas').read_text()
    assert compile_policy(p)==source and extract(source,p)==p
    bundle(p,out)


def main():
    protected=STUDY/'protected-followup'
    result=read(protected/'discovery-result.json')
    assert result['qualified']==[] and result['arms']['g002/guard30/red']['wins']==0
    assert all(r['all_full_audits_passed'] for r in result['arms'].values())
    trials=[
        (STUDY,'watch20','Broad20 failed local10/12vsdeployed12/12; no hosted upload.','B_red_watch',STUDY/'local/qualification.json'),
        (protected,'guard20','Protected20 freshlocal12/12 butfailed required retrospective default819300; no hosted upload.','B_red_protected_watch',protected/'regression-819300/result.json'),
        (protected,'guard30','Protected30 passed local12/12and retrospective default819300, buthostedREDg0020/40versusfreshdeployed23/40. All80replay/runtime/roster/gear audits passed. Competitive gate refuted; not promoted. Localbehavior proof cannot establish rival superiority.','B_red_protected_watch',protected/'discovery-result.json')]
    for args in trials:feedback(*args)
    summary={'episode':read(STUDY/'diagnosis.json')['episode'],'diagnosis':str(STUDY/'diagnosis.json'),
      'candidate_variants':6,'local_games':183,'hosted_games':160,'champions_changed':False,'validated_replacement':None,
      'broad':{'candidate_red_wins':3,'deployed_red_wins':20,'games_per_arm':40},
      'protected':{'candidate_red_wins':0,'deployed_red_wins':23,'games_per_arm':40},
      'narrow':{'candidate_local_wins':[11,11],'deployed_local_wins':12,'games_per_arm':12,'hosted_tested':False},
      'scope':'Fixed5v5two-player lineups on2026.9.16.5. Both complete hosted candidate packages refuted. Localmechanism fixes do not justify promotion. No physicalcollisiondeadlock proven; reportedclump contains repeated accepted identicalwaitorders.',
      'readback':str(STUDY/'final-champions-readback.json')}
    write(STUDY/'final-result.json',summary)
    lab=Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena')
    path=lab/'experiments/2026-09-18-g002-protected-watch.md'
    text=path.read_text().replace('status: running','status: refuted')
    text=text.split('## Result',1)[0]+'''## Result
Protected30:0/40 REDg002 vsfreshdeployed23/40. All80 fullaudits passed. Freshlocal
12/12and retrospective defaultwin didnottransfer. Actuallocalfullreconstruction:
22180ticks136604ownedcommands exact; advance5768, recall6155, criticalcoreguard8629.
Protected20 failed retrospective default819300 and wasnotuploaded.

## Verdict
Refuted competitive gate; no promotion. Both champions remain relh154legacy.
Measured rejected IR/BASIC pairs and all artifacts preserved. Fixedlineup results
are correlated and do not support an independent-trial significance claim.
'''
    path.write_text(text)
    closed=lab/'closed_levers.md';text=closed.read_text()
    for line in [
      '- **Narrow red quietadvance with retainedrecall20/30 (.5):** both11/12localvs12/12; nohostedqualification. Fullnarrow30loss shows allgod400HP losttocreeps whileheroesfaraway. Retainedheroalarm doesnotcoverindependentcreeps.',
      '- **Protected red quietadvance30 plus3sentries atgod afterguardHP<975 (.5):** local12/12and repaireddefaultcase, but0/40REDg002vs23/40deployed. Reject; localcounterpush/recallactivation didnottransfercompetitively. Do notpromote.'
    ]:
        if line not in text:text+='\n'+line+' Evidence: '+str(STUDY/'final-result.json')+'\n'
    closed.write_text(text)
    # Update the two inert uploaded versions with the completed rejection, not their champion status.
    with client() as c:
        for root,name,note in [(STUDY,'watch30','Rejected: REDg0023/40 vsfreshdeployed20/40; all80 fullaudits. No promotion.'),
                               (protected,'guard30','Rejected: REDg0020/40 vsfreshdeployed23/40; all80 fullaudits. Local12/12 andmechanismactivation didnottransfer. No promotion.')]:
            version=read(root/'hosted'/name/'uploaded-version.json');remote=get(c,'/stats/policy-versions/'+version['id'])
            tags=(remote.get('tags') or {})|{'validation':note,'research_status':'rejected'}
            response=c.put('/stats/policy-versions/'+version['id']+'/tags',json=tags);response.raise_for_status()
            checked=get(c,'/stats/policy-versions/'+version['id']);assert checked['tags']['validation']==note
            write(root/'hosted'/name/'rejected-tags-readback.json',{'id':version['id'],'tags':checked['tags']})
            with (HERE/'VERSION_LOG.md').open('a') as f:f.write('\nCompleted evaluation '+version['id']+': '+note+' Evidence: '+str(root/'discovery-result.json')+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()

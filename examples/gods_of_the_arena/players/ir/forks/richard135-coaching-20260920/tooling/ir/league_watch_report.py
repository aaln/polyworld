"""Snapshot bounded monitoring evidence and retain an exact deployed IR/BASIC pair."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse
from economy_feedback import record
from league_threat_watch import ROOT
from policy_ir import HERE,read,write,digest,compile_policy,extract
from release_workspace import verify,RUN


def main(final=False):
    if final and (ROOT/'final-report/deployed-feedback/manifest.json').exists():
        raise FileExistsError('Final watch report is immutable; retain it and use a separate research conclusion.')
    state=read(ROOT/'state.json');plan=read(ROOT/'plan.json')
    if final:
        if datetime.now(timezone.utc)<datetime.fromisoformat(plan['ends_at']):raise ValueError('Monitoring window still active')
        if any(r['status']!='completed' for r in state['rounds'].values()):raise ValueError('Finish watched rounds first')
    rounds={};threats=[];reviews=[];external=Counter();self_duels=set()
    for eid,rows in state['episodes'].items():
        proof=ROOT/'artifacts'/eid/'review.json'
        if final and not proof.exists():raise ValueError('Unreviewed episode '+eid)
        if proof.exists():reviews.append({'episode':eid,'path':str(proof),'sha256':digest(proof.read_bytes())})
        for row in rows:
            rounds.setdefault(str(row['round_number']),Counter())[row['outcome']]+=1
            if row['self_duel']:self_duels.add(eid)
            else:external[row['outcome']]+=1
            if row['needs_replay_review']:
                threats.append({k:row[k] for k in ('episode','round_number','team','opponents')})
    studies={}
    for name in ['r5-ranger-guard','r5-red-pressure','r5-threat-coverage','r5-breach-pressure',
                 'r5-core-pressure','r5-bounded-core','r5-mage-reserve','r5-warlock-cadence',
                 'r5-owned-duel','r5-rolling-core']:
        folder=RUN/'coached-lanes'/name;entry={}
        for key in ['hosted-comparison.json','local/comparison.json','promotion-guardrail/result.json',
                    'comparison.json','queue-state.json','hosted-process.json']:
            p=folder/key
            if p.exists():entry[key]={'path':str(p),'sha256':digest(p.read_bytes())}
        studies[name]=entry
    source=verify()
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'monitoring_complete':final,
            'window':plan,'last_checked_at':state['last_checked_at'],'outcomes':state['outcomes'],
            'team_games':state['team_outcome_count'],'unique_episodes':state['episode_count'],
            'external_outcomes':external,'self_duel_episodes':sorted(self_duels),
            'rounds':rounds,'positions':state['positions'],
            'threats':threats,'reviews':reviews,'source':source,'research':studies,
            'deployed_champions':read(ROOT/'champions-latest.json'),
            'scope':'Actual league team outcomes, not independent hero copies. Research counts are separate; fixed-lineup repeated seeds are not independent tactical situations. Deferred XP is not a completed result.'}
    folder=ROOT/('final-report' if final else 'interim-report');folder.mkdir(exist_ok=True)
    write(folder/'report.json',report)
    lines=[f"League watch {'completed' if final else 'in progress'}: {external['win']} wins, {external['loss']} losses, {external['draw']} draws against other players.",
           f"{len(self_duels)} matches between our own players are counted separately; {state['episode_count']} unique episodes total.",
           f"Checked {state['last_checked_at']}. {len(reviews)} complete replay/owned-command reviews.",
           '', '| Round | Wins | Losses | Draws |','|---|---:|---:|---:|']
    for r,c in sorted(rounds.items(),key=lambda x:int(x[0])):lines.append(f"| {r} | {c['win']} | {c['loss']} | {c['draw']} |")
    lines+=['','Current positions: '+', '.join(f"{r['player_name']} #{r['rank']} ({r['score']:.2f} MMR)" for r in state['positions'])+'.','',
            'Observed losses requiring research:']
    for t in threats:
        rivals=', '.join(r['label'] for r in t['opponents']);url='https://softmax.com/observatory/v2?tab=overview&detail=episode-request:'+t['episode']
        lines.append(f"- Round {t['round_number']}, {'red' if t['team']==0 else 'blue'}: [{rivals}]({url}).")
    lines+=['','The current deployed pair remains blue_repair unless a separate verified deployment receipt says otherwise.',
            'Rejected experiments and pending evaluations remain in their original study folders; no failed gate has been relabeled as passed.',
            'Live XP dashboard: http://localhost:8801.','',report['scope']]
    (folder/'report.md').write_text('\n'.join(lines)+'\n')
    if final:
        active=read(HERE/'active_policy.json');parent=Path(active['semantic_ir']);bas=Path(active['policy'])
        claim=(f"Three-hour league monitoring: {state['outcomes']} across{state['team_outcome_count']} team games; "
               f"all{len(reviews)} replays and owned commands reconstructed on published.5. "
               'Threat reviews exposed red defensive focus/retention, caster inventory capacity, and independent core-creep coverage gaps. '
               'Follow-up candidates keep their own complete or pending verdicts. This evidence does not establish universal superiority; '
               'the exact deployed executable and original promotion basis are retained.')
        out=folder/'deployed-feedback'
        if not out.exists():record(parent,bas,claim,folder/'report.json',out)
        p=read(out/'policy.ir.json');text=bas.read_text()
        if compile_policy(p)!=text or extract(text,p)!=p:raise ValueError('Monitoring feedback changed executable')
        active['semantic_ir']=str(out/'policy.ir.json');active['monitoring_report']=str(folder/'report.json')
        active['monitoring_feedback_sha256']=digest(p);write(HERE/'active_policy.json',active)
    print(str(folder/'report.md'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');main(parser.parse_args().final)

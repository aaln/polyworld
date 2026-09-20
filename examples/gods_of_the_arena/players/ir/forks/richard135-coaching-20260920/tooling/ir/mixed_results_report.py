"""Publish a local human-readable result after the full mixed replay review."""
import argparse,os,time
from pathlib import Path
from policy_ir import read


def report(study):
    name=read(study/'local/comparison.json')['selected'];root=study/'hosted'/name
    r=read(root/'mixed-result.json');a=r['arms']['candidate'];b=r['arms']['control']
    verdict='passed' if r['passed'] else 'failed'
    lines=['# Ten-player base-defense comparison','',
           f'The candidate won **{a["wins"]}/80**, versus **{b["wins"]}/80** for the deployed pair, and **{verdict}** the declared comparison criteria. The candidate registrations have not been selected as league champions.','',
           '| Arm | Red wins / 40 | Blue wins / 40 | Total wins / 80 |',
           '|---|---:|---:|---:|',
           *[f'| {label} | {v["colors"]["red"]["win"]} | {v["colors"]["blue"]["win"]} | {v["wins"]} |' for label,v in [('Deployed',b),('Candidate',a)]],
           '', 'Only the two owned players changed between arms. The other eight versions were pinned to the reported episode; the second color mirrors both complete teams. These are two fixed role contexts with repeated trajectories, not a broad league win-rate estimate. All games underwent full replay, VM, source, roster, ownership and equipment validation.',
           '', 'The coordinated candidate adds blue assigned response to a visible isolated hero targeting an own final guard or god, with nearby interception and staggered remote backup. It retains group sentries, individual rally destinations and nearby core interception. Red retains the fused parent behavior. Local confirmation was58/60 versus deployed56/60 and fused58/60; the solo-response component had no additional local win gain over fused.',
           '', 'Criteria: blue gain at least8/40, total gain at least16/80, no red win regression, both owned heroes buy items. Exact checks: `'+str(r['checks'])+'`.',
           '', 'The original replay diagnosis was corrected using actual orders: the Ranger briefly targeted Jordan, then abandoned the defense. By4:25 all living allies were away from home. Tick traces also show short guard-attack bursts separated by six-second gaps. A separate warning-memory follow-up is being tested; this160-game candidate was kept fixed.',
           '', '## Representative replay inspection','',
           'The largest blue command group per outcome in each arm was selected for inspection. The counts below are sampled time observations in those representatives, not independent episodes or an all-game response rate.','',
           '| Arm / outcome | Episode | Isolated attack samples | Samples followed by owned attack-target orders | Owned repeated-walk windows |',
           '|---|---|---:|---:|---:|']
    for row in read(root/'replay-review/result.json')['rows']:
        link='https://softmax.com/observatory/v2?tab=experience-requests&detail=episode-request:'+row['episode']
        lines.append(f'| {row["arm"]} / {row["outcome"]} | [Replay]({link}) | {row["isolated_samples"]} | {row["isolated_samples_with_owned_target_order"]} | {row["owned_stall_windows"]} |')
    lines+=['', '[Complete results](hosted/'+name+'/mixed-result.json) · [Evaluated IR](hosted/'+name+'/mixed-feedback/policy.ir.json) · [Generated BASIC](hosted/'+name+'/mixed-feedback/policy.bas)', '',
            'Captured inputs and rejected experiments remain preserved. Compilation and reverse extraction retain the exact tested behavior when adding measured evidence.']
    (study/'REPORT.md').write_text('\n'.join(lines)+'\n')
    return study/'REPORT.md'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path);p.add_argument('--wait-pid',type=int)
    a=p.parse_args();name=read(a.study/'local/comparison.json')['selected'];root=a.study/'hosted'/name
    while not (root/'mixed-feedback/policy.ir.json').exists() or not (root/'replay-review/result.json').exists():
        if not a.wait_pid:raise ValueError('Complete mixed audit, review and feedback required')
        try:os.kill(a.wait_pid,0)
        except ProcessLookupError:raise RuntimeError('Hosted runner stopped before feedback; inspect preserved logs')
        time.sleep(15)
    print(report(a.study))

"""Write a compact macro review and reproducible XP/league discrepancy report."""
import json
from counterpush import STUDY
from policy_ir import read, write


def main():
    out=STUDY/'artifacts/ereq_9a4bd7d2-c873-4007-a12d-fe77976a0cce'
    frames={r['tick']:r for line in (out/'decoded.jsonl').open()
            if (r:=json.loads(line)).get('type')=='frame'}
    decisions={(r['tick'],r['slot']):r for line in (out/'decisions-team-0.jsonl').open()
               if (r:=json.loads(line)).get('type')=='decision'}
    rows=[]
    for tick in [6480,8400,8640,8760,9240,9600,12000,14400,17280]:
        f=frames[tick]
        rows.append({'tick':tick,'living':[sum(h['hp']>0 and h['team']==c for h in f['heroes']) for c in (0,1)],
                     'towers':[sum(b['kind']=='TowerBuilding' and b['team']==c and b['hp']>0 for b in f['buildings']) for c in (0,1)],
                     'defending_no_target':[s for s in range(5) if (d:=decisions.get((tick,s))) and
                                            d['memory']['defActive'] and d['memory']['bestId']==0],
                     'owned_levels':[h['level'] for h in f['heroes'][:5]]})
    write(STUDY/'macro-timeline.json',rows)
    lines=['# Richard v78: the red defense trap', '',
        'The linked XP run is exclusively blue. Its 40/40 wins do not contradict the red league loss.', '',
        '| Context | Red wins / losses / draws | Blue wins / losses / draws |',
        '|---|---:|---:|', '| Completed paired XP | 11 / 24 / 5 | 40 / 0 / 0 |', '',
        '- [Blue XP](https://softmax.com/observatory/v2?tab=experience-requests&detail=experience-request:xreq_b6fa0306-c8e7-4aa9-948b-60556343742b)',
        '- [Red XP](https://softmax.com/observatory/v2?tab=experience-requests&detail=experience-request:xreq_5431a9cf-7c86-4f34-b8d3-8b69958a5842)',
        '- [League loss](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_9a4bd7d2-c873-4007-a12d-fe77976a0cce)', '',
        'Both contexts use game 2026.9.16.5, the same map and gameplay settings, and Richard v78 '
        '(881a807d-68ab-4a62-9b6c-e98694cf0bc3). Aaron and Optimizer registrations contain identical '
        'BASIC (f8fba2fa812f9d88f156a928daecc5ea5509c0388187e2ee9f324f12cd6899e2). '
        'Resolved config differences are player display names. Generated replay seeds differ.', '',
        '**The complete league command sequence matches 12 red XP losses exactly**, across all '
        'heroes and ticks. See xp-discrepancy/league-command-comparison.json. The full 80-game '
        'cohort contains 9 distinct command tapes per color, so 80 episodes are not 80 independent '
        'tactical trials.', '',
        'All 17,356 league state hashes and 105,265 actual owned commands were reconstructed '
        'using the exact deployed source. This is a decision-state diagnosis, not an inference '
        'from the screenshot alone.', '',
        '| Tick | Living red / blue | Towers red / blue | Red defending without a target |',
        '|---:|---:|---:|---|']
    names=['Death Knight','Crossbowman','Lich','Warlock','Berserker']
    for r in rows:
        lines.append(f'| {r["tick"]} | {r["living"][0]} / {r["living"][1]} | '
                     f'{r["towers"][0]} / {r["towers"][1]} | '+', '.join(names[s] for s in r['defending_no_target'])+' |')
    lines += ['', 'At tick 8,760, four living heroes shared rally (73,11), with no selected '
        'target. Their former anchor, tower 11, had already been destroyed by tick 8,640. '
        'Vanguard and Demon Hunter were dead; the three living opponents were far from our base. '
        'Our Berserker had pushed alone and died. Three sentries retained commitment until '
        '15,811, another 293.8 seconds; Crossbowman until 10,051, another 53.8 seconds.', '',
        'From tick 8,760 onward, 70–72% of the four defenders’ sampled living decisions were '
        'active defense with no target. These are five-second snapshots, not exact duty-time totals. '
        'The group repeatedly won fights but yielded the next move to Richard. At 17,280 all '
        'four defenders were dead; the lone Berserker was far away. Richard finished the core '
        'at 17,356. This establishes the mechanism of lost pressure, not a guarantee that any '
        'particular counterattack would win.', '',
        'Red retains the old long sentry commitment and shared rally. Blue already has '
        'objective-relative target coverage and class-separated rally points; its two attacking '
        'roles can leave quiet defense. That intentional color split explains why a blue-only '
        'test looked strong while league red games exposed the weakness.', '',
        'The new IR candidates retire a missing friendly anchor, require a survivor to actually '
        'attack a standing anchor before renewing duty, keep active combat and fresh rushes '
        'eligible for defense, separate rally points, and resume wave pressure after bounded '
        'quiet. Three coordinated schedules are tested: 20 seconds, 40 seconds, or 20 seconds '
        'with a 60-second Death Knight rear guard. Blue behavior and item buying remain covered '
        'by parity checks. Existing solo/core-creep limitations are not claimed fixed.', '',
        'Validation and status are in local/comparison.json and hosted-comparison.json when '
        'complete. No new champion is selected by these test runners. A Richard pass requires '
        'at least 28/40 red wins, a gain of at least 10, and at least 38/40 blue wins. Jordan, '
        'other known threats, and 200 ten-player games follow only after that gate passes.', '']
    (STUDY/'REPORT.md').write_text('\n'.join(lines))


if __name__=='__main__':main()

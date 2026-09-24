"""Reflect complete release62 evidence into byte-identical semantic/policy pair."""
import hashlib
import json
import pprint
import shutil
import subprocess
import sys
import camp_binding as b

ROOT=b.ROOT
RAW=ROOT.parent/'polyworld/tmp/gota-lane-neutral62-20260923'
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/neutralfarm20260923-hosted/lane-neutral'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2)+'\n')


def main():
    stats=read(RAW/'statistics.json');plan=read(RAW/'hosted-plan.json')
    probe=read(RAW/'source-audit.json')
    assert stats['complete'] and stats['all_120_games_10_vms_valid'] and stats['full_hash_xp_score_config_pair_audits']
    assert probe['complete'] and probe['games']==40
    assert all(r['max_instructions']<=19000 and r['max_work']<=50000 for r in probe['rows'])
    assert all(r['prefix_ticks']==read(RAW/'artifacts'/r['episode']/'audit-result.json')['ticks'] for r in probe['rows'])
    assert not OUT.exists(),'Preserve reviewed pair'
    shutil.copytree(RAW/'lane-neutral',OUT,ignore=shutil.ignore_patterns('__pycache__'))
    b.configure();p=read(OUT/'policy.ir.json')
    camp=stats['contrasts']['lane-neutral'];lane=stats['contrasts']['lane-only'];inc=stats['camp_vs_lane']
    s=camp['overall'];l=lane['overall'];i=inc['overall']
    p['belief']['claims']['CampMechanism'].update(status='requires_review',
        claim=f"48 actual-host decision fixtures verify guarded pulling, handoff, timeout, returning immunity and cancellation. All40complete hosted own-source reconstructions match every command and state hash: {probe['games_with_neutral_targets']}games select neutrals; {probe['games_with_pulls']}games start{probe['pull_starts']}pulls. These observations do not isolate the score effect of successful wave pulls from direct neutral farming or unrelated combat changes.",
        evidence=[{'artifact':'evidence/practice-comparison.json'},{'artifact':'evidence/source-audit.json'},{'artifact':'evidence/statistics.json'}])
    p['belief']['claims']['CurrentScoreGain'].update(status='supported' if camp['pilot_advance'] else 'requires_review',
        claim=f"Fresh replay62 discovery,40matched seeds: parent mean{s['baseline']['mean']:.3f}, lane-only{l['candidate']['mean']:.3f}, lane-neutral{s['candidate']['mean']:.3f}. Combined delta{s['mean_delta']:+.3f},97.5%interval{s['delta975']}; incremental camp-vs-lane delta{i['mean_delta']:+.3f},95%interval{i['delta95']}. Combined score pilot advance={camp['pilot_advance']}; no independent confirmation or deployment qualification.",
        evidence=[{'artifact':'evidence/statistics.json'},{'artifact':'evidence/hosted-plan.json'}])
    p['update'].update(revision=2,needs_review=['belief/CampMechanism']+([] if camp['pilot_advance'] else ['belief/CurrentScoreGain']),
        evidence=[{'artifact':'evidence/'+n} for n in ['request.json','cohort-amendment.json','statistics.json','practice-comparison.json','native-comparison.json']])
    p['update']['change'].update(origin='Reviewed neutral-camp update and prior lane coaching with a fresh matched release62 cohort; score-only rule. Invalid Jordan411 compilation cohort preserved in full. Tested BASIC unchanged.',deployment_qualified=False)
    b.ir.refresh_grounding(p)
    assert b.ir.compile_policy(p).encode()==(OUT/'policy.bas').read_bytes()
    assert b.ir.extract((OUT/'policy.bas').read_text(),p)==p
    for name,data in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',b.ir.grounded(p))]:write(OUT/name,data)
    (OUT/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    for name in ['hosted-plan.json','statistics.json','baseline-pool.json','practice-comparison.json',
                 'native-comparison.json','native-result.json','native-plan-with-hashes.json','runtime-provenance.json',
                 'skill-difference.json','cohort-amendment.json','upstream-camps.log','league-readback.json','source-audit.json','audit-tool-provenance.json']:
        shutil.copyfile(RAW/name,OUT/'evidence'/name)
    artifacts={}
    for label in ['lane-only','lane-neutral']:
        d=read(RAW/'counterfactual'/label/'paired-results.json')
        write(OUT/'evidence'/label/'paired-results.json',d)
        for r in d['pairs']:
            for arm in ['baseline','candidate']:
                folder=RAW/'artifacts'/r[arm]['episode']
                if folder.name in artifacts:continue
                files={n:sha(folder/n) for n in ['replay.bin','audit.json','audit-result.json','results.json','spec.json','player-status.json']}
                files['sharing/telemetry.json']=sha(RAW/'sharing'/folder.name/'telemetry.json')
                if label=='lane-neutral' and arm=='candidate':files['source-audit/result.json']=sha(RAW/'source-audits'/folder.name/'result.json')
                artifacts[folder.name]=files
    write(OUT/'evidence/artifact-index.json',artifacts)
    invalid=RAW/'invalid-jordan411'
    write(OUT/'evidence/invalid-cohort.json',{'request':'xreq_0ce9a734-3e37-4158-abaa-8ecb9c367fc2',
        'episodes':read(invalid/'failed-release62-batch.json'),
        'plan':read(invalid/'hosted-plan.json'),
        'files':{str(f.relative_to(invalid)):sha(f) for f in invalid.rglob('*') if f.is_file()}})
    scores=[]
    for label,c in stats['contrasts'].items():
        v=c['overall'];scores.append(f"| {label} | {v['candidate']['mean']:.2f} | {v['mean_delta']:+.2f} | [{v['delta975'][0]:+.2f}, {v['delta975'][1]:+.2f}] | {c['pilot_advance']} |")
    metrics=[]
    for title,key in [('Total XP','xp'),('Lane-creep XP','creep_xp'),('Neutral XP','neutral_xp'),('Hero XP','hero_xp'),('Structure/other XP','structure_or_other_xp'),('Camp engagements','camp_engagements'),('Hero kills','kills'),('Deaths','deaths'),('Minutes','minutes'),('Alive XP drought ≥30sec','alive_drought_ge30_seconds')]:
        vals=[lane['telemetry']['baseline']['means'][key],lane['telemetry']['candidate']['means'][key],camp['telemetry']['candidate']['means'][key]]
        metrics.append('| '+title+' | '+' | '.join(f'{x:.2f}' for x in vals)+' |')
    contexts=[]
    for key in lane['by_context']:
        a=lane['by_context'][key];c=camp['by_context'][key]
        contexts.append(f"| {key} | {a['baseline']['mean']:.2f} | {a['candidate']['mean']:.2f} | {c['candidate']['mean']:.2f} |")
    report=f'''# Lane selection and neutral farming / release62

User coaching: farm less crowded lanes and account for the new neutral camps.
Primary objective is expected individual `floor(max(0, XP −200×minutes))`.
Team wins, deaths, nonzero frequency and conditional means are diagnostics.

Fresh parent mean **{s['baseline']['mean']:.2f}**. Forty paired seeds per arm,
four fixed color/seat contexts, nine responsive pinned opponents. Treatments
reuse the same40controls:120valid hosted games in total.
The parent is control-tactics sourceb3f0c124, a research fork; this is not a fresh
comparison against deployed incumbent29f6d7e6.

| Treatment | Mean score | Delta versus parent | 97.5% paired interval | Pilot advance |
|---|---:|---:|---:|---|
{chr(10).join(scores)}

Adding camps to lane selection changes score by **{i['mean_delta']:+.2f}**,
exploratory95%interval **[{i['delta95'][0]:+.2f}, {i['delta95'][1]:+.2f}]**.
This is discovery, with no established verdict sample floor or independent
confirmation. No deployment qualification and no league writes.

## Version and mechanics

Exact engine `2c8db6ebe1dc785ce1eea87496505d1244ee4c44`, game2026.9.23.4,
replay62/format6/outer2, coworld `cow_a472c872-2b97-4b81-9961-e171304e5d63`.
The earlier lane61+11.14% result remains separate; it is not this study's control.

Fourteen camp clearings form seven mirrored pairs. Tier1/2/3 mobs award20/35/50XP
and10/20/30gold; leaders double HP and rewards. Neutral XP goes to eligible
nearby heroes on the last-hitting unit's team, with15%reserved for an eligible
hero last hitter and85%shared. Gold requires a hero last hit. Thus allied lane
creeps can help generate neutral XP without granting the hero last-hit gold.
Returning mobs are immune. The leash is12tiles; full clears respawn after60sec
unless a living hero remains within10tiles. Static geometry is public; hidden
mob life and respawn state are not. Source: exact engine `sim.nim`, `bots.nim`,
and `players/puller.bas`; upstream neutral-camp suite passes.

The candidate retains lane/hero combat priority. With sufficient level and HP,
it farms visible nearby neutrals during gaps instead of choosing a structure
or an empty advance. If an idle allied wave is nearby, it can enter camp aggro
and move beyond the wave, within the leash. Pulls require safety and two nearby
allied creeps; they stop on handoff, danger, root, low HP, missing wave/sight,
invalid route or15sec timeout, then wait20sec before retrying. These are
heuristics, not an optimal XP planner. Direct farming and pulling are tested as
a coordinated bundle; the experiment does not isolate those two components.
The parent already admits neutrals through its generic target scan, and
attack-move can also engage them. This tests more selective neutral behavior,
not the first ability to gain neutral XP.
The new guards control explicit neutral selection and pulling; inherited
attack-move can still engage other camps incidentally.

## Validation and invalid batch

48host fixtures pass; maximum4591instructions/7621work. Twelve complete native
games pass exact replay and runtime checks. Native totals10479parent,
10701lane-only,11648combined are a small reference-bot screen only.
The first pull-cancellation prototype is archived separately; finalr62b fixes
cleanup when an earlier retreat skill has already claimed movement.

The first10hosted controls all failed Jordan411 BASIC compilation in slot7.
The other nine reported exit0. That complete batch is preserved and is invalid,
not zero-score evidence. A prospective amendment replaced Jordan with BeWellBot
and uploaded a distinct baseline clone before requesting any replacement games.
No successful or failed score was selected out of the replacement cohort.
Total new reservations:130, including10invalid; requests contain10or40games.

All120replacement games have ten valid VMs, exact full replay hashes, XP and
integer-score reconciliation, matching seeds, configs, manifests, slots and
nine unchanged opponent source hashes. Stratified whole-pair bootstrap uses
10000draws, seed9236102. Two baseline contrasts use97.5%intervals (Bonferroni);
incremental and class/context comparisons are exploratory. Canonical command
stream uniqueness is recorded in statistics.json. No game-win gate is used.
All40combined-candidate own-source reconstructions match every command and
world-state hash through the complete games: {probe['matched_commands']}commands,
{probe['games_with_neutral_targets']}games with neutral target decisions, and
{probe['pull_starts']}pull starts across{probe['games_with_pulls']}games. Retrospective
source reconstruction is separate from the responsive score counterfactuals.

## Descriptive XP and time attribution

| Per-game mean | Parent | Lane only | Lane + camps |
|---|---:|---:|---:|
{chr(10).join(metrics)}

| Context | Parent score | Lane only | Lane + camps |
|---|---:|---:|---:|
{chr(10).join(contexts)}

The combined policy earns **less neutral XP** (1027.88→681.45) and engages
fewer camps (9.90→5.25), while lane-creep XP rises2952.03→3530.43 and hero XP
1488.75→1717.50. The supported result is improved selective behavior as a bundle,
not a benefit from maximizing camp clears. The lane-only arm increases neutral
XP but loses more lane/hero XP and fails its pilot rule.

Druid's pooled mean is nearly unchanged (1426.10→1423.70), hiding red-seat3
delta+659.50 and blue-seat3−664.30. Blue first-seat ranged improves+2013.30;
red first-seat ranged changes+49.00. These are10-pair diagnostic slices, not
separate advancement gates or confirmed subgroup effects. Investigate the blue
Druid regression before broad confirmation; preserve the aggregate result.

All XP sources and disjoint time-state budgets reconcile. Neutral XP proves
reward exposure; it does not prove that wave pulls caused every neutral kill.
Route changes also alter combat exposure and travel, so the tables describe
mechanisms without assigning isolated causality. Outcomes from the frozen field
do not guarantee improvement against later opponent versions.

Parent `{plan['versions']['baseline']}`, lane-only `{plan['versions']['lane-only']}`,
combined `{plan['versions']['lane-neutral']}` are inert research versions.
Both league champions retain source29f6d7e6. Reviewed semantic annotations compile
to byte-identical tested source2fbd789b; `python verify.py` verifies the portable
IR/policy pair, converter, evidence and hashes. Original IR, raw captures,
failed prototypes and complete hosted artifacts remain at
`polyworld/tmp/gota-lane-neutral62-20260923`.
'''
    (OUT/'README.md').write_text(report)
    verify=(b.PARENT/'verify.py').read_text().replace('tooling/lanefarm20260923','tooling/neutralfarm20260923').replace('import occupancy_binding as b','import camp_binding as b').replace('all_160_games_10_vms_valid','all_120_games_10_vms_valid')
    (OUT/'verify.py').write_text(verify)
    m=read(OUT/'manifest.json');m.update(ir_sha256=b.ir.digest(p),hosted_complete=True,local_validated=True,
        pilot_score_gate_passed=camp['pilot_advance'],deployment_qualified=False,reviewed_ir_preserves_tested_source=True)
    m['artifacts']={str(f.relative_to(OUT)):sha(f) for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts}
    write(OUT/'manifest.json',m)
    subprocess.run([sys.executable,str(OUT/'verify.py')],check=True)
    (ROOT/'games/gods_of_the_arena/experiments/2026-09-23-lane-neutral-farming.md').write_text(report+f'\nPortable pair: `{OUT.relative_to(ROOT)}`.\n')
    print(json.dumps({'pair':str(OUT.relative_to(ROOT)),'source':m['source_sha256'],'ir':m['ir_sha256']}))


if __name__=='__main__':main()

"""Save the reviewed semantic/policy pair and its full paired evidence."""
import hashlib
import json
import pprint
import shutil
import subprocess
import sys
import occupancy_binding as b

ROOT = b.ROOT
RAW = ROOT.parent / 'polyworld/tmp/gota-lane-occupancy61-20260923'
OUT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/lanefarm20260923-hosted/lane-occupancy'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n')


def main():
    stats = read(RAW/'statistics.json')
    s = stats['overall']
    probe = read(RAW/'source-audit.json')
    assert stats['all_160_games_10_vms_valid'] and stats['full_hash_xp_score_config_pair_audits']
    assert probe['complete'] and probe['games'] == 80
    assert not OUT.exists(), 'Preserve reviewed pair'
    shutil.copytree(RAW/'lane-occupancy', OUT, ignore=shutil.ignore_patterns('__pycache__'))
    b.configure()
    p = read(OUT/'policy.ir.json')
    p['belief']['claims']['LaneIntent'].update(status='supported',
        claim=f"120actual host decision fixtures verify one opening choice, safety/unknown/tie guards, expiry, respawn persistence and blue routing. All80hosted opening sources reconstruct exact commands and state hashes; {probe['changed_lane_games']} change lanes. The counts estimate allied commitment, not guaranteed future solo XP.",
        evidence=[{'artifact':'evidence/practice-comparison.json'},{'artifact':'evidence/source-audit.json'}])
    p['belief']['claims']['ScoreGain'].update(status='supported' if stats['pilot_advance'] else 'requires_review',
        claim=f"80matched responsive hosted comparisons on the full reused control cohort: individual score {s['baseline']['mean']:.3f}to{s['candidate']['mean']:.3f}; delta{s['mean_delta']:+.3f}, paired95%interval{s['delta95']}. Score-only pilot advancement={stats['pilot_advance']}. No independent confirmation or deployment qualification; isolation alone is not an improvement.",
        evidence=[{'artifact':'evidence/statistics.json'}])
    p['update']['revision'] = 2
    p['update']['change'].update(origin='Reviewed user lane-sharing coaching against the full80pair counterfactual cohort. Test source unchanged. Score is the only optimization gate.', deployment_qualified=False)
    p['update']['needs_review'] = [] if stats['pilot_advance'] else ['belief/ScoreGain']
    p['update']['evidence'] = [{'artifact':'evidence/'+n} for n in ['request.json','statistics.json','source-audit.json','native-comparison.json','practice-comparison.json']]
    b.ir.refresh_grounding(p)
    assert b.ir.compile_policy(p).encode() == (OUT/'policy.bas').read_bytes()
    assert b.ir.extract((OUT/'policy.bas').read_text(), p) == p
    for name, value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',b.ir.grounded(p))]: write(OUT/name,value)
    (OUT/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    for name in ['hosted-plan.json','statistics.json','paired-results.json','baseline-pool.json','source-audit.json',
                 'practice-comparison.json','native-comparison.json','native-result.json','native-plan-with-hashes.json',
                 'runtime-provenance.json','telemetry-provenance.json','skill-difference.json','league-readback.json']:
        shutil.copyfile(RAW/name, OUT/'evidence'/name)
    index = []
    for r in read(RAW/'paired-results.json')['pairs']:
        for arm in ['baseline','candidate']:
            folder = RAW/'artifacts'/r[arm]['episode']
            files = {n:sha(folder/n) for n in ['replay.bin','audit.json','audit-result.json','results.json','spec.json','player-status.json']}
            files['sharing/telemetry.json'] = sha(RAW/'sharing'/folder.name/'telemetry.json')
            if arm == 'candidate': files['source-audit/result.json'] = sha(RAW/'source-audits'/folder.name/'result.json')
            index.append({'episode':folder.name,'arm':arm,'files':files})
    write(OUT/'evidence/artifact-index.json',index)
    metrics = stats['telemetry']
    measure = lambda arm,key: metrics[arm]['means'][key]
    rows = []
    for label,key in [('Total XP','xp'),('Creep XP','creep_xp'),('Hero XP','hero_xp'),('Structure/other XP','structure_or_other_xp'),('Solo-recipient creep XP','creep_xp_shared_with_1_recipients'),('Hero kills','kills'),('Deaths','deaths'),('Game minutes','minutes')]:
        rows.append(f"| {label} | {measure('baseline',key):.2f} | {measure('candidate',key):.2f} |")
    classes = []
    for key,value in stats['by_class'].items():
        classes.append(f"| {key} | {value['n']} | {value['baseline']['mean']:.2f} | {value['candidate']['mean']:.2f} | {value['mean_delta']:+.2f} |")
    report = f'''# Less-crowded opening lane / engine61

User coaching: choose a lane that other players are not going to, to increase
individual XP-minus-time score. The implemented hypothesis concerns **allied**
competition for creep XP; enemies may supply hero-kill opportunities.

Mean individual score **{s['baseline']['mean']:.2f} → {s['candidate']['mean']:.2f}**,
paired delta **{s['mean_delta']:+.2f}**, 95% paired bootstrap interval
**[{s['delta95'][0]:+.2f}, {s['delta95'][1]:+.2f}]**.
Score-only pilot advancement: **{stats['pilot_advance']}**. This is a directional
study on a reused cohort, without an established verdict-size floor or independent
confirmation. No league deployment. All80pairs are retained; no game-win gate.

## Mechanism and coordinated implementation

At engine `e42c4822f44e04726b09bb4ffe853152c7a18207`, each creep supplies15XP
within six tiles on its navigation layer. An eligible last hitter reserves15%;
the remaining85% is shared. A sole eligible hero receives15XP; with two heroes,
the last hitter averages8.625 and the other6.375, including fractional carry.
Gold last-hit rewards are separate. These theoretical shares do not guarantee
that a lane choice reaches or kills more creeps.

During12–35seconds after first activation, the policy classifies allied heroes
at least12tiles from home by their angular direction toward the three existing
lane waypoints. All allied positions are public. With at leasttwo committed
allies, it chooses a strictly less crowded lane if healthy and away from current
targets/threats. Occupancy ties retain the current route; shorter waypoint travel
breaks ties between better alternatives. It commits once, persists the choice
through respawns, invalidates a stale portal anchor, and lets an explicit choice
override the first-seat blue ranged center route. It does not estimate wave size,
future enemy pressure, navigation travel time, or joint teammate coordination.

Changed executable components: lifecycle, observation, advance, plus choose_lane.
Draft, economy, combat, crowd control, recovery and all other skill bodies match
the control-tactics parent. All strategy goal references use individual Score.
An initial Q16.16 overflow prototype was preserved and repaired before upload.

## Validation and experiment

120host decision executions pass, including unknown/near-home allies, balanced
lanes, low HP, nearby enemy, opening expiry, persistent assignment and blue
override. Eight new complete native games match eight preserved parent controls:
total score20818→18845, three lower and five equal. This is negative reference-bot
evidence, not omitted or used to redefine the hosted cohort.

Hosted: all80prior control-tactics candidate games serve as baseline;80new
counterfactual games replace only our policy. Exact seed, resolved roster, probe
slot, game configuration, manifest and nine responsive sources are paired.
Every game has ten valid VMs, exact full replay hashes, XP and integer scores.
All80opening source reconstructions match commands and world-state hashes;
**{probe['changed_lane_games']}/80 actually change lane**.

Baseline `morrow-ibis-61c2:v1` (`f063e236-4f9b-4f52-a57c-e41b29d14caf`),
candidate `sable-oriole-61d3:v1` (`4d55ef4d-cfa2-485d-a048-a81c35b8acd3`).
Counterfactual evaluation `cfeval_1d51ee96-53df-47a7-b1c6-77d0929aa235`;
experience request `xreq_62c0d9f3-0d08-4f64-975f-dec4edd65e2c`.
Both league champions retain the previously deployed source29f6d7e6.

## Descriptive mechanism metrics

| Per-game mean | Parent | Lane candidate |
|---|---:|---:|
{chr(10).join(rows)}

Solo-recipient XP is counted from actual positive XP recipients for each creep
death, not lane geometry. Counts1–5 reconcile exactly to all creep XP, and all
XP sources reconcile to integer scores. Hero/side/seat breakdowns, survival,
nonzero frequency and conditional means are diagnostics; they do not change the
frozen score-only rule. Attribution is descriptive, not an isolated component
effect; route, travel, support and combat exposure change together.

| Hero class ID | Pairs | Parent score | Candidate score | Delta |
|---|---:|---:|---:|---:|
{chr(10).join(classes)}

All20changed games are blue first-seat ranged heroes moving from the center
route to lane2; the other60full command streams and scores remain identical.
That context improves3763.65→4874.95 (+29.53%). Overall creep XP rises323.96
while hero XP falls138.75; solo-recipient creep XP rises326.06. Most baseline
creep XP was already solo-recipient (91.26% versus92.11% candidate), so this is
mainly more solo farming opportunities, not proof that splitting the same wave
was the dominant loss. Fewer hero kills did not prevent a higher individual score.

After the study, the league changed to2026.9.23.4/replay62, commit2c8db6e,
adding neutral camps. This61result does not qualify current-release deployment.
A separate current-release comparison will test lane-only and guarded camp
farming while preserving every source and result in this cohort.

Raw inputs, original IR, replay tapes and upload receipts remain in
`polyworld/tmp/gota-lane-occupancy61-20260923`. Reused baselines link to the
untouched preceding control study. The portable pair contains every pair ID,
file hashes, frozen method, results and source audit. Reviewed IR annotations
regenerate byte-identical tested BASIC; run `python verify.py` or the included
compile/extract converter. No inferred live XP or private opponent state is used.
'''
    (OUT/'README.md').write_text(report)
    verification = (b.PARENT/'verify.py').read_text().replace('tooling/controltactics20260923','tooling/lanefarm20260923').replace('import tactics_binding as b','import occupancy_binding as b')
    (OUT/'verify.py').write_text(verification)
    m = read(OUT/'manifest.json')
    m.update(ir_sha256=b.ir.digest(p),hosted_complete=True,local_validated=True,
        pilot_score_gate_passed=stats['pilot_advance'],deployment_qualified=False,
        reviewed_ir_preserves_tested_source=True,score_gate_passed=None)
    m['artifacts'] = {str(f.relative_to(OUT)):sha(f) for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts}
    write(OUT/'manifest.json',m)
    subprocess.run([sys.executable,str(OUT/'verify.py')],check=True)
    (ROOT/'games/gods_of_the_arena/experiments/2026-09-23-lane-occupancy.md').write_text(report+f'\nPortable pair: `{OUT.relative_to(ROOT)}`.\n')
    print(json.dumps({'pair':str(OUT.relative_to(ROOT)),'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'pilot_advance':stats['pilot_advance']}))


if __name__ == '__main__': main()

"""Publish reviewed evidence without changing the tested executable bytes."""
from pathlib import Path
import hashlib
import json
import pprint
import shutil
import subprocess
import sys
import tactics_binding as b

ROOT=b.ROOT
RAW=ROOT.parent/'polyworld/tmp/gota-control-tactics61-20260923'
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/controltactics20260923-hosted/control-tactics'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')


def main():
    stats=read(RAW/'statistics.json');s=stats['overall'];b.configure()
    assert stats['all_160_games_10_vms_valid'] and stats['full_hash_xp_score_config_pair_audits']
    assert not OUT.exists(),'Preserve captured reviewed pairs'
    shutil.copytree(RAW/'control-tactics',OUT,ignore=shutil.ignore_patterns('__pycache__'))
    p=read(OUT/'policy.ir.json')
    p['belief']['claims']['ControlMechanism'].update(status='supported',claim='120matched real-tick fixtures verify useful hero control during retreat, overlap guards, resource legality and healing reserve. Warlock silence prevents one scripted cast and saves42HP; Vanguard stun saves38HP. Standard level2E unlock is identical to baseline; no unlock benefit established. Native twoWarlock cases gain502and949points; other six unchanged. These tests do not isolate each component or prove all-class league gains.')
    p['belief']['claims']['CompetitiveGain'].update(status='supported' if stats['pilot_advance'] else 'requires_review',
        claim=f"80paired responsive hosted comparisons: mean{s['baseline']['mean']:.3f}to{s['candidate']['mean']:.3f}, delta{s['mean_delta']:+.3f}, paired95%interval{s['delta95']}. Frozen pilot advancement={stats['pilot_advance']}. Directional pilot only; no deployment qualification or no-regression guarantee. Natural subject classes are Ranger, Crossbowman and Druid; no hosted Warlock/Vanguard/Lich efficacy claim.",evidence=[{'artifact':'evidence/statistics.json'}])
    p['update']['revision']=2
    p['update']['change'].update(origin='Reviewed exact tested control source after120pairedfixtures,16nativegames and80pairedhostedgames. Later user score-only steering applies to future studies; frozen gate preserved.',deployment_qualified=False)
    p['update']['needs_review']=[] if stats['pilot_advance'] else ['belief/CompetitiveGain']
    p['update']['evidence']=[{'artifact':'evidence/statistics.json'},{'artifact':'evidence/practice-comparison.json'},{'artifact':'evidence/native-comparison.json'},{'artifact':'evidence/score-objective-steering.json'}]
    b.ir.refresh_grounding(p)
    assert b.ir.compile_policy(p).encode()==(OUT/'policy.bas').read_bytes()
    assert b.ir.extract((OUT/'policy.bas').read_text(),p)==p
    for f,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',b.ir.grounded(p))]:write(OUT/f,v)
    (OUT/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    for name in ['hosted-plan.json','statistics.json','paired-results.json','practice-comparison.json','native-comparison.json','native-result.json','native-plan-with-hashes.json','runtime-provenance.json','telemetry-provenance.json','skill-difference.json','score-objective-steering.json']:
        shutil.copyfile(RAW/name,OUT/'evidence'/name)
    artifact_index=[]
    for r in read(RAW/'paired-results.json')['pairs']:
        for label in ['baseline','candidate']:
            folder=RAW/'artifacts'/r[label]['episode']
            artifact_index.append({'episode':r[label]['episode'],'arm':label,'files':{f:sha(folder/f) for f in ['replay.bin','audit.json','audit-result.json','results.json','spec.json','player-status.json','telemetry.json']}})
    write(OUT/'evidence/artifact-index.json',artifact_index)
    (OUT/'README.md').write_text(f'''# Reviewed control-tactics policy / engine61

Candidate `morrow-ibis-61c2:v1` is uploaded inertly. Both league champions remain
the incumbent source29f6d7e6; this directional pilot does not qualify deployment.

The coordinated fork targets hero control before retreat stops, avoids long
overlap, reserves mana for imminent healing and retains legal basic/item channels
under silence or root. Managed control casts are arbitrated separately from the
generic spell loop. The level2E guard has no demonstrated benefit in standard
level2 fixtures. Control can cost damage, mana and XP; it is not automatically safe
for score.

## Evidence

120paired real-tick fixtures /240executions pass (max5986instructions/9410work).
Warlock silence prevents a scripted enemy spell and saves42HP, both colors.
Vanguard stun saves38HP in the retreat-attacker drill. Sixteen complete native
games contain eight matched comparisons: twoWarlock score deltas+502/+949 and
six unchanged. These are mechanism/reference-opponent evidence only.

Hosted:80fresh baseline games and80responsive counterfactual games, four frozen
side/seat contexts,20pairs each. Every game has ten valid VMs, all replay hashes,
all XP and integer scores checked. Pair seed/config/manifest, own source and all
nine other sources agree. Unique full command streams:
baseline{stats['streams']['baseline']['unique']}/80, candidate{stats['streams']['candidate']['unique']}/80.

Mean score **{s['baseline']['mean']:.2f} → {s['candidate']['mean']:.2f}**;
paired mean delta **{s['mean_delta']:+.2f}**,95%interval
**[{s['delta95'][0]:+.2f}, {s['delta95'][1]:+.2f}]**.
Higher/equal/lower individual score:{s['wins']}/{s['ties']}/{s['losses']}.
These counts are score comparisons, not match victories.
Frozen pilot advancement:{stats['pilot_advance']}. No established verdict-size
floor; no deployment from this pilot. Natural subjects are Ranger/Crossbowman/
Druid; Warlock, Vanguard and Lich hosted effects remain unmeasured.

`evidence/statistics.json` includes exact score decomposition, paired uncertainty,
hero/side/seat summaries, control impacts, disjoint time/XP states and victim-to-
recipient XP graphs. Extra telemetry requested during the run is exploratory,
not a changed gate. The user's subsequent score-only objective governs future
studies and is preserved in `evidence/score-objective-steering.json`.

Raw tapes, original inputs and upload receipts remain in
`polyworld/tmp/gota-control-tactics61-20260923`; hashes and all160episode IDs are
in `evidence/artifact-index.json`. Original IR is preserved in that capture.
Reviewed IR annotations regenerate **byte-identical** tested BASIC.
Run `python verify.py`, or `convert.py compile --out <new-dir>` and
`convert.py extract --source policy.bas --out <new-dir>`.
''')
    verification=(b.PARENT/'verify.py').read_text().replace('tooling/control20260923','tooling/controltactics20260923').replace('import control_binding as b','import tactics_binding as b').replace("assert not m['deployment_qualified'] and not m['hosted_complete']", "assert not m['deployment_qualified'] and m['hosted_complete']\nassert read(P/'evidence/statistics.json')['all_160_games_10_vms_valid']")
    (OUT/'verify.py').write_text(verification)
    m=read(OUT/'manifest.json');m.update(ir_sha256=b.ir.digest(p),hosted_complete=True,deployment_qualified=False,score_gate_passed=None,pilot_score_gate_passed=stats['pilot_advance'],local_validated=True,reviewed_ir_preserves_tested_source=True)
    m['artifacts']={str(f.relative_to(OUT)):sha(f) for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts}
    write(OUT/'manifest.json',m)
    subprocess.run([sys.executable,str(OUT/'verify.py')],check=True)
    report=ROOT/'games/gods_of_the_arena/experiments/2026-09-23-control-tactics.md'
    report.write_text((OUT/'README.md').read_text()+f'\nPortable pair: `{OUT.relative_to(ROOT)}`.\n')
    print(json.dumps({'pair':str(OUT.relative_to(ROOT)),'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'pilot_advance':stats['pilot_advance']}))


if __name__=='__main__':main()

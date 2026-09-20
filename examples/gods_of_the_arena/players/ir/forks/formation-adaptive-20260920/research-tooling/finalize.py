"""Save validated semantic feedback without changing the tested executable."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
import shutil
import subprocess
import sys
from build import ROOT, STUDY, read, write, digest
from binding import CONTRACTS, Contract
from policy_ir import bundle, compile_policy, refresh_grounding, extract

DEST = ROOT/'examples/gods_of_the_arena/players/ir/forks/formation-adaptive-20260920'


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main():
    discovery = read(STUDY/'hosted-result.json')
    confirmation = read(STUDY/'confirmation-result.json')
    assert discovery['complete'] and discovery['passed']
    assert confirmation['complete'] and confirmation['passed']
    for name in ('review-progress.json', 'confirmation-review.json'):
        assert read(STUDY/name)['complete']
    assert not DEST.exists(), 'Refuse to overwrite a previously frozen final pair'
    for name, fields in read(STUDY/'compiler/contracts.json').items():
        for key in ('reads','writes','actions','memory'):
            fields[key] = tuple(fields[key])
        fields['parameters'] = {k: tuple(v) for k,v in fields['parameters'].items()}
        CONTRACTS[name] = Contract(**fields)
    folder = STUDY/'candidates/profile_pruned'
    original = read(folder/'policy.ir.json')
    p = deepcopy(original)
    evidence = []
    for name in ('hosted-result.json','confirmation-result.json','review-progress.json','confirmation-review.json',
                 'hosted-plan.json','confirmation-plan.json','hosted-admission.json','pruned-verdict.json'):
        evidence.append({'artifact': 'evidence/'+name, 'sha256': digest((STUDY/name).read_bytes())})
    p['belief']['claims']['ProfileSwitch'] = {
        'claim': 'The complete public-inventory adaptive formation3600 package met the frozen exact-target '
                 'discovery and prospective confirmation win thresholds against Alex g002v1, Jordan v268 '
                 'and Richard v135 on the published 2026.9.16.5 engine. Evidence is limited to pinned '
                 'five-copy teams, these versions and correlated deterministic trajectories. The profile '
                 'is not an authenticated player identity. No individual-component causal effect, '
                 'Richard red superiority, broad-field preservation or mixed-team generalization is established.',
        'status': 'supported', 'evidence': evidence}
    p['update']['revision'] += 1
    p['update']['parent'] = digest(original)
    p['update']['change'] = {'origin': 'Validated adaptive-fork feedback; executable unchanged',
                             'experiment': '2026-09-20-formation-adaptive',
                             'source_sha256': digest((folder/'policy.bas').read_bytes())}
    p['update']['needs_review'] = ['profile ambiguity on other opponents', 'mixed-team generalization',
                                  'Richard red losses', 'broader field before new league promotion']
    p['update']['evidence'] += evidence
    refresh_grounding(p)
    assert compile_policy(p).encode() == (folder/'policy.bas').read_bytes()
    assert extract(compile_policy(p), p) == p
    bundle(p, DEST)
    (DEST/'policy.py').write_text('"""Validated adaptive formation3600 semantic IR; bounded evidence in README."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    for name in ('compiler.zip','contracts.json'):
        copy(STUDY/'compiler'/name, DEST/name)
    copy(STUDY/'compiler/manifest.json', DEST/'compiler-manifest.json')
    copy(Path(__file__).with_name('verify_frozen.py'), DEST/'verify.py')
    files = ('hosted-result.json','confirmation-result.json','review-progress.json','confirmation-review.json',
             'hosted-plan.json','confirmation-plan.json','hosted-admission.json','pruned-verdict.json',
             'vm-proof-profile_pruned.json','inputs.json','storage-aliases.json','local-verdict.json',
             'refinement-plan.json','pruned-plan.json','confirmation-novelty.json','captured-input-preservation.json',
             'final-league-status.json')
    for name in files:
        copy(STUDY/name, DEST/'evidence'/name)
    copy(folder/'uploaded-version.json', DEST/'uploaded-version.json')
    copy(folder/'upload-request.json', DEST/'upload-request.json')
    copy(STUDY/'detection/result.json', DEST/'evidence/archived-detector-feasibility.json')
    copy(folder/'policy.ir.json', DEST/'evidence/tested-unannotated.ir.json')
    for reference in ('formation','legacy','jordan','handoff'):
        for name in ('policy.py','policy.ir.json','policy.bas'):
            copy(STUDY/'inputs'/reference/name, DEST/'evidence/inputs'/reference/name)
    requests = []
    table = []
    for stage, plan_name in [('discovery','hosted-plan.json'),('confirmation','confirmation-plan.json')]:
        plan = read(STUDY/plan_name)
        for arm in plan['arms']:
            d = Path(arm['directory']); target = DEST/'evidence'/stage/arm['key']
            for name in ('arm-result.json','trajectory-correlation.json','plan.json','request.json'):
                copy(d/name, target/name)
            for path in d.glob('profile-*.json'):
                assert not path.stem.endswith('-error'), path
                copy(path, target/path.name)
            request = read(d/'batch/created.json')['id']
            requests.append({'stage': stage, 'key': arm['key'], 'request': request})
            r = read(d/'arm-result.json'); c = read(d/'trajectory-correlation.json')
            table.append(f"| {stage} | {arm['key']} | {r['wins']} | {r['losses']} | {r['draws']} | {c['distinct_complete_command_streams']} |")
    write(DEST/'requests.json', requests)
    references = []
    for name in ('2026-09-20t17-21-56-307zf4f7b3','2026-09-20t19-10-35-082z64deb6'):
        session = Path('/Users/aaln/Documents/Policy Loops/sessions')/name
        references.append({'session': str(session), 'captured_inputs_modified': False,
                           'sha256': {n: digest((session/n).read_bytes()) for n in ('notes.md','session.json')}})
    write(DEST/'session-references.json', references)
    for path in Path(__file__).parent.iterdir():
        if path.suffix in ('.py','.nim'):
            copy(path, DEST/'research-tooling'/path.name)
    summary = {'at': datetime.now(timezone.utc).isoformat(), 'source_sha256': digest((DEST/'policy.bas').read_bytes()),
               'discovery_passed': True, 'confirmation_passed': True, 'hosted_games': 640,
               'deployment_changed': False, 'formal_research_acceptance_changed': False,
               'raw_evidence': str(STUDY), 'controls': 'Fresh formation3600 Alex/Jordan; Richard historical only',
               'limitations': ['Repeated trajectories are correlated, not independent trials',
                               'Five-copy teams and three exact target versions',
                               'No broad-field or joint Richard-per-color promotion qualification']}
    write(DEST/'validation.json', summary)
    (DEST/'README.md').write_text('''# Adaptive formation3600 fork

This frozen IR/policy pair uses public enemy equipment to choose previously tested response components. It passed the precommitted discovery and fresh confirmation thresholds against Alex g002v1 and Jordan v268 while preserving the bounded Richard v135 aggregate win threshold. All 640 hosted games were fully audited; the executable was unchanged between stages. League memberships and formal research acceptance were not changed.

Two distinct simultaneously visible living enemies with exact boots+elixir, boots-only, or dagger-only inventories select the respective response. Conflicting recognized profiles abstain. Observation is sampled every 24 ticks through tick 1800; a selected profile persists for the episode. Other policies can share these inventories: this is behavioral adaptation, not reliable player identification.

Blue selects the historical Alex remote alarm and hero-first priority, Jordan local counterpressure, or formation3600 critical defense for dagger/unknown. Red combines early caster transit and low-HP tower handoff with late formation only for dagger/unknown. The coordinated package is supported; individual causal contributions were not isolated.

| Stage | Opponent / policy / our color | W | L | D | Distinct complete streams |
|---|---|---:|---:|---:|---:|
'''+ '\n'.join(table) + '''

Draws count zero. There were no invalid games. Generated seeds were not paired. Repeated streams are correlated and distinct streams do not automatically establish independent trials. The Richard control is the earlier formation3600 cohort (blue 40W, red 0W/14L/26D), not a fresh Richard A/B. The fork does not establish Richard red improvement or broad-field/mixed-team generalization. Discovery and confirmation remain separate in all evidence.

`policy.py` is primary; JSON and BASIC are generated from the seven-layer IR. Validated beliefs were reflected back without changing BASIC. `compiler.zip` freezes the loaded compiler and required pinned-engine data; `contracts.json` freezes the exact instantiated binding contracts. Reproduce offline with:

```sh
python3 verify.py
```

`evidence/` contains frozen plans, all per-episode outcomes and replay hashes, complete trajectory counts, representative source reconstructions, the four original reference pairs and failed native-admission history. `requests.json` supplies retrieval IDs. Source reconstruction matches every owned command and every replay state hash, but is retrospective rather than a counterfactual opponent rollout. Raw replays and VM statuses remain in the private study path in `validation.json`. All 130 files from the two original coaching captures retain their original hashes; failed candidates were preserved.
''')
    manifest = read(DEST/'manifest.json')
    manifest['artifacts'] = {str(path.relative_to(DEST)): digest(path.read_bytes())
                              for path in sorted(DEST.rglob('*')) if path.is_file() and path.name!='manifest.json'}
    write(DEST/'manifest.json', manifest)
    subprocess.run([sys.executable, str(DEST/'verify.py')], check=True)
    print(DEST, flush=True)


if __name__ == '__main__':
    main()

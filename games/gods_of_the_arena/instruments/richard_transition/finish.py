"""Finish all purchased evidence and save reproducible evaluated artifacts."""
import importlib.util
import json
from pathlib import Path
import subprocess
import time
from fresh_hit import ROOT,STUDY,INITIAL,read,write,digest

def local_module(name):
    spec=importlib.util.spec_from_file_location('transition_finish_'+name,Path(__file__).with_name(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

finalizer=local_module('finalize')
DEST=finalizer.DEST
finalize=finalizer.main
render=local_module('report').render

PYTHON='/Users/aaln/experiments/softmax/metta/.venv/bin/python'


def main():
    while not (INITIAL/'promotion-check/result.json').exists():time.sleep(20)
    spec=importlib.util.spec_from_file_location('transition_final_correlations',ROOT/'games/gods_of_the_arena/instruments/richard_coaching/correlate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    paths=[STUDY/'hosted-plan.json',INITIAL/'promotion-check/plan.json']
    requests=[];episodes=[]
    for path in paths:
        for arm in read(path)['arms']:
            directory=Path(arm['directory'])
            print(module.process(directory),flush=True)
            requests.append(read(directory/'batch/created.json')['id'])
            episodes.extend(row['episode'] for row in read(directory/'arm-result.json')['rows'])
    assert len(requests)==len(set(requests))==10
    assert len(episodes)==len(set(episodes))==400
    write(INITIAL/'purchased-evidence-accounting.json',{'unique_requests':requests,
        'unique_episodes':len(set(episodes)),'all_purchased_episode_ids':episodes,
        'baseline_reused_once':True,'intermediate_cadence_candidates_requested_games':0})
    finalize()
    with (DEST/'reproduction-proof.json').open('w') as out:
        subprocess.run([PYTHON,str(DEST/'reproduce.py')],cwd='/tmp',stdout=out,check=True)
    assert read(DEST/'reproduction-proof.json')['passed']
    result=read(DEST/'results.json');promotion=result['conditional_promotion']
    selected=promotion['selection']['name'];name=promotion['selection']['version']['name']
    lines=['# Richard coaching and conditional promotion check','',
        'Reviewed session `2026-09-20t19-10-35-082z64deb6` and reconstructed the exact user episode. All 70 captured files remain unchanged.','',
        'Completed 108 local games and 400 hosted games: 240 against Richard v135 and 160 against Alex g002:v1 / Jordan v268. All hosted games passed full replay and all-ten-VM checks. Generated seeds are not paired across hosted arms, and repeated command trajectories are correlated.','',
        '| Richard v135 | Red | Blue |','|---|---:|---:|']
    for label,cells in [('Coached baseline',result['baseline'])]+[(r['name'],r['Richard']) for r in result['candidates'] if r['Richard']]:
        lines.append(f"| {label} | {cells['red']['wins']}/40 | {cells['blue']['wins']}/40 |")
    lines+=['','The original both-color Richard gate failed for both final variants. The user subsequently authorized promotion if the unchanged policy beats Alex and Jordan; this is a separate gate, not a relabeling of Richard failure.','',
        f'Selected unchanged source: `{name}:v1`, `{selected}`.','',
        '| Conditional promotion test | Wins | Losses | Draws |','|---|---:|---:|---:|']
    for c in promotion['cells']:lines.append(f"| {c['key']} | {c['wins']} | {c['losses']} | {c['draws']} |")
    lines+=['','Conditional promotion gate: **'+('passed' if promotion['user_conditional_promotion_gate_passed'] else 'failed')+'**. Deployment, if eligible, is recorded separately under `promotion-check/deployment`.','',
        'The implementation couples finite defense memory, observed-clear offense, a bounded Crossbowman scout, shared Ranger focus, synchronized legal strikes, and fresh-hit movement recovery; an alternative buys armor earlier. Scenario proofs establish command behavior, not combat success. The native engine supplies no gap-closing stun for the chosen strikes.','',
        'The original replay has 197/286 sampled emergency decisions without a fresh alarm. The Ranger finishes level 10 with five items; our Death Knight is level 4 with one. Ranger late hit intervals were often nine ticks with post-hit movement. Our Crossbowman had higher nominal damage and range, so raw attack stats alone do not explain the wipe.','',
        'The new variants lost earlier on red. Smaller end-game stat gaps or fewer raw deaths therefore do not establish improved scaling or survival. See the full-cohort progression comparison.','',
        'Saved primary IR/BASIC pairs: `evaluated/` and `coached-baseline/`. `reproduce.py` verifies every pair using the captured repo conversion; `reproduction-proof.json` was generated from `/tmp`. Failed and superseded versions remain archived.','',
        'Study and raw audits: `'+str(INITIAL)+'`. Session/evidence hashes: `session-references.json`, `captured-inputs.json`, `additional-validation.json`. Layer mapping: `semantic-coaching-map.json`.']
    (DEST/'README.md').write_text('\n'.join(lines)+'\n')
    render()
    for dest in (DEST/'report.html',ROOT/'docs/reports/2026-09-20-richard135-transition.html'):
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((INITIAL/'report.html').read_bytes())
    write(INITIAL/'finish-result.json',{'complete':True,'pairs_reproduced':len(read(DEST/'reproduction-proof.json')['pairs']),
        'results_sha256':digest((DEST/'results.json').read_bytes()),'conditional_promotion_gate_passed':promotion['user_conditional_promotion_gate_passed'],
        'report':str(DEST/'report.html'),'requires_visual_review':True})
    print('ARTIFACTS COMPLETE',DEST,flush=True)


if __name__=='__main__':main()

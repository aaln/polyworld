"""Preserve completed results and reflect validation into byte-identical IR."""
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
import pprint
import shutil
from build import ROOT,STUDY,PAIR,ENGINE,COMMIT,write
from policy_ir import compile_policy,extract,refresh_grounding,digest,grounded

def main():
    result=json.loads((STUDY/'hosted-result.json').read_text())
    review=json.loads((STUDY/'review.json').read_text())
    assert result['complete'] and review['complete']
    field=json.loads((STUDY/'field-result.json').read_text()) if (STUDY/'field-result.json').exists() else None
    field_review=json.loads((STUDY/'field-review.json').read_text()) if field else None
    if field:assert field['complete'] and field_review['complete']
    field_clean=bool(field) and all(r['clean_games']>=30 for r in field['results'])
    field_label=('passed' if field['passed'] else 'failed' if field_clean else 'unqualified: insufficient clean games') if field else 'not run'
    assert not PAIR.exists(),'Preserve previous frozen bundle'
    source=(STUDY/'candidates/lane/policy.bas').read_bytes()
    p=json.loads((STUDY/'candidates/lane/policy.ir.json').read_text())
    original=digest(p)
    p['goal']['Score']={'preference':'Maximize the new live league score max(0, lifetime XP - 200 * elapsed world ticks / 1440); fort outcomes are a separate diagnostic.', 'provenance':'authored'}
    for rule in p['strategy']:rule['for'].append('Score')
    p['belief']['claims']['NewWeekBundle'].update(
      claim='Passed the fixed-opponent hosted score gate versus the exact compatibility incumbent; scope and correlation limits are recorded in evidence/review.json.' if result['passed'] else 'The coordinated new-week bundle passed native contract checks, but did not pass the frozen hosted score improvement gate. Preserve source and failed evidence; not qualified for promotion.',
      status='supported' if result['passed'] else 'contradicted',
      evidence=[{'artifact':'evidence/hosted-result.json'},{'artifact':'evidence/review.json'}])
    p['belief']['claims']['HostContract']={'claim':'All ten classes on both colors pass 126 actual-VM mechanism/stress checks; complete source parses and round-trips, and two hosted replays match all state hashes, XP and the new score formula.',
      'status':'supported','evidence':[{'artifact':'evidence/scenarios-extra.json'},{'artifact':'evidence/build-proof.json'},{'artifact':'evidence/extra-build-proof.json'},{'artifact':'evidence/calibration.json'}]}
    if field:
        p['belief']['claims']['MixedTeamScore']={
          'claim':'The new bundle improves clean mixed-team mean score over the compatibility incumbent on each color and by at least 20% overall. Observed gate: '+field_label+'. Two exact rosters and middle draft seats cannot establish universal league superiority.',
          'status':'supported' if field['passed'] else 'contradicted' if field_clean else 'requires_review',
          'evidence':[{'artifact':'evidence/field-plan.json'},{'artifact':'evidence/field-result.json'},{'artifact':'evidence/field-review.json'}]}
    p['update'].update(revision=2,parent=original,change={'origin':'Completed new-week hosted comparison and native validation; executable preserved exactly'},needs_review=['mixed-team-score-generalization','current-leader-comparison'],evidence=[{'artifact':'evidence/hosted-result.json'},{'artifact':'evidence/experiment.md'}])
    refresh_grounding(p)
    assert compile_policy(p).encode()==source
    assert extract(source.decode(),p)==p
    PAIR.mkdir(parents=True)
    write(PAIR/'policy.ir.json',p);write(PAIR/'extracted.ir.json',p);write(PAIR/'semantics.json',grounded(p))
    (PAIR/'policy.bas').write_bytes(source)
    (PAIR/'policy.py').write_text('"""Validated new-week policy with explicitly bounded claims."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    tooling=Path(__file__).parent
    shutil.copytree(tooling,PAIR/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(tooling/'verify_pair.py',PAIR/'verify.py')
    evidence=PAIR/'evidence';evidence.mkdir()
    names=['hosted-plan.json','hosted-result.json','review.json','scenarios.json','scenarios-extra.json','build-proof.json','extra-build-proof.json','calibration.json','lane-local-plan.json','lane-local-result.json','baseline-local-plan.json','baseline-local-result.json','game-config.json','field-plan.json','source-update.json']
    if field:names+=['field-result.json','field-review.json','field-errors.json']
    for name in names:shutil.copyfile(STUDY/name,evidence/name)
    shutil.copyfile(ROOT/'games/gods_of_the_arena/experiments/2026-09-21-week-policy.md',evidence/'experiment.md')
    shutil.copytree(STUDY/'candidates/lane',evidence/'initial-pair')
    shutil.copytree(STUDY/'initial-compiler',evidence/'initial-compiler')
    shutil.copytree(STUDY/'initial-native',evidence/'initial-native')
    for kind in (('hosted','field') if field else ('hosted',)):
        for name in ('candidate','incumbent'):
            for side in (0,1):
                src=STUDY/kind/name/str(side);dst=evidence/kind/name/str(side);dst.mkdir(parents=True)
                for fn in ('arm.json','request.json','result.json','trajectory-correlation.json'):
                    shutil.copyfile(src/fn,dst/fn)
                write(dst/'request-id.json',{'id':json.loads((src/'batch/created.json').read_text())['id']})
    for name in ('lane','baseline'):
        dst=evidence/'uploads'/name;dst.mkdir(parents=True)
        for fn in ('upload-request.json','uploaded-version.json'):shutil.copyfile(STUDY/'uploads'/name/fn,dst/fn)
    (PAIR/'README.md').write_text('# New-week Gods of the Arena policy\n\n'
      'Targets **2026.9.21.5**, upstream `'+COMMIT+'`. Primary semantic IR is `policy.py`; `policy.ir.json` and `policy.bas` are its verified generated pair.\n\n'
      'The new league score is `max(0, lifetime XP - 200 * ticks / 1440)`, with draft ticks included. The policy drafts from public choices, spends ability points, farms separate lanes, buys permanent gear in its keep, uses recovery/portals, releases defense when the current threat clears, and avoids unsupported tower exposure.\n\n'
      'Hosted frozen score gate: **'+('passed' if result['passed'] else 'failed')+'**. Results are against an exact updated baseline opponent with candidate/compatibility control on each color. Repeated trajectories are correlated. No league champion was changed.\n\n'
      '| Policy | Color | Mean score per hero | Wins / 40 | Invalid | Distinct command streams |\n|---|---|---:|---:|---:|---:|\n'+''.join('| '+c['name']+' | '+('red' if c['side']==0 else 'blue')+' | '+f"{c['mean_score']:.2f}"+' | '+str(c['wins'])+' | '+str(c['invalid'])+' | '+str(c['distinct_command_streams'])+' |\n' for c in review['cells'])+
      ('\nMixed-team frozen score gate: **'+field_label+'**. One subject seat, nine distinct frozen players, third pick on each team. Scores below use games with all ten VMs valid; tainted games remain in the evidence.\n\n| Policy | Color | Clean mean score | Clean games | Subject errors | Distinct streams |\n|---|---|---:|---:|---:|---:|\n'+''.join('| '+c['name']+' | '+('red' if c['side']==0 else 'blue')+' | '+(f"{c['mean_score_clean']:.2f}" if c['clean_games'] else 'N/A')+' | '+str(c['clean_games'])+' | '+str(c['subject_invalid'])+' | '+str(c['distinct_command_streams'])+' |\n' for c in field_review['cells']) if field else '\nMixed-team holdout was frozen but not run because the prerequisite uniform gate failed.\n')+
      ('\nOther-policy VM failures and exact affected versions are recorded in `evidence/field-errors.json`; zero clean games provide no clean mixed-team score estimate.\n' if field and not field_clean else '')+
      '\nThese fixed rosters do not establish superiority over every current leader or a future rank. Native diagnostics: 8/8 candidate wins against the new baseline, 126 real-host scenario checks, maximum 11,960 instructions/18,684 work. Two prior hosted replays calibrated the engine and new score calculation. Six compiler tests passed. All captured earlier policies and coaching inputs remain unchanged.\n\n'
      'Verify without network or a separate game checkout:\n\n```sh\npython3 verify.py\n```\n\n'
      'See `evidence/hosted-result.json`, `evidence/review.json`, and `tooling/README.md` for reproducibility, requests, budgets and limitations. Raw game tapes remain private under `tmp/gota-week-20260921`.\n')
    write(PAIR/'manifest.json',{'at':datetime.now(timezone.utc).isoformat(),'game_version':'2026.9.21.5','engine_commit':COMMIT,
      'source_sha256':digest(source),'ir_sha256':digest(p),'hosted_gate_passed':result['passed'],'mixed_team_gate_passed':field['passed'] if field else None,'mixed_team_verdict':field_label,
      'artifacts':{str(x.relative_to(PAIR)):digest(x.read_bytes()) for x in sorted(PAIR.rglob('*')) if x.is_file()}})
    print(PAIR)

if __name__=='__main__':main()

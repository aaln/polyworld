"""Preserve current-release feedback separately from the completed target pair."""
from datetime import datetime, timezone
from pathlib import Path
import json
import pprint
import shutil
import practiced
from healthy_field import h, OUT

HERE = Path(__file__).resolve().parent
PARENT = h.ROOT / 'examples/gods_of_the_arena/players/ir/forks/microplay20260922'
PAIR = PARENT.parent / 'current20260922'


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    result, review = h.read(OUT / 'result.json'), h.read(OUT / 'review.json')
    assert result['complete'] and review['complete']
    middle = h.read(h.STUDY / 'middle-field/result.json')
    middle_review = h.read(h.STUDY / 'middle-field/review.json')
    assert middle['complete'] and middle_review['complete']
    assert h.read(h.STUDY / 'runnable-proof.json')['passed']
    assert h.read(h.STUDY / 'draft-practice.json')['passed']
    assert not h.read(h.STUDY / 'attention-confirm-decision.json')['admitted']
    assert not PAIR.exists(), 'Preserve frozen pairs'
    practiced.configure('potions')
    ir = practiced.ir
    p = h.read(PARENT / 'policy.ir.json')
    parent_ir = ir.digest(p)
    source = (PARENT / 'policy.bas').read_bytes()
    p['goal']['Win']['preference'] = 'Objective pressure supports XP production; fort outcomes are diagnostic, while current league XP score is primary.'
    p['situation']['notes'] += ' Draft availability is shared across both teams. Prefer an available ranged hero; never assume Ranger remains available in a late pick. The supplied old-compat replay does not identify the current policy.'
    # Keep directly supported current mechanics; remove old qualification gates
    # from active beliefs. Their frozen evidence remains in the parent archive.
    p['belief']['claims'] = {
        k: v for k, v in p['belief']['claims'].items()
        if k in ('PracticeMechanics', 'HostContract', 'TargetScoreImprovement')}
    p['belief']['claims'].update({
        'CurrentContract': {'claim': 'The current decimal-aware binding and XP-score metric govern new experiments. Historical integer assumptions, opponent versions and fort-win qualification gates are not active constraints.',
            'status': 'supported', 'evidence': [{'artifact': 'evidence/current/contract.json'}, {'artifact': 'evidence/current/guide.md'}]},
        'DraftOpening': {'claim': 'Real-host public opening fixtures select Ranger at tick13 after enemy Crossbowman; if enemy takes Ranger, select Arcanist at tick13. This prevents the observed compat Vanguard choice when these ranged options are available, without promising any class from every draft seat.',
            'status': 'supported', 'evidence': [{'artifact': 'evidence/current/draft-practice.json'}]},
        'ObservedCompatFailure': {'claim': 'Supplied replay: Coach compat explicitly chose Vanguard while Ranger was available, earned209XP and died5times; relh Ranger earned2685XP with no deaths. Three Coach teammates had VM failures. Outcome/draft are verified; internal policy beliefs and causal class superiority are not established.',
            'status': 'supported', 'evidence': [{'artifact': 'evidence/current/user-episode/analysis.json'}]},
        'MixedScoreImprovement': {'claim': 'Exact practiced source versus live compatibility policy in two frozen healthy-preflight mixed rosters,40games per version/color. Current-score gate passed: ' + str(result['research_improved']) + '. Results are scoped to these rosters and first-pick seats.',
            'status': 'supported' if result['research_improved'] else 'contradicted',
            'evidence': [{'artifact': 'evidence/current/field/plan.json'}, {'artifact': 'evidence/current/field/result.json'}, {'artifact': 'evidence/current/field/review.json'}]},
        'LaterDraftScore': {'claim': 'Unchanged executable tested from third-pick seats on both colors, 40 games per version/color. Current-score gate passed: ' + str(middle['research_improved']) + '. This verifies a later draft context, not every possible hero or roster.',
            'status': 'supported' if middle['research_improved'] else 'contradicted',
            'evidence': [{'artifact': 'evidence/current/middle-field/plan.json'}, {'artifact': 'evidence/current/middle-field/result.json'}, {'artifact': 'evidence/current/middle-field/review.json'}]},
        'ObservedMixedTargetScores': {'claim': 'Retrospective opposing-player score readout: own mean exceeds relh161 in all four frozen mixed lineup/color cells, and Jordan317/Richard153 in both red cells. Jordan/Richard are allies in the blue cells and provide no blue-side counter evidence. Opponent identity is audit metadata, not an input to the executable.',
            'status': 'supported', 'evidence': [{'artifact': 'evidence/current/field-target-scores.json'}]},
        'RefinementRejection': {'claim': 'Scarce-gold armor reserves and faster observation improve some practice measures but fail matched responsive native comparison. Retain the original practiced BASIC, rather than assuming individual drill gains improve full matches.',
            'status': 'supported', 'evidence': [{'artifact': 'evidence/current/attention-confirm-decision.json'}, {'artifact': 'evidence/current/reserve-control-result.json'}]},
        'Generalization': {'claim': 'No universal class-strength, every-draft-position, current-target-every-color score superiority or number-one league rank claim. Completed uniform target panel uses Jordan306; mixed follow-up uses Jordan317. Jordan356 appeared during the follow-up and is untested. Further current responsive validation is required.',
            'status': 'requires_review', 'evidence': [{'artifact': 'evidence/current/experiment.md'}, {'artifact': 'evidence/current/target-drift.json'}, {'artifact': 'evidence/review.json'}]}})
    p['update'] = {'revision': 5, 'parent': parent_ir,
        'change': {'origin': 'User requested current-game IR isolation and analysis of relh Ranger versus compat Vanguard; preserve strongest executable and reflect audited draft/field evidence',
                   'episode': 'ereq_cd49a7f0-5410-4506-9c2d-c8c275d9c749'},
        'needs_review': ['belief/Generalization'],
        'evidence': [{'artifact': 'evidence/current/experiment.md'}]}
    ir.refresh_grounding(p)
    assert ir.compile_policy(p).encode() == source
    assert ir.extract(source.decode(), p) == p
    shutil.copytree(PARENT, PAIR, ignore=shutil.ignore_patterns('__pycache__'))
    evidence = PAIR / 'evidence/current'
    copy(PARENT / 'manifest.json', evidence / 'parent-manifest.json')
    copy(PARENT / 'README.md', evidence / 'parent-readme.md')
    copy(PARENT / 'verify.py', PAIR / 'verify_base.py')
    copy(HERE / 'verify_current_pair.py', PAIR / 'verify.py')
    for name, data in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
        h.write(PAIR / name, data)
    (PAIR / 'policy.py').write_text('"""Current-release semantic policy and evidence; exact tested BASIC retained."""\n\nPOLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    for name in ('attention-confirm-local-plan.json', 'attention-confirm-local-result.json', 'attention-confirm-decision.json',
                 'attention-local-plan.json', 'attention-local-result.json', 'attention-current-scenarios.json',
                 'reserve-local-plan.json', 'reserve-local-result.json', 'melee-reserve-local-plan.json',
                 'melee-reserve-local-result.json', 'reserve-control-plan.json', 'reserve-control-result.json',
                 'draft-practice.json', 'draft-practice-build.log'):
        copy(h.STUDY / name, evidence / name)
    for src in h.STUDY.glob('*scenarios.json'):
        copy(src, evidence / 'scenarios' / src.name)
    for src in h.STUDY.glob('practice-*.json'):
        copy(src, evidence / 'practice' / src.name)
    for name in ('reserve', 'melee_reserve', 'scan128', 'think3', 'think3_scan128', 'attention_current'):
        shutil.copytree(h.STUDY / 'candidates' / name, evidence / 'candidates' / name)
    for name in ('analysis.json', 'summary.json', 'focus.json'):
        copy(h.STUDY / 'user-episode' / name, evidence / 'user-episode' / name)
    copy(h.STUDY / 'compat-metadata/identity.json', evidence / 'compat-identity.json')
    copy(h.STUDY / 'runnable-proof.json', evidence / 'runnable-proof.json')
    copy(h.STUDY / 'target-drift.json', evidence / 'target-drift.json')
    copy(h.STUDY / 'field-target-scores.json', evidence / 'field-target-scores.json')
    for name in ('plan.json', 'result.json', 'review.json', 'preflight-result.json'):
        copy(OUT / name, evidence / 'field' / name)
    for label in ('candidate', 'control'):
        for side in (0, 1):
            folder = OUT / label / str(side)
            dst = evidence / 'field' / label / str(side)
            for name in ('arm.json', 'request.json', 'trajectory-correlation.json'):
                copy(folder / name, dst / name)
            h.write(dst / 'request-id.json', {'id': h.read(folder / 'batch/created.json')['id']})
    for name in ('plan.json', 'result.json', 'review.json'):
        copy(h.STUDY / 'middle-field' / name, evidence / 'middle-field' / name)
    for label in ('candidate', 'control'):
        for side in (0, 1):
            folder = h.STUDY / 'middle-field' / label / str(side)
            dst = evidence / 'middle-field' / label / str(side)
            for name in ('arm.json', 'request.json', 'trajectory-correlation.json'):
                copy(folder / name, dst / name)
            h.write(dst / 'request-id.json', {'id': h.read(folder / 'batch/created.json')['id']})
    # These are tooling/provenance, not private API envelopes or signed URLs.
    for name in ('reserve.py', 'melee_reserve.py', 'attention.py', 'current_attention.py', 'current_score.py',
                 'test_current_score.py', 'economy_practice.nim', 'draft_practice.nim', 'focus_episode.nim',
                 'healthy_field.py', 'guardrail_field.py', 'review_healthy_field.py', 'finalize_current.py',
                 'verify_current_pair.py', 'verify_runnables.py', 'deploy_current.py', 'field_target_scores.py'):
        copy(HERE / name, evidence / 'instruments' / name)
    copy(h.ROOT / 'games/gods_of_the_arena/current.json', evidence / 'contract.json')
    copy(h.ROOT / 'docs/guides/guide-gota-current-release.md', evidence / 'guide.md')
    copy(h.ROOT / 'games/gods_of_the_arena/experiments/2026-09-22-draft-and-current-score.md', evidence / 'experiment.md')
    table = '| Policy | Color | Mean score | Mean XP | Deaths | Level | W/L/D | Distinct streams |\n|---|---|---:|---:|---:|---:|---|---:|\n'
    for c in review['cells']:
        m = c['means']
        table += f"| {c['label']} | {('red','blue')[c['side']]} | {c['own_score']:.2f} | {m['xp']:.1f} | {m['deaths']:.2f} | {m['level']:.2f} | {c['wins']}/{c['losses']}/{c['draws']} | {c['distinct_command_streams']} |\n"
    (PAIR / 'README.md').write_text(
        '# Current-release ranged draft and microplay\n\n'
        'Primary IR: `policy.py`. Generated BASIC retains exact practiced source **b82c3799**, registered as Aaron **f3f8baab-d02a-4f7f-8fc9-e1f050f967a7**. Engine **2026.9.21.5 / f776d5e**. This evidence bundle does not itself select a league champion.\n\n'
        'The user episode ran old Coach compat, which chose Vanguard while Ranger was available. relh Ranger ended level 8 with 2,685 XP/no deaths; Coach level 2 with 209 XP/five deaths. Three teammates failed their VMs. Exact replay/draft/XP are verified, but that game is not clean strength evidence. Current real-host fixtures pick Ranger after Crossbowman and Arcanist when Ranger is taken, at tick 13.\n\n'
        'The current pair keeps ranged-first drafting, explicit ability upgrades, practiced basic recovery/last hits/XP positioning, gear purchases and purposeful portals. Further reserve/attention changes were rejected after fresh responsive matched-color tests. Old IR assumptions and historical win-only gates no longer govern new experiments; the completed parent panel remains frozen.\n\n'
        'Mixed comparison: 160 audited hosted games, one first-pick subject per team, exact matched rosters per color. Current score gate passed: **' + str(result['research_improved']) + '**. An additional 160-game third-pick guardrail passed: **' + str(middle['research_improved']) + '**; its full results are in `evidence/current/middle-field`.\n\n' + table +
        '\nXP-score comparison is per hero, with draft/world-time penalty. Fort outcomes are diagnostic. The two fixed rosters, repeated streams and first-pick seats limit generalization. No number-one rank or every-opponent/every-color score claim. Full original target evidence and all rejected refinements are preserved.\n\n'
        'Run `python3 verify.py` for offline identity/result checks. Use `python3 convert.py compile --policy policy.py --out /tmp/new-current-pair` to regenerate edited IR, or `extract --source edited.bas` to reflect BASIC edits back into IR. Changed executable bytes invalidate prior beliefs. Raw replays/API inputs remain in `tmp/gota-targets-20260922`; historical coaching captures are unchanged.\n')
    h.write(PAIR / 'manifest.json', {
        'at': datetime.now(timezone.utc).isoformat(), 'game_version': h.VERSION, 'engine_commit': h.COMMIT,
        'source_sha256': h.sha(source), 'ir_sha256': ir.digest(p), 'parent_ir_sha256': parent_ir,
        'current_field_gate_passed': result['research_improved'],
        'later_draft_gate_passed': middle['research_improved'],
        'historical_target_fort_gate_passed': False, 'historical_target_score_gate_passed': False,
        'artifacts': {str(x.relative_to(PAIR)): h.sha(x.read_bytes()) for x in sorted(PAIR.rglob('*')) if x.is_file() and x != PAIR / 'manifest.json'}})
    print(PAIR)


if __name__ == '__main__':
    main()

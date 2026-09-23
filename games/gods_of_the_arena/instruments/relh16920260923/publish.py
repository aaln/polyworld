"""Publish the relh169 source audit without modifying a live policy or league."""
import copy
import datetime
import hashlib
import json
import shutil
from pathlib import Path

from audit import CLASSES, OUT, RAW, ROOT, SOURCE, read, sha, write


def main():
    analysis = read(RAW / 'analysis.json')
    plan = read(RAW / 'plan.json')
    old = ROOT / 'docs/opponents/richard-v174/source-audit-20260923'
    marker = b'if drafting then'
    body = SOURCE.read_bytes().split(marker, 1)[1]
    old_body = (old / 'richard-v174.bas').read_bytes().split(marker, 1)[1]
    assert body == old_body
    proof = {
        'comparison': 'Exact bytes beginning with first if drafting then through EOF',
        'equal': True,
        'relh_source_sha256': sha(SOURCE),
        'richard174_source_sha256': sha(old / 'richard-v174.bas'),
        'body_sha256': hashlib.sha256(marker + body).hexdigest(),
        'relh_body_start_line': 405,
        'richard_body_start_line': 55,
        'line_offset': 350,
        'richard_source': '../../richard-v174/source-audit-20260923/richard-v174.bas',
        'meaning': 'Draft subroutine differs. Identical combat bytes do not imply identical class, opponent, engine or score outcomes.',
    }
    write(OUT / 'battle-body-comparison.json', proof)
    for name in ['plan.json', 'runtime-provenance.json', 'buff-visits.json', 'live-readback.json', 'request.txt']:
        shutil.copyfile(RAW / name, OUT / name)
    for name in ['players-data.json', 'heroes-data.json', 'players.html', 'heros.html', 'players.js']:
        dest = OUT / 'evidence/buff' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAW / name, dest)
    # Reported historical findings must remain distinguishable from this audit.
    cogas = ROOT.parent / 'co-gas'
    for rel, name in [
        ('players/users/relh/co-gas/gota-training-v6/README.md', 'training-notes.md'),
        ('players/users/relh/co-gas/gota-training-v6/FULL_NEURAL_CONTRACT.md', 'training-contract.md'),
    ]:
        shutil.copyfile(cogas / rel, OUT / 'source' / name)
    for name in ['drafts-before-compile-fix.nim', 'build-drafts-initial-error.log']:
        dest = OUT / 'evidence/instrument-correction' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if name.endswith('.log'):
            write(dest.with_suffix('.json'), {'raw_path': str(RAW / name), 'sha256': sha(RAW / name), 'original_text': (RAW / name).read_text()})
        else:
            shutil.copyfile(RAW / name, dest)

    # Reuse only identical-controller semantics. Replace identity, draft and all
    # retrospective activation claims; old Warlock outcomes do not describe relh.
    ir = copy.deepcopy(read(old / 'richard_v174.source.ir.json'))
    ir['id'] = 'relh_v169_source_20260923'

    def relocate(value):
        if isinstance(value, dict):
            if value.get('artifact') == 'richard-v174.bas':
                value['artifact'] = 'source/relh-v169.bas'
                for field in ['start_line', 'end_line']:
                    value[field] += 350
            for k, v in list(value.items()):
                value[k] = relocate(v)
        elif isinstance(value, list):
            value = [relocate(v) for v in value]
        elif isinstance(value, str) and value == 'neural-controller.json':
            value = '../../richard-v174/source-audit-20260923/neural-controller.json'
        return value

    ir = relocate(ir)
    ir['situation']['identity'] = {
        'label': 'relh-gods-of-the-arena:v169', **plan['identity'],
        'replay_game_version': 59, 'repository_provenance': 'provenance.json',
    }
    ir['situation']['perspective'] = 'Relh public observations and source-private memory reconstructed retrospectively. No player identity or hidden XP enters a live controller.'
    ir['situation']['class_evidence'] = '../../richard-v174/source-audit-20260923/class-mapping.json'
    ir['situation']['draft_features'] = {
        '0_to_9': 'Public legal hero availability',
        '10_to_19': 'Own team already-picked class indicators',
        '20_to_29': 'Enemy team already-picked class indicators',
        '30_and_31': 'Own/enemy picked counts divided by five',
        'weights': 'draft-controller.json',
        'arithmetic': 'BASIC Q16.16; six-decimal exported literals; strict first maximum among legal classes',
        'unknown': ['Opponent policy identity', 'Lifetime XP', 'Counterfactual score from a different pick'],
    }
    ir['belief'] = {
        'claims': {
            'SourceIdentity': {'status': 'verified', 'source_sha256': sha(SOURCE), 'full_games': 8, 'commands_matched': 142715, 'all_world_hashes_equal': True},
            'SharedCombat': {'status': 'byte_verified', 'claim': 'Battle body is identical to Richard174; the new component is draft selection.', 'evidence': 'battle-body-comparison.json'},
            'DraftBehavior': {'status': 'source_and_current_replay_verified', 'relh_picks_matched': 200, 'own_draft_control_picks_matched': 200, 'actual_relh_classes': {'Arcanist': 96, 'Lich': 104}},
            'DraftTransfer': {'status': 'counterfactual_choice_only', 'changed_own_choices': 30, 'change': 'DeathKnight to VanguardKnight; all other170 unchanged', 'limits': 'No hypothetical score simulated. No ranged hero is legal in any of100own late drafts.'},
            'Productivity': {'status': 'retrospective_descriptive', 'score_mean': 2027.89, 'nonzero_rate': 0.95, 'productive_score500_rate': 0.9, 'hero_kills_mean': 15.46, 'creep_xp_mean': 2235.185, 'hero_xp_mean': 2319, 'scope': 'Fixed roster; relh is our teammate; classes and seats differ.'},
            'ActiveModes': {'status': 'observed_on_eight_paths', 'normal_nearest_enemy': 49650, 'objective_build_mode8': 87026, 'retreat_mode1': 0, 'siege_retaliation_guards': 95, 'post_hit_walks': 1566, 'limits': 'Counts are eligible controller decisions, not distinct kills or causal benefits. Home-defense guard did not activate in these eight paths.'},
            'HistoricalPromotion': {'status': 'reported_not_reaudited', 'evidence': 'source/candidate.yaml', 'claim': 'Draft-only change fixed v161 overlooking an available Crossbowman in two selected failures; four paired controls reported. Raw co-gas runtime captures unavailable here.'},
            'PreviousCombatTransfers': {'status': 'prior_failures_preserved', 'evidence': ['../../richard-v174/source-audit-20260923/transfer-review.json', '../../richard-v174/source-audit-20260923/scoped-transfer-review.json'], 'claim': '800earlier games did not qualify either broad or blue-Druid siege transfer; do not retry unchanged just because relh shares the body.'},
        },
        'uncertainty': 'No matched class/seat competitive ablation of relh versus ours; no rank forecast. Eight reconstructed mage paths do not establish every class or branch.',
    }
    ir['goal']['DraftLegalContext'] = 'Imitate observed leading-player picks under legal/team context; exported head is not a learned score-value estimator.'
    ir['skill'].pop('DraftPatchAware')
    ir['skill']['DraftLegalContext'] = {
        'initiation': 'Own public draft turn',
        'operation': 'Build32public features, apply10linear logits plus biases, mask unavailable classes, select first strict maximum, submit draftHero and end.',
        'evidence': [{'artifact': 'source/relh-v169.bas', 'start_line': 5, 'end_line': 403}, 'draft-controller.json'],
        'training': 'Reported153training and51development examples; 78.43% agreement versus72.55% masked-frequency. Same development set selected epoch; no independent holdout claim.',
        'transfer': 'Choice compatibility check fails to address our forced-melee problem; no direct promotion.',
    }
    for rule in ir['strategy']:
        rule['id'] = rule['id'].replace('R174', 'RELH169')
        if rule['skill'] == 'DraftPatchAware':
            rule['skill'] = 'DraftLegalContext'
            rule['for'] = ['DraftLegalContext']
    ir['execution']['runtime_max'] = {k: analysis['source_probe'][f'max_{k}'] for k in ['instructions', 'work']}
    ir['execution']['runtime_scope'] = 'Observed maxima across8current-engine Arcanist/Lich full reconstructions; not a universal bound.'
    ir['execution']['draft_terminal_before_battle'] = True
    ir['execution']['portal_support'] = 'None in this source; preserve our qualified portal/channel behavior.'
    ir['update'] = {
        'revision': 1, 'origin': 'User source-review request; source inputs preserved.',
        'evidence': ['provenance.json', 'plan.json', 'evidence/analysis.json', 'battle-body-comparison.json', 'live-readback.json'],
        'hypotheses': 'transfer-hypotheses.ir.json',
        'competitive_transfer_status': 'No live-policy edits; proposals require current-engine controlled evaluation.',
    }
    write(OUT / 'relh_v169.source.ir.json', ir)

    hypotheses = {
        'schema': 'semantic-coaching-hypotheses/1', 'id': 'relh169_transfer_20260923',
        'situation': {
            'source_ir': 'relh_v169.source.ir.json',
            'own_reference_source_sha256': '29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36',
            'engine_commit': plan['identity']['engine'],
            'measured_contexts': '200existing replay59 games,50each own red/blue lead/late; relh always team slot1.',
            'predicates': {
                'forced_melee_draft': 'No ranged or magic class legal; own current draft turn.',
                'reachable_income_target': 'Visible enemy unit in feasible current attack/cast reach with a public path; creep XP same-floor radius must be respected.',
                'class_kit_ready': 'Proposed class-specific core capability is acquired, using own public inventory; exact definition must be frozen before a trial.',
                'safe_productive_return': 'Public buyback price, gold, respawn wait and remaining game time support return; route is not known lethal.',
            },
        },
        'belief': {
            'verified': ['Relh draft head is new; shared combat is already audited.', 'Our carry choices agree with relh head in100/100states.', 'All100own late draft states have only melee legal.', 'Our late melee100games average118.23score; only23%nonzero versus98%for our100carry games.'],
            'not_established': ['Relh head raises our score.', 'More buybacks or fewer rejected orders are independently causal.', 'Mage performance transfers to forced melee.', 'Relh will win future league rounds.'],
        },
        'goal': {
            'primary': 'Improve mean floor(max(0,XP-200*minutes)).',
            'co_primary': ['Raise productive-game rate(score>=500)', 'Preserve or raise nonzero frequency and nonzero mean'],
            'guardrail': 'Preserve productive carry behavior and live champion until a frozen joint gate passes.',
        },
        'skill': {
            'OwnControllerDraftValue': {
                'status': 'proposed_learning_workflow; not a copied runtime',
                'from_relh': 'Explicit legal mask and public ally/enemy composition, timestamp-clean labels, fixed-point export.',
                'operation': 'Estimate returns for our controller by legal class and draft context; compare with our carry-first baseline on separate future rounds. Do not call imitation agreement predicted XP.',
                'negative_case': 'If all available choices are weak melee, no draft model can select an absent carry; focus on the melee controller.',
            },
            'MeleeIncomeAndReach': {
                'status': 'proposed coordinated policy change',
                'from_relh': 'Persistent active engagement and class-conditioned controller; high mage hero-XP contribution is supporting observation, not melee causal evidence.',
                'operation': 'Practice melee target approach, ability-specific legal reach and healing behind allied creeps as a bundle. Pursue a hero only when a plausible reachable finish beats immediate creep income; break stalled chases and retain safe XP-sharing range.',
                'negative_case': 'Do not inherit relh700squared hero pursuit or300squared tower preference; those transfers lack a passing score result.',
            },
            'ClassKitAndReturn': {
                'status': 'proposed coordinated economy/lifecycle change',
                'from_relh': 'Class-aware gear path plus prompt affordable buyback; exact source observable, causal benefit untested.',
                'operation': 'Test a melee-specific affordable kit and a corresponding readiness threshold for buyback together. Keep gold/time safety, farming recovery and portals. Track time-to-kit, recovered field time and XP gained after return.',
                'negative_case': 'No blind always-buyback or extra-potion policy; relh has higher death count, very little healing and no portals.',
            },
        },
        'strategy': [
            {'id': 'RELH169_VALIDATE_DRAFT', 'when': 'considering draft transfer', 'prefer': 'OwnControllerDraftValue', 'for': 'primary'},
            {'id': 'RELH169_MELEE_FLOOR', 'when': 'forced_melee_draft then playing selected melee', 'prefer': 'MeleeIncomeAndReach', 'for': 'co_primary'},
            {'id': 'RELH169_MELEE_RETURN', 'when': 'melee kit/shop/death decisions', 'prefer': 'ClassKitAndReturn', 'for': 'primary'},
        ],
        'execution': {
            'binding': None, 'executable': False, 'deployed': False,
            'already_present': ['Explicit draft and skill upgrades', 'Post-hit recovery', 'Validated core-aware buyback', 'Safe portal channel lock', 'Druid lane recovery'],
            'not_transferred': ['Neural head unchanged', 'Old siege bundle', 'No-portal omission', 'Stale item affordability constants', 'Broad emergency defense behavior'],
        },
        'update': {
            'manual_coaching': '../../../coaching/2026-09-23-manual-score/suggestions.ir.json',
            'proposed_tests': [
                {'id': 'T_DRAFT_COMPATIBILITY', 'status': 'completed offline exact-choice screen', 'result': '200/200relh and200/200own decisions match; transplant changes only30DeathKnight picks toVanguard; no score improvement claimed.'},
                {'id': 'T_MELEE_INCOME', 'status': 'not_started', 'design': 'IR-first combined melee-only reach/target/lane-presence skills; native practice plus matched full-game current-engine comparison. Class/controller and draft seat must be separated; retain identical carry commands where unaffected.', 'falsifier': 'No improvement in nonzero/productive frequency or lower mean; shorter chases/rejection counts without accepted effects do not pass.'},
                {'id': 'T_KIT_RETURN', 'status': 'not_started', 'design': 'Combined class-kit and buyback-readiness intervention; prospective late-seat controls both colors, carry regression controls, then independent fresh score comparison. Use ablations before attributing benefit to gear versus buyback.', 'falsifier': 'Gold diverted from kit, recurring low-income deaths or more field time with worse XP-minus-time.'},
            ],
            'admission': 'Freeze source/IR/engine/field first. Current default400new games/cycle across both colors and draft contexts;>=10%pooled mean gain,each cell>=95%control,positive lower95%gain interval,nonzero mean>=105%control,nonzero frequency>=control and productive frequency higher. No invalid games; exact10source/VM/replay/XP checks. Re-resolve opponents. Permanent100000/day authorization unchanged.',
        },
    }
    write(OUT / 'transfer-hypotheses.ir.json', hypotheses)

    # Source and derived data are portable; bulk captured replay bytes stay at
    # their frozen paths and are content-addressed in the plan/input manifest.
    inputs = []
    for case in plan['cases']:
        folder = Path(case['folder'])
        files = [folder / n for n in ['replay.bin', 'spec.json', 'economy.json', 'results.json', 'episode.json', 'player-status.json']]
        files += [RAW.parent / 'gota-manual-score20260923/episodes' / case['episode'] / 'audit.json', RAW / 'episodes' / case['episode'] / 'drafts.json']
        if (RAW / 'episodes' / case['episode'] / 'source_probe.json').exists():
            files.append(RAW / 'episodes' / case['episode'] / 'source_probe.json')
        inputs.extend({'path': str(p), 'sha256': sha(p)} for p in files)
    write(OUT / 'evidence/input-manifest.json', inputs)
    players = read(RAW / 'players-data.json')
    relh = next(p for p in players['players'] if p['name'] == 'relh')
    buff = {
        'visits': 'buff-visits.json',
        'players_metadata': {k: v for k, v in players.items() if k not in ['players', 'rejections']},
        'relh_versions': relh['policyVersions'],
        'limitation': 'Player window mixes336replay58and24replay59games. Relh169has26games,13per engine. Hero summary is984older games. Neither snapshot alone verifies latest-patch superiority or draft causality.',
    }
    write(OUT / 'buff-context.json', buff)
    provenance = {
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'identity': plan['identity'], 'request': 'request.txt',
        'source_path': str(cogas / 'players/users/relh/co-gas/polyworld-basic/gods_of_the_arena_neural_v58_drafthead_diagnostic.bas'),
        'scope': plan['limitations'], 'raw_root': str(RAW),
        'selection': 'plan.json', 'runtime': 'runtime-provenance.json',
        'games': 200, 'unique_replay_sha256': len({c['replay_sha256'] for c in plan['cases']}),
        'full_reconstructions': 8, 'matched_commands': 142715,
        'new_hosted_games': 0, 'league_writes': 0,
        'preserved_failure': 'Initial draft instrument build referenced unexported ReplayError; changed to ValueError, then rebuilt. No source policy changes.',
        'prior_scope': 'Source trained/promoted on replay58. All new independent replay reconstruction and200game analysis use replay59.',
        'verification': 'verify.py',
    }
    write(OUT / 'provenance.json', provenance)
    # Local immutable artifact integrity; README and verifier are included by
    # seal.py after they are written. Bulk replays are checked with --inputs.
    print(json.dumps({'published': str(OUT), 'source_body_equal': True, 'unique_replays': provenance['unique_replay_sha256']}))


if __name__ == '__main__':
    main()

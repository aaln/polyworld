"""Capture release60 mechanics and amend active research context, not old results."""
import datetime
import json
from pathlib import Path
import shutil
import subprocess
from check import ROOT, RAW, ENGINE, COMMIT, POLICY, sha

OUT = ROOT / 'games/gods_of_the_arena/release-audits/2026-09-23-explicit-abilities'
read = lambda p: json.loads(p.read_text())


def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    live = read(RAW / 'live-readback.json')
    assert live['version'] == '2026.9.23.2' and COMMIT in live['source_url']
    checks, probe, smoke = [read(RAW / n) for n in ['checks.json', 'healing-probe.json', 'smoke.json']]
    assert all(c['passed'] for c in checks['checks']) and smoke['passed']
    assert len(probe['rows']) == 20 and probe['vm_failures'] == 0
    release = json.loads(subprocess.check_output(['git', 'show', 'origin/main:coworld/releases/2026-09-23-gota-explicit-abilities.json'], cwd=ROOT.parent / 'polyworld', text=True))
    assert release['source_commit'] == COMMIT and release['coworld_id'] == live['coworld_id']
    write(OUT / 'release.json', release)
    for n in ['live-readback.json', 'request.txt', 'checks.json', 'healing-probe.json', 'smoke.json', 'smoke-plan.json', 'game-config.json']:
        shutil.copyfile(RAW / n, OUT / n)
    inputs = []
    for p in sorted(RAW.rglob('*')):
        if p.is_file() and not any(part in ['deps', 'bin'] for part in p.relative_to(RAW).parts):
            inputs.append({'path': str(p), 'sha256': sha(p)})
    write(OUT / 'input-manifest.json', inputs)
    for name in ['test_gota_attacks', 'test_gota_spells', 'test_gota_base']:
        path = RAW / (name + '-run.log')
        write(OUT / 'tests' / (name + '.json'), {'source_path': 'tests/' + name + '.nim', 'source_commit': COMMIT, 'output': path.read_text(), 'output_sha256': sha(path), 'exit_code': 0})
    scope = {
        'source_sha256': sha(POLICY), 'engine_commit': COMMIT,
        'old_engine': 'd6827a4bd3a55a46cf86f88e921f147137709c64/replay59',
        'old_evidence_scope': 'Relh169 audit, manual score coaching and completed unit/selective-finish trials used replay59. Those captures stay unchanged; their current-engine wording is historical relative to this release.',
        'fixture_corrections': 'Preliminary all-visible fixture and then all-blind fixture are preserved under raw/preliminary-*. The latter incorrectly hid self-target visibility. Accepted final20fixtures use normal engine vision and assert selected enemy ID is zero every tick. Only final fixture results support healing claims.',
        'membership_scope': 'Live game manifest verified independently. No new membership readback or deployment. Last successful own membership check remains17:48UTC; later credential-scoped reads were unavailable.',
        'new_hosted_games': 0, 'league_writes': 0,
    }
    write(OUT / 'scope.json', scope)
    ir = {
        'schema': 'semantic-coaching-hypotheses/1', 'id': 'explicit_abilities_release60_20260923',
        'situation': {
            'game_version': live['version'], 'coworld_id': live['coworld_id'],
            'engine_commit': COMMIT, 'replay_version': 60,
            'baseline_source_sha256': sha(POLICY),
            'verified_contract': {
                'abilities': 'Every ability, including slot0, healing, restoration and ultimates, requires an explicit castTarget/castPoint command.',
                'items': 'Explicit useItem/useItemAt remains required; this is not a newly introduced item-use rule.',
                'basic_attacks': 'Idle acquisition now includes nearest visible attackable creeps, heroes and exposed structures. walkTo still suppresses acquisition.',
                'removed': ['Hero.manualSpells', 'ActionManualSpells14', 'tryCombatAbilities', 'tryCastAbility'],
                'unchanged': ['Draft and skill point requirements', 'Portal channel and cooldown', 'Keep-only shopping', 'XP-minus200perminute score', 'Current balance stats'],
            },
            'predicates': {
                'ready_safe_heal': 'Learned self-capable healing ability; missing health worthwhile; enough mana and charge; cooldown ready; no active portal channel; safe field context.',
                'ready_mana_restore': 'Learned abilityRestore>0; worthwhile missing mana; charge and cooldown ready; no active portal channel.',
                'valuable_cast': 'Visible legal target and correct ability shape/reach; plausible hero finish, efficient wave clear or justified structure finish; public observations only.',
            },
        },
        'belief': {
            'engine_change': {'status': 'source_and_runtime_verified', 'evidence': ['release.json', 'live-readback.json', 'tests/test_gota_spells.json', 'tests/test_gota_attacks.json']},
            'healing_gap': {'status': 'observed_fixture', 'claim': 'Incumbent Vanguard and DeathKnight at29%HP with mana/rank/charges available issue zero healing spells and walk home in both colors. Generic combat casting is bypassed by retreat/no-target flow.', 'evidence': 'healing-probe.json'},
            'druid_preserved': {'status': 'observed_fixture', 'claim': 'Dedicated Druid lane rule explicitly casts3heals, restores212HP and exits retreat in both colors over180ticks. This is fixture behavior, not score qualification.', 'evidence': 'healing-probe.json'},
            'mana_restore_gap': {'status': 'source_inspected_not_low_mana_fixture', 'claim': 'Incumbent generic casting handles abilityHeal and abilityDamage but never abilityRestore. Arcanist and Warlock restoration abilities have neither heal nor damage, so this path omits them.', 'evidence': 'Pinned content.nim and incumbent R_combat; no native score attribution.'},
            'runtime': {'status': 'four_complete_native_games_pass', 'claim': 'Unchanged incumbent works on new host with nine updated reference VMs; all replay hashes and40integer hero scores match. Not rival qualification.', 'evidence': 'smoke.json'},
            'rejected_orders': {'status': 'interpretation_updated', 'claim': 'Rejected casts still spend no ability resources, but no automatic ability fallback can compensate for omitted or invalid explicit calls. Measure accepted releases and effects.'},
            'opponent_models': {'status': 'requires_new_release_evidence', 'claim': 'Relh169/Richard174 source modes0and8 relied on automatic spells in the old audits except special Lich behavior. Source identity remains verified, but old activation/score findings do not establish new-patch strength.'},
        },
        'goal': {
            'score': 'Raise mean floor(max(0,XP-200*elapsed_minutes)) with more productive games and improved nonzero mean.',
            'spells': 'Explicitly schedule useful healing and damage while protecting escape/heal reserves; no blanket ban on efficient creep casts.',
        },
        'skill': {
            'ExplicitFieldSustain': {'status': 'proposed_not_implemented', 'initiation': 'ready_safe_heal, including no enemy selected and health-only retreat', 'operation': 'Evaluate healing before retreat/target stop conditions. Use self/ally-capable targets correctly; retain channel lock and useful shop return. Re-evaluate safety and ability availability.', 'evidence': 'healing-probe.json'},
            'ExplicitManaRestore': {'status': 'proposed_not_implemented', 'initiation': 'ready_mana_restore, including no enemy selected', 'operation': 'Explicitly cast the learned restoration ability on self; avoid spending at full mana, preserve channel lock, and test low-mana retreat interruption separately.'},
            'LegalExplicitCombat': {'status': 'proposed_not_implemented', 'initiation': 'valuable_cast', 'operation': 'Use current shape/range table, legal minimum distances, target-tracking projectiles and damaging ring placement. Prioritize meaningful hero or wave opportunities; evaluate accepted effects, not attempted-command count.', 'evidence': 'release.json'},
            'ReserveHighValueCharges': {'status': 'proposed_not_implemented', 'operation': 'Reserve scarce ultimates/mana for high-value public opportunities; allow an affordable cast to secure sufficient creep income. Learn thresholds under new-engine controls.'},
        },
        'strategy': [
            {'id': 'EXPLICIT60_SAFE_HEAL', 'when': 'ready_safe_heal and no active portal channel', 'prefer': 'ExplicitFieldSustain', 'over': 'unnecessary health-only walk home', 'for': 'score'},
            {'id': 'EXPLICIT60_MANA_RESTORE', 'when': 'ready_mana_restore', 'prefer': 'ExplicitManaRestore', 'for': 'score'},
            {'id': 'EXPLICIT60_CAST_EFFECT', 'when': 'valuable_cast', 'prefer': 'LegalExplicitCombat', 'for': 'spells'},
            {'id': 'EXPLICIT60_CHARGE_VALUE', 'when': 'multiple legal cast opportunities', 'prefer': 'ReserveHighValueCharges', 'for': 'score'},
        ],
        'execution': {'binding': None, 'executable': False, 'deployed': False, 'baseline_unchanged': True, 'proposed_order': ['Preserve active portal-channel lock', 'Read current ranks/resources/visible targets', 'Evaluate safe self/ally sustain before no-target or retreat stops', 'Choose useful legal damage cast', 'Preserve independent basic/route actions']},
        'update': {
            'revision': 1, 'origin': 'User game-creator update; independently verified published source and live manifest.',
            'preserve': ['Replay59engine and locked dependencies', 'All historical results and source/IR pairs', 'Previous rejected transfer records'],
            'next_tests': ['IR-first explicit-sustain candidate with no-target/retreat, unsafe threat, shop and portal-channel guards', 'All40ability geometry/resource fixtures plus current-engine native matches', 'Fresh controlled replay60score trial and opponent refresh before promotion'],
            'qualification': 'No new competitive gain measured. Prior negative experiments keep their original release scope; changed mechanics justify a separately frozen new test.',
        },
    }
    write(OUT / 'mechanics-and-coaching.ir.json', ir)
    current = read(ROOT / 'games/gods_of_the_arena/current.json')
    if current['game_version'] != live['version']:
        current['engine_history'].append({k: current[k] for k in ['game_version', 'engine_commit', 'coworld_id', 'reference_validation_game_version', 'reference_validation_engine_commit']})
    current.update(game_version=live['version'], engine_commit=COMMIT, coworld_id=live['coworld_id'])
    rel = str(OUT.relative_to(ROOT))
    current['explicit_abilities_release'] = {'report': rel + '/README.md', 'ir': rel + '/mechanics-and-coaching.ir.json', 'verified_at': live['at'], 'replay_version': 60, 'qualification': 'Engine contract and native runtime verified; incumbent not competitively requalified on replay60.', 'new_hosted_games': 0}
    current['research_status'] = 'Replay60explicit-abilities release verified. All automatic ability casting removed.20natural-vision healing fixtures expose missing noncombat Vanguard/DeathKnight sustain; dedicated Druid recovery works. Four complete native matches/hash audits pass for unchanged incumbent. Prior score/opponent comparisons remain historical on their exact releases; next priority explicit casting/healing before a fresh hosted score comparison.'
    current['priority_opponent']['qualification'] = 'Relh169exact source audit remains valid; its200game score/activation cohort is replay59 and must not be treated as current replay60strength. Re-resolve current opponents before testing.'
    current['manual_score_coaching']['release_amendment'] = rel + '/mechanics-and-coaching.ir.json'
    current['relh169_source_audit']['release_scope'] = '2026.9.23.1/replay59; source identity preserved; automatic spell and score observations do not qualify replay60 behavior.'
    write(ROOT / 'games/gods_of_the_arena/current.json', current)
    print(json.dumps({'published': rel, 'engine': live['version'], 'source_unchanged': True, 'new_hosted_games': 0}))


if __name__ == '__main__':
    main()

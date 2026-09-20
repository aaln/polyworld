"""Read-only historical comparison; preserve the exact Alex-winning ancestor."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import pprint
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'tmp/gota-ir/alex-history-20260920'
DEST = ROOT / 'examples/gods_of_the_arena/players/ir/forks/alex-history-20260920'
CAMPAIGN = ROOT.parent / 'gota-autoresearch'
ARCHIVE = ROOT.parent / 'gota-research-20260916'
VERSION = '53f15b12-2198-41d1-bb99-df4bdb1ff7fd'
ALEX = 'a30542cb-54de-4109-92e6-bcabca7db4d8'
SOURCE = 'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2) + '\n')


def ref(p):
    return {'path': str(p), 'sha256': sha(p)}


def historical_cell(path):
    v, plan = read(path), read(path.parent / 'plan.json')
    assert plan['policy_version'] == VERSION
    assert plan.get('rival_version', ALEX) == ALEX
    assert len(plan['roster']) == 10
    assert all(v == (VERSION if slot in plan['own_slots'] else ALEX)
               for slot, v in enumerate(plan['roster']))
    assert plan['game_version'] == '2026.9.16.5'
    assert v['games'] == len(v['rows']) == 40 and v['all_full_audits_passed']
    assert v.get('structured_ten_vm_exits', True)
    streams = []
    structured_status_games = 0
    for row in v['rows']:
        d = path.parent / 'artifacts' / row['episode']
        audit = read(d / 'audit.json')
        assert audit['hash_mismatches'] == 0
        assert audit['actions_consumed'] == audit['recorded_actions']
        assert audit['ticks'] == row['ticks'] == audit['recorded_ticks']
        assert sha(d / 'replay.bin') == row['replay_sha256']
        if (d / 'player-status.json').exists():
            assert sha(d / 'player-status.json') == row['player_status_sha256']
            players = read(d / 'player-status.json')['players']
            assert len(players) == 10 and {p['slot'] for p in players} == set(range(10))
            assert all(p['state'] == 'exited' and p['exit_code'] == 0 for p in players)
            structured_status_games += 1
        else:
            vm = read(d / 'vm-validity.json')
            assert vm['method'] == 'headless_summary' and sha(d / 'game.log') == vm['log_sha256']
        command = path.parent / 'command-diversity-v1' / (row['episode'] + '.json')
        if command.exists():
            streams.append(read(command)['stream_sha256'])
    for key, field in [('wins', 'win'), ('losses', 'loss'), ('draws', 'draw')]:
        assert sum(r[field] for r in v['rows']) == v[key]
    return {k: v[k] for k in ('games', 'wins', 'losses', 'draws')} | {
        'cohort': next(name for name in ('scoped-followup', 'target_geometry',
            'urgent-jordan-20260919', 'role_raid', 'nearby_raid', 'weapon_dense', 'readiness')
            if name in path.parts),
        'color': plan['color'], 'policy_version': VERSION, 'opponent_version': ALEX,
        'request': read(path.parent / 'batch/created.json')['id'],
        'stored_full_audits_and_hashes_verified': True,
        'structured_ten_vm_status_games': structured_status_games,
        'distinct_command_streams': len(set(streams)) if len(streams) == 40 else None,
        'plan': ref(path.parent / 'plan.json'), 'result': ref(path)}


def main():
    # Work only in this new research archive. The original policies and worker
    # experiments remain untouched; no upload, XP purchase or promotion occurs.
    DEST.mkdir(parents=True, exist_ok=True)
    source_dir = STUDY / 'references/relh154-legacy'
    assert sha(source_dir / 'policy.bas') == SOURCE
    registration = ARCHIVE / 'coached-lanes/r5-relh154/scoped-followup/hosted/legacy'
    assert read(registration / 'upload-request.json')['content_hash'] == SOURCE
    assert read(registration / 'uploaded-version.json')['id'] == VERSION
    for name in ('policy.ir.json', 'policy.bas', 'parity.json'):
        shutil.copy2(source_dir / name, DEST / name)
    policy = read(DEST / 'policy.ir.json')
    (DEST / 'policy.py').write_text('"""Recovered historical IR; no behavior changes."""\n\nPOLICY = ' +
        pprint.pformat(policy, width=110, sort_dicts=False) + '\n')
    for name in ('legacy-to-jordan-skills.json', 'jordan-to-critical-skills.json',
                 'critical-to-current-skills.json'):
        shutil.copy2(STUDY / name, DEST / name)
    assert list(read(STUDY / 'legacy-to-jordan-skills.json')) == ['observe']
    assert list(read(STUDY / 'jordan-to-critical-skills.json')) == ['observe']
    paths = [Path(r['path']) for r in read(STUDY / 'result-index.json')['rows']
             if '/g002/parent/' in r['path'] or '/g002/legacy/' in r['path']]
    cells = [historical_cell(p) for p in paths]
    chosen = [r for r in cells if '/readiness/' in r['result']['path']]
    assert len(chosen) == 2
    assert {r['color']: r['wins'] for r in chosen} == {'red': 30, 'blue': 40}
    assert all(r['structured_ten_vm_status_games'] == 40 for r in chosen)
    tower = CAMPAIGN / 'forks/fork_20260920_045449_29b23b/tower_handoff_v2'
    tp = read(tower / 'hosted-discovery/plan.json')
    tower_cells = []
    for arm in tp['arms']:
        if arm['role'] == 'candidate' and arm['rival'] in (
            ALEX, '207ffaf9-0d1e-4d92-a15d-4352f1bddec2', '7c370daf-3c5f-42f8-870b-54b79c495a44'):
            p = tower / 'hosted-discovery' / arm['name'] / 'result.json'
            v = read(p)
            assert v['valid_games'] == len(v['rows']) == 40 and v['all_vm_replay_identity_checks']
            assert all(r['valid'] for r in v['rows'])
            assert sum(r['win'] for r in v['rows']) == v['wins']
            tower_cells.append({k: v[k] for k in ('arm', 'wins', 'losses', 'draws', 'request')} |
                               {'version': arm['subject'], 'opponent': arm['rival'], 'evidence': ref(p)})
    trace_dir = STUDY / 'legacy-blue-median'
    full = [json.loads(line) for line in (trace_dir / 'owned-full.jsonl').open() if line.strip()]
    summary = full[-1]
    assert summary['all_state_hashes_equal'] and summary['all_actions_consumed']
    decisions = [r for r in full if r['type'] == 'decision']
    # A flag alone can persist when no current front is seen. Count fresh
    # middle-alarm contexts only when the same decision renews the commitment.
    middle = [r for r in decisions if r['memory']['middleRush'] and
              r['memory']['defCount'] >= 3 and r['memory']['defAnchor'] in (19, 20, 21) and
              r['memory']['defUntil'] == r['tick'] + r['memory']['defHoldTicks']]
    trace = {'episode': 'ereq_961b5050-b94e-454f-af6c-a9be2300d867',
        'selection': 'Median-duration recorded blue win in the readiness parent cohort',
        'equivalence': read(trace_dir / 'equivalence.json'), 'all_decision_summary': summary,
        'active_defense_decisions': sum(bool(r['memory']['defActive']) for r in decisions),
        'fresh_middle_alarm_decisions': len(middle),
        'first_fresh_middle_alarm': middle[0] if middle else None,
        'fresh_alarm_slots': sorted({r['slot'] for r in middle}),
        'full_owned_trace': ref(trace_dir / 'owned-full.jsonl'),
        'limits': 'One reconstructed winning episode. This proves behavior occurred, not that a particular rule caused the win.'}
    write(STUDY / 'legacy-blue-mechanism.json', trace)
    transition = ROOT / 'tmp/gota-ir/richard-transition-20260920'
    record = {'at': datetime.now(timezone.utc).isoformat(), 'source_sha256': SOURCE,
        'version': VERSION, 'name': 'aaron-gota-ir-relh154-legacy-0916:v1',
        'source_registration': [ref(registration / 'upload-request.json'),
                                ref(registration / 'uploaded-version.json')],
        'opponent': ALEX, 'game_version': '2026.9.16.5',
        'historical_cells': cells, 'highlighted_cohort': chosen,
        'distinct_historical_requests': len({r['request'] for r in cells}),
        'red_win_range': [min(r['wins'] for r in cells if r['color'] == 'red'),
                          max(r['wins'] for r in cells if r['color'] == 'red')],
        'behavior_diff': 'Only observe skill differs between this ancestor and deployed Jordan counter. Combat, equipment and navigation skill definitions match.',
        'blue_replay': trace, 'tower_handoff_experiment': tower_cells,
        'tower_plan': ref(tower / 'hosted-discovery/plan.json'),
        'tower_rejection': ref(tower / 'hosted-discovery/final-verdict.json'),
        'current_failed_gate': ref(transition / 'promotion-check/result.json'),
        'new_hosted_games': 0, 'league_changed': False,
        'limits': 'Historical fixed-lineup cohorts, correlated trajectories and differing generated seeds. No independent-trial significance, live retest, or isolated causal attribution. New red tower-handoff branch is separate from the historical deployed ancestor.'}
    write(STUDY / 'findings.json', record)
    write(DEST / 'findings.json', record)
    blue = [r for r in cells if r['color'] == 'blue']
    rows = '\n'.join(f"| {r['cohort']} | {r['color']} | {r['wins']} | {r['losses']} | {r['draws']} | {r['distinct_command_streams'] if r['distinct_command_streams'] is not None else 'not counted'} |" for r in cells)
    report = f'''# Recovered Alex-winning policy — September 20, 2026

The previous `aaron-gota-ir-relh154-legacy-0916:v1` repeatedly beat the exact current Alex `gota-g002:v1` UUID. In the highlighted September 19 comparison it won **70/80: red30/40, blue40/40**. All {len(blue)} recovered blue cohorts won40/40. Red was less reliable: {record['red_win_range'][0]}–{record['red_win_range'][1]} wins per40 across the recovered cohorts. This is a historical result, not a fresh retest.

Exact policy version: `{VERSION}`. BASIC SHA256: `{SOURCE}`. Opponent: `{ALEX}`. Engine:2026.9.16.5. The recovered primary `policy.py`, JSON IR and BASIC preserve the old behavior; compile/extract parity is recorded. Original evidence and captured coaching inputs remain unchanged.

The executable difference from the later deployed Jordan counter is confined to **the observer/defense decision**. Attack, spell/equipment and navigation skill definitions match. This narrows the investigation to when those unchanged skills are used; it does not independently prove which recall change caused every loss.

- **Early middle warning on blue:** during the first75seconds, three visible clustered enemies near a standing middle tower can trigger recall instead of waiting for four.
- **Damaged side-tower warning on blue:** during the first150seconds, a visible pair near a standing side tower with150HP missing triggers ordinary recall. This is current damage, not a measured damage rate.
- **Defend the threatened objective:** remember the protected structure; consider visible enemies within24tiles of it and32tiles of the acting hero. The role and commitment clocks retain defense. Non-sentries with no actionable target for20seconds can release; fog is never treated as proof of safety.
- **What the Jordan counter changed:** it cancels defense beyond28tiles from the friendly god; blue also clears solo backdoor commitment. This preserves distant offense, but removes the old remote return behavior.
- **What the Richard counter then added:** a two-enemy, anchored near-core alarm within60tiles can override that cancellation for50seconds. This broader rule is different from restoring the old objective-specific alarms. Our latest inherited blue won40/40 against Richard but0/40 against Alex.

The historical median-duration blue win was reconstructed from its exact source: **24,618 owned commands and all5,880 state hashes match**. The fresh early-middle alarm occurred on {len(trace['fresh_alarm_slots'])} hero slots, across {trace['fresh_middle_alarm_decisions']} decisions. This establishes that the early defense behavior was used in an actual win; it is not an ablation proving that rule alone won the game.

| Historical cohort | Our color | Wins | Losses | Draws | Distinct full command streams |
|---|---|---:|---:|---:|---:|
{rows}

Stored native replay audits, row counts and replay hashes were rechecked for these cohorts. The highlighted80games have all ten successful structured VM exits and player-status hashes rechecked. The older legacy confirmation has archived headless-log validation but no structured player-status files; the manifest keeps that distinction. Seeds and repeated trajectories are correlated; do not interpret the rows as independent Bernoulli trials or select the best red cohort as a guaranteed87.5%future win rate. The broader record explains the remembered near-perfect blue results.

A separate September20 experiment, `tower_handoff_v2` (`17db3a9d-b5eb-4f5a-b5aa-10654e9555bd`), recovered **Alex red40/40**, while **Alex blue0/40**. It also won40/40 each color against Jordan and0/40 each color against Richard. Its red behavior couples caster transit/support with a low-HP tower disengagement requiring a nearby live allied creep, and preserves attacks on nearly finished towers. A reviewed Alex red win contains three actual tower-target changes. The complete package, not tower disengagement alone, owns that win count. It was rejected for joint target advancement and remains unpromoted.

Two discriminating follow-ups are supported by this research, not yet validated:

1. Restore the historical blue observer as an exact reference, then test objective-triggered recall versus the28-tile cancellation and the broad Richard exception with other skills fixed. Predicted effect: recover early middle defense and Alex blue wins; Jordan and Richard must be checked because the timing tradeoff may return.
2. Test the newer red caster/tower-handoff component with the historical blue observer in a separately versioned IR combination. Predicted effect: preserve the red Alex result while recovering blue; mixing individually successful color components is not proof the combined executable will win. The worker's separate critical-blue fusion is a different hypothesis and is left untouched.

No policy was pushed. The latest unchanged coaching candidate failed the user-authorized Alex/Jordan check: Alex red2W24L14D, blue0W40L; Jordan0W40L on each color. Its evaluated IR/BASIC pair and all400hosted/108local results are saved in the sibling `richard135-transition-20260920` bundle. The live incumbent was retained.

Evidence manifest: `findings.json`; exact skill changes: `legacy-to-jordan-skills.json`, `jordan-to-critical-skills.json`, `critical-to-current-skills.json`. Raw historical research: `{STUDY}`. No new hosted games were purchased for this historical investigation.
'''
    (DEST / 'README.md').write_text(report)
    (STUDY / 'README.md').write_text(report)
    (ROOT / 'docs/reports/2026-09-20-alex-policy-history.md').write_text(report)
    # Use the lab's report template typography without fabricated significance.
    template = (ROOT.parent / 'optimizer-seed/docs/reports/_template.html').read_text()
    head = template.split('<body>')[0].replace('REPORT TITLE — YYYY-MM-DD', 'Recovered Alex-winning policy — 2026-09-20')
    paragraphs = []
    for block in report.split('\n\n'):
        if block.startswith('# '):
            paragraphs.append('<h1>' + html.escape(block[2:]) + '</h1>')
        elif block.startswith('| '):
            table = []
            for line in block.splitlines():
                if line.startswith('|---'): continue
                cells_html = [html.escape(c.strip()) for c in line.strip('|').split('|')]
                tag = 'th' if not table else 'td'
                table.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells_html) + '</tr>')
            paragraphs.append('<table>' + ''.join(table) + '</table>')
        else:
            escaped = html.escape(block)
            escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
            escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
            paragraphs.append('<p style="overflow-wrap:anywhere;white-space:pre-line">' + escaped + '</p>')
    page = head + '<body><div class="page">' + ''.join(paragraphs) + '</div></body></html>'
    (ROOT / 'docs/reports/2026-09-20-alex-policy-history.html').write_text(page)
    print(json.dumps({'historical_cells': len(record['historical_cells']), 'blue_perfect_cohorts': len(blue),
        'fresh_middle_alarm_decisions': len(middle), 'archive': str(DEST)}, indent=2))


if __name__ == '__main__':
    main()

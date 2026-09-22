"""Version-scoped stats review; aggregate observations are hypotheses, not A/Bs."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import study

h, ROOT = study.h, study.ROOT
raw = h.STUDY / 'player-stats'
out = ROOT / 'docs/reports/gota-player-stats-20260922'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not out.exists(), 'Keep captured reports immutable'
    data = h.read(raw / 'data.json')
    ids = {'Aaron': study.BASELINE,
           'Coach': '35c85505-1977-4bad-b4ea-f1473aaa79dc',
           'khors:v114': '145c01e0-0cbf-4e1e-8120-11b437175b91',
           'Jordan:v411': 'a15665be-4edf-4857-b23b-2888b4b49868'}
    versions = {v['id']: v for p in data['players'] for v in p['policyVersions']}
    selected = {name: versions[ident] for name, ident in ids.items()}
    assert all(set(v['engines']) == {'57'} for v in selected.values())
    own, rival = selected['Aaron']['values'], selected['khors:v114']['values']
    metrics = [('score', 'Recorded score'), ('minutes', 'Game minutes'), ('xp', 'Lifetime XP'),
               ('xp_lasthit', 'XP at creep last hits'), ('xp_shared', 'XP from nearby creep deaths'),
               ('xp_herokill', 'Hero-kill XP'), ('xp_building', 'Building XP'),
               ('kills', 'Hero kills'), ('deaths', 'Deaths'), ('level', 'Final level'),
               ('target_building', 'Building-target order share'), ('target_hero', 'Hero-target order share'),
               ('gold_end', 'Unspent end gold'), ('buy_portal', 'Scrolls purchased'),
               ('buybacks', 'Buybacks'), ('casts_pm', 'Accepted casts/min alive'),
               ('rej_ActionOutOfRange', 'Out-of-range rejections'),
               ('rejected_share', 'Rejected order share'), ('time_near_own_god', 'Alive time near own god')]
    lines = ['| Metric | Aaron (70) | Coach (71) | khors:v114 (13) | Jordan:v411 (97) |',
             '|---|---:|---:|---:|---:|']
    for key, label in metrics:
        percent = key.endswith('share') or key.startswith('target_') or key.startswith('time_')
        vals = [(f"{v['values'][key] * 100:.1f}%" if percent else f"{v['values'][key]:,.1f}") for v in selected.values()]
        lines.append('| ' + label + ' | ' + ' | '.join(vals) + ' |')
    rate = {name: v['values']['xp'] / v['values']['minutes'] for name, v in selected.items()}
    delta_xp = rival['xp'] - own['xp']
    delta_minutes = rival['minutes'] - own['minutes']
    delta_score = rival['score'] - own['score']
    derived = {'pooled_xp_per_recorded_minute': rate,
               'khors_minus_aaron': {'xp': delta_xp, 'minutes': delta_minutes,
                                     'extra_time_cost': 200 * delta_minutes,
                                     'unclamped_score_difference': delta_xp - 200 * delta_minutes,
                                     'recorded_score_difference': delta_score,
                                     'mean_clamp_and_rounding_residual': delta_score - (delta_xp - 200 * delta_minutes)},
               'break_even_xp_per_minute': 200,
               'scope': 'Ratios of summed XP to summed recorded duration, not means of per-game rates. Includes drafting; version windows/drafts/teams differ. Marginal future XP cannot be inferred causally from historical pooled rates.'}
    out.mkdir(parents=True)
    for f in ('data.json', 'players.html', 'players.js', 'PLAYERS.md', 'extract.nim', 'engines.json'):
        shutil.copy2(raw / f, out / f)
    h.write(out / 'selected.json', selected)
    h.write(out / 'derived.json', derived)
    # All players are available for inspection; mixed-engine versions are labeled.
    with (out / 'all-players-latest.csv').open('w') as f:
        keys = sorted({k for p in data['players'] for k in p['values']})
        w = csv.DictWriter(f, fieldnames=['player', 'version', 'games', 'engines'] + keys)
        w.writeheader()
        for p in data['players']:
            if not p['policyVersions']:
                continue
            v = p['policyVersions'][0]
            w.writerow({'player': p['name'], 'version': f"{v['name']}:v{v['version']}",
                        'games': v['games'], 'engines': json.dumps(v['engines']), **v['values']})
    model = {
        'schema': 'gota-optimization-hypotheses/1',
        'situation': {'game_version': h.VERSION, 'engine_commit': h.COMMIT,
                      'stats_window': [data['windowStart'], data['windowEnd']],
                      'direct_inputs': ['public targets and distances', 'current HP/mana', 'public ranks/cooldowns', 'own inventory/gold', 'observed score/XP progress'],
                      'evaluation_only': ['opponent UUIDs', 'hidden replay positions', 'other-VM failures', 'aggregate player statistics']},
        'belief': {'observed': derived, 'causal_status': 'unidentified from this snapshot',
                   'confounders': ['unequal time windows and sample sizes', 'draft/role/side', 'teammates', 'failed other VMs', 'duration selection', 'score clamping'],
                   'rejected_shortcuts': ['maximize duration unconditionally', 'minimize deaths without XP', 'maximize command count', 'treat every repeated command as waste', 'spend all gold without measuring opportunity cost']},
        'goal': {'primary': 'Improve individual integer XP score on both colors against exact khors:v114',
                 'secondary': ['deny avoidable enemy kill XP', 'preserve productive field time', 'preserve necessary base defense']},
        'skill': {'productive_farm': {'status': 'proposed', 'measure': 'creep XP per alive field minute and last-hit opportunities'},
                  'productive_engage': {'status': 'proposed', 'measure': 'hero XP minus expected death/recovery opportunity cost'},
                  'safe_field_recall': {'status': 'already under frozen A/B', 'measure': 'wasted home portals, interruptions, recovery time, resumed XP and score'},
                  'range_aware_casting': {'status': 'source-grounded opportunity', 'measure': 'accepted effective casts, damage and XP; rejections secondary'},
                  'profitable_extension': {'status': 'proposed', 'measure': 'extra XP minus200 per additional minute; do not idle to extend clock'},
                  'economy_conversion': {'status': 'proposed', 'measure': 'net score gain from useful consumables or timely buyback, not raw gold spent'}},
        'strategy': [
            {'id': 'S_XP_OPPORTUNITY', 'when': 'A public farming or safe hero-engagement opportunity is available and no immediate own-base emergency exists', 'skill': 'productive_farm_or_engage', 'for': ['primary'], 'status': 'proposed', 'comparison': 'Versus current strong structure target preference; required access-opening structures remain possible'},
            {'id': 'S_PROFITABLE_DURATION', 'when': 'A repeatable farming opportunity has expected marginal XP above200/minute with acceptable death risk', 'skill': 'profitable_extension', 'for': ['primary'], 'status': 'proposed', 'limits': 'No unconditional stalling, no inference from aggregate duration alone'},
            {'id': 'S_CAST_REACH', 'when': 'A damaging spell is ready and the selected public target is within that current host ability range', 'skill': 'range_aware_casting', 'for': ['primary'], 'status': 'proposed'}],
        'execution': {'binding': 'research-hypotheses/1', 'executable': False,
                      'active_portal_candidate_unchanged': study.HASH,
                      'note': 'Do not merge into a controller before its own local drills and fresh hosted comparison.'},
        'update': {'origin': 'User-provided player statistics guide, September22',
                   'priority': ['XP-producing target allocation and profitable duration', 'portal recovery A/B', 'spell range/effectiveness', 'gold conversion'],
                   'evidence': ['data.json', 'derived.json', 'extract.nim', 'README.md']}}
    h.write(out / 'optimization.ir.json', model)
    (out / 'README.md').write_text(f'''# Player statistics: where to improve

Source: [Gods of the Arena player statistics](https://metta-ai.github.io/polyworld-buff/GOTA/players/).
Captured snapshot generated **{data['generatedAt']}**, covering **360 replays**
between **{data['windowStart']}** and **{data['windowEnd']}**.
Use exact policy versions. Aaron/Coach's deployed source and khors:v114/Jordan411
below all use replay engine57 (current patched game). Richard153 and relh161
combine engines51/56/57 in this snapshot; their rows in the CSV are descriptive
history and are not a clean current-patch comparison.

{chr(10).join(lines)}

## Primary opportunity: productive targets

Our current controller allocates about36% of accepted attack-target orders to
buildings; khors:v114 allocates essentially none. Its higher score accompanies
more hero-kill and creep XP, despite more deaths and fewer team wins. The
comparison suggests testing lower structure priority when a productive creep
wave or safe hero fight is available. Preserve emergency defense and structures
that open useful access. Barracks destruction can remove future enemy creep
income, so objective timing belongs in this test too. Order share is a proxy for
attention, not time or damage, and does not prove that structure targeting caused
the score difference.

## Longer games: evaluate marginal XP, not duration alone

Current score is `max(0, floor(lifetime XP - 200 * world minutes))`, including
draft. Each extra minute must earn more than200 XP to raise unclamped score.
For example, another minute earning400 XP adds about200 points; one earning100
XP loses about100 points before clamping. Zero-XP waiting costs200 per minute.

Khors averages **{delta_minutes:.2f} more minutes** and **{delta_xp:.1f} more XP**
than Aaron. Extra time costs **{200 * delta_minutes:.1f} points**, leaving an
unclamped difference of **{delta_xp - 200 * delta_minutes:.1f}**. The recorded gap
is **{delta_score:.1f}**; per-game clamping/rounding explains the residual.
Pooled XP per recorded minute is **{rate['Aaron']:.1f} for Aaron**,
**{rate['Coach']:.1f} for Coach**, and **{rate['khors:v114']:.1f} for khors**.
These are ratios of totals, not average per-game rates or estimates of future
marginal income. Longer games may result from stronger farming or weaker
objectives; this snapshot cannot separate cause and consequence.

## Direct-control cleanup

Aaron records about591 out-of-range rejections per game, versus6 for khors.
In pinned `sim.nim`, the explicit `ActionOutOfRange` return is object-targeted
spell range validation. Our generated `R_combat` tries damaging spells against
the chosen target without a range guard. `attackTarget` itself does not return
that range error. Prioritize effective spell usage and positioning, rather than
assuming these are missed basic attacks. Suppressing failed attempts alone can
improve the dashboard without improving score; measure landed effects and XP.
Current BASIC lacks an ability-range query, so a future guard needs a
current-engine, class/rank-aware binding or conservative public geometry test.

The portal A/B already tests field recall, reserves and the final channel-tick
lock. The new stats do not change the executable being evaluated. Track avoided
home-to-home channels, failed channels, recovery duration and XP after return.

## Indirect economy and survival

Aaron ends with about1501 unspent gold; Coach1309 and khors1391. Spending more is
not automatically useful: six inventory slots and no sell/upgrade operation
limit conversion. Test stacked useful consumables and buyback only when their
expected productive time exceeds the purchase/return cost. Extra shopping trips
can erase the benefit. Our lower deaths and high average HP are strengths, but
could also coexist with missed profitable fights; target net XP, not minimum
deaths or maximum HP. Jordan illustrates the limit: very low rejections and
high survival accompany much less hero-kill XP and lower score.

## Scope and proposed tests

The13 khors:v114 games come from one round; Aaron70 and Coach71 span a longer
window. Draft, side, teammates and failed VMs differ. Website statistics exclude
replay hash failures but do not certify all participants' VMs succeeded. This
is hypothesis generation, not causal or independent competitive validation.

`optimization.ir.json` records seven research layers and the proposed priorities.
It is deliberately non-executable; current accepted IR stays unchanged until
combined changes are practiced and compared against frozen fresh controls.
`all-players-latest.csv` retains every observed player's latest-version values,
including explicit engine coverage. Original downloaded files are byte-preserved.
Definitions and limitations follow the [site's extractor guide](https://github.com/Metta-AI/polyworld-buff/blob/main/tools/PLAYERS.md).
''')
    h.write(out / 'manifest.json', {'captured_at': h.research.now(), 'source_url': 'https://metta-ai.github.io/polyworld-buff/GOTA/players/',
                                  'stats_repo_commit': h.read(raw / 'source-tree.json')['sha'],
                                  'files': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps(derived))


if __name__ == '__main__':
    main()

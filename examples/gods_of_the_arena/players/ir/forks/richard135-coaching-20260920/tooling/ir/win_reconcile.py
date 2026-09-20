"""Close the completed win-first evidence -> IR -> identical BASIC loop."""
from copy import deepcopy
from datetime import datetime, timezone

from policy_ir import HERE, bundle, compile_policy, digest, extract, read, refresh_grounding, write
from release_reconcile import reconcile
from win_screen import STUDY


def main():
    confirmation = STUDY / 'hosted-confirmation/result.json'
    field_path = STUDY / 'field/result.json'
    result, field = read(confirmation), read(field_path)
    name = result['selected']
    if not result['passed'] or not field['passed'] or field['candidate'] != name:
        raise ValueError('Finish passing confirmation and field validation first')
    candidate, control = result['arms'][name], result['arms']['current']
    comparison = result['comparisons'][name]
    version = read(STUDY / 'hosted-discovery' / name / 'uploaded-version.json')
    source_path = STUDY / 'local/candidates' / name / 'policy.bas'
    source = source_path.read_text()
    evidence = [STUDY / 'local/screen-result.json', STUDY / 'hosted-discovery/result.json', confirmation, field_path, STUDY / 'rival-matchups/result.json']
    claim = (f'Published 2026.9.16.3, completed fresh held-out confirmation: {candidate["wins"]}/400 fort wins '
        f'versus current deployed Lich {control["wins"]}/400, gain {comparison["gain"]*100:.2f} percentage points, '
        f'one-sided Fisher p={comparison["one_sided_p"]:.8g} under ten pinned role rotations. '
        f'Mean subject hero deaths/game {candidate["mean_deaths"]:.4f} versus {control["mean_deaths"]:.4f}; '
        f'deaths/alive-minute {candidate["death_rate"]:.4f} versus {control["death_rate"]:.4f}. '
        f'All 400 candidate games purchased equipment; no adverse class guard failed. '
        f'Separate 100-game sampled-current-field check: {field["wins"]}/100 wins, all equipment and validity checks passed. '
        'All requested episodes retained and fully replay-audited. Conditional roster results do not establish rank #1 or arbitrary-opponent superiority.')
    out = STUDY / 'reconciled' / name
    out.parent.mkdir(exist_ok=True)
    refs = [{'artifact':str(p.resolve()), 'sha256':digest(p.read_bytes())} for p in evidence]
    parent_path = STUDY / 'hosted-confirmation' / name / 'feedback/policy.ir.json'
    scoped = out.parent / (name + '-scoped')
    if scoped.exists():
        intermediate = read(scoped / 'policy.ir.json')
        if (intermediate['update']['parent'] != digest(read(parent_path)) or
                intermediate['belief']['claims']['B_release_evaluation'] != {'claim':claim,'status':'supported','evidence':refs} or
                compile_policy(intermediate) != source or extract(source,intermediate) != intermediate):
            raise ValueError('Existing scoped feedback has changed')
    else:
        intermediate = reconcile(parent_path, source_path, evidence, claim, scoped,
            resolved_reviews=('belief/B_candidate', 'goal/G_fort', 'goal/G_survival'))
    policy = deepcopy(intermediate)
    policy['belief']['claims']['B_macro'] = {'claim':
        'Rejecting the selected mobile target beyond 12 tiles, retaining wave navigation and class combat, '
        'with the separately declared dense-object recovery fallback, improved measured fort wins in the completed study. '
        'The results do not isolate the pursuit bound from that fallback. ' + claim,
        'status':'supported', 'evidence':refs}
    rivals = read(evidence[-1])
    policy['belief']['claims']['B_named_rivals'] = {'claim':
        '; '.join(f'{r["label"]}: {r["wins"]}/80 wins, red {r["colors"]["red"]["win"]}/40, blue {r["colors"]["blue"]["win"]}/40'
                  for r in rivals['rivals'].values()) + '. Five policy copies per team, two fixed tactical lineups per rival. Seeded repeats can reproduce identical behavior; no broad significance claim.',
        'status':'supported', 'evidence':[refs[-1]]}
    review = STUDY / 'review/druid-review-manifest.json'
    reviews = list(policy['update']['needs_review'])
    if review.exists():
        druid_field = field.get('class_wins', {}).get('DruidWarden')
        field_context = (f' In the separate sampled-current-field check Druid won {druid_field["wins"]}/{druid_field["games"]}, so this gap is roster-dependent.' if druid_field else '')
        policy['belief']['claims']['B_lane_coverage'] = {'claim':
            'Remaining follow-up hypothesis: class-specific lane coverage may improve Druid Warden outcomes. '
            'Completed discovery: bounded 0/10 Druid wins versus full lane routing 7/10, but full lane routing failed overall survival. '
            'A reviewed bounded loss ended at 3:03 with one Druid death while its undefended lane collapsed; '
            'a different-seed lane win lasted 7:49 with six Druid deaths. These anecdotes do not establish a causal effect, '
            'and this evaluated executable has not incorporated that proposed route change.' + field_context,
            'status':'requires_review', 'evidence':[refs[1], refs[3], {'artifact':str(review.resolve()), 'sha256':digest(review.read_bytes())}]}
        reviews.append('belief/B_lane_coverage')
    policy['update'] = {'revision':intermediate['update']['revision']+1, 'parent':digest(intermediate),
        'change':'Resolve measured macro and rival beliefs; retain lane-coverage uncertainty and exact tested executable.',
        'needs_review':sorted(set(reviews)-{'belief/B_macro'}), 'evidence':refs}
    refresh_grounding(policy)
    if compile_policy(policy) != source or extract(source, policy) != policy:
        raise ValueError('Feedback changed tested behavior or failed reverse extraction')
    if out.exists():
        if read(out / 'policy.ir.json') != policy or (out / 'policy.bas').read_text() != source or read(out / 'extracted.ir.json') != policy:
            raise ValueError('Existing final feedback has changed')
    else:
        bundle(policy, out)
    write(out / 'pre-reconcile-parent.ir.json', read(parent_path))
    write(out / 'parent.ir.json', intermediate)
    canonical = 'win_' + name + '_0916.evaluated'
    write(HERE / (canonical + '.ir.json'), policy)
    (HERE / (canonical + '.bas')).write_text(source)
    write(out / 'reconciliation.json', {'policy_version':version['id'], 'ir_sha256':digest(policy),
        'basic_sha256':digest(source.encode()), 'confirmation_sha256':digest(confirmation.read_bytes()),
        'field_sha256':digest(field_path.read_bytes()), 'compile_and_reverse_extract_exact':True,
        'remaining_uncertainty':'Class-specific lane coverage is recorded for future testing, not implemented.'})
    log = HERE / 'VERSION_LOG.md'
    text = log.read_text()
    marker = f'## Win-first validated {version["id"]}'
    if marker not in text:
        text += (f'\n{marker}\n\n- UTC {datetime.now(timezone.utc).isoformat()}. {claim}\n'
            f'- Final IR `{digest(policy)}`; exact evaluated BASIC `{digest(source.encode())}`. Evidence `{STUDY}`.\n'
            '- Rollback baselines: Optimizer `3b5d11e5-cd80-4783-afae-0aa2ef1e4505`; Aaron `7321f8ff-f9d7-46fe-828c-3168bc21af1a`.\n'
            '- User authorization persists: “update the policies from my players on the league”. Final selection and exactly-two-player verification are recorded separately in deployment-pair.\n')
        log.write_text(text)
    print(out)


if __name__ == '__main__':
    main()

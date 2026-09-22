"""Documented auto-champion fallback after reconciled manual-selection 500s."""
import time
import jsonschema
import deploy_current as d

h = d.h


def memberships(c):
    return h.get(c, f'/v2/league-policy-memberships?league_id={d.LEAGUE}&mine=true&limit=100')


def auto(c, label, version, schema):
    player = d.PLAYERS[label]
    out = d.OUT / label / 'auto-selection'
    rows = memberships(c)
    existing = [r for r in rows if r['player']['id'] == player and r['policy_version']['id'] == version['id'] and r['end_time'] is None]
    if any(r['is_champion'] and r['status'] == 'competing' and r['substatus'] == 'active' for r in existing):
        return next(r for r in existing if r['is_champion'])
    # Only retire the already reconciled, unselected manual-attempt membership.
    # The old live champion is not retired here.
    for row in existing:
        assert label == 'aaron' and row['id'] == 'lpm_47482d86-f6fc-4121-98de-71ad39d9f51d'
        assert not row['is_champion'] and row['policy_version']['id'] == version['id']
        h.write(out / 'unselected-before-retire.json', row)
        body = {'reason': 'Reconcile unselected membership after two manual champion HTTP500s; resubmit identical version using documented auto_champion=always. Existing compat champion retained until replacement.'}
        r = c.post('/v2/league-policy-memberships/' + row['id'] + '/retire', json=body)
        h.write(out / 'retire-response.json', {'status': r.status_code, 'body': r.text})
        r.raise_for_status()
        after = next(x for x in memberships(c) if x['id'] == row['id'])
        # The current retirement endpoint represents retirement as
        # disqualified/inactive with end_time, not a status named retired.
        assert after['status'] in ('retired', 'disqualified') and after['end_time'] is not None and not after['is_champion']
    body = {'league_id': d.LEAGUE, 'policy_version_id': version['id'], 'player_id': player,
            'auto_champion': 'always', 'notes': d.NOTE + ' Supported automatic selection fallback after reconciled manual endpoint HTTP500; exact source/evidence unchanged.'}
    h.freeze(out / 'request.json', body)
    definition = schema['paths']['/v2/league-submissions']['post']['requestBody']['content']['application/json']['schema']
    jsonschema.validate(body, definition, resolver=jsonschema.RefResolver.from_schema(schema))
    receipt = out / 'created.json'
    if not receipt.exists():
        # Resuming an uncertain create must reconcile by version and preference.
        query = f'/v2/league-submissions?league_id={d.LEAGUE}&player_id={player}&policy_version_id={version["id"]}&limit=100'
        submissions = h.get(c, query)
        prior = [r for r in submissions if r.get('auto_champion') == 'always' and r['status'] not in ('failed', 'rejected', 'cancelled')]
        assert len(prior) <= 1
        if prior:
            h.write(receipt, prior[0])
        else:
            r = c.post('/v2/league-submissions', json=body)
            h.write(out / 'create-response.json', {'status': r.status_code, 'body': r.text})
            r.raise_for_status()
            h.write(receipt, r.json())
    for _ in range(120):
        rows = memberships(c)
        h.write(out / 'readback.json', rows)
        selected = [r for r in rows if r['player']['id'] == player and r['policy_version']['id'] == version['id'] and r['end_time'] is None]
        if selected:
            assert len(selected) == 1
            row = selected[0]
            assert row['status'] not in ('disqualified', 'rejected', 'retired')
            if row['status'] == 'competing' and row['substatus'] == 'active' and row['is_champion']:
                print('VERIFIED automatic selection', label, version['id'], row['id'], flush=True)
                return row
        time.sleep(5)
    raise RuntimeError('Existing automatic submission pending; reconcile and resume exact receipt')


def main():
    with h.research.lock(h.CAMPAIGN / 'league-deployment.lock', blocking=False), h.client() as c:
        h.live(c)
        assert h.sha((d.PAIR / 'policy.bas').read_bytes()) == d.SOURCE
        assert h.read(d.OUT / 'preflight.json')['ready']
        for stage in ('healthy-field', 'middle-field'):
            assert h.read(h.STUDY / stage / 'result.json')['research_improved']
        versions = {d.PLAYERS['aaron']: h.read(h.STUDY / 'uploads/practiced/uploaded-version.json'),
                    d.PLAYERS['coach']: h.read(d.OUT / 'coach/uploaded-version.json')}
        current = d.champions(c)
        assert all(current[p]['policy_version']['id'] in {d.PRIOR[label], versions[p]['id']} for label, p in d.PLAYERS.items())
        schema = h.get(c, '/openapi.json')
        h.freeze(d.OUT / 'auto-selection-decision.json', {
            'authorization_verbatim_prior_turns': d.AUTH, 'source_sha256': d.SOURCE,
            'evidence': 'Same verified pair and 320-game comparison in decision.json',
            'reason': 'Manual selection returned HTTP500 twice; readback showed no switch. Use documented automatic champion selection during normal league placement.',
            'reconciliation': 'Coach has no submitted membership yet. Retire only the exact unselected Aaron research membership before resubmitting that version with auto_champion=always.',
            'scope': 'Only the same two owned players and exact tested bytes; no server/configuration or policy change.'})
        for label in ('coach', 'aaron'):
            auto(c, label, versions[d.PLAYERS[label]], schema)
        final = d.champions(c)
        assert all(final[p]['policy_version']['id'] == versions[p]['id'] for p in versions)
        h.write(d.OUT / 'deployment-verified.json', {'at': h.research.now(), 'league': d.LEAGUE,
                'players': final, 'versions': versions, 'source_sha256': d.SOURCE,
                'state': 'both_competing_active_champions', 'scope': d.NOTE,
                'selection_route': 'Documented auto_champion=always; manual endpoint HTTP500 preserved and reconciled.'})
        h.write(d.OUT / 'rollback-route-status.json', {
            'prior_memberships': h.read(d.OUT / 'rollback.json'),
            'manual_route': 'Champion endpoint returned500 for new membership during this deployment; do not assume immediate manual rollback until service recovery.',
            'alternative': 'A newly registered copy of the prior executable can use automatic selection if needed, after retrieving it and verifying the saved content hash. No rollback was triggered.'})
        d.log_once('## Current-release deployment verified 2026-09-22',
                   '- Both Aaron and Coach active, competing champions with exact BASIC `' + d.SOURCE + '`. Validation: submitted.\n'
                   '- Manual selection returned HTTP500 twice; readback confirmed unchanged old champion. The documented automatic selection route succeeded. Only the unselected failed-attempt membership was retired; receipts preserved.\n'
                   '- Receipt: `tmp/gota-targets-20260922/deployment/deployment-verified.json`.')
        print('Both policies deployed and verified through automatic selection.', flush=True)


if __name__ == '__main__':
    main()

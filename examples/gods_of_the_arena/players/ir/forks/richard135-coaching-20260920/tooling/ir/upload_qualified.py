"""Upload a locally qualified campaign candidate as an inert BASIC version.

Use Metta's virtualenv. Does not submit to the league or select a champion.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path

import httpx

from hosted_wave import client, get
from policy_ir import HERE, compile_policy, digest, extract, read, write

PLAYER = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    parser.add_argument('--name', default='aaron-gota-ir-waveguard-r4')
    parser.add_argument('--requested-xp', action='store_true',
                        help='Use a recorded explicit user request for exploratory XP after failed local qualification')
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    confirmation = read(campaign / 'confirmation-result.json')
    if args.requested_xp:
        authorization = read(campaign / 'xp-authorization.json')
        if not authorization.get('explicit_user_requested_xp'):
            raise ValueError('Explicit XP request record missing')
    if not confirmation['passed'] and not args.requested_xp:
        raise ValueError('Local confirmation failed; candidate is not qualified for this upload')
    local_status = 'Local confirmation passed' if confirmation['passed'] else 'Local win qualification failed; user-requested exploratory XP'
    name = confirmation['candidate']
    plan = read(campaign / 'plan.json')
    frozen = campaign / 'candidates' / name
    evaluated = campaign / 'confirmation-feedback' / name
    policy = read(evaluated / 'policy.ir.json')
    source = (frozen / 'policy.bas').read_bytes()
    source_hash = digest(source)
    if (source_hash != plan['inputs'][plan['sources'][name]] or
            compile_policy(policy).encode() != source or extract(source.decode(), policy) != policy):
        raise ValueError('Candidate IR, BASIC or frozen source hash disagrees')
    out = campaign / 'upload'
    out.mkdir(exist_ok=True)
    metadata = {'name': args.name, 'content_hash': source_hash, 'size_bytes': len(source),
                'player_id': PLAYER, 'attributes': {}, 'tags': {
                    'game': 'gods_of_the_arena', 'game_version': plan['game_version'],
                    'source_commit': plan['source'], 'semantic_ir_sha256': digest(policy),
                    'change': name + ': replay-grounded IR campaign',
                    'evaluation': local_status + '; hosted unvalidated; no league selection'}}
    request = out / 'upload-request.json'
    if request.exists() and read(request) != metadata:
        raise ValueError('Frozen upload metadata changed')
    write(request, metadata)
    receipt = out / 'uploaded-version.json'
    with client() as c:
        if not receipt.exists():
            response = c.post('/stats/policies/files/upload', json=metadata)
            response.raise_for_status()
            upload = response.json()
            version = upload.get('existing_policy_version')
            if version is None:
                # A separate client keeps Observatory credentials off the storage request.
                response = httpx.put(upload['upload_url'], content=source,
                                     headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                response.raise_for_status()
                response = c.post('/stats/policies/files/complete', json=metadata)
                response.raise_for_status()
                version = response.json()
            write(receipt, version)
        version = read(receipt)
        # Record immediately, including recovery after an interrupted completed upload.
        log = HERE / 'VERSION_LOG.md'
        text = log.read_text()
        if version['id'] not in text:
            text += (f"\n## {version['name']}:v{version['version']}\n\n"
                     f"- Immutable ID: `{version['id']}`. Recorded UTC: {datetime.now(timezone.utc).isoformat()}.\n"
                     f"- Change: {name}; stable-destination post-hit retreat with separation feedback and ranged starting damage.\n"
                     f"- Runtime: BASIC on {plan['game_version']}, source `{plan['source']}`; SHA256 `{source_hash}`.\n"
                     f'- Validation: **hosted unvalidated**. {local_status}; upload is inert.\n'
                     f"- Evidence and receipts: `{campaign.relative_to(HERE.parents[3])}/`.\n")
            log.write_text(text)
        readback = get(c, '/stats/policy-versions/' + version['id'])
        write(out / 'uploaded-version-readback.json', readback)
        owned = get(c, '/v2/policy-versions?mine=true&limit=100&q=' + args.name)
        write(out / 'owned-versions-readback.json', owned)
        entries = owned if isinstance(owned, list) else owned.get('entries', owned.get('policy_versions', []))
        matches = [entry for entry in entries if entry.get('policy_version_id', entry.get('id')) == version['id']]
        if len(matches) != 1 or matches[0].get('player_id') != PLAYER:
            raise ValueError('Uploaded version ownership/player binding did not verify')
    print(f"Uploaded {version['name']}:v{version['version']} ({version['id']}); hosted unvalidated; no league change")


if __name__ == '__main__':
    main()

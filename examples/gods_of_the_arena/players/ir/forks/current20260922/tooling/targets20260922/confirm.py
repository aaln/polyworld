"""Confirm the practiced revision after completing baseline discovery."""
from datetime import datetime, timezone
from pathlib import Path
import jsonschema
import httpx
import panel

h = panel.h


def prepare():
    baseline = h.read(h.STUDY / 'baseline/result.json')
    assert baseline['complete']
    assert not baseline['fort_passed'] and not baseline['score_passed']
    local = h.read(h.STUDY / 'practiced-local-result.json')['rows']
    assert len(local) == 4 and all(r['valid'] and r['runtime_margin'] for r in local)
    assert sum(r['own_score'] for r in local) > sum(r['opponent_score'] for r in local)
    assert h.read(h.STUDY / 'practiced-scenarios-r2.json')['passed']
    source = h.STUDY / 'candidates/practiced/policy.bas'
    data = source.read_bytes()
    manifest = h.read(source.parent / 'manifest.json')
    assert h.sha(data) == manifest['source_sha256']
    # A new hypothesis, not a continuation with a reset budget: baseline
    # discovery is closed; actual-tick drills falsified same-tick recovery.
    h.CYCLE = 'interactive-microplay-r2-20260922'
    h.freeze(h.STUDY / 'confirmation-rationale.json', {
        'cycle': h.CYCLE,
        'prior_cycle': 'interactive-targets-20260922-01',
        'prior_games': 240,
        'hypothesis': 'One physics tick of post-hit movement, XP positioning before navigation throttles, power purchases and defensive portals improve current target matches.',
        'source_sha256': h.sha(data),
        'games': 240,
        'budget': 'Shared journal, normal 400/cycle and 1600/UTC day; no limit changes.',
        'rule': 'Same six target/color cells and gates as discovery; compare all results, retain only evidence-bounded improvements. No promotion.'})
    out = h.STUDY / 'uploads/practiced'
    meta = {
        'name': 'aaron-gota-micro0922', 'content_hash': h.sha(data),
        'size_bytes': len(data), 'player_id': h.PLAYER, 'attributes': {},
        'tags': {'game': 'gods_of_the_arena', 'game_version': h.VERSION,
                 'engine_commit': h.COMMIT,
                 'validation': 'Native admitted; hosted target qualification unvalidated'}}
    h.freeze(out / 'upload-request.json', meta)
    jsonschema.validate(meta, h.read(panel.PREVIOUS / 'openapi.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    with h.client() as c:
        h.live(c)
        assert h.read(h.CAMPAIGN / 'service.json')['state'] == 'paused'
        receipt = out / 'uploaded-version.json'
        if not receipt.exists():
            r = c.post('/stats/policies/files/upload', json=meta)
            if r.status_code == 409:
                r = c.post('/stats/policies/files/complete', json=meta)
                r.raise_for_status()
                version = r.json()
            else:
                r.raise_for_status()
                payload = r.json()
                version = payload.get('existing_policy_version')
                if version is None:
                    r = httpx.put(payload['upload_url'], content=data,
                                  headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                    r.raise_for_status()
                    r = c.post('/stats/policies/files/complete', json=meta)
                    r.raise_for_status()
                    version = r.json()
            h.write(receipt, version)
        version = h.read(receipt)
        log = h.ROOT / 'games/gods_of_the_arena/players/micro20260922/VERSION_LOG.md'
        text = log.read_text() if log.exists() else '# Microplay versions\n'
        if version['id'] not in text:
            log.parent.mkdir(parents=True, exist_ok=True)
            text += f"\n## {meta['name']}:v{version['version']}\n\n"
            text += f"- Version `{version['id']}`; registered {datetime.now(timezone.utc).isoformat()}.\n"
            text += f"- BASIC SHA256 `{meta['content_hash']}`; game {h.VERSION}, engine `{h.COMMIT}`.\n"
            text += '- Coordinated user-requested microplay: one-tick recovery, feasible last hits, six-tile XP positioning, damage equipment and purposeful portals. Individual contributions are not inferred from full matches.\n'
            text += '- Runtime: uploaded BASIC file, no container/argv. Native practice and responsive match validation completed; hosted quality unvalidated at upload. Inert version, no league selection.\n'
            log.write_text(text)
        assert h.get(c, '/stats/policy-versions/' + version['id'])['name'] == meta['name']
    return panel.prepare('practiced', version['id'], source)


if __name__ == '__main__':
    panel.setup()
    panel.run(prepare())

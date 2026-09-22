"""Check actual episode player-file hashes; stats metadata may have null hashes."""
from concurrent.futures import ThreadPoolExecutor
from panel import h


def main():
    cases = []
    for stage in ('healthy-field', 'middle-field'):
        plan = h.read(h.STUDY / stage / 'plan.json')
        for arm in plan['arms']:
            folder = h.STUDY / stage / arm['name'] / str(arm['side'])
            result = h.read(folder / 'result.json')
            cases.append((stage, arm, folder, result['rows'][0]['episode']))
    old = h.read(h.STUDY / 'compat-metadata/identity.json')
    assert old['same_executable_verified']
    hashes = {'control': old['aaron']['content_hash'],
              'candidate': 'b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098'}
    def check(case):
        stage, arm, folder, episode = case
        with h.client() as c:
            path = folder / 'artifacts' / episode / 'spec.json'
            if not path.exists():
                h.write(path, h.get(c, '/v2/episode-requests/' + episode + '/artifacts/spec'))
            spec = h.read(path)
            entry = spec['players'][arm['own_slots'][0]]
            assert entry['type'] == 'player-file' and entry['content_hash'] == hashes[arm['name']]
            return {'stage': stage, 'label': arm['name'], 'side': arm['side'],
                    'version': arm['version'], 'episode': episode, 'slot': arm['own_slots'][0],
                    'runnable': entry, 'verified': True}
    with ThreadPoolExecutor(3) as pool:
        rows = list(pool.map(check, cases))
    h.write(h.STUDY / 'runnable-proof.json', {'passed': True, 'rows': rows,
             'scope': 'One actual episode runnable per arm; every episode roster UUID is separately audited. Stats null fields are not used as proof.'})
    print('All eight actual arm runnables have the expected source hashes.')


if __name__ == '__main__':
    main()

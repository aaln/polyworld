"""Execute the frozen new-release discovery after local games finish."""
from hosted_wave import client, get
from hosted_queue import run
from policy_ir import read
from prepare_release_xp import prepare
from release_hosted import upload, compare
from release_workspace import RUN, VERSION, SOURCE, verify


if __name__ == '__main__':
    verify()
    prepare()
    with client() as c:
        league = get(c, '/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        game = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
        if game['version'] != VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:
            raise ValueError('Live release changed; new study required')
    upload(RUN)
    selected = read(RUN/'local/screen-result.json')['selected']
    run([RUN/'hosted-discovery'/n for n in ['v2', 'cadence', *selected]])
    compare(RUN)

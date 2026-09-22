"""Read-only field snapshots. Version changes trigger new comparisons, never mid-A/B substitution."""
from pathlib import Path
import json,sys,argparse
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'score20260922'))
import hosted_score as old
h=old.h
LEAGUE='league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
DIVISION='div_a4534073-c5d2-4193-a94a-93d9c5e2e443'

def snapshot(c,out):
    if (out/'snapshot.json').exists():return h.read(out/'snapshot.json')
    game=h.live(c)
    members=h.get(c,'/v2/league-policy-memberships?league_id='+LEAGUE+'&champions_only=true&active_only=true&limit=1000')
    board=h.get(c,'/v2/divisions/'+DIVISION+'/leaderboard')
    h.freeze(out/'game.json',game);h.freeze(out/'memberships.json',members);h.freeze(out/'leaderboard.json',board)
    data={'captured_at':h.research.now(),'game_version':game['version'],'coworld_id':game['id'],
          'champions':{m['player']['id']:{'player':m['player']['name'],'version':m['policy_version']['id'],'policy':m['policy_version']['policy']['name'],'number':m['policy_version']['version']} for m in members},'standings':board}
    h.freeze(out/'snapshot.json',data);return data

def compare(before,after):
    old,new=before['champions'],after['champions']
    return {'game_changed':(before['coworld_id'],before['game_version'])!=(after['coworld_id'],after['game_version']),
            'champion_changes':[{'player_id':p,'before':old.get(p),'after':new.get(p)} for p in sorted(set(old)|set(new)) if old.get(p)!=new.get(p)],
            'action':'Revalidate changed opponents and refreshed mixed rosters. Frozen A/B results retain exact pinned-version scope; do not substitute versions or claim enduring rank.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--before',type=Path);a=p.parse_args()
    with h.client() as c:data=snapshot(c,a.out)
    if a.before:h.freeze(a.out/'changes.json',compare(h.read(a.before),data))
    print(json.dumps({'captured_at':data['captured_at'],'champions':len(data['champions']),'game_version':data['game_version']}))

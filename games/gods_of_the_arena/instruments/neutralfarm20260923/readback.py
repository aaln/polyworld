"""Sanitized current league/game readback; no membership writes."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('neutral_readback_hosted',Path(__file__).with_name('hosted.py'))
run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run)

h,RAW=run.h,run.RAW


def main():
    with h.client() as c:
        league=h.get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        h.write(RAW/'league-after-study.json',league)
        active_coworld=league['game']['coworld_id']
        game=h.get(c,'/v2/coworlds/'+active_coworld)
        source_url=game['manifest']['game']['runnable']['source_url']
        active_commit=source_url.split('/tree/')[1].split('/')[0]
        members=h.get(c,'/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&active_only=true&limit=1000')
        board=h.get(c,'/v2/divisions/div_a4534073-c5d2-4193-a94a-93d9c5e2e443/leaderboard?include_recent_rounds=false')
        champions={m['player']['name']:{'player_id':m['player']['id'],'membership':m['id'],
            'version':m['policy_version']['id'],'label':m['policy_version']['label'],
            'status':m['status'],'substatus':m.get('substatus'),'is_champion':m['is_champion']} for m in members}
        versions=h.read(RAW/'hosted-plan.json')['field']
        changes=[n for n,v in versions.items() if champions.get(n,{}).get('version')!=v['id']]
        d={'at':datetime.now(timezone.utc).isoformat(),'game':{'version':game['version'],'coworld_id':active_coworld,'engine':active_commit},
           'champions':champions,'standings':board,'changed_opponents':changes,'game_changed':active_coworld!=h.GAME,
           'league_writes_in_this_call':False,'no_league_writes':not (RAW/'deployment/result.json').exists()}
        if (RAW/'deployment/result.json').exists():d['publication_receipt']='deployment/result.json'
        h.write(RAW/'league-readback.json',d)
        h.write(RAW/'game-after-study.json',game)
        print({'at':d['at'],'changed_opponents':changes,'incumbents':{n:champions[n] for n in ['Aaron',"Aaron's Co-play Coach"]}})


if __name__=='__main__':main()

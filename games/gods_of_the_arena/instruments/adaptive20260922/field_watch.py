"""Read-only research priorities from fresh standings and exact champion changes."""
import argparse,json
from pathlib import Path
import field
h=field.h
OWN={'ply_630a768f-d623-44b2-80fa-36968d6fa75a','ply_594ec24d-d7f3-4370-a000-468354ec41c9'}

def priorities(before,after):
    changes=field.compare(before,after)
    previous={r['player_id']:r for r in before['standings']}
    ours=next(r for r in after['standings'] if r['player_id']=='ply_630a768f-d623-44b2-80fa-36968d6fa75a')
    queue=[]
    standings={r['player_id']:r for r in after['standings']}
    for player,champion in after['champions'].items():
        if player not in standings:
            standings[player]={'player_id':player,'player_name':champion['player'],'rank':None,'score':None,'rounds_played':0}
    for row in standings.values():
        player=row['player_id']
        if player in OWN:continue
        champion=after['champions'].get(player)
        if not champion:continue
        old=before['champions'].get(player)
        same=not changes['game_changed'] and old and old['version']==champion['version'] and player in previous and row['score'] is not None
        queue.append({'player_id':player,'player':row['player_name'],'rank':row['rank'],'score':row['score'],'rounds_played':row['rounds_played'],'champion':champion,'new_or_changed_champion':old is None or old['version']!=champion['version'],'our_mean_score_minus_rival':ours['score']-row['score'] if row['score'] is not None else None,'same_version_score_change':row['score']-previous[player]['score'] if same else None,'next_action':'Freeze new exact-version comparison and infer a new current-engine model.' if changes['game_changed'] or not same else 'Use fresh controls for any new candidate; old mixed-roster results retain their original scope.'})
    queue.sort(key=lambda r:(not r['new_or_changed_champion'],-(r['score'] or 0),r['player_id']))
    return {'captured_at':after['captured_at'],'comparison_from':before['captured_at'],'field_changes':changes,'priorities':queue,'scope':'Research queue, not a controller feature or forecast. Changed champions first, then current score. Score changes are descriptive cumulative standings, not causal effects or guaranteed trends. No automatic spending, deployment or opponent-source access.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    assert not (a.out/'snapshot.json').exists(),'Use a new output directory for a fresh check.'
    with h.client() as c:after=field.snapshot(c,a.out)
    report=priorities(h.read(a.before),after);h.freeze(a.out/'research-priorities.json',report)
    print(json.dumps({'captured_at':report['captured_at'],'field_changed':report['field_changes']['game_changed'] or bool(report['field_changes']['champion_changes']),'top_priorities':[{k:r[k] for k in ['player','rank','score','new_or_changed_champion']} for r in report['priorities'][:5]]}))

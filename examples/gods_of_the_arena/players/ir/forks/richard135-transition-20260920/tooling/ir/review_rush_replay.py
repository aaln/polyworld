"""Summarize movement, shared visibility, and structure losses from decoded tapes.

Usage: python review_rush_replay.py replay.jsonl --own-team 1 --output review.json
Frame observations are post-tick and sampled; they are not VM decision logs.
"""
import argparse
import json
from pathlib import Path
from policy_ir import write, digest


def review(path, own_team):
    frames, summary, header = [], None, None
    with path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['type'] == 'header': header = row
            elif row['type'] == 'frame': frames.append(row)
            elif row['type'] == 'summary': summary = row
    if not header or not summary or summary['hash_mismatches']:
        raise ValueError('Require a complete source-matched decoded replay')
    timeline, losses, first_group = [], {}, None
    for frame in frames:
        allies = [h for h in frame['heroes'] if h['team'] == own_team]
        enemies = [h for h in frame['heroes'] if h['team'] != own_team]
        visible = [o for o in allies[0]['visible_post_tick'] if o['team'] != own_team and o['kind'] == 2 and o['hp'] > 0]
        if len(visible) >= 4 and first_group is None:
            first_group = frame['tick']
        for b in frame['buildings']:
            if b['hp'] <= 0 and str(b['id']) not in losses:
                losses[str(b['id'])] = {'team':b['team'], 'kind':b['kind'], 'lane':b['lane'],
                                       'first_sampled_nonpositive_seconds':frame['tick']/24}
        if frame['tick']%480 == 0 or frame is frames[-1]:
            position = lambda h: {'slot':h['slot'], 'position':h['position'], 'hp':h['hp'], 'target':h['target']}
            timeline.append({'seconds':frame['tick']/24, 'own':[position(h) for h in allies],
                             'enemy':[position(h) for h in enemies], 'visible_enemy_heroes':len(visible)})
    return {'source':header['source'], 'version':header['version'], 'input_sha256':digest(path.read_bytes()),
            'own_team':own_team, 'summary':summary, 'timeline':timeline, 'structure_losses':losses,
            'first_sampled_four_visible_enemy_heroes_tick':first_group,
            'interpretation':'Positions and visible lists are post-tick samples every120ticks. First sampled '
                             'visibility and structure losses are upper bounds. Visibility alone does not '
                             'prove policy reaction or clustering; examine positions and actual commands.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('--own-team', type=int, choices=[0,1], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = review(args.replay,args.own_team)
    write(args.output,result)
    print(result['summary'])

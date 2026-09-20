"""Freeze two exact-version observer studies from already downloaded league metadata."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from guide import freeze_guide

ROOT = Path(__file__).resolve().parents[4]
PAIR = ROOT / 'tmp/gota-ir/opponent-pair-20260920'
OWN = {'4cdbbf36-3d70-4ea3-8aed-c92ee0e024be', '00cd9483-0309-4613-bf61-89f3f4a33d01'}
TARGETS = {'richard-v135': ('Richard135', '7c370daf-3c5f-42f8-870b-54b79c495a44', 'richard-gods-of-the-arena:v135'),
           'alex-g002-v1': ('AlexG002v1', 'a30542cb-54de-4109-92e6-bcabca7db4d8', 'gota-g002:v1')}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')

def main():
    rows = []
    for group in json.loads((PAIR/'round-episodes.json').read_text()):
        for ep in group['episodes']:
            vv = ep['policy_version_ids']
            if ep['status'] != 'completed' or ep['coworld_version'] != '2026.9.16.5' or len(vv) != 10:
                continue
            for slot in (0,5):
                other = 5-slot
                if vv[slot] in OWN and vv[other] not in OWN and len(set(vv[slot:slot+5])) == len(set(vv[other:other+5])) == 1:
                    rows.append({'episode': ep, 'observer_slot': slot})
    rows.sort(key=lambda r: (r['episode']['created_at'], r['episode']['id']))
    assert len({(r['episode']['id'],r['observer_slot']) for r in rows}) == len(rows)
    excluded = OWN | {r[1] for r in TARGETS.values()}
    for slug, (prefix, version, label) in TARGETS.items():
        dest = ROOT/'tmp/gota-ir'/('opponent-'+slug+'-20260920')
        if (dest/'study-plan.json').exists():
            print(slug,'already frozen');continue
        targets = [r for r in rows if r['episode']['policy_version_ids'][5-r['observer_slot']] == version][-20:]
        assert len(targets) == 20
        heldout = targets[-4:]
        cutoff = heldout[0]['episode']['created_at']
        population = {}
        for r in rows:
            ep = r['episode'];side = r['observer_slot'];rival = ep['policy_version_ids'][5-side]
            if rival not in excluded and ep['created_at'] < cutoff:
                population.setdefault((rival,side),r)
        # Bound decoding cost without outcome selection: first eight chronological
        # opponent versions, one earliest episode per available observer side.
        versions = list(dict.fromkeys(k[0] for k in population))[:8]
        prior = [r for (v,_),r in population.items() if v in versions]
        planrows=[]
        for split, entries in [('train',targets[:-4]),('heldout',heldout),('population',prior)]:
            for r in entries:
                ep=r['episode'];op=next(p for p in ep['participants'] if p['position']==5-r['observer_slot'])
                planrows.append({'id':ep['id'],'created_at':ep['created_at'],'observer_slot':r['observer_slot'],
                    'split':split,'opponent_version':op['policy_version_id'],'opponent_label':op['policy_name']+':v'+str(op['version']),
                    'opponent_player_id':op['player_id'],'opponent_player_name':op['player_name'],
                    'own_version':ep['policy_version_ids'][r['observer_slot']],'version':ep['coworld_version']})
        parent=ROOT/'examples/gods_of_the_arena/players/ir/forks/jordan268'
        plan={'schema':'gota-opponent-study/1','frozen_at':datetime.now(timezone.utc).isoformat(),
            'target_version':version,'target_label':label,'target_slug':slug,'preference_prefix':prefix+'_I',
            'selection':'Most recent20 completed exact-target-vs-current-own-executable episodes in the frozen latest60round metadata. Outcome ignored. Own players have byte-identical primary IR source.',
            'holdout':'Chronologically last4/20 target episodes; no target heldout behavior decoded before model freeze. The prior analysis of other Richard episodes is disclosed and excluded from this selection when not recent enough.',
            'population_selection':'Earliest eligible episode per non-target/non-own opponent-version and observer side, first8versions chronologically, before heldout cutoff; both target versions excluded.',
            'observation':'One actual hero policy instance, slot0or5; exact predecision host-visible objects; opponent commands excluded from features; no teammate sensor pooling.',
            'validation':'Primary seven-layer Python layout; lagged features at sustained motif starts. n<8 or no heldout lift against population -> provisional; no tested proxy or automatic counterstrategy adoption.',
            'our_policy':{'directory':str(parent),'id':json.loads((parent/'policy.ir.json').read_text())['id'],
                'basic_sha256':hashlib.sha256((parent/'policy.bas').read_bytes()).hexdigest(),
                'ir_file_sha256':hashlib.sha256((parent/'policy.ir.json').read_bytes()).hexdigest(),'versions':sorted(OWN)},
            'selection_metadata_sha256':hashlib.sha256((PAIR/'round-episodes.json').read_bytes()).hexdigest(),
            'episodes':planrows}
        plan['guide'] = freeze_guide(dest)
        write(dest/'study-plan.json',plan)
        write(dest/'eligible.json',{'target':targets,'population':prior})
        for name in ['policy.bas','policy.ir.json']:
            shutil.copy2(parent/name,dest/('observer-'+name))
        probe=ROOT/'tmp/gota-ir/opponent-jordan-v268-20260919/observer-probe'
        shutil.copy2(probe,dest/'observer-probe')
        write(dest/'probe-provenance.json',{'binary':str(probe),'sha256':hashlib.sha256(probe.read_bytes()).hexdigest(),
            'source':str(Path(__file__).with_name('replay_observer.nim')),
            'source_sha256':hashlib.sha256(Path(__file__).with_name('replay_observer.nim').read_bytes()).hexdigest(),
            'commit':'f2ab9598d8f8001b6beae3e66404e341770c803f','version':'2026.9.16.5'})
        print(slug,'target20 prior',len(prior),'split_sides',dict(Counter((r['split'],r['observer_slot']) for r in planrows)),
              'owner',targets[0]['episode']['participants'][5-targets[0]['observer_slot']]['player_name'],flush=True)

if __name__=='__main__':main()

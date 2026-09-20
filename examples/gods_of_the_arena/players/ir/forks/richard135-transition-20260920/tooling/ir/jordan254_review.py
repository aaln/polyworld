"""Select full cohort representatives, reconstruct actual positions and owned decisions."""
from concurrent.futures import ThreadPoolExecutor
import json
import sys

from jordan254_research import STUDY, PARENT
from league_threat_review import run_native
from policy_ir import read,write
from ranger_guard_hosted import freeze
from win_replay_review import plot

ROOT=STUDY/'baseline-review'
COHORT=STUDY/'baseline-result.json'
ARTIFACTS=STUDY/'baseline/jordan254'
ARM='candidate'


def folder(case):
    return ARTIFACTS/ARM/case['color']/'artifacts'/case['episode']


def prepare():
    ROOT.mkdir(exist_ok=True)
    result=read(COHORT);cases=[]
    for color in ('red','blue'):
        rows=result['arms']['jordan254/'+ARM+'/'+color]['rows']
        for outcome in ('win','loss'):
            subset=sorted((r for r in rows if r[outcome]),key=lambda r:(r['ticks'],r['episode']))
            if subset:
                chosen=subset[len(subset)//2]
                cases.append(chosen|{'color':color,'name':color+' '+outcome})
                if outcome=='loss':
                    alternate=[r for r in subset if r['ticks']!=chosen['ticks']]
                    if alternate:cases.append(alternate[len(alternate)//2]|{'color':color,'name':color+' alternate loss'})
    freeze(ROOT/'selection.json',{'method':'Median duration win/loss by color, plus median among remaining different-duration losses, selected before reconstruction.','cases':cases})
    def one(case):
        f=folder(case)
        proof=run_native('macro-replay-v5',f/'replay.bin',f/'decoded.jsonl')
        assert proof['hash_mismatches']==0
        items=[json.loads(l) for l in (f/'decoded.jsonl').open()]
        return {'name':case['name'],'row':case,'header':next(x for x in items if x['type']=='header'),
                'frames':[x for x in items if x['type']=='frame']}
    with ThreadPoolExecutor(3) as pool:views=list(pool.map(one,cases))
    plot(views,ROOT/'positions.png','Jordan254: '+ARM+' replay positions',
         'Our slots0–4 on red,5–9 on blue. Actual native reconstruction; standing structures are squares.')
    print(ROOT/'positions.png',flush=True)


def decisions():
    def one(case):
        f=folder(case);slots=range(5) if case['color']=='red' else range(5,10)
        proof=run_native('replay-middle-rush-probe',f/'replay.bin',f/'decisions.jsonl',
                        {'PROBE_POLICY':str(PARENT/'policy.bas'),'PROBE_SLOTS':','.join(map(str,slots)),'PROBE_SAMPLE_EVERY':'1'})
        assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
        first={};counts={}
        for line in (f/'decisions.jsonl').open():
            r=json.loads(line)
            if r['type']!='decision':continue
            m=r['memory'];s=r['slot'];c=counts.setdefault(s,{'decisions':0,'defense':0,'idle_defense':0})
            c['decisions']+=1;c['defense']+=bool(m['defActive']);c['idle_defense']+=bool(m['defActive'] and not m['bestId'])
            if m['defActive'] and s not in first:first[s]={'tick':r['tick'],'memory':m}
        return case|{'proof':proof,'first_recalls':first,'counts':counts}
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(one,read(ROOT/'selection.json')['cases']))
    write(ROOT/'decisions.json',{'cases':rows})
    print([{ 'case':r['name'],'first':{k:v['tick'] for k,v in r['first_recalls'].items()},'counts':r['counts']} for r in rows],flush=True)


if __name__=='__main__':
    if len(sys.argv)>2:
        ARM=sys.argv[2]
        assert ARM in ('warning100','reach14')
        ROOT=STUDY/'warning-followup/hosted'/ARM/'review'
        COHORT=STUDY/'warning-followup/hosted-result.json'
        ARTIFACTS=STUDY/'warning-followup/batches/jordan254'
        PARENT=STUDY/'outer-warning/local/candidates'/ARM
    prepare() if sys.argv[1]=='prepare' else decisions()

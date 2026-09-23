"""Audit exact relh169 source and existing200-game cohort; creates no hosted jobs."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import hashlib,json,os,re,statistics,subprocess

ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT.parent/'polyworld/tmp/gota-relh169-audit-20260923'
OUT=ROOT/'docs/opponents/relh-v169/source-audit-20260923'
SOURCE=OUT/'source/relh-v169.bas'
OLD=RAW.parent/'gota-manual-score20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
CLASSES=['VanguardKnight','Ranger','Arcanist','DruidWarden','DemonHunter','DeathKnight','Crossbowman','Lich','Warlock','Berserker']
ROLES=[0,1,2,3,4,0,1,2,3,4]

def draft_weights():
    source=SOURCE.read_text();head=source[:source.index('if drafting then')]
    weights=[[0]*10 for _ in range(33)]
    def fixed(s):return int((abs(Decimal(s))*65536).to_integral_value(rounding=ROUND_HALF_UP))*(-1 if Decimal(s)<0 else 1)
    for cls,block in re.findall(r'if draftF\((\d+)\) then\n(.*?)  end if',head,re.S):
        cls=int(cls);bias=re.search(r'draftScore = ([-\d.]+)',block)[1];weights[32][cls]=fixed(bias)
        for feature,value in re.findall(r'draftScore = draftScore \+ draftF\((\d+)\) \* ([-\d.]+)',block):weights[int(feature)][cls]=fixed(value)
    assert len(re.findall(r'if draftF\(\d+\) then',head))==10
    return weights

def predict(row,weights):
    features=[int(x)*65536 for x in row['legal']]+[0]*22
    allies=enemies=0
    for pick in row['picks']:
        if pick['class']<0:continue
        allied=pick['team']==row['team'];features[(10 if allied else 20)+pick['class']]=65536
        allies+=allied;enemies+=not allied
    features[30]=(allies*65536+2)//5;features[31]=(enemies*65536+2)//5
    scores=[weights[32][c]+sum((features[f]*weights[f][c]+32768)//65536 for f in range(32)) for c in range(10)]
    choice=max((c for c in range(10) if row['legal'][c]),key=lambda c:scores[c])
    # Exact deployed draft heuristic, independently checked against its200actual picks.
    priors=[100,180,170,140,100,130,460,150,120,100]
    ours=max((c for c in range(10) if row['legal'][c]),key=lambda c:priors[c]-25*sum(p['class']>=0 and p['team']==row['team'] and ROLES[p['class']]==ROLES[c] for p in row['picks']))
    return {'relh_choice':choice,'our_choice':ours,'scores_q16':scores,'features_q16':features}

def instrument(case,kind):
    f=Path(case['folder']);dst=RAW/'episodes'/case['episode']/(kind+'.json')
    assert sha(f/'replay.bin')==case['replay_sha256']
    if not dst.exists():
        env=dict(os.environ,AUDIT_SLOTS=str(case['slot']),AUDIT_POLICY=str(SOURCE),AUDIT_KIND='relh')
        p=subprocess.run([str(RAW/kind),'--replay',str(f/'replay.bin')],env=env,capture_output=True,text=True,timeout=900)
        dst.parent.mkdir(parents=True,exist_ok=True);dst.with_suffix('.stderr').write_text(p.stderr)
        if p.returncode:(dst.parent/(kind+'-failed.stdout')).write_text(p.stdout)
        assert p.returncode==0,(case['episode'],kind,p.stderr[-1800:],p.stdout[-1800:])
        write(dst,json.loads(p.stdout.splitlines()[-1]))
    d=read(dst)
    assert d['all_state_hashes_equal'] and d['all_actions_consumed'] if kind=='source_probe' else d['prefix_hashes_equal']
    if kind=='source_probe':print(json.dumps({'episode':case['episode'],'source_commands_matched':d['commands_matched']}),flush=True)
    return d

def aggregate(rows):
    counts=sorted({k for r in rows for k in r['counts']})
    nonzero=[r['score'] for r in rows if r['score']>0]
    return {'n':len(rows),'score':statistics.mean(r['score'] for r in rows),'nonzero_mean':statistics.mean(nonzero) if nonzero else 0,'nonzero_rate':len(nonzero)/len(rows),'productive_rate':sum(r['score']>=500 for r in rows)/len(rows),'means':{k:statistics.mean(r['counts'].get(k,0) for r in rows) for k in counts},'classes':dict(Counter(r['class'] for r in rows))}

def main():
    plan=read(RAW/'plan.json');weights=draft_weights()
    write(OUT/'draft-controller.json',{'source_sha256':sha(SOURCE),'features':'10legal flags,10allied class flags,10enemy class flags,allied/enemy picked counts divided by5; all public.','q16_weights':weights,'arithmetic':'Exact decimal literal rounding, Q16.16 nearest-product rounding and first strict maximum. No float approximation or retraining.','origin':'Imitation head trained for replay58; current-engine behavior tested separately.'})
    jobs=[(r,'source_probe') for r in plan['source_reconstruction']]+[(r,'drafts') for r in plan['cases']]
    with ThreadPoolExecutor(3) as pool:list(pool.map(lambda job:instrument(*job),jobs))
    rows=[];drafts=[]
    for case in plan['cases']:
        f=Path(case['folder']);econ=read(f/'economy.json');results=read(f/'results.json');resources=read(OLD/'episodes'/case['episode']/'audit.json');episode=read(f/'episode.json');spec=read(f/'spec.json')
        assert sha(f/'spec.json')==case['spec_sha256']
        assert spec['players'][case['our_slot']]['content_hash']=='29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36'
        assert resources['hash_mismatches']==0 and resources['all_actions_consumed']
        assert len(read(f/'player-status.json')['players'])==10 and all(x['exit_code']==0 for x in read(f/'player-status.json')['players'])
        for label,slot in [('relh169',case['slot']),('ours',case['our_slot'])]:
            h=resources['heroes'][slot];e=econ['heroes'][slot]
            assert h['xp']==e['total_xp'] and results['scores'][slot]==max(0,h['xp']*1440-200*resources['ticks'])//1440
            assert sum(e['xp_sources'].values())==h['xp']
            if label=='relh169':assert spec['players'][slot]['content_hash']==sha(SOURCE)
            row={'label':label,'episode':case['episode'],'context':case['context'],'slot':slot,'class':h['class'],'score':results['scores'][slot],'xp':h['xp'],'minutes':resources['ticks']/1440,'deaths':h['deaths'],'gold_end':h['gold_end'],'counts':dict(h['counts']), 'xp_sources':e['xp_sources']}
            for k,v in e['xp_sources'].items():row['counts']['xp_'+k]=v
            row['counts']['deaths']=h['deaths'];row['counts']['minutes']=resources['ticks']/1440
            rows.append(row)
        raw=read(RAW/'episodes'/case['episode']/'drafts.json')['rows']
        for label,slot in [('relh169',case['slot']),('ours',case['our_slot'])]:
            ds=[r for r in raw if r['slot']==slot];assert len(ds)==1
            r=ds[0];prediction=predict(r,weights)
            assert prediction['relh_choice' if label=='relh169' else 'our_choice']==r['choice'],(case['episode'],label,r,prediction)
            drafts.append({'label':label,'episode':case['episode'],'context':case['context'],**r,**prediction})
    summaries={label:{'overall':aggregate([r for r in rows if r['label']==label]),'contexts':{c:aggregate([r for r in rows if r['label']==label and r['context']==c]) for c in sorted({r['context'] for r in rows})},'by_class':{c:aggregate([r for r in rows if r['label']==label and r['class']==c]) for c in sorted({r['class'] for r in rows if r['label']==label})}} for label in ['relh169','ours']}
    probes=[{'episode':r['episode'],'context':r['context'],'slot':r['slot'],**read(RAW/'episodes'/r['episode']/'source_probe.json')} for r in plan['source_reconstruction']]
    counts=Counter()
    for p in probes:counts.update(p['counts'])
    comparison=Counter((CLASSES[r['choice']],CLASSES[r['relh_choice']]) for r in drafts if r['label']=='ours')
    result={'complete':True,'games':200,'rows':rows,'summary':summaries,'drafts':drafts,'own_draft_hypothetical_transitions':[{'ours':a,'relh_head':b,'n':n} for (a,b),n in sorted(comparison.items())],'source_probe':{'episodes':len(probes),'commands_matched':sum(r['commands_matched'] for r in probes),'decisions':sum(r['decisions'] for r in probes),'max_instructions':max(r['max_instructions'] for r in probes),'max_work':max(r['max_work'] for r in probes),'counts':dict(counts),'rows':probes},'new_hosted_games':0,'scope':plan['limitations']}
    write(RAW/'analysis.json',result);write(OUT/'evidence/analysis.json',result)
    print(json.dumps({'relh':{k:v for k,v in summaries['relh169']['overall'].items() if k!='means'},'our_draft_hypothetical_transitions':result['own_draft_hypothetical_transitions'],'source_commands':result['source_probe']['commands_matched']}))

if __name__=='__main__':main()

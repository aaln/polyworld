"""Publish current-engine retrospective economy, keeping source ordering unidentified."""
from pathlib import Path
from collections import Counter
import json,hashlib,statistics,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-adaptive-score-20260922';OLD=STUDY.with_name('gota-score-20260922')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    plan=read(OLD/'hosted/plan.json');expected={r['version']:r['source_sha256'] for r in read(OLD/'preflight.json')['rows']}
    for arm in plan['arms']:
        if arm['name']!='baseline':continue
        cell=read(OLD/'hosted/baseline'/str(arm['side'])/'result.json');assert len(cell['rows'])==40
        for row in cell['rows']:
            assert row['valid'] and row['all_hashes_equal']
            p=OLD/'hosted/baseline'/str(arm['side'])/'artifacts'/row['episode'];spec=read(p/'spec.json')
            for i,v in enumerate(arm['roster']):assert spec['players'][i]['content_hash']==expected[v]
            audit=read(p/'audit.json');eco=read(p/'economy.json')
            assert audit['hash_mismatches']==eco['hash_mismatches']==0
            for i,h in enumerate(audit['heroes']):
                assert h['xp']==eco['heroes'][i]['total_xp']
                assert max(0,h['xp']*1440-200*audit['ticks'])//1440==row['scores'][i]
    data=read(STUDY/'paired-economy.json');rows=data['rows'];summary=[]
    for name in ['ours','khors114','richard167']:
        for side in [0,1]:
            r=[x for x in rows if x['name']==name and x['side']==side];assert len(r)==40
            fields=['score','minutes','total_xp','hero_kills','creep_last_hits','deaths','level','spells']
            summary.append({'name':name,'own_color':side,'games':40,'classes':dict(Counter(x['class'] for x in r)),'means':{k:statistics.mean(x[k] for x in r) for k in fields},'mean_xp':{k:statistics.mean(x['xp_sources'].get(k,0) for x in r) for k in ['hero','creep','structure_or_other']}})
    detail=[]
    for path in sorted((STUDY/'diagnosis').glob('*/audit.json')):
        d=read(path);assert d['hash_mismatches']==0
        detail.append({'episode':path.parent.name,'sha256':sha(path),'ticks':d['ticks'],'heroes':d['heroes']})
    report={'games':80,'all_ten_vm_source_replay_xp_checks':True,'control_source':expected['b65ccf7b-d7a1-4681-b57f-a55f5ace43c7'],'game_version':'2026.9.22.3','engine_commit':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','summaries':summary,'detailed_selection':read(STUDY/'diagnosis-plan.json'),'detailed':detail,'scope':'All80 prior .3 baseline games, retrospective same-roster diagnostics; not fresh candidate evidence. Detailed first4 lexical UUIDs per subject color selected before fine analysis. Own color is policy-specific; opposing heroes in a game have opposite colors. Full replay truth never enters our live policy.'}
    write(STUDY/'diagnosis-summary.json',report)
    out=ROOT/'docs/opponents/richard-v167/replay-audit-20260922';out.mkdir(parents=True,exist_ok=True)
    write(out/'economy-summary.json',report)
    guide=ROOT/'docs/guides/guide-opponent-model-ir.md'
    identities=[('richard167','richard_v167','e811221e-c419-4f7b-9629-01f8722ab9f7'),('khors114','khors_v114','145c01e0-0cbf-4e1e-8120-11b437175b91')]
    for name,ident,version in identities:
        r=[x for x in rows if x['name']==name]
        model={'schema':'gota-opponent-descriptive-ir/1','id':ident+'_current_score_20260922',
          'situation':{'authority':'Retrospective full replay truth and typed events; no opponent source or private VM memory','game_version':report['game_version'],'engine_commit':report['engine_commit'],'policy_version':version,'source_sha256_from_host_specs':expected[version],'control_source_sha256':report['control_source'],'selection':'All80 exact previous-study clean baseline games. Four lexical episode UUIDs per control color for deeper spell and position diagnosis.','guide_sha256':sha(guide),'episodes':[x['episode'] for x in r]},
          'belief':{'observed':{'classes':dict(Counter(x['class'] for x in r)),'mean_hero_kills':statistics.mean(x['hero_kills'] for x in r),'mean_creep_last_hits':statistics.mean(x['creep_last_hits'] for x in r),'mean_spells':statistics.mean(x['spells'] for x in r),'all_other_vms_clean':True},'claims':[{'id':'CURRENT_ARCHETYPE','status':'observed','claim':'Warlock73/80, Vanguard3, Berserker4; oldv135 Ranger model is not a current class model.' if name=='richard167' else 'Ranger/Crossbow80/80; approximately20 hero kills per game versus our13.4 despite fewer creep last hits and spell releases.'},{'id':'ORDER_UNKNOWN','status':'unidentified','claim':'Draft preference conditional on availability, exact target ordering, cast timing, escape guards and intent cannot be inferred from marginal aggregates.'}]},
          'goal':{'individual_xp':{'status':'hypothesis','purpose':'Accumulate individual score through XP-producing actions; actual internal priority graph unidentified.'}},
          'skill':{'combat':{'observed':'Typed actual damage and XP in economy-summary.json','initiation':'unidentified','termination':'unidentified'},'replenishment':{'observed':'Accepted purchases and portals in detailed audit','priority':'unidentified'}},
          'strategy':[{'id':'COUNTER_SPELL_OPPORTUNITY','when':'Our visible basic target differs from a nearby visible enemy hero; a damaging ability is ready','skill':'independent_public_spell_target','for':['individual_xp'],'status':'counter hypothesis; actual source tested separately','priority_identified_for_opponent':False}],
          'execution':{'binding':'retrospective-descriptive/1','source_available':False,'proxy_usable':False,'forecast_validated':False,'heldout_forecast':None,'boundary':'Use exact hosted responsive policy. No UUID/player name, future commands or hidden replay coordinates enter live control.'},
          'update':{'kind':'New game/version-aware descriptive record; preserve earlier opponent models and failed score study','evidence':['economy-summary.json'],'preserved_raw_root':str(STUDY),'next_discriminator':'Frozen responsive mixed-roster240game screen, followed by conditional independent160game confirmation. Repeat after field/version changes.'}}
        write(out/(ident+'.ir.json'),model)
    print(json.dumps({'games':80,'detail_games':len(detail),'summaries':summary}))
if __name__=='__main__':main()

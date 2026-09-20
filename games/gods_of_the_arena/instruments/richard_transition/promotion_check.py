"""User-authorized fixed-source Alex/Jordan check after Richard selection."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os
from pathlib import Path
import time
from fresh_hit import ROOT,STUDY,INITIAL,NAMES,read,write,digest
from study import CAMPAIGN

DEST=INITIAL/'promotion-check'
spec=importlib.util.spec_from_file_location('transition_promotion_support',ROOT/'games/gods_of_the_arena/instruments/richard_transition/hosted.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
shared=support.shared;r=support.r
CYCLE='interactive-richard-transition-promotion-20260920'


def freeze(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert read(path)==value,str(path)
    else:write(path,value)


def main():
    with r.lock(DEST/'runner.lock',blocking=False):
        authorization=read(DEST/'authorization-and-gate.json')
        while not (STUDY/'hosted-result.json').exists():time.sleep(20)
        completed=read(STUDY/'hosted-result.json');assert completed['complete'] and completed['games']==240
        rows=[]
        for name in NAMES[1:]:
            cells={c:read(STUDY/'hosted'/name/c/'arm-result.json') for c in ('red','blue')}
            assert all(v['all_full_audits_passed'] and v['games']==40 for v in cells.values())
            local=[r for r in read(STUDY/'local-results.json')['rows'] if r['candidate']==name]
            rows.append({'name':name,'red_wins':cells['red']['wins'],'total_wins':sum(v['wins'] for v in cells.values()),
                'total_deaths':sum(row['subject_deaths'] for v in cells.values() for row in v['rows']),
                'local_wins':sum(r['win'] for r in local)})
        rows.sort(key=lambda x:(-x['red_wins'],-x['total_wins'],x['total_deaths'],-x['local_wins'],x['name']))
        chosen=rows[0]['name'];candidate=STUDY/'candidates'/chosen
        version=read(candidate/'uploaded-version.json');source=(candidate/'policy.bas').read_bytes()
        selection={'name':chosen,'version':version,'source_sha256':digest(source),'ranking':rows,
            'authorization_sha256':digest((DEST/'authorization-and-gate.json').read_bytes()),
            'Richard_results_sha256':digest((STUDY/'hosted-result.json').read_bytes()),
            'rule':authorization['selection_rule']}
        freeze(DEST/'selection.json',selection)
        shared.live();config=r.config(CAMPAIGN)
        arms=[]
        for rival_name in ('Alex Smith','Jordan'):
            rival=authorization['targets'][rival_name]['policy_version'];key='alex' if rival_name=='Alex Smith' else 'jordan'
            for color in ('red','blue'):
                slots=list(range(5)) if color=='red' else list(range(5,10))
                roster=[version['id'] if i in slots else rival for i in range(10)]
                directory=DEST/'hosted'/chosen/key/color
                arm={'key':f'{chosen}/{key}/{color}','name':chosen,'kind':'team','policy_version':version['id'],
                    'rival_version':rival,'rival_name':rival_name,'color':color,'own_slots':slots,
                    'roster':roster,'games':40,'directory':str(directory)}
                body={'idempotency_key':'transition-user-promote-'+digest(arm)[:24],
                    'target':config['target'],'game_config_overrides':config['game_config'],'num_episodes':40,
                    'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                    'notes':'Explicit user conditional promotion check of unchanged selected source; '+arm['key']+
                        '. >=30/40 each color against BOTH current Alex and Jordan, all160 complete audits. '
                        'Richard results reported separately; no automatic claim of rank1 or independent seeds.'}
                freeze(directory/'plan.json',arm);freeze(directory/'request.json',body);arms.append(arm)
        freeze(DEST/'plan.json',{'cycle':CYCLE,'games':160,'arms':arms,'selection':selection,'gate':authorization['gate'],
            'config_sha256':digest(config['game_config'])})
        os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(DEST/'owner.json',{'pid':os.getpid(),'started_at':r.now(),'cycle':CYCLE})
        print('SELECTED',chosen,version['id'],flush=True)
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(shared.collect,arms))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(arms,results)]
        passed=all(v['wins']>=30 and v['games']==40 and v['all_full_audits_passed'] for v in results)
        write(DEST/'result.json',{'complete':True,'games':160,'selection':selection,'cells':cells,
            'user_conditional_promotion_gate_passed':passed,'league_changed':False,
            'note':'Original both-color Richard gate is independent and is not relabeled. Requires exact source/owner/current-opponent readbacks before applying authorized promotion.'})
        print('CONDITIONAL GATE',passed,flush=True)


if __name__=='__main__':main()

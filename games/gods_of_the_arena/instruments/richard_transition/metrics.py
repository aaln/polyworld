"""Whole-cohort progression and survival, alongside actual fort outcomes."""
from statistics import mean,median
from pathlib import Path
import re
from fresh_hit import ROOT,STUDY,read,write,digest


def item_specs():
    source=ROOT.parent/'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/content.nim'
    text=source.read_text()
    enums=text.split('  Item* = enum\n',1)[1].split('  ItemKind*',1)[0]
    names=[s.strip().rstrip(',') for s in enums.splitlines() if s.strip()]
    section=text.split('  ItemSpecs*: array[Item, ItemSpec] = [',1)[1].split('proc ',1)[0]
    blocks=re.findall(r'ItemSpec\((.*?)\)',section,re.S)
    assert len(names)==len(blocks)==21
    result={}
    for name,block in zip(names,blocks):
        result[name]={k:int(m[1]) if (m:=re.search(r'\b'+k+r':\s*(\d+)',block)) else 0
            for k in ('cost','damage','maxHp','maxMana')}
        result[name]['equipment']='kind: Equipment' in block
    return result,{'source':str(source),'sha256':digest(source.read_bytes())}


def main():
    specs,provenance=item_specs();cells={}
    files=[Path(a['directory'])/'arm-result.json' for a in read(STUDY/'hosted-plan.json')['arms']]
    for file in files:
        if not file.exists():continue
        value=read(file);assert value['games']==40 and value['all_full_audits_passed']
        name,color=file.parent.parent.name,file.parent.name
        slots=list(range(5)) if color=='red' else list(range(5,10))
        data=[]
        for row in value['rows']:
            audit=read(file.parent/'artifacts'/row['episode']/'audit.json')
            assert audit['hash_mismatches']==0
            heroes=[]
            for h in audit['heroes']:
                equipment=[i for i in h['inventory'] if specs[i]['equipment']]
                heroes.append({'slot':h['slot'],'class':h['class'],'level':h['level'],'xp':h['total_xp'],
                    'deaths':h['deaths'],'alive_ticks':h['alive_ticks'],'basic_hits':h['basic_hits'],
                    'tower_target_ticks':h['tower_target_ticks'],'equipment_items':len(equipment),
                    'equipment_value':sum(specs[i]['cost'] for i in equipment),'equipment':equipment,
                    'equipment_damage':sum(specs[i]['damage'] for i in equipment),
                    'equipment_hp':sum(specs[i]['maxHp'] for i in equipment)})
            data.append({'episode':row['episode'],'ticks':row['ticks'],'heroes':heroes})
        by_slot={}
        for slot in range(10):
            hs=[d['heroes'][slot] for d in data]
            by_slot[str(slot)]={'class':hs[0]['class'],'games':40,
                **{'mean_'+k:mean(h[k] for h in hs) for k in ('level','xp','deaths','basic_hits','tower_target_ticks','equipment_items','equipment_value','equipment_damage','equipment_hp')},
                'deaths_per_alive_minute':sum(h['deaths'] for h in hs)/(sum(h['alive_ticks'] for h in hs)/1440)}
        cells[name+'/'+color]={'fort_outcomes':{k:value[k] for k in ('wins','losses','draws')},
            'median_ticks':median(d['ticks'] for d in data),'own_slots':slots,'by_slot':by_slot,'rows':data,
            'arm_sha256':digest(file.read_bytes())}
    write(STUDY/'progression-metrics.json',{'item_provenance':provenance,'cells':cells,
        'interpretation':'All40valid games per included cell, not selected examples. Descriptive final-game progression differs with duration and deaths; generated seeds are not paired and trajectories correlate. Equipment value is current held shop cost, not net worth or income. These metrics cannot replace fort-win or survival gates.'})
    print('Measured',len(cells),'complete40game cells',flush=True)


if __name__=='__main__':main()

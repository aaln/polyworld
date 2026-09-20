"""Run all twelve frozen100-episode requests before reading confirmation."""
import argparse
from pathlib import Path
import shutil

from hosted_queue import run
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest
from release_hosted import prepare_confirmation,compare
from release_workspace import VERSION,SOURCE,verify

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);a=parser.parse_args();directory=a.directory.resolve()
    verify()
    result=read(directory/'hosted-discovery/result.json')
    name=result['selected']
    if name is None: raise ValueError('No qualifying discovery candidate')
    with client() as c:
        league=get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        game=get(c,'/v2/coworlds/'+league['game']['coworld_id'])
        if game['version']!=VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:
            raise ValueError('Live release changed before confirmation')
    prepare_confirmation(directory)
    frozen=directory/'confirmation-tools'
    if not frozen.exists():
        frozen.mkdir()
        for p in HERE.glob('*.py'):
            if not p.name.startswith('test_'): shutil.copy2(p,frozen/p.name)
        write(frozen/'manifest.json',{p.name:digest(p.read_bytes()) for p in frozen.glob('*.py')})
    run([directory/'hosted-confirmation'/arm/f'part-{i}' for i in range(4) for arm in ['v2','cadence',name]])
    compare(directory,True)

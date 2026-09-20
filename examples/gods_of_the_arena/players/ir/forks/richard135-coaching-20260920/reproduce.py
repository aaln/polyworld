"""Verify a saved primary IR/BASIC pair using the captured repo conversion."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'tooling'))
sys.path.insert(0,str(HERE/'tooling/ir'))
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v7
from policy_ir import read,compile_policy,extract


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair',type=Path,action='append')
    args=parser.parse_args()
    manifest=read(HERE/'tooling-manifest.json')
    for relative,sha in manifest['files'].items():
        assert hashlib.sha256((HERE/relative).read_bytes()).hexdigest()==sha,relative
    pairs=args.pair or sorted((HERE/'evaluated').glob('*'))+[
        HERE/'retained-baseline',HERE/'validated-blue-component']
    results=[]
    for directory in pairs:
        p=read(directory/'policy.ir.json');source=(directory/'policy.bas').read_bytes()
        assert compile_policy(p).encode()==source,str(directory)
        assert extract(source.decode(),p)==p,str(directory)
        module=ast.parse((directory/'policy.py').read_text())
        assignments=[n for n in module.body if isinstance(n,ast.Assign)]
        assert len(assignments)==1 and ast.literal_eval(assignments[0].value)==p
        results.append({'pair':str(directory.resolve()),'compile_extract_primary_parity':True,
                        'source_sha256':hashlib.sha256(source).hexdigest()})
    print(json.dumps({'passed':True,'pairs':results},indent=2))


if __name__=='__main__':main()

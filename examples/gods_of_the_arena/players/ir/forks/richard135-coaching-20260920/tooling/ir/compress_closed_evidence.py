"""Transparent APFS compression of completed evidence, with byte-hash receipts."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import time
from policy_ir import read,write
from ranger_guard_queue import alive


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while data:=f.read(1024*1024): h.update(data)
    return h.hexdigest()


def compress(study,scope=None,completed_result=None,process_record=None):
    if process_record:
        p=study/process_record
        if not p.exists() or alive(read(p)['pid']): raise RuntimeError('Missing or still-live process record: '+str(p))
    for role in (('local',) if scope=='local' else ('hosted','local','activation')):
        p=study/(role+'-process.json')
        if p.exists() and alive(read(p)['pid']): raise RuntimeError('Study still running: '+str(p))
    verdict=study/completed_result if completed_result else (study/'local/comparison.json' if scope=='local' else study/'hosted-comparison.json')
    if not verdict.exists(): raise RuntimeError('Closed verdict required')
    if completed_result:
        if not process_record: raise RuntimeError('Explicit completed result requires its stopped process record')
        result=read(verdict)
        if not {'checks','passed','heads','arms'}.issubset(result): raise RuntimeError('Expected completed field verdict, whether passed or rejected')
    target=study/scope if scope else study
    receipt=study/('evidence-compression-'+(scope+'-' if scope else '')+str(int(time.time()))+'.json')
    rows=[]
    for p in sorted(target.rglob('*')):
        if not p.is_file() or p.is_symlink(): continue
        before=p.stat()
        if before.st_size<131072 or before.st_blocks*512 < before.st_size*.7: continue
        tmp=p.with_name('.'+p.name+'.hfs-temp')
        if tmp.exists(): raise RuntimeError('Unexpected temporary file: '+str(tmp))
        original=sha(p)
        subprocess.run(['/usr/bin/ditto','--hfsCompression','--noclone',str(p),str(tmp)],check=True)
        if sha(tmp)!=original: raise RuntimeError('Compression changed bytes: '+str(p))
        after=p.stat()
        if (after.st_size,after.st_mtime_ns)!=(before.st_size,before.st_mtime_ns) or sha(p)!=original:
            raise RuntimeError('Evidence changed during compression: '+str(p))
        os.replace(tmp,p)
        rows.append({'path':str(p),'sha256':original,'before_blocks':before.st_blocks,'after_blocks':p.stat().st_blocks,'bytes':before.st_size})
    result={'study':str(study),'scope':scope,'closed_verdict':str(verdict),'closed_verdict_sha256':sha(verdict),'method':'Transparent HFS/APFS compression, unchanged paths and SHA256 bytes; no evidence deleted.',
        'files':len(rows),'saved_bytes':sum((r['before_blocks']-r['after_blocks'])*512 for r in rows),'rows':rows}
    write(receipt,result)
    print(study.name,result['files'],result['saved_bytes']//1048576,'MiB saved',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path);p.add_argument('--scope',choices=['local'])
    p.add_argument('--completed-result');p.add_argument('--process-record')
    args=p.parse_args();compress(args.study,args.scope,args.completed_result,args.process_record)

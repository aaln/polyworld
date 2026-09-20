"""Overlap identical replay audits with a frozen study's remaining games.

No score aggregation. The original study still revalidates every audit before
its verdict. Stop scheduling once all games exist, leaving its audit pool to
finish the remainder. Writes are atomic to permit that handoff.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time

from policy_ir import ROOT, digest, read, write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("--stage",default="validation",choices=["screen","validation"])
    parser.add_argument("--workers",type=int,default=2)
    args=parser.parse_args();d=args.directory.resolve();plan=read(d/"plan.json")
    binary=d/"audit"
    if digest(binary.read_bytes())!=plan["auditor_sha256"]:raise ValueError("Auditor changed")
    for path,sha in plan["instruments"].items():
        if digest((ROOT/path).read_bytes())!=sha:raise ValueError("Frozen instrument changed")
    write(d/(args.stage+"-audit-overlap.json"),{
        "started_at":datetime.now(timezone.utc).isoformat(),"workers":args.workers,
        "helper_sha256":digest(Path(__file__).read_bytes()),"auditor_sha256":plan["auditor_sha256"],
        "change":"Execution scheduling only: run identical replay checks on completed cases while remaining games run. No policy, input, sample, audit requirement or decision-rule changes. No outcome aggregation."})
    def audit(path):
        folder=path.parent;result=read(path);tape=folder/"episode.replay"
        if digest(tape.read_bytes())!=result["replay_sha256"]:raise ValueError("Tape changed")
        proc=subprocess.run([str(binary),"--replay",str(tape)],cwd=ROOT,
                            capture_output=True,text=True,timeout=300,check=True)
        a=json.loads(proc.stdout.splitlines()[-1])
        if a["hash_mismatches"] or a["ticks"]!=result["ticks"] or a["actions_consumed"]!=result["actions"]:
            raise ValueError("Replay did not reproduce the complete game")
        a.update(binary_sha256=plan["auditor_sha256"],replay_sha256=result["replay_sha256"])
        temporary=folder/f"audit.{os.getpid()}.tmp"
        write(temporary,a);temporary.replace(folder/"audit.json")
    attempted=set();pending={};completed=0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while True:
            for future,path in list(pending.items()):
                if not future.done():continue
                try:
                    future.result();completed+=1
                    if completed%10==0:print(f"Verified {completed} complete replays ahead of the final audit phase",flush=True)
                except Exception as error:
                    write(path.parent/"audit-overlap-failure.json",{
                        "type":type(error).__name__,"recovery":"Original study must retry the identical replay; this attempt contributes no score or cached audit."})
                del pending[future]
            paths=sorted((d/args.stage).glob("*/*/result.json"))
            if len(paths)==len(plan[args.stage])*3:break
            for path in paths:
                if len(pending)>=args.workers:break
                if path in attempted or (path.parent/"audit.json").exists():continue
                attempted.add(path);pending[pool.submit(audit,path)]=path
            time.sleep(1)
        # Drain the few active checks; the original runner handles any remainder.
        for future,path in pending.items():
            try:future.result()
            except Exception as error:
                write(path.parent/"audit-overlap-failure.json",{"type":type(error).__name__})
    print("Audit overlap finished; original study retains final verification and scoring.",flush=True)


if __name__=="__main__":main()

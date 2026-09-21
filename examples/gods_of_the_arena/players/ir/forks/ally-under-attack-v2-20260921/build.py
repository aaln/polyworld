"""Fork formation-adaptive-20260920 with H-ALLY-UNDER-ATTACK-01; never patch generated BASIC.

Uses the parent's frozen compiler.zip + contracts.json. Adds one contract that
extends the attack skill: when a visible living enemy hero within assist_tiles
publicly targets a living allied hero, focus the lowest-HP such enemy hero
instead of the ordinary candidate (self must keep >= 25 percent HP).
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pprint
import runpy
import sys
import tempfile
import zipfile
from dataclasses import replace

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'formation-adaptive-20260920'  # v2 narrows v1 (regressed blue vs Richard)
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_text())

ASSIST = '''    mMin = 0
    mSum = 2147483647
    mIndex = 0
    while mIndex < objectCount() and mIndex < 64
      mKind = objectKind(mIndex)
      if mKind = 3 then
        mIndex = 64
      else
        if mKind = 2 and objectTeam(mIndex) <> selfTeam and objectHp(mIndex) > 0 and objectHp(mIndex) < mSum then
          mId = objectTarget(mIndex)
          if mId <> 0 and mId <> selfId then
            mDx = objectX(mIndex) - selfX
            mDy = objectY(mIndex) - selfY
            if mDx * mDx + mDy * mDy <= param_assist_tiles * param_assist_tiles then
              mStep = 0
              while mStep < objectCount() and mStep < 64
                if objectKind(mStep) = 3 then
                  mStep = 64
                else
                  if objectId(mStep) = mId and objectKind(mStep) = 2 and objectTeam(mStep) = selfTeam and objectHp(mStep) > 0 then
                    mTryX = objectX(mStep) - selfX
                    mTryY = objectY(mStep) - selfY
                    if mTryX * mTryX + mTryY * mTryY <= 36 then
                      mMin = objectId(mIndex)
                      mSum = objectHp(mIndex)
                    end if
                  end if
                end if
                mStep = mStep + 1
              wend
            end if
          end if
        end if
      end if
      mIndex = mIndex + 1
    wend
    if mMin <> 0 and (bestId = 0 or mTD = 3) and selfHp * 100 >= selfMaxHp * 25 then
      bestId = mMin
    end if
'''


def main():
    m = read(PARENT/'compiler-manifest.json')
    assert sha((PARENT/'compiler.zip').read_bytes()) == m['compiler_zip_sha256']
    tmp = tempfile.mkdtemp(prefix='ally-under-attack-ir-')
    with zipfile.ZipFile(PARENT/'compiler.zip') as z:
        z.extractall(tmp)
    sys.path.insert(0, str(Path(tmp)/'examples/gods_of_the_arena/players/ir'))
    from binding import CONTRACTS, Contract
    contracts = read(PARENT/'contracts.json')
    for name, fields in contracts.items():
        f = dict(fields)
        for key in ('reads','writes','actions','memory'):
            f[key] = tuple(f[key])
        f['parameters'] = {k: tuple(v) for k,v in f['parameters'].items()}
        CONTRACTS[name] = Contract(**f)
    from policy_ir import compile_policy, extract, digest, grounded, bundle, refresh_grounding
    parent = runpy.run_path(str(PARENT/'policy.py'))['POLICY']
    assert compile_policy(parent).encode() == (PARENT/'policy.bas').read_bytes()

    old_name = parent['skill']['attack']['operator']
    old = CONTRACTS[old_name]
    token = '    if motionActive = 0 and bestId <> 0 then\n      attackTarget(bestId)\n    end if\n'
    assert old.template.count(token) == 1
    loop = '      if mId = selfId then\n        mFacingX = objectFacingX(mIndex)\n'
    assert old.template.count(loop) == 1
    init = '    mIndex = 0\n    while mIndex < objectCount()\n'
    assert old.template.count(init) == 1
    new_name = 'richard_formation_combat_ally_under_attack_v2'
    new = replace(old, template=old.template.replace(init, '    mTD = 0\n'+init, 1).replace(loop, '      if mId = bestId then\n        mTD = mKind\n      end if\n'+loop, 1).replace(token, ASSIST+token, 1),
                  parameters=old.parameters | {'assist_tiles': (6, 4, 12)},
                  memory=old.memory,
                  meaning=old.meaning + ' H-ALLY-UNDER-ATTACK-01: before the ordinary attack order, scan visible '
                  'living enemy heroes (heroes precede creeps in the object list). If one within assist_tiles '
                  'publicly targets a living allied hero other than self, focus the lowest-HP such enemy hero '
                  'instead of the ordinary candidate while self keeps at least 25 percent HP. Public objectTarget '
                  'only; no opponent identity, seed or hidden state is read. Scratch variables mMin/mSum/mIndex/mKind/mId/mDx/mDy/mStep are reused because the parent is at the VM global-variable cap; each is reassigned before any later read. v2: override only when the ordinary candidate is a creep or absent and the victim ally is within 6 tiles of self; v1 (any candidate, 8 tiles) regressed blue vs Richard v135 0W/3L. Focus intent does not guarantee '
                  'kills or ally survival; measure full games.')
    CONTRACTS[new_name] = new
    contracts[new_name] = {'template': new.template, 'meaning': new.meaning, 'parameters': {k: list(v) for k,v in new.parameters.items()},
                           'reads': list(new.reads), 'writes': list(new.writes), 'actions': list(new.actions), 'memory': list(new.memory)}
    p = deepcopy(parent)
    p['id'] = 'gota_formation3600_ally_under_attack_v2'
    p['skill']['attack'] = {'operator': new_name, 'parameters': dict(parent['skill']['attack']['parameters']) | {'assist_tiles': 6}}
    p['goal']['G_assist'] = {'preference': 'Do not let a stacked teammate be focus-fired alone: join on the enemy hero '
                             'attacking a nearby ally. Ranked below fort defense; a hypothesis, not a validated gain.', 'provenance': 'authored'}
    for r in p['strategy']:
        if r['skill'] == 'attack':
            r['for'] = r['for'] + ['G_assist']
    p['belief']['claims']['AllyUnderAttack'] = {
        'claim': 'H-ALLY-UNDER-ATTACK-01: in relh v159 losses (episodes ereq_ea546a70/7fc140bc, ticks 1470-1560) our '
                 'other stack members kept attacking creeps while one hero was focus-fired to death. Retargeting to the '
                 'enemy hero attacking a nearby ally is predicted to convert 0-3 skirmishes into trades. Falsifiers: the '
                 '3v3 is still lost, or Alex g002v1 / Jordan v268 / Richard v135 pinned controls regress, or runtime '
                 'grows by more than 1,500 instructions.', 'status': 'untested',
        'evidence': [{'artifact': 'docs/opponents/relh-v159/inferred-20260921/model.json'}]}
    p['update'].update(revision=p['update']['revision']+1, parent=digest(parent),
        change={'origin': 'Devin cycle 04 fork for relh v159 trigger', 'hypothesis': 'H-ALLY-UNDER-ATTACK-01 v2 (creep-only override, ally within 6 tiles)',
                'layer': 'skill (attack) + belief', 'rule': 'R2'},
        needs_review=['local screen vs Richard/Alex/Jordan both colours', 'hosted A/B vs relh v159', 'runtime cost'])
    refresh_grounding(p)
    source = compile_policy(p)
    assert extract(source, p) == p
    out = HERE/'bundle'
    import shutil
    if out.exists(): shutil.rmtree(out)
    bundle(p, out)
    for f in out.iterdir(): shutil.move(str(f), HERE/f.name)
    out.rmdir()
    (HERE/'policy.py').write_text('"""H-ALLY-UNDER-ATTACK-01 fork of the adaptive formation3600 IR; untested until README says otherwise."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (HERE/'contracts.json').write_text(json.dumps(contracts, indent=1, sort_keys=True))
    (HERE/'compiler.zip').write_bytes((PARENT/'compiler.zip').read_bytes())
    cm = dict(m); cm['source_sha256'] = sha(source.encode()); cm['contracts_sha256'] = sha((HERE/'contracts.json').read_bytes())
    cm['interpretation'] = 'Parent frozen compiler modules; contracts add richard_formation_combat_ally_under_attack_v2 (template-level, no BASIC patch).'
    (HERE/'compiler-manifest.json').write_text(json.dumps(cm, indent=1))
    (HERE/'verify.py').write_text((PARENT/'verify.py').read_text())
    manifest = read(HERE/'manifest.json')
    manifest['artifacts'] = {str(path.relative_to(HERE)): sha(path.read_bytes())
                             for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'manifest.json'}
    (HERE/'manifest.json').write_text(json.dumps(manifest, indent=1))
    print(json.dumps({'source_sha256': sha(source.encode()), 'policy_sha256': digest(p), 'parent_source': sha((PARENT/'policy.bas').read_bytes()),
                      'bytes': len(source), 'parent_bytes': len((PARENT/'policy.bas').read_bytes())}))


if __name__ == '__main__':
    main()

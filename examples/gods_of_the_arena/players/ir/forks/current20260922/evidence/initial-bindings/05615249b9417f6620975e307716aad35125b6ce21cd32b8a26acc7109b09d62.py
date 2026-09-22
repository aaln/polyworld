"""Editable semantic skills for practiced timing, growth, gear and portals."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import argparse
import json
import pprint
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'week20260921'))
import contracts as legacy
from binding import contract
import binding
import policy_ir as ir

STUDY=ROOT/'tmp/gota-targets-20260922'
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/week20260921'
VERSION='gota-bassy/microplay-2026-09-22'

def changed(spec,old,new,**kwargs):
    assert spec.template.count(old)==1,old
    return replace(spec,template=spec.template.replace(old,new),**kwargs)

TIMING=contract(r'''
if active = 0 and drafting = 0 and selfHp > 0 then
  if selfChannelTicks = 0 and selfStunTicks = 0 and selfRootTicks = 0 then
    if retreat = 0 and selfTarget > 0 then
      if selfAttacksLanded > previousHits then
        previousHits = selfAttacksLanded
        walkTo(selfX + 0.25, selfY + 0.25)
        attackTarget(selfTarget)
      end if
    end if
  end if
end if
''',{},(),(),('walkTo','attackTarget'),
 'Between full six-tick decisions, reset recovery once after an observed landed hit and reacquire the same public target. Never cancel an unfinished windup, retreat, stun, root or portal channel.',('previousHits',))

XP_CLOSE=contract(r'''
if stopped = 0 and selfClass = Crossbowman and bestKind = 3 and bestId > 0 then
  if bestDistance > 25 and bestDistance <= 64 and enemyPower <= friendPower then
    if selfRootTicks = 0 and worldTick >= moveTick then
      walkTo((selfX + bestX) / 2, (selfY + bestY) / 2)
      moveTick = worldTick + 6
    end if
    stopped = 1
  end if
end if
''',{},(),(),('walkTo',),
 'For safe Crossbowman creep farming, step inside the six-tile XP radius instead of stopping at its 6.5-tile attack range. Defer while tower safety or recovery owns movement.')

HOME_PORTAL=contract(r'''
if stopped = 0 and retreat = 0 and portalSlot >= 0 then
  if ordinal <= 1 and homeEnemyHeroes > 0 and homeDefenders < 2 then
    dx = selfX - homeX
    dy = selfY - homeY
    if dx * dx + dy * dy > 625 and selfHp * 100 >= selfMaxHp * 60 then
      if selfPortalCooldown = 0 and threatDistance > 225 and worldTick - hurtTick > tickRate * 2 then
        if useItemAt(portalSlot, homeX, homeY) = 1 then
          stopped = 1
        end if
      end if
    end if
  end if
end if
''',{},(),(),('useItemAt',),
 'At most the first two public team ordinals may safely channel home when visible enemy heroes threaten the keep and fewer than two allies already defend. Require health, distance, no recent damage and portal readiness; current threat disappearance releases defense.')

def economy(potions):
    gear=[(11,110),(16,160),(18,180),(19,180)]+([] if potions else [(13,150)])
    lines=['gearCount = 0','healSlot = -1','healCount = 0','portalSlot = -1','portalCount = 0','empty = 0']
    lines += [f'has{item} = 0' for item,_ in gear]
    lines += ['s = 0','while s < 6','  item = itemId(s)','  if item = 0 then','    empty = empty + 1','  end if']
    for item,_ in gear:
        lines += [f'  if item = {item} then',f'    has{item} = 1','    gearCount = gearCount + 1','  end if']
    lines += ['  if item = 1 then','    healSlot = s','    healCount = itemCount(s)','  end if','  if item = 21 then','    portalSlot = s','    portalCount = itemCount(s)','  end if','  s = s + 1','wend']
    if potions:
        lines += ['if healSlot >= 0 and inOwnSpawn() = 0 then','  if itemCooldown(healSlot) = 0 and selfMaxHp - selfHp >= 70 and threatDistance > 64 then','    if worldTick - hurtTick > tickRate then','      useItem(healSlot)','    end if','  end if','end if']
    lines += ['if canShop() = 1 then','  restock = 0','  budget = selfGold']
    order=gear[:3]+[(21,100)]+gear[3:]+([(1,30)] if potions else [])
    for item,cost in order:
        condition=f'has{item} = 0' if item not in (1,21) else ('healCount = 0' if item==1 else 'portalCount = 0')
        lines += [f'  if {condition} and budget >= {cost} and empty > 0 then',f'    if buyItem({item}) = 1 then',f'      budget = budget - {cost}','      empty = empty - 1']
        if item not in (1,21):lines += ['      gearCount = gearCount + 1']
        lines += ['    end if','  end if']
    if potions:lines += ['  if healCount > 0 and healCount < 2 and budget >= 30 then','    buyItem(1)','  end if']
    lines += ['else',f'  if gearCount < {len(gear)} and selfGold >= param_shop_gold and threatDistance > 225 then','    restock = 1','  end if','end if','if restock = 1 then','  retreat = 1','end if']
    return contract('\n'.join(lines),{'shop_gold':(500,300,1200)},(),(),('buyItem','useItem'),
      ('Reserve potion and portal slots; buy dagger, armor, axe and crossbow instead of low-impact boots.' if potions else 'Reserve one portal slot; spend on five permanent items: dagger, armor, axe, crossbow and longsword.')+' Safely return to shop when useful equipment remains missing and gold is banked.',('restock',))

def specs(mode):
    s=deepcopy(legacy.SPECS)
    if mode=='baseline':return s
    s={'draft':s.pop('draft'),'timing':TIMING,**s}
    if mode=='timing':return s
    obs=s['observe']
    obs=changed(obs,'homeThreat = 0','homeThreat = 0\nhomeEnemyHeroes = 0\nhomeDefenders = 0\nhitReach = selfAttackRange \\ 60000 + 1')
    obs=changed(obs,'if kind = 2 and id <> selfId and distance <= 100 then',
      'if kind = 2 and id <> selfId then\n  hx = x - homeX\n  hy = y - homeY\n  if hx * hx + hy * hy < 400 then\n    homeDefenders = homeDefenders + 1\n  end if\nend if\nif kind = 2 and id <> selfId and distance <= 100 then')
    obs=changed(obs,'if dx * dx + dy * dy < 144 then',
      'if kind = 2 and dx * dx + dy * dy < 225 then\n  homeEnemyHeroes = homeEnemyHeroes + 1\nend if\nif dx * dx + dy * dy < 144 then')
    obs=changed(obs,'if hp <= selfAttackDamage then\n              score = score + 350',
      'if hp <= selfAttackDamage and distance <= hitReach * hitReach then\n              score = score + 650')
    obs=changed(obs,'dx = x - enemyX\n          dy = y - enemyY',
      'farmX = mapWidth \\ 2\nfarmY = mapHeight \\ 2\nif lane = 0 then\n  farmX = mapWidth \\ 10\n  farmY = mapHeight \\ 10\nend if\nif lane = 2 then\n  farmX = mapWidth * 9 \\ 10\n  farmY = mapHeight * 9 \\ 10\nend if\ndx = x - farmX\ndy = y - farmY')
    s['observe']=replace(obs,meaning='Visible bounded scan: reward in-range last hits, count current keep attackers and defenders, and select an allied portal tower toward the assigned farming lane.')
    s['economy']=economy(mode=='potions')
    out={}
    for name,spec in s.items():
        if name=='recover':out['home_portal']=HOME_PORTAL
        if name=='combat':out['xp_close']=XP_CLOSE
        out[name]=spec
    return out

def configure(mode):
    legacy.register()
    binding.VERSION=ir.VERSION='gota-bassy/2026-09-21' if mode=='baseline' else VERSION
    current=specs(mode)
    if mode!='baseline':
        binding.VERSION=VERSION
        binding.CONTRACTS.clear();binding.CONTRACTS.update({'micro_'+k:v for k,v in current.items()})
    return current

def build(name,mode):
    p=json.loads((PARENT/'policy.ir.json').read_text())
    parent=ir.digest(p);current=configure(mode)
    if mode!='baseline':
        p['skill']={k:{'operator':'micro_'+k,'parameters':v.defaults()} for k,v in current.items()}
        p['strategy']=[{'id':'R_'+k,'when':'always' if k in ('draft','timing','lifecycle') else 'active','skill':k,'for':['Win','Grow','Survive','Score','Practice']} for k in current]
        p['execution']['binding']=VERSION
    if mode!='baseline':p['id']='gota_targets20260922_'+name
    p['goal']['Practice']={'preference':'Secure feasible last hits and shared XP, buy useful permanent power, and use safe portals for urgent defense or productive recovery.','provenance':'authored'}
    p['belief']['claims']['Microplay']={'claim':'Practiced timing, XP position, equipment and portal skills improve the current relh/Jordan/Richard matchups.','status':'untested','evidence':[]}
    p['situation']['notes']+=' Current target identities are evaluation metadata, never live policy inputs. Creep XP requires same floor and six-tile proximity; Crossbowman attack range exceeds it.'
    p['update']={'revision':3,'parent':parent,'change':{'origin':'User requested semantic IR and practice on last hits, XP, gear and defensive portals','variant':mode},'needs_review':['belief/Microplay'],'evidence':[{'artifact':'games/gods_of_the_arena/experiments/2026-09-21-targets-microplay.md'}]}
    ir.refresh_grounding(p)
    source=ir.compile_policy(p)
    assert ir.extract(source,p)==p
    if mode=='baseline':assert source==(PARENT/'policy.bas').read_text()
    folder=STUDY/'candidates'/name
    assert not folder.exists(),'Preserve frozen source: '+str(folder)
    folder.mkdir(parents=True)
    for filename,obj in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:
        (folder/filename).write_text(json.dumps(obj,indent=2)+'\n')
    (folder/'policy.py').write_text('"""Semantic policy; compile through the versioned microplay binding."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (folder/'policy.bas').write_text(source)
    (folder/'manifest.json').write_text(json.dumps({'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'mode':mode,'binding_sha256':ir.digest(Path(__file__).read_bytes()),'exact_roundtrip':True,'validation':'unvalidated'},indent=2)+'\n')
    print(name,ir.digest(source.encode()),len(source.encode()))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--mode',choices=('baseline','timing','growth','potions'),required=True);a=parser.parse_args();build(a.name,a.mode)

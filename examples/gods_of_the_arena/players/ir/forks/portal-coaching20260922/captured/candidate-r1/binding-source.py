"""Semantic portal coaching, grounded in the current patched host contract."""
from dataclasses import replace
from pathlib import Path
import json
import pprint
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUDY = ROOT.parent / 'polyworld/tmp/gota-portals-20260922'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/balance-draft20260922'
sys.path.insert(0, str(HERE.parent / 'balance20260922'))
import draft_only
ir, binding = draft_only.build.ir, draft_only.build.binding
BINDING = 'gota-bassy/portals-2026-09-22-r1'


def spec(source, meaning, parameters=None, memory=(), actions=()):
    return binding.contract(source, parameters or {}, (), (), actions, meaning, memory)


def configure():
    old = draft_only.configure()
    specs = dict(old)
    observe = old['observe'].template.replace('threatDistance = 1000000', '''threatDistance = 1000000
recallHeroDistance = 1000000
recallCreepDistance = 1000000
homeAnchorDistance = 1000000''')
    observe = observe.replace('if kind = 4 then', '''if kind = 4 then
          homeDx = x - spawnX
          homeDy = y - spawnY
          homeGap = homeDx * homeDx + homeDy * homeDy
          if homeGap < homeAnchorDistance then
            homeAnchorDistance = homeGap
          end if''', 1)
    observe = observe.replace('if kind = 2 or kind = 3 then', '''if kind = 2 and distance < recallHeroDistance then
          recallHeroDistance = distance
        end if
        if kind = 3 and distance < recallCreepDistance then
          recallCreepDistance = distance
        end if
        if kind = 2 or kind = 3 then''', 1)
    specs['observe'] = replace(old['observe'], template=observe,
        meaning=old['observe'].meaning + ' Separately measure public hero/creep gaps and require a living home-area tower for recall; never infer hidden enemies are absent.')
    # Keep gear/potion behavior, buy the first scroll before the axe, and only
    # fund a second stacked scroll after the complete four-item core.
    economy = old['economy'].template
    axe_start = economy.index('  if has18 = 0')
    portal_start = economy.index('  if portalCount = 0')
    crossbow_start = economy.index('  if has19 = 0')
    economy = economy[:axe_start] + economy[portal_start:crossbow_start] + economy[axe_start:portal_start] + economy[crossbow_start:]
    marker = '  if healCount > 0 and healCount < 2 and budget >= 30 then'
    economy = economy.replace(marker, '''  if gearCount >= 4 and selfGold >= 100 then
    reserveSlot = 0
    while reserveSlot < 6
      if itemId(reserveSlot) = 21 and itemCount(reserveSlot) = 1 then
        buyItem(21)
      end if
      reserveSlot = reserveSlot + 1
    wend
  end if
''' + marker)
    specs['economy'] = replace(old['economy'], template=economy,
        meaning='Buy dagger and armor, then the first retreat scroll before axe/crossbow. Once all four core items are owned, maintain up to two stacked scrolls using live inventory/gold. Outward travel must leave one emergency scroll; no additional inventory slot required.')
    specs['recovery_intent'] = spec('''
if retreat = 0 then
  active = 1
end if
retreat = 1
resumeTarget = 0
''', 'Critical field health takes priority before post-hit attack reacquisition; commit to survive_and_replenish until recovered at spawn.', memory=('retreat','resumeTarget'))
    specs['portal_context'] = spec('''
inBase = canShop()
portalSlot = -1
portalCount = 0
portalReady = 0
s = 0
while s < 6
  if itemId(s) = 21 and itemCount(s) > 0 then
    portalSlot = s
    portalCount = itemCount(s)
    if itemCooldown(s) = 0 and selfPortalCooldown = 0 and selfChannelTicks = 0 then
      if selfRootTicks = 0 and selfStunTicks = 0 then
        portalReady = 1
      end if
    end if
  end if
  s = s + 1
wend
''', 'Re-read live inventory after purchases. Ready means an actual charge, zero shared/item cooldown, alive and free of root/stun/channel; in_base uses the host keep/spawn query.')
    specs['replenish'] = spec('''
if inOwnSpawn() = 1 then
  if selfHp * 10 >= selfMaxHp * 9 and selfMana * 10 >= selfMaxMana * 8 then
    retreat = 0
  else
    retreat = 1
    stopped = 1
    if selfRootTicks = 0 and worldTick >= moveTick then
      walkTo(spawnX, spawnY)
      moveTick = worldTick + 24
    end if
  end if
end if
''', 'Finish rapid fountain recovery until 90% HP and 80% mana, then release the retreat goal. Do not cast a home scroll inside the keep or spawn.', memory=('retreat','moveTick'), actions=('walkTo',))
    specs['channel_town_scroll'] = spec('''
dx = selfX - spawnX
dy = selfY - spawnY
if dx * dx + dy * dy > 64 and homeAnchorDistance <= 400 then
  if recallHeroDistance > 100 and recallCreepDistance > 36 and towerDistance > 100 then
    if towerAggro = 0 and worldTick - hurtTick >= tickRate then
      warningSafe = 1
      warnings = spellCount()
      if warnings > 24 then
        warningSafe = 0
      end if
      w = 0
      while w < warnings and w < 24
        dx = spellX(w) - selfX
        dy = spellY(w) - selfY
        if dx * dx + dy * dy <= 64 and spellImpactTick(w) <= worldTick + tickRate * 3 then
          warningSafe = 0
        end if
        w = w + 1
      wend
      if warningSafe = 1 then
        if useItemAt(portalSlot, spawnX, spawnY) = 1 then
          stopped = 1
          resumeTarget = 0
        end if
      end if
    end if
  end if
end if
''', 'Prefer a safe field channel to walking home. Require a living home-area tower, useful travel distance, no damage for one second, no nearby heroes/creeps/towers or imminent public spell warning. Enemy uncertainty remains; this is a bounded safety heuristic, not guaranteed invulnerability.', memory=('resumeTarget',), actions=('useItemAt',))
    specs['walk_to_base'] = spec('''
if selfRootTicks = 0 and worldTick >= moveTick then
  walkTo(spawnX, spawnY)
  moveTick = worldTick + 24
end if
stopped = 1
''', 'When recall is unsafe/unavailable, or already inside the keep, walk toward spawn and reconsider on later decisions. Interrupted channels use live cooldown/root state; no retry loop spends extra charges.', memory=('moveTick',), actions=('walkTo',))
    specs['home_portal'] = replace(old['home_portal'],
        template=old['home_portal'].template.replace('if stopped = 0 and retreat = 0 and portalSlot >= 0 and selfRootTicks = 0 then', 'if stopped = 0 and retreat = 0 and inBase = 0 and portalReady = 1 and homeAnchorDistance <= 400 then'),
        meaning=old['home_portal'].meaning + ' Never recall defensively from inside the keep; require a live home anchor and current item readiness.')
    specs['advance'] = replace(old['advance'], template=old['advance'].template.replace(
        'if canShop() = 1 and portalSlot >= 0 and selfPortalCooldown = 0 then',
        'if inBase = 1 and portalReady = 1 and portalCount >= 2 then'),
        meaning=old['advance'].meaning + ' Outbound portals require two scrolls so one remains for field recovery after cooldown; home and outward channel purposes are distinct.')
    del specs['recover']
    order = ['draft','recovery_intent','timing','lifecycle','observe','economy','portal_context','replenish','channel_town_scroll','walk_to_base','home_portal','tower_safety','xp_close','combat','advance']
    specs = {name:specs[name] for name in order}
    binding.VERSION = ir.VERSION = BINDING
    binding.CONTRACTS.clear()
    binding.CONTRACTS.update({'portal_' + k:v for k,v in specs.items()})
    binding.PREDICATES.update({
        'low_health_in_field': ('drafting = 0 and selfHp > 0 and selfChannelTicks = 0 and selfStunTicks = 0 and canShop() = 0 and selfHp * 100 < selfMaxHp * 30', (), 'Below 30% health outside the friendly keep/spawn, alive and not channeling/stunned. Recovery takes priority over farming and attack reacquisition.'),
        'town_scroll_ready': ('active = 1 and stopped = 0 and retreat = 1 and inBase = 0 and portalReady = 1', (), 'Committed field recovery with an actual ready scroll; safe channel checks must still pass.'),
        'recovery_remaining': ('active = 1 and stopped = 0 and retreat = 1', (), 'Recovery owns the decision and no successful channel/replenishment action has claimed it.'),
        'in_base': ('active = 1 and inBase = 1', (), 'Host canShop identifies own keep or spawn; home recalls are disallowed here while useful outbound channels remain legal.')})
    return specs


def main():
    p = json.loads((PARENT/'policy.ir.json').read_text())
    parent = ir.digest(p)
    specs = configure()
    p['id'] = 'gota_portal_coaching20260922'
    p['execution']['binding'] = BINDING
    p['goal']['survive_and_replenish'] = {'preference':'At critical field health, disengage and channel safely home before more farming; restore HP/mana at spawn and return productively with a reserved scroll.','provenance':'interpretation'}
    p['skill'] = {k:{'operator':'portal_'+k,'parameters':s.defaults()} for k,s in specs.items()}
    predicates = {'recovery_intent':'low_health_in_field','channel_town_scroll':'town_scroll_ready','walk_to_base':'recovery_remaining','replenish':'in_base'}
    p['strategy'] = [{'id':'R_'+k,'when':predicates.get(k,'always' if k in ('draft','timing','lifecycle') else 'active'),'skill':k,'for':['Grow','Survive','Score','Practice','survive_and_replenish']} for k in specs]
    p['situation']['notes'] = 'Coached home recall differs from outbound tower travel. in_base=canShop, fountain=inOwnSpawn. Public hero/creep separation and warnings gate a field channel. Global geometry and Crossbow draft are retained; current engine rejects ordinary commands during channels. Actual stun/root, anchor loss or death interrupts; a bot cannot cancel a channel by walking.'
    p['belief']['claims'] = {
        'PortalPattern': {'claim':'All16 preselected baseline diagnostic games contain a home-directed portal starting inside the keep; useful outward portals also occur. The supplied episode confirms it for both owned slots, but contains a failed rival VM and is mechanism evidence only.','status':'supported','evidence':[{'artifact':'evidence/diagnosis-result.json'}]},
        'CoachingFidelity': {'claim':'Coordinated priorities, live scroll readiness/reserves, field safety and in-base walking realize the coaching on both colors.','status':'untested','evidence':[]},
        'CompetitiveGain': {'claim':'The combined portal controller improves current league XP score without a color regression. Native practice alone cannot establish this.','status':'untested','evidence':[]}}
    p['update'] = {'revision':1,'parent':parent,'change':{'origin':'Session2026-09-22t16-43-56-076z862811; coordinated field recall and scroll economy','episode':'ereq_2d958e27-210e-461d-b6af-b2e26dfa3a81'},'needs_review':['belief/CoachingFidelity','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/coaching/notes.md'},{'artifact':'evidence/coaching/synthesis.json'}]}
    ir.refresh_grounding(p)
    source = ir.compile_policy(p)
    assert ir.extract(source,p)==p
    out = STUDY/'candidate-r1'
    assert not out.exists(), 'Preserve captured candidates'
    out.mkdir()
    for name,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:
        (out/name).write_text(json.dumps(v,indent=2)+'\n')
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (out/'policy.bas').write_text(source)
    (out/'manifest.json').write_text(json.dumps({'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':BINDING,'parent_source_sha256':ir.digest((PARENT/'policy.bas').read_bytes()),'engine_commit':draft_only.build.COMMIT,'validation':'untested'},indent=2)+'\n')
    print(ir.digest(source.encode()))


if __name__=='__main__':
    main()

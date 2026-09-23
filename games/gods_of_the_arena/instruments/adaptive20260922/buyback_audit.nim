## Retrospective public-equivalent buyback affordances, never live hidden inputs.
import std/[json]
import ../[game,sim,replays,content]
doAssert run.replayMode
var deadTicks,eligibleTicks,excludedTicks:array[10,int64]
var wasDead:array[10,bool]
var moments=newJArray()
while run.world.tick<run.replayData.hashes.len:
  advanceGame()
  if run.world.phase==Drafting:continue
  for i,h in run.world.heroes:
    let dead=h.state==Dying
    if dead:
      inc deadTicks[i]
      let core=CrimsonDagger in h.inventory and KnightArmor in h.inventory and BattleAxe in h.inventory and RuneCrossbow in h.inventory
      let price=run.world.buybackPrice(h.id)
      let remaining=h.respawnTicks()
      let eligible=core and price>0 and remaining>5*TickRate and h.gold>=price+100
      let parent=price>0 and remaining>25*TickRate and h.gold>=price+200
      if eligible:inc eligibleTicks[i]
      if eligible and not parent:inc excludedTicks[i]
      if not wasDead[i]:moments.add(%*{"tick":run.world.tick,"slot":i,"deaths":h.deaths,"level":h.level,"gold":h.gold,"price":price,"remaining":remaining,"core":core,"new_eligible":eligible,"parent_eligible":parent})
    wasDead[i]=dead
doAssert run.hashCheck.mismatches==0
var heroes=newJArray()
for i,h in run.world.heroes:
  heroes.add(%*{"slot":i,"class": $h.class,"deaths":h.deaths,"dead_ticks":deadTicks[i],"eligible_ticks":eligibleTicks[i],"parent_excluded_ticks":excludedTicks[i]})
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,"heroes":heroes,"moments":moments,"scope":"Observed affordances on original trajectories. Eligible dead time is not saved future time or a score forecast; decisions can change gold, fights and game duration."})

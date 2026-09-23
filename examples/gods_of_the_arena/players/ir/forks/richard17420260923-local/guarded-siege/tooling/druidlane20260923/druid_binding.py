"""Scope practiced recovery to Druid; retain every other hero's commands."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / 'lane20260923'))
import lane_binding as lane

ir, host = lane.ir, lane.host
PARENT = lane.PARENT
VERSION = 'gota-bassy/druid-lane-recovery-2026-09-23-r1'


def configure():
    recovery = lane.configure()['lane_recovery']
    specs = dict(lane.parent.configure())
    old = specs['lifecycle']
    specs['lifecycle'] = replace(old, template=old.template.replace(
        '    retreat = 0', '    retreat = 0\n    if selfClass = DruidWarden then\n      laneUntil = 0\n      laneHealUntil = 0\n    end if'),
        memory=old.memory + ('laneUntil', 'laneHealUntil'))
    old = specs['economy']
    assert old.template.count('useItem(healSlot)') == 1
    specs['economy'] = replace(old, template=old.template.replace('useItem(healSlot)', '''if selfClass = DruidWarden then
        if useItem(healSlot) = 1 then
          laneHealUntil = worldTick + tickRate * 10
        end if
      else
        useItem(healSlot)
      end if'''), memory=old.memory + ('laneHealUntil',),
        meaning=old.meaning + ' Only Druid records accepted potion recovery for the lane-healing controller; other classes keep the original calls.')
    specs['lane_recovery'] = replace(recovery, meaning='Druid only. ' + recovery.meaning)
    order = [key for key in specs if key != 'lane_recovery']
    order.insert(order.index('replenish'), 'lane_recovery')
    specs = {key: specs[key] for key in order}
    host.PREDICATES['active_druid'] = (
        'active = 1 and selfClass = DruidWarden', (),
        'Current public hero class is Druid and its normal decision is active; all other classes skip lane recovery entirely.')
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'druidlane_' + key: value for key, value in specs.items()})
    return specs

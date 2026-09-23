"""Scope the coordinated Richard transfer to public blue-Druid context."""
from dataclasses import replace
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'richard17420260923'))
import pressure_binding as parent
ir,host,PARENT=parent.ir,parent.host,parent.PARENT
VERSION='gota-bassy/blue-druid-siege-2026-09-23-r2'
def configure():
 specs=dict(parent.configure());old=specs['guarded_siege'];source=old.template
 assert source.count('if stopped = 0 then')==1
 source=source.replace('if stopped = 0 then','if stopped = 0 and selfTeam = 1 and selfClass = DruidWarden then')
 specs['guarded_siege']=replace(old,template=source,meaning='Only when public selfTeam=blue and selfClass=Druid: '+old.meaning+' Red and all other heroes retain the deployed target selection. The prior broad source failed its400-game gate; this scoped source needs a new independent comparison.')
 host.VERSION=ir.VERSION=VERSION
 host.CONTRACTS.clear();host.CONTRACTS.update({'siege_'+k:v for k,v in specs.items()})
 return specs

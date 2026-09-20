"""Equivalent early rejection once enough closer responders are observed."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_scoped_core_response_v1

parent=CONTRACTS['lineup_scoped_core_response_v1']
old='while responseIndex < objectCount() and responseIndex < 64'
assert parent.template.count(old)==1
value=replace(parent,template=parent.template.replace(old,old+' and responseRank < param_response_members'),
  meaning=parent.meaning+' Equivalent admission work bound: once response_members '
  'closer living heroes have been found, further counting cannot restore '
  'eligibility. Stop that counting pass immediately. The scratch rank is now '
  'saturated at the admission threshold; eligibility, selected anchor, deadlines '
  'and commands are unchanged. Preserve V1 dense native failures and test exact '
  'admission semantics before full games.')
name='lineup_scoped_core_response_v2'
if name in CONTRACTS and CONTRACTS[name]!=value:raise ValueError('Conflicting scoped response V2 contract')
CONTRACTS[name]=value

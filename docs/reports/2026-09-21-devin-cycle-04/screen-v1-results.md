# v1 screen (candidate 28a33472… vs authentic Richard v135 f48bb005…; parent c708970d…)
richard-*.json/.replay for the CANDIDATE arm were accidentally overwritten by a mis-pathed v2 run at 04:33Z
(files preserved in ../screen-v2-partial-overwrite/). Values below were captured from the harness summary before the overwrite.
## parent baseline vs richard (control)
blue-101 W ticks 4824 deaths 4/7 max_instr 15999 hash 000000008A91181B
blue-202 W ticks 4824 deaths 4/7 max_instr 15999 hash 000000002F9081DF
blue-54  W ticks 4824 deaths 4/7 max_instr 15999 hash 00000000D3D43335
red-101  L ticks 5898 deaths 7/1 max_instr 18410 hash 00000000C7E34274
red-202  L ticks 5898 deaths 7/1 max_instr 18410 hash 00000000077F3B72
red-54   L ticks 5898 deaths 7/1 max_instr 18410 hash 00000000A642C998
## candidate v1 vs richard
blue-101 L ticks 12306 deaths 21/16 max_instr 17587 hash 0000000099A69452
blue-202 L ticks 5856  deaths 32/3  max_instr 16717 hash 0000000037606270
blue-54  L ticks 5446  deaths 20/1  max_instr 17858 hash 00000000CA176784
red-101  L ticks 25921 deaths 51/34 max_instr 16681 hash 0000000010ACFD27
red-202  L ticks 9475  deaths 38/17 max_instr 17649 hash 00000000999B48B8
red-54   L ticks 6333  deaths 38/7  max_instr 16184 hash 000000009FBA2FE2
## candidate v1 vs parent (blue only completed; red jobs killed)
parent-blue-{54,101,202} W ticks 16483 deaths 40/25 max_instr 17137 (identical stream)
Verdict: FALSIFIED / regression (blue vs Richard 0W/3L vs parent 3W/0L; 6 distinct streams; 0 vm failures; 0 invalid).

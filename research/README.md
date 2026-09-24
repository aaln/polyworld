# Score recovery on release62

Fresh engine checkout; no accumulated gameplay merges. The previous high-scoring deployed source29f6d7e6 is the historical reference, current source2fbd789b is the deployed comparison, and c2321ead is a weak-hero nearby-neutral hypothesis. None is assumed best on the current broad field.

Raw captured league evidence: /Users/aaln/experiments/softmax/polyworld/tmp/gota-khors180-observations-20260924

Start with [the current contract](CURRENT_CONTRACT.md) and [completed results](RESULTS.md). The 180-game comparison is complete: neither the previous policy nor the weak-neutral candidate passed the improvement rule. The deployed policy remains the working reference. The historical source is preserved for isolated, newly tested transfers.

Tested hypothesis: weak heroes directly finish nearby safe tier-eligible neutrals rather than spend time pulling waves or pursuing distant units. The candidate increased neutral kills overall but lowered mean score in this panel. Death Knight gained neutral XP without gaining score; Lich was encouraging in only four games. These findings do not support a general weak-hero rollout.

The [khors:v180 semantic model](opponents/khors-v180/README.md) uses 28 version-bound appearances. Historical inputs, failed experiments and frozen IR are preserved. No JEV integration is required.

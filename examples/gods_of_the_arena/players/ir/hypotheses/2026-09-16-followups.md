# Current follow-up state after cadence discovery

The historical hypotheses below led to the completed cadence screen and hosted
discovery. One-tick all-class recovery is now in independent400/arm confirmation;
do not modify it or inspect partial outcomes to choose a successor. A separate
IR branch under cadence-cycle/cadence-diagnostics/aligned-feedback aligns goals
with measured attack recovery; it must be merged with completed confirmation
evidence later. Source bytes remain unchanged.

Further observations from ALL300 discovery tapes for the two controls and the
cadence candidate:

- Hit frequency rose12.6–12.8 to21.3 per alive minute. Dominant repeated-hit
  intervals shortened in every class; post-hit median displacement was zero.
  Timing is supported, effective escape movement is not.
- Two candidate episodes had30second-plus stalls against friendly tower23.
  Prior tower-route16/40, tower-weapon18/40 and combined17/40 cells already
  failed local advancement, despite32707–40329 detour commands. Do not repeat
  the unchanged nearest-tower rerouting. A distinct future test could use a
  persistent intermediate destination and explicit exit/cooldown to avoid
  overriding pursuit on every tick. Necessity and win value remain untested.
- Cadence discovery Berserker3/10 versus waveguard8/10 is descriptive only.
  Class remains coupled to the fixed roster. The predeclared confirmation
  class guard will assess regression; do not choose class exclusions using
  unfinished confirmation games or call this intrinsic class weakness.
- End-of-game gold medians40/25/20 for cadence/motion/waveguard do not prove
  purchase starvation. End inventory and gold alone lack purchase timing and
  available-slot context. A new loadout test requires that causal trace.

The sections below retain the earlier predictions and caveats.

# Follow-up mechanisms, not evaluated candidates

Do not alter the running frozen economy screen or its hosted selection rules.

1. **Range-sensitive danger.** In9 hash-verified recent ranged-hero league
   tapes,12of24 deaths had at least one preceding half-second health-loss sample
   where every observed attacker targeting us was beyond5tiles. One Lich death
   and four deaths in its low-XP loss had no walk burst in the preceding6seconds.
   The selected motion controller uses a fixed5tile normal-trigger radius.
   Increasing it for ranged attackers or using observed damage/target intent may
   prevent late responses, but could sacrifice damage or retreat from safe
   creeps. The existing early-pressure candidate failed its old local screen:
   a new test must distinguish range coverage from simply raising HP thresholds.
   Evidence: `tmp/gota-ir/autoresearch-20260916/motion-diagnostics/range-findings.json`.
   Target intent plus HP loss does not identify every damage source; causal
   benefit remains untested.

2. **Attack recovery versus movement duration.** Published e127989 sim.nim
   lines2732–2757 applies a basic hit at45%of the class swing duration, restarts
   the swing after the duration, and sets swingTicks=-1 when marching. A legal
   one-tick movement followed by another attack may shorten recovery, at the
   cost of almost no displacement while turning. This is a source-derived
   hypothesis about ordinary legal commands, NOT a demonstrated faster cadence
   or a survival improvement. Test actual hit timestamps in the unchanged
   engine first. Contrast isolated recovery timing with a longer damage-aware
   escape; do not credit accepted movement as real kiting. Existing10tick and
   32tick retreat failures remain recorded and must not be reclassified.

3. **Purchase priority.** Current ordered-loadout candidates still buy
   consumables before equipment. If their completed traces show repeated
   consumable purchases starving the second weapon, test equipment priority
   only when gold already covers the next planned item, with an explicit lethal
   HP exception. No such priority change is in the running screen.

4. **Roster generalization.** The refreshed fixed-roster control batch has
   extreme class differences (e.g.waveguard Arcanist0/10,DeathKnight10/10).
   A policy's class is coupled to teammate/opponent placement under rotation;
   this does not establish intrinsic class weakness. Future studies can freeze
   several opponent-order permutations shared by all arms. The current study's
   fixed roster and separate sampled-field check remain unchanged.

## Bounded cadence probe result

On a verified Crossbow replay prefix at tick4680, the240tick probe with
one tick of legal post-hit walking produced7basic hits, versus3for attack-only
and4in the original recording. Repeated hit intervals shortened from36to17ticks.
Every arm still died and displacement was small: this supports the recovery
timing mechanism, not survival or competitive superiority. Peers and target
schedule retained their recorded commands, so this is not a full policy eval.
A first probe confounded cadence with stale target retention; corrected source,
old source/binary/output and all hashes are preserved. See RUN/cadence-finding.json.
No candidate or deployed policy has this timing change yet.

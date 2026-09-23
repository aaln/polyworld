# Gods of the Arena symmetry/Q16 optimizer

This is the source-backed neural lineage for the GotA symmetry release rooted
at Polyworld `02897e8201b9761be577587019c479973d9f08a6`. It is intentionally
separate from `gota-training-v5`: v5 remains the reproducible GameVersion 51
lineage, while v6 changes the observation, action, numeric, and reward
contracts.

The deployable actor is still a real RL policy: Metta PPO trains a 39-input,
configurable 1-32-hidden-unit ReLU network with 22 action logits, and `export.py` materializes
the trained weights into bounded BASIC Q16.16 arithmetic. The BASIC template
contains the deterministic legality shell for drafting, skill points, buyback,
shopping, potions, and keep defense.

## Contract

- Every spatial feature is expressed in one red-side team frame, then converted
  back to global coordinates only at the command boundary. The obsolete
  faction draft preference is removed.
- Inputs are Q16.16 values clamped to `[-1, 1]`. They include fractional
  health/mana, team geometry, class and legal ability readiness, objective state, nearby ally
  count, enemies focusing this hero, deaths, attack/portal/channel control
  state, and observed target velocity.
- Actions 0-17 retain the v5 combat/economy macros. Action 18 makes the existing
  specialist perimeter route reachable. Actions 19-21 are fractional kiting,
  velocity-led ground casting, and tower-anchored Portal Scroll relocation.
- Legal readiness combines learned rank, charges, cooldown, mana, exact
  class-specific cast range, and point-versus-target shape. Extended actions
  are exclusive rather than additions to a default attack. Unchanged attack
  targets are not reissued, Poison Potion requires the current in-range target,
  and each keep visit queues at most one purchase per decision.
- Draft scoring is team-symmetric and follows the current global balance:
  Crossbowman and Warlock receive priority after their 50% damage buffs, while
  Ranger is deprioritized after losing half of her HP growth. There is no
  faction-derived class bonus.
- Actor parameters are quantized with a straight-through 1/1024 grid during
  training and exported as decimal BASIC literals. Export performs interval
  checks against the Q16.16 range and the 64 KiB source limit. When a dense
  checkpoint would exceed that limit, export preserves the strongest input to
  every hidden unit and strongest output to every action, then deterministically
  prunes the smallest quantized connections to at most 320 input and 160 output
  connections. The layer-balanced 480-connection budget preserves a meaningful
  action head while leaving VM instruction headroom for class-dependent feature
  and control paths.
  Exact-release screens measure the resulting sparse actor, not the dense
  PyTorch checkpoint.
- The native training reward is the delta of the five controlled heroes'
  nonnegative lifetime-XP-minus-200-per-minute scores, averaged and scaled by
  1/1,000. The optional native terminal-credit patch adds a small win/loss
  signal; timeouts remain neutral. BASIC export does not change game rewards.
- Native environments rotate the official baseline and each supplied frozen
  opponent across seeds. The opponent-pool patch is part of the staged source
  contract; silently training against only one opponent is not allowed.

## Release gate

Do not train, upload, or request hosted XP merely because the upstream commit
exists. First capture the live Coworld environment and confirm that its exact
mechanics source is the deployed symmetry/scoring descendant. Pass that exact
commit as `RELEASE_COMMIT` to `prepare_symmetry_optimizer.sh`; the script
rejects commits that are not descendants of the reviewed symmetry base.

After staging, submit `build_smoke_mettabox.sbatch` first. It compiles the
native bridge, exercises all 22 actions, checks every observation is finite and
inside `[-1,1]`, and reports BASIC work/instruction maxima. Only then stage the
campaign on a B300 node, run `prepare_b300_runtime.sh`, recheck live Slurm
occupancy, and submit the bounded `train_pilot_b300.sbatch` pilot. The pilot
uses one B300, 24 CPUs, and 500 GiB: one eighth of the eight-GPU node.
The pilot defaults to zero baseline-action bias; the earlier `4.0` default
prevented the expanded action head from materially controlling behavior.
Both pilot launchers verify the staged training policy and frozen opponent
hashes before allocating environments, so a stale B300 campaign fails closed
instead of silently training a different contract.

Export and screen checkpoints under the exact deployed commit in both colors
against the official baseline, the lower owned champion, the protected owned
champion, public leaders, and diagnosed bad matchups. A candidate may be
uploaded with `--no-submit` only after source/VM smoke passes. Promotion still
requires completed hosted XP artifacts and must target the lower live owned
lane while protecting the other lane.

`screen_v57_checkpoint.sbatch` exports this lineage's 39×32×22 Q16 checkpoint
and runs exact GameVersion 57 replays in both colors against the official base,
relh v161, richard v153, and the last programmatic control. Public leaders are
then mandatory hosted-XP opponents because their policy source is not locally
available.

The optimizer archive has existed with both the nine-action `relu-mlp-v7`
contract and the later 18-action `relu-mlp-v8` contract. Preparation detects
the staged source contract and applies the corresponding checked v9 delta;
unknown contracts fail closed.

## GameVersion 58 pilot (2026-09-22)

The deployed `2026.9.22.3` release is pinned to Polyworld
`1b70894436b7ffdcd0d421b6b32c2415c9c8bfde`. Set
`GOTA_CAMPAIGN_DIR=/home/metta/relh-gota-symmetry-v58` when running the
preparation script to keep the earlier campaign intact. The checked bridge
commit produced by that staging run is recorded in its `bridge-commit.txt`.
`build_smoke_v58_mettabox.sbatch` targets the staging node, and
`smoke_v58_b300.sbatch` verifies that its transferred library and source run
inside the B300 container before `train_pilot_v58_b300.sbatch` begins.

The v58 pilot requests exactly one B300 from Slurm and refuses to run if the
visible GPU count is not exactly one. Its read-only mount of the older v6
campaign supplies shared Python dependencies; all optimizer output and source
for this release are isolated in `/home/ec2-user/relh-gota-symmetry-v58`.
The smoke exercised all 22 actions, reported 7,916 maximum BASIC
instructions and 12,978 maximum work, and exported a 23,692-byte BASIC
actor. B300 native smoke returned finite 39-feature observations.

The first pilot exposed a replay-verified shop loop: repeated equipment buys
were rejected as already equipped and full inventories provoked consumable
buys. The template now tracks each owned equipment ID and requires a free
slot for a new consumable. For a corrected parallel pilot, copy the v58
campaign to an isolated directory without its `train_dir`, replace only that
copy's `hero.bas`, refresh its `training-policy.sha256`, and submit the v58
pilot with `GOTA_CAMPAIGN_DIR` set to the isolated directory. This preserves
both the original run's checkpoints and its unchanged training contract.

An early corrected checkpoint collapsed to walking to its own keep on every
decision. A temporary healthy-hero route guard raised hits for that checkpoint,
but a later checkpoint lost a baseline win and its blue-side score with the
same guard. The guard was withdrawn; the separate staged route campaign was
not trained. Future action-selection changes must survive matched later-
checkpoint screens, not only rescue a collapsed early actor.

## Neural learning and compute use

This is reinforcement learning, not a hand-authored weight table: the native
Puffer environment pauses each of five controlled BASIC VMs at `chooseAction`,
Metta PPO updates a shared 39→32→22 actor, and `export.py` quantizes its
learned weights into BASIC. The current Metta tree vendors `pufferlib-core`
**3.0.23**. PufferLib 5 has a different native backend; a migration needs a
separate exact-v58 bridge, reward/observation parity tests, and a matched
checkpoint evaluation (see the [PufferLib 5 native environment guide](https://puffer.ai/docs.html)).
Do not label these existing pilots as PufferLib 5.

The 39→32→22 template is a **hybrid**, not the requested fully neural relh
submission. `hero.bas` chooses the draft, skill upgrades, buyback, shopping,
consumables, and emergency defense with hand-written rules; the network chooses
combat and movement macros inside that shell. A fully neural candidate must
put each of those decision families under learned control, with game-rule
masking for unavailable heroes, locked abilities, unaffordable items, invalid
targets, and portal channels. Deterministic observation encoding and legality
checks may remain in the runtime, but they must not choose a strategy in place
of the actor. Track the fraction of executed decisions by family and verify
that actor outputs, not fallback rules, selected them in exact-release replays.
The concrete phase, action-mask, and provenance requirements are in
[`FULL_NEURAL_CONTRACT.md`](FULL_NEURAL_CONTRACT.md).

Round 672 gives a current training target: relh v161 scored zero in five
hash-verified GameVersion 58 games spanning Vanguard, Death Knight, Warlock,
and Berserker. Two were team wins, yet the hero's XP remained below the
200-XP-per-minute score floor. A strong Warlock control scored 3805, so draft
class or spell use alone does not explain the gap. The exact IDs, XP margins,
and cast counts are in
`experiments/candidates/gods-of-the-arena-round672-relh-full-neural-target-20260923.yaml`.
Compare any new actor to relh v161 and Richard's protected champion in both
colors; require completed hosted XP against public leaders before submission.

The first two corrected pilots ran 16,777,216 environment steps each on one
B300 GPU per job. Exact-v58 mirrored replays showed early improvement against
the official baseline but neither terminal checkpoint beat the relh incumbent.
The documented 12.57–13.03 thousand steps/second measurements in
`experiments/candidates/gods-of-the-arena-release-neural-optimizer-20260922.yaml`
are from the earlier score-objective B300 jobs at their 2,097,152-step mark;
they are not a fresh GameVersion 58 throughput measurement. The v58 pilot
records establish step budgets and outcome screens, but do not preserve a
comparable SPS figure. Read its live progress log before quoting current
throughput or comparing it to another trainer.
In one terminal replay a hero sent 19,730 of 20,325 walk orders to its own
keep. A narrow keep-exit shell guard reduced the repeated orders but did not
win a match, so it was withdrawn. The next training question is whether longer
PPO optimization or better *per-hero* credit assignment fixes this behavior;
merely filling GPUs with copies of a weak seed is not evidence of learning.

The balanced 60x-sparse continuation from v16 (Slurm 4357) ran beyond the
earlier 6.3-million-step pilot. At v20, after 7,864,320 additional decisions,
the exact-v58 four-game screen lost both colors to the official baseline and
both colors to the frozen neural incumbent (mean candidate score 215.9). It
was stopped, and its exact named Docker container was stopped before Slurm
cancelation. A decoded GameVersion 58 replay shows why continuing the same
objective is questionable: Death Knight 104 issued 23,745 own-keep walks
among 23,750 orders after tick 5,000 and gained no XP for the remainder of the
match. A narrowly targeted keep-exit guard improved activity but still lost
to the incumbent, so it was not deployed.

The next experiment, `polyworld-unclipped-time-credit.patch`, keeps the hosted
score reward unchanged and adds 20% of its *unclipped* XP-minus-time delta as
an auxiliary training signal. This specifically makes time spent idle costly
after the public score has clipped to zero; it does not change game mechanics,
observations, actions, or the deployed BASIC policy. The isolated bridge is
`01ff66fd125b83dbb8a9de7b464d87ad9bd5e555`; the canonical release
remains `1b70894436b7ffdcd0d421b6b32c2415c9c8bfde`. The isolated Metta
environment uses `metta-rawcredit-commit-pin.patch` so it validates that
bridge without modifying the control campaign. A paired 1,024-step native
smoke with identical seeds and retreat actions found identical observations
and state hashes on every step; 408 rewards changed, all from zero to
negative. `verify_v58_rawcredit_reward.py` is the reproducible check.

The first raw-credit run accidentally loaded the *balanced continuation* v16
checkpoint (mean 91.55), not the stronger *scaled sparse* v16 checkpoint
(mean 318.45). After 1,572,864 fresh steps, its v4 improved to mean 231.1
but won none of four exact-v58 games. Both parent controls were reproduced
through the canonical worker. Preserve this weaker run for analysis; the
corrected matched continuation starts from the stronger scaled checkpoint.
Check full checkpoint ancestry before interpreting a run tag.

The corrected run from that stronger checkpoint was also stopped at a bounded
3,145,728 fresh steps. Its exact-v58 four-game means at v2/v4/v6/v8 were
126.35/195.55/86.0/194.6, with zero wins at each checkpoint, versus the
parent's 318.45. V8 scored only 3.2 and 9.6 against the frozen neural
incumbent in red and blue. A v4 native audit found argmax action selection
concentrated on retreat (2,322/8,192) and W (5,870/8,192), with every other
macro at zero. At scale 60, mean top action probability was only 0.206;
training already uses this scale, so this is not an omitted-scale bug. The
remaining sampling-to-deterministic-deployment mismatch and two-macro
collapse warrant a separate source-backed experiment, not more steps under
the failed reward alone. No raw-credit checkpoint was uploaded.

## V161 neural-weight transfer into v58 (2026-09-23)

The older relh v161 neural checkpoint is a genuine 25→16→18 PPO actor that
still beats the new v58 checkpoints locally. Its original binary weights are
preserved in the B300 v5 release campaign. `map_v51_checkpoint_to_v58.py`
embeds that actor into the 39→32→22 checkpoint shape, scaling its first-layer
weights by 100. The isolated `metta-v51-feature-warmstart.patch` makes the
first 25 Q16 observations reproduce the old feature values divided by 100;
the other 14 new observations remain available for fine-tuning. The older
actor's four missing actions start with low biases rather than fabricated
learned weights. The mapper tests 1,024 random feature vectors and records
the maximum old/new logit difference before writing the checkpoint (6.11e-5
for this transfer).

The standard 320/160 sparse mask removed 208 of the legacy actor's 688
connections and its exact-v58 screen went 0–4, mean 33.7. In an isolated
Metta copy, `metta-v51-full-head-warmstart.patch` raises those two masks to
400/288 so PPO sees what BASIC exports. The full-connection BASIC is 40,662
bytes and its four exact-v58 replays have zero hash mismatches, no VM failure,
maximum 14,830 instructions and 23,810 work. It went 1–2–1, mean 329.8,
including a blue-side baseline win, but still lost both incumbent matches.
This is a *training start*, not a candidate upload.

On 8,192 native decisions from the mapped actor, scale 60 made the training
distribution almost deterministic (mean top probability .995); scale 1 gave
.582 and entropy 1.039. The isolated
`metta-v51-warmstart-temperature.patch` sets PPO scale 1, leaving BASIC
argmax unchanged. `verify_train_logit_scale.py` checks the actual forward
against the exported 400/288 mask. Fine-tune this source- and checkpoint-
backed branch in bounded Slurm runs; keep the v161 checkpoint and both control
screens intact. The transfer is useful only if later exact-v58 mirrored
screens and hosted XP beat the lower owned champion and public leaders.

The source-backed `train_scale_v58_b300.sbatch` began this continuation on
one B300 GPU as Slurm job 4487, with 24 CPUs, a 33,554,432-step cap, a frozen
official/incumbent/programmatic opponent pool, and the mapped v161 actor.
Its exact-v58 four-game checkpoint screens at 786,432, 1,572,864,
3,145,728, 4,718,592, and 6,291,456 fresh decisions scored mean
344.45/358.0/361.3/217.5/114.55, respectively. Each won at most the
official baseline match and lost both colors against the neural incumbent.
At v16 it lost three and timed out once, with no wins. The exact trainer
container was stopped and the Slurm job ended after this bounded screen;
continuing the same branch was not justified. No checkpoint was uploaded.

An incumbent-red replay suggested Ranger draft exclusion might explain weak
XP: the opponent Ranger earned 4,153 XP while the candidate lineup had no
Ranger. `make_v58_ranger_draft_variant.py` changes only the Ranger draft
score in a checkpoint export, and `screen_v58_policy_b300.sh` measures that
source under the canonical v58 worker. The first four-game test at v4 favored
the variant (467.25 versus 358.0 mean score), but a fresh-seed, matched
16-game test reversed it: 224.81 versus 252.56, with zero versus four wins.
At v8 the four-game variant also regressed to 58.3 versus 361.3. The Ranger
change is withdrawn; neither variant nor continuation checkpoint was uploaded.

## Actor-attributed score-credit probe (2026-09-23)

The canonical v58 native bridge emits the five-hero score delta only when a
tick advances. In a 12,000-decision baseline audit, 5,801 rewards were
nonzero and every one occurred on a tick advance; each hero acts at a
different frequency. The failed v161 transfer continuation sharpened the
question: after 6,291,456 fresh decisions its four-game exact-v58 mean was
114.55 with zero wins, below the earlier v8 checkpoint mean 361.3.

`polyworld-actor-score-credit.patch` is an isolated *training reward* change.
It leaves the actual hosted score, game mechanics, observations, actions, and
deployed BASIC untouched. Half of each reward remains the canonical
five-hero score delta; half follows the acting hero's own clipped
XP-minus-time score potential, paid on that hero's next decision. This shifts
credit from the actor that happens to advance the tick toward the hero whose
score changed, while retaining the same objective. The staged bridge commit
is `1b743e3e287a713dd1cedf20e26dba92f2fd21c0`, with the paired Metta
pin in `metta-actor-score-credit-commit-pin.patch`.

The CPU-only B300 build used `build_v58_actorcredit_b300.sh`; its native
library SHA-256 is
`adca7754cf918bf0ae7373bde3d7ccb863565b85d2ff41b7ffd1aa382c74dc64`.
`verify_v58_actor_score_credit.py` ran 8,192 paired baseline-action decisions
against the unchanged v58 bridge: all observations, terminal flags, and
state hashes matched; 1,787 rewards changed, including 175 actor-credit
rewards where the team-tick reward was zero. Cumulative reward was 0.1036333
for control and 0.1037167 for actor credit. A retreat-only probe was
uninformative because it generated no positive hosted-score events; it was
replaced before training.

Slurm job 4566 was a bounded, one-B300-GPU matched continuation from the same
validated v161 checkpoint as job 4487, with the same 3e-5 learning rate,
0.005 entropy coefficient, full 400/288 actor mask, and frozen balanced
opponents. It stopped after the bounded v12 screen (4,718,592 fresh steps),
not its 16,777,216-step cap. Exact-v58 v2/v4/v8/v12 four-game means were
371.25/342.1/189.8/249.3; none won against the frozen incumbent in both
colors, and v4/v8/v12 lost both colors. The v12 native action audit selected
only legacy actions 13/15/17 in 4,096 decisions. The exact trainer container
was stopped and Slurm ended; no actor-credit checkpoint was uploaded.

## Cloned-head exploration probe (2026-09-23)

The action audit exposed a separate initialization bug: the old 18 heads had
maximum logits of 108–187 on real v58 observations, while new heads 18–21
were fixed at −2. Their combined sampling probability was effectively zero
even at PPO logit scale 0.25 (about 1.2e-13 over 4,096 decisions). Lowering
temperature alone is therefore *not* a new-ability experiment.

The optional `--clone-new-heads --clone-bias-gap 4` mapper initializes new
heads 18–21 from related legacy heads 17/13/15/17, each four logits lower.
This preserves all old-action logits and the initial argmax while giving the
new actions a measured 24.6% combined sampling mass at scale 0.25. The
isolated `metta-v51-explore025-temperature.patch` changes PPO scale 1→0.25;
`metta-v51-cloned-head-352.patch` raises both the PPO and BASIC output masks
288→352 to retain all 18 legacy and four cloned 16-weight rows. The mapped
checkpoint weights SHA-256 is
`0f0d1cb5a05e4957b3cf7b7e5b0052bf48c94bf9dc54980730e8643b6b920940`.

The actual PPO forward/mask check passed at scale 0.25, 400/352. Its untrained
42,158-byte BASIC export reproduced the earlier mapped policy's four exact-
v58 results exactly (1 win, 2 losses, 1 timeout, mean 329.8, zero replay-hash
mismatches). Job 4752 began from that checkpoint with the unchanged v58
team-score reward, but was stopped before its first checkpoint when the repo's
new `docs/slurm.md` rule landed: it caps GotA campaigns at **two B300 GPU
allocations across running and pending `metta` jobs**. The job's two-slot
reservation plus an existing one-slot job exceeded that cap. The exact Docker
container stopped, Slurm ended, and no training result is claimed.

An unrelated process occupied Slurm's first available B300 GPU, so the
source-backed `train_explore025_b300.sbatch` defaults to two Slurm GPU slots,
rejects any allocated device with ≥1 GiB memory or ≥5% utilization, and runs
Docker only on a physically idle device. A one-slot submission can override
the directive with `sbatch --gres=gpu:nvidia_b300_sxm6_ac:1` if a fresh
physical check shows that Slurm's selected device is idle. This design may be
submitted **only** when `co-gas gota slurm-capacity` allows the exact planned
one- or two-slot request after a fresh `squeue --json -u metta` capture. If
the only one-slot device is physically occupied outside Slurm, the launcher
fails closed; do not bypass Slurm's device assignment. On the first post-stop
check, one B300 job was running and another was pending; the checker counted
both (existing 2, requested 2, disallowed).
Three mettabox nodes were occupied, and B200 was fully allocated by nightly
work. Do not queue this campaign merely to wait for capacity; recheck before
submission. Once permitted, screen early checkpoints and stop regression.
The source-backed CPU-only `audit_v58_expanded_actions.py` forced all 22
macros 372–373 times each across 8,192 native decisions, including the four
new macros, and observed finite data with maximum 11,615 BASIC instructions
and 19,713 work, below the 20,000/50,000 VM allowances. This is a compatibility
smoke, not an RL result or promotion evidence.

Treat any raw-credit checkpoint as experimental until its exported BASIC
passes exact-release screens against both champions and public leaders. Use
`build_v58_rawcredit_mettabox.sh` and the checked scale launcher for the
isolated campaign; preserve the control checkpoint and benchmark both at
matched seeds. Stop unpromising runs at a checkpoint screen instead of
spending millions more steps on a demonstrated regression.

Use Slurm for every long run. Count all owned and other relh allocations before
launching, keep at most three accelerator jobs across B200/B300 (and at most
three of the five mettaboxes), and make each run independently informative:
distinct warm-start checkpoint/seed or a replay-motivated reward contract.
Keep one evidence-generating GotA neural run active whenever the exact-release
environment, verified physical device, and tighter `docs/slurm.md` capacity
gate permit it. A training run is evidence-generating only if its source,
checkpoint ancestry, opponent pool, reward contract, and first mirrored
checkpoint screen are recorded; an idle allocation or a long continuation of
an already-regressing branch does not satisfy this operating target. Recheck
`squeue --json -u metta` with `co-gas gota slurm-capacity` before each launch,
including pending jobs and unrelated `metta` work. If the checker denies even
a mettabox-only request because existing B300 reservations exceed the global
two-GPU campaign cap, preserve the staged campaign and resume at the next
compliant window instead of bypassing Slurm or displacing another job.
Check `docker ps` and physical GPU processes as well as Slurm: canceled Docker
trainers have survived Slurm cancellation on B300. The scale launcher names
its container `relh-gota-$SLURM_JOB_ID` and attempts an EXIT/TERM cleanup,
but cancellation of job 4210 proved that trap is not reliable under `scancel`.
Before canceling a running Docker-backed job, stop its exact named container
on the allocated node, then cancel the Slurm job and verify `docker ps` and
`nvidia-smi`. Never infer physical GPU release from `squeue` alone.
Reserve one mettabox for exact-release checkpoint export/replay audits while
training runs. Record the source, template, opponent pool, reward contract,
checkpoint URI, seed, step count, Slurm job ID, GPU visibility, and local
behavior in `.runtime/`. Screen selected checkpoints in both colors as they
appear; use completed hosted XP against the live leaders and incumbent before
any promotion. A billion steps is a scale target only if measured learning
continues, not an automatic acceptance criterion.

### Keep-idle credit experiment

The control continuations were stopped after checkpoint screens showed
regression at both 3.1M and 7.9M additional steps. One exact-v58 failure
replay had 19,730 walk orders aimed at the own keep, while the earlier
baseline-winning checkpoint had zero such orders. The optional
`metta-idle-keep-credit.patch` changes only the native training reward: when a
hero already at the keep, at least 95% healthy and 75% supplied, with no
visible home threat chooses either retreat macro, it subtracts `0.0001` from
that decision's reward. It does not edit the BASIC actor, game simulation,
match score, legal wounded retreats, or keep defense. Its synthetic mask test
is `verify_idle_keep_credit.py`. Apply it only in a separate campaign, record
`native.py` SHA-256 in `reward-contract.sha256`, and compare a warm-started
checkpoint to its unshaped parent under identical exact-v58 replay seeds.
If it does not improve both-color behavior, stop that experiment and revisit
the reward/credit contract rather than scaling it to a billion steps.

### Native terminal-outcome credit experiment

The active PPO recipe uses `NativeGotaPufferEnv`; its C/Nim bridge rewards the
change in the controlled team's hosted XP-score potential, not the similarly
named reward function in `environment.py`. A completed exact-v58 replay of a
baseline-winning checkpoint lost its god to the incumbent with a -25,953
structure-HP difference despite 15 kills by the inspected hero. To test
whether objective conversion needs more credit,
`metta-native-terminal-credit.patch` adds a training-only +0.25 reward for a
win and -0.25 for a loss after the native step, equivalent to 250 hosted-score
points; time-limit endings stay neutral. It also corrects the native info
label that otherwise reports a time limit as a loss. The unmodified dense
score reward and BASIC/game mechanics remain intact.

`verify_native_terminal_credit.py` exercises the actual native `step` path
with win/loss/timeout transitions and runs a two-lane GameVersion 58 smoke,
including a real short timeout. Apply the patch in an isolated campaign,
record the `native.py` SHA-256 in `reward-contract.sha256`, and warm-start a
matched seed/optimizer checkpoint. Compare exact-version mirrored screens to
the unshaped control before spending more GPU time. A prior attempt changed
only `environment.py`; it did not affect this native training path and was
reverted rather than treated as evidence.

### Checkpoint stability experiment

The matched seed-580322 unshaped continuation won both baseline-color games
after 1.57M fresh steps, then lost both by 3.15M steps; the shaped branch
fixed one idle-keep replay but did not beat the matched control or incumbent.
Preserve the strong early checkpoint and test whether less aggressive PPO
updates prevent this rapid regression. `train_scale_v58_b300.sbatch` accepts
optional positional learning rate and entropy coefficient after campaign
directory (defaults `0.00005` and `0.02`). A low-rate continuation from that
checkpoint is a separate Slurm run with a distinct seed/tag and the same
frozen game/opponents. Compare its matched-step exports against the original
run and incumbent in both colors. Stop it if the exact-version screens do not
improve; do not promote based only on smoother training curves.

### Sparse-forward parity experiment

The standard PPO forward uses all 1,248 input and 704 output connections,
but the deployable BASIC actor keeps at most 320 and 160 respectively. In
exact-v58 screens, both low-rate and mid-rate continuations changed quantized
weights through 4.7M steps without changing any of four game scores or the
incumbent-red action-count vector. A wider 500/250 export of the same early
checkpoint was worse, so simply raising the BASIC budget is not supported.

`metta-sparse-forward-parity.patch` applies the exporter's row-protected,
smallest-first mask to quantized weights **during PPO forwards**. It leaves
the BASIC exporter, reward contract, opponent pool, and simulation unchanged.
`verify_sparse_forward_parity.py` compares its selected weights and logits to
the export rule on random, tied, zero, CPU, and CUDA cases and checks that
retained weights receive gradients. With `--campaign` and `--checkpoint`, it
also samples exact-release native observations and reports where dense and
sparse argmax actions differ. On 2,048 sampled v58 decisions from the v8
checkpoint, the logits differed but argmax actions did not; the mismatch is
therefore still an unproven explanation of competitive losses. The staged
actor SHA-256 is pinned in `sparse-forward-actor.sha256`; the Slurm launcher checks
`actor-contract.sha256` when present. This is a training experiment, not a
candidate: screen exported checkpoints in both colors against the frozen
baseline and incumbent, and proceed to hosted XP only if the exact-version
behavior improves.

### Training-logit scale experiment

The sparse-forward v4/v8/v12 BASIC screens all reproduced the same four game
outcomes and audited incumbent event summary. Native v58 observation sampling
at v16 (6.3M fresh steps) exposed a more direct training/deployment gap: the
largest of 22 PPO action probabilities averaged 4.773% (uniform is 4.545%),
entropy was 3.0909 (the maximum is ln 22 ≈ 3.0910), while deterministic BASIC
argmax chose action 4 on every one of 2,048 sampled decisions. More PPO steps
with this distribution are not automatically meaningful.

`metta-train-logit-scale.patch` multiplies the sparse actor's logits by 60
*before PPO action sampling*; positive scaling leaves BASIC argmax and exported
weights unchanged. On those same v58 observations, 60× would yield mean top
probability 45.3% and entropy 2.216, allowing exploration without a nearly
uniform sampling policy. The staged source hash is
`scaled-sparse-actor.sha256`. Test this as a separate lower-learning-rate
warm-start run; exact-version both-color checkpoint screens, then hosted XP,
remain the gates. This is a measured training hypothesis, not a demonstrated
competitive improvement.

The 60× continuation through 6.3M fresh steps was not competitive: its
v4/v8/v12/v16 exact-v58 BASIC screens never beat the frozen incumbent neural
policy and finished below the unscaled control's four-game mean score. The
checkpoint's sampled native policy still selected the same argmax action on
8,000 decisions. Stop weak runs at diagnostic checkpoints, preserve their
artifacts, and investigate specific replay behavior before spending another
multi-million-step budget. A replay of v12 identified Portal Scroll channel
orders rejected by the game. A shell guard reduced those rejections but
regressed the matched four-game screen, so it was not retained in the policy.

The later scaled-v16 actor is not literally fixed to one action. A 40,000-
decision native-v58 sample chose retreat 10,023 times and cast-W 29,977 times.
W was ready on only 17,662 of those cast-W choices; its existing attack
fallback is therefore part of the learned behavior. Masking cast-W whenever
it was unready dropped the matched four-game mean from 318.45 to 48.75, so
that mask was withdrawn. Use `audit_v58_readiness_b300.sh` on a Slurm CPU
step to reproduce the observation and spell-readiness audit. It deliberately
requests no GPU and uses the source-pinned native-v58 bridge.

The exact-v58 baseline-red v16 replay also exposed a severe individual
failure: one controlled Death Knight issued 23,745 own-keep walk orders after
tick 5,000 and earned no additional XP beyond 111. A broad healthy-keep exit
guard and two narrower tests changed that behavior but did not improve the
four-game incumbent comparison, so none entered the training template. A
single B300 Slurm continuation from v16 with a balanced, rather than
incumbent-heavy, opponent pool is a bounded test of whether further PPO can
develop useful action diversity. Screen checkpoints and stop it if behavior
or exact-v58 matchup results fail to improve; do not infer competitive value
from steps completed alone.

For checkpoint screens in parallel with that GPU run, stage
`screen_v58_checkpoint_b300.sh` into the campaign and run it as a CPU-only
Slurm step with the checkpoint directory and a unique screen tag. It verifies
the pinned bridge/opponents, exports the BASIC source, and audits four exact-
v58 games (both colors against the official baseline and frozen incumbent).
Re-exporting the preserved scaled-v16 checkpoint yielded the identical
`b3ccd703…` BASIC SHA and four-game mean 318.45, which checks that the screen
script did not change the comparison before testing new checkpoints.

### Live v161 failure sample (round 669, GameVersion 58)

Four zero-score relh episodes were downloaded and fully replayed with the
current-release auditor; all four had zero state-hash mismatches. The
stable-player-ID-mapped traces are in
`.runtime/gota-neural-continuation-20260923/neural-v161-zero-score-audit.json`.
Three heroes drafted Death Knight and issued attack-target for 85–92% of their
orders. Each left its passive at level zero, died five or six times, and
repeatedly targeted unavailable or out-of-range objects. Two of those games
were team wins despite relh's zero individual score, so low score alone does
not establish a lost match. The fourth hero drafted Demon Hunter, died eleven
times, and triggered 219
inventory-full and 278 cooldown rejections. These observations motivate
checking draft, skill allocation, and legal-action behavior in the next
trained policy, but do not establish that a particular mask or draft override
wins. The earlier GameVersion 51 passive-unlock hybrid v162 was held because
its hosted panel reduced Richard's score, so repeating that change without a
new paired test would not be a justified promotion. Preserve v161 until a
source-backed neural replacement passes exact-release screens and
completed hosted XP against the public leaders and both owned champions.

Round 670 provided an independent same-release check: five more relh
zero-score replays hash-verified, four as Death Knight and one as Vanguard.
Across rounds 669–670, seven of nine relh zero-score games drafted Death
Knight; six of those seven ended with its passive locked. The stable-ID-mapped
episode details and rejection counts are in
`.runtime/gota-continuation-20260923-pass14/cross-round-v161-failure-synthesis.json`.
Richard's single round-670 zero-score game was Warlock, leaving him second
while relh remains fifth in the completed public division. The observed
pattern is a concrete training target for draft and skill choice, but the
earlier v162 paired XP result still rules out promoting an untested passive
override as the answer. The live Slurm capacity check for one GotA B300 GPU
was denied because running and pending jobs already exceed the campaign
limits; preserve the staged training scripts and recheck before launch.

Round 685 adds five more low-score v161 examples under the same release.
The exact-release audits in
`.runtime/gota-continuation-20260923-pass9/round685-relh-low/` verify every
replay hash and map the actor to relh's stable player ID. Four heroes drafted
Death Knight (scores 0, 0, 9, and 441); the other drafted Vanguard and scored
zero despite a team win. Two choices were avoidable at the observed draft:
the first-pick Vanguard had all ten classes available, and a first-team
Death Knight had both Ranger and Crossbowman available. Both were explicit
policy draft orders, not deadline autopicks. The other three Death Knight
picks had no carry left. This makes phase-aware draft control a concrete
requirement for a fully neural candidate, while preserving the caution from
the held v168 neutral-draft test: changing melee picks alone left relh at
zero and dropped Richard from 1506/888 to zero in two paired games.

A fresh Slurm check at 2026-09-23 13:54 UTC counted nine running or pending
B300 GPUs against the campaign limit of two. A concurrent capacity-checker
fix correctly counts zero mettabox jobs in that snapshot; its earlier count
of five included non-4090 partitions. No GotA training job was submitted.
The current-release trainer still
has no preserved comparable SPS figure; the earlier 12.57–13.03k SPS B300
measurements above must not be relabeled as GameVersion 58 throughput.

### Relh v169 draft-head interim promotion (2026-09-23)

The [candidate record](../../../../../experiments/candidates/gods-of-the-arena-relh-draft-head58-diagnostic-20260923.yaml)
links the exact v58 replay states, learned draft-head source, paired hosted XP,
and live membership readback. On four fixed-roster, fixed-seed controls,
relh's scores changed from `[0, 0, 0, 0]` to `[2318, 6969, 0, 2637]`.
Richard's scores in the two shared-roster pairs were unchanged or higher.
All eight completed replays hash-verified and had no VM failures. V169 was
therefore submitted only to relh; Richard v195 remained champion. At the
immediate readback, the leaderboard still reflected v161's previous games,
so a live v169 rank gain remains unverified until a completed public round.

This is an **interim hybrid**, not the requested fully neural relh policy.
Its learned head makes draft choices, while the existing BASIC shell still
makes skill, buyback, shop, consumable, portal, and some combat decisions.
The phase/action requirements and actor-provenance checks for the later
full-neural submission are in [FULL_NEURAL_CONTRACT.md](FULL_NEURAL_CONTRACT.md).

The first completed public v169 round was #688: relh appeared 13 times,
averaged 1688 score (360–2710), and had the highest per-round average in the
field. The rolling ladder still placed relh fifth and Richard fourth after
that round. Three sampled exact-release replays hash-verified. The lowest
relh game was a forced Berserker final pick; another low game chose Warlock
from five classes after both ranged carries were gone. The result verifies
live compatibility and a promising round, while leaving the top-two goal
open. Continue using completed public rounds and paired XP for replacement
decisions rather than treating this one-round average as a rank forecast.

## GameVersion 59 release drift (2026-09-23)

The GotA league now points to Coworld `2026.9.23.1`, sourced from Polyworld
`d6827a4bd3a55a46cf86f88e921f147137709c64`. Its replay format is 6 and
gameplay version is 59. The current content diff raises Ranger HP per level
from 19 to 29, lowers Crossbowman base damage from 69 to 58, raises Demon
Hunter's Gale Slash damage from 52 to 65, and raises Death Knight's Sanguine
Chalice heal from 36 to 45. The prior v58 draft-head and hosted XP results
are historical; any replacement needs a hash-verified v59 failure and v59 XP.

The local `gota_audit.nim --smoke` runner had been initializing a replay with
`maxTicks=0`. It completed the draft, then stopped before a battle tick while
appearing to pass its VM check. The runner now sets the requested battle
budget and reports phase, draft turn, draft ticks, and battle ticks. Against
the exact v59 source, 3,000-tick smokes for the active relh v169 and Richard
v195 sources both reached 2,891 battle ticks with no VM failure; relh's team
heroes earned 5,449 XP and Richard's earned 4,910 XP in separate self-play
smokes. These checks establish source compatibility only. The `--match` path
also now sets its intended 28,800-tick battle budget.

Two completed round-689 relh v169 zero-score losses have now been audited
against that exact v59 source with zero replay-hash mismatches. The Arcanist
game had 13 deaths, 103 full-inventory buy rejections, and 12 unavailable-
target casts. The Druid Warden game had 1,497 unavailable-target rejections
among 1,592 slot-one casts. Its slot-one Healing Bloom is an allied heal,
while the deployed BASIC shell targeted observed enemies. An instrumented
replay confirmed an enemy creep target in that loop. A v59 candidate now
targets the injured Druid instead; matched short local smoke removed 733
unavailable-target casts for one Druid, but XP did not improve. Do not
promote on that local smoke alone; completed hosted XP is still required. The
immutable loss scope is `.runtime/gota-v59-relh/environment-loss-3f09.json`,
with replay downloads and audits under `.runtime/gota-v59-relh/`.

At 16:05 UTC on September 23, three `metta` B300 GPU jobs were running.
That already exceeds this campaign's two-GPU cap, so no v59 B300 optimizer
was launched. Recheck the whole queue and physical GPU use before any
subsequent submission.

The hosted v170 test confirms the ability-target fix but does **not** support
promotion. In a decoded v59 Druid game, unavailable-target casts dropped
from 1,330 for v169 to zero for v170; v170's Druid reached 3,147 XP but
still scored zero. Four eight-game mixed-leader XP requests in two fixed
positions favored v169, as did a four-game original-loss-roster test. These
requests had independent seeds and sometimes different draft classes, so
the score gaps are decision evidence against replacing a champion, not a
clean causal estimate of the range gate. The complete artifacts and hold
decision are in the v170 candidate record.

V171 isolates **only** the Druid healing correction, leaving v169 behavior
for other classes. Short exact-v59 red/blue smokes had no VM failures and
removed the Druid's rejected enemy-heal casts. Its four-game hosted
original-loss-roster screen scored `[0, 0, 0, 0]`; two Druid appearances
had zero target-unavailable casts, and one earned 3,119 XP, yet both scored
zero. V171 is therefore also held. Neither hosted version was submitted:
relh v169 and Richard v195 remain champions. After public round 690,
Richard ranked second and relh fifth. In the exact v59 source, `scores()`
in `sim.nim` reports win flags, while `scores.nim` computes the platform
score from lifetime XP minus 200 XP per simulated minute, rounded down and
clamped to zero. The Druid's zero score cannot be attributed to its loss
without checking duration and XP. The separate full-neural contract is
still unmet.

Before resuming PPO on v59, verify that its reward tracks the actual
XP-per-time leaderboard score. Victory grants every allied hero 500 XP and
can shorten the time penalty, but losses and timeouts retain their own
time-adjusted XP. An exact round-690 timeout replay with 29,821 ticks and
4,180 XP scored 38; the `scores.nim` formula reproduced all ten hosted
scores, including that nonzero timeout score. The audit is recorded under
`.runtime/gota-neural-phase-20260923/round690-score-contract.json`.
Evaluate survival, last hits, and objective pressure by how much they raise
this score; do not substitute win flags for it. Confirm native transitions
and exported BASIC behavior on exact v59 replays before a capped Slurm
pilot. The earlier v58 checkpoints and PufferLib 3 bridge are not a v59
full-neural run, and an idle GPU alone is not a reason to restart them.

### V59 native numeric bridge (2026-09-23)

The official v59 Polyworld `training.nim` existed but disabled fixed-point
BASIC arithmetic. Its `chooseAction` callback took integer observations,
truncating fractional coordinates and other numeric features. Its reward
was team XP difference plus structure HP and a terminal win bonus, not the
hosted score. The reproducible overlay
[`polyworld-v59-numeric-score.patch`](polyworld-v59-numeric-score.patch)
applies with `git apply --unidiff-zero` to exact source commit
`d6827a4bd3a55a46cf86f88e921f147137709c64`. It preserves fixed-point
features and emits normalized floats. A full-length baseline rollout ended
at tick 9,491 with only 2,491 XP across its five heroes and zero hosted
score; the prior terminal-corrected reward also summed to zero. That made
the pilot's starting experience nearly uninformative. The revised reward is
`delta_owned_team_xp / 20,000` on every decision plus exact hosted team score
`/ 5,000` at match end. This auxiliary XP credit is deliberately **not**
score-exact: it teaches below the hosted zero floor, while promotion still
depends on the exact hosted score. Three ABI fields expose owned-team XP,
raw score numerator, and clipped hosted score numerator for parity checks.

The existing Metta Puffer 5 adapter also needs the same apply flag for
[`metta-puffer5-v59-numeric.patch`](metta-puffer5-v59-numeric.patch),
which pins the v59 source, updates the native transition layout, and keeps
the BASIC encoder in Q16.16 range. Its native path verifies the exact
trainer-file SHA-256 and rejects any other tracked Polyworld modification.
The patched Metta adapter passed a reset/step smoke through the numeric
environment contract. The repo-local
[`hero_v59_numeric.bas`](hero_v59_numeric.bas) is that exact patched encoder.
Build the Polyworld library against the exact source and dependency lock;
then run [`verify_v59_numeric_bridge.py`](verify_v59_numeric_bridge.py) with
`--repo`, `--library`, `--policy hero_v59_numeric.bas`, and
`--source-commit`. The revised bridge completed an exact-v59 9,491-tick
baseline loss (seed 17) with 180,317 fractional feature values, no VM
failure, and 0.12455 total reward despite zero hosted score. These are
integration smokes, **not** evidence of learning or a deployable checkpoint.
The current 22-action actor still delegates draft, skills, shopping, and
some combat choices to BASIC, so this bridge does not satisfy the full-neural
contract. Train and evaluate only under a current Slurm capacity check.

The bounded [Puffer 5 pilot](train_v59_puffer5_pilot.py) and
[metta0 Slurm job](train_v59_puffer5_metta0.sbatch) are staged for 131,072
steps, eight environments, and a 14,400-tick match cap. The pinned adapter
passed a reset/step check on metta0. At 17:45 UTC, the required
`co-gas gota slurm-capacity` check rejected submission: five running or
pending `metta` B300 GPU requests exceeded the two-GPU campaign limit.
No v59 Puffer 5 GPU job was submitted. The library was subsequently rebuilt
through Metta's lock-verified native builder, with the exact v59 dependency
lock synchronized. The rebuilt library SHA-256 is
`0eff70eb8ab111e76eaf9f7027d18184a1a3a07dd7bd913785785bc1446f49d3`;
the same bytes were staged on metta0. That was the earlier score-only reward
bridge, now superseded by the auxiliary-XP bridge. The revised lock-verified
library SHA-256 is
`7f6e049967dbaf67de7dc048b1e665c650f55ecc22287a2a3280ef66a6be7b2b`.
It replaced the staged metta0 library, and the patched adapter passed a
remote reset/step check. When staging only the GotA Metta subtree, include
`metta/rl/external_envs/__init__.py`: without it Python selected an older
installed `gota.native`. The Slurm script now asserts the imported module
path before training. At the next queue read, a separate Puffer 5
job had taken metta0 and the B300 over-cap remained. Repeat queue,
`co-gas gota slurm-capacity`, and physical-GPU checks before submission.
A dry-run configuration or an idle mettabox alone does not override a
failed capacity gate.

The v59 BASIC exporter also had a deployment-scale mismatch: Fabric multiplies
normalized actor inputs by `0.01`, but the old exporter omitted that scale and
accumulated integer-scaled logits. Fractional BASIC observations promote these
expressions to signed Q16.16, whose intermediates wrap above 32767. Apply
[`metta-v59-q16-safe-export.patch`](metta-v59-q16-safe-export.patch) after the
numeric adapter patch. It emits the quantized actor in bounded decimal BASIC,
retains Fabric's `0.01` input scale, and rejects Q16.16-unsafe weights. A
one-hidden-unit synthetic actor on the exact v59 simulator produced different
red-team movement before and after the fix (the old actor left its keep;
the corrected actor selected the expected retreat); neither VM reported an
error, showing why a compile-only smoke would miss this. This is an exporter
regression test, **not** a trained-policy performance result.

At 18:16 UTC the live league switched to GotA `2026.9.23.2` (source commit
`fd315c8fa30f8923c7a7709a577c40ac071b1c2a`). That source removes
automatic hero spell casting and changes the bundled BASIC player. The v59
trainer must not be started or promoted against this release. First capture
and replay-audit a completed v60 failure, update the opponent snapshot, then
repeat export parity, short smoke, and hosted XP before considering either
champion lane. The unchanged `training.nim` accepts the numeric overlay byte
for byte on `fd315c8…`; apply
[`metta-v60-release-pin.patch`](metta-v60-release-pin.patch) after the numeric
and safe-export Metta patches. The new dependency lock pins Bassy
`b25e0efe…`; a lock-verified native build produced a 272-byte transition and
passed a v60 adapter reset/step. A 3,000-tick seed-18 diagnostic had 54,440
fractional feature values, no VM failure, 401 owned-team XP, and 0.02005
training reward. Its hosted score remained zero. These are infrastructure
checks only; the live v60 replay gate and GPU capacity gate remain open.

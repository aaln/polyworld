# khors v114 and our low-score situations

Read-only retrospective analysis of72frozen current league games, plus200previously verified controls. No hosted-game creation, upload or deployment calls. The one viewer session is a replay-viewing operation; its private URL stays in ignored raw storage.

The seven-layer model is in `docs/opponents/khors-v114/score-audit-20260923`. Khors source is unavailable. The four source-reconstruction cases execute **our** authentic29f6d7e6 controller, never an inferred khors implementation.

Raw root: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-khors114-audit-20260923`. Python with authenticated HTTP dependencies is `/Users/aaln/experiments/softmax/metta/.venv/bin/python`. Scripts resolve paths from this worktree. Preserve the original72-episode plan and input files.

Run from the research root:

```sh
python games/gods_of_the_arena/instruments/khors11420260923/collect.py
python games/gods_of_the_arena/instruments/khors11420260923/build.py
python games/gods_of_the_arena/instruments/khors11420260923/collect.py --stalls
python games/gods_of_the_arena/instruments/khors11420260923/reconstruct_ours.py
python games/gods_of_the_arena/instruments/khors11420260923/analyze.py
python games/gods_of_the_arena/instruments/khors11420260923/supporting.py
python games/gods_of_the_arena/instruments/khors11420260923/publish.py
python games/gods_of_the_arena/instruments/khors11420260923/plot.py
python docs/opponents/khors-v114/score-audit-20260923/verify.py
```

`build.py` requires the exact engine worktree at1b708944 and clean locked dependencies. The collector also uses the existing calibrated replay58 episode/economy/command-hash binaries and combat-audit; their hashes are frozen in the plan. Missing binaries can be rebuilt from the referenced score20260922 bootstrap and adaptive20260922 source in the same pinned engine. Do not substitute the research branch's engine.

Results are cached by immutable episode. To independently reexecute one decoder, archive its generated output and logs under a new revision directory before rerunning; never remove the downloaded replay/spec/results. `verify.py` checks saved proof consistency and raw hashes when present; it does not pretend to rerun the simulator.

Interpretation limits:

- Nine games have all clean VMs;63have other-player failures. Our and khors VMs are clean. Report actual league scores and clean subset separately.
- Raw XP and post-tick full truth are diagnostic inputs, unavailable to live BASIC. Public progress proxies need validation.
- Drought includes preceding dead time. Battle-aligned complete minute windows omit the final partial window from minute counts; total XP/score includes it.
- Draft class, position and roster are confounded. Shared-game appearances are not independent samples.
- `bestKind` persists when target ID is zero. Source probe kind counters are explicitly not used as a target histogram.
- Successful replay reconstruction validates behavior on those paths, not a counterfactual fix. Counter IR remains proposed.

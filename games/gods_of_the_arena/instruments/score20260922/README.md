# Individual score opportunity research

Live patch2026.9.22.3, source1b708944, replay58. The prior replay57 engine and
all frozen portal evidence remain separate. Raw study:
`../polyworld/tmp/gota-score-20260922` from the research worktree root.

`score_binding.py` extends the frozen portal contracts with separate hero,
creep and structure utility, then evaluates complete public threat context.
`build.py --out <new-path>` generates and reverses a semantic IR/BASIC pair;
existing candidates cannot be overwritten. R1's fractional quotient overflowed
on100000synthetic HP; R2 uses integer division. R3 adopts the live patch's
500XP god reward. Old alternatives remain captured.

`bootstrap.py` validates exact engine/dependencies and builds actual-host
instruments. Use Nim2.2.10; local absolute defaults can be adapted on another
machine. The engine worktree is `polyworld-gota-engine-score-20260922`.
The corrected `practice.nim` forces a due decision before automatic creep
acquisition, then asserts selected target, actual attack intent and kill XP.
`native.py` runs eight complete one-subject ten-VM games and verifies every
replay hash plus XP and score; local outcomes are diagnostic only.

`hosted_score.py --prepare` creates an inert candidate version and schema-valid
four-cell160-game plan. It does not create experience requests or deploy.
`hosted_score.py` executes the frozen plan only through the shared cap/journal,
with global runner lock, paused-worker check, current-game verification and
sequential requests plus streaming audits. **September22 cap1760 is exhausted.**
Do not bypass it. Before execution, reconcile the current UTC day, authorization,
pending requests and source/roster/game pins; launch a progress dashboard.

After hosted completion, report confidence intervals, duplicates and exact
hero/creep/building/god XP before any deployment. The existing economy decoder
groups god XP under structure_or_other; split500perhero when that hero's enemy
god is destroyed, using replay events/final fort state. Never call these
postgame facts live policy features. No automatic deployment is implemented.

`finalize.py` saves local results into the portable pair; `verify.py` is copied
there and checks source/IR round-trip and evidence hashes. Competitive belief
remains requires_review. Parent session references are preserved in the pair;
none of the original recordings or inputs is edited.

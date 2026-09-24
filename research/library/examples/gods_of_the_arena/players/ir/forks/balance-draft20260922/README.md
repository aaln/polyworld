# Crossbowman draft-only follow-up

Engine **2026.9.22.2 / ffcedcd**. Source **7631fa32fb7ef6725074ad6778f4f94fe1e18ac5018bece1eed40e32cbef9bb8**. Score gate **passed**; this bundle itself does not select a league champion.

| Color | Control score | Crossbow draft score | Change |
|---|---:|---:|---:|
| Red | 2337.40 | 2888.97 | +23.6% |
| Blue | 2701.97 | 3273.50 | +21.2% |

Mean score 3081.24 versus 2519.69, +22.3%. Fort outcomes and deaths are diagnostics. Only draft priority changes; existing post-draft behavior is retained. 40 games/color, one subject seat, exact roster/configuration and all ten VMs/replay hashes/source specs/XP/integer scores checked. The 80 control games come from the preceding study: this is a sequential follow-up, not independent confirmation. No universal hero ranking or late-draft/#1 claim. All failed mirrored alternatives remain in the sibling `balance20260922` bundle.

Edit `policy.py`; `python3 convert.py compile --out <new-directory>` regenerates BASIC. Use `extract --source <file>` for reverse extraction, and `python3 verify.py` for offline pair/evidence verification.

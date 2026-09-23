# Richard v174 guarded siege transfer: local validation

The [portable IR/policy pair](guarded-siege/) adds covered tower pressure and counterattacks against reachable heroes during a siege to the deployed Druid-lane source. Its BASIC SHA256 is `f7873bb2ec9ef14eb118639568144cadc75ad9a67f6b202a25a802890c85f143`. The reviewed local IR SHA256 is `f1926b00764488c758b0c758c4db6d6674b8d77398bfa06a8bd31876ec262473`.

All662 local checks and16 native full games pass on2026.9.22.3. These establish intended behavior and runtime, not a competitive gain. The400-game hosted comparison is frozen in the pair's evidence directory; the deployed Druid policy stays live while it runs. The source-informed opponent model and all captured inputs are retained.

Run `python guarded-siege/verify.py`. `convert.py compile --out NEW_DIRECTORY` regenerates BASIC from semantic IR; `convert.py extract --source policy.bas --out NEW_DIRECTORY` reflects executable changes back through the frozen binding. Editing executable bytes invalidates old evidence automatically.

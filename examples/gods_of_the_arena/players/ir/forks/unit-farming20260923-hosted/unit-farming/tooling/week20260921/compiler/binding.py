"""Versioned semantic skills for the Gods of the Arena BASIC host.

Templates are the executable definitions of these skills, not opaque policy
payloads. The reverse extractor matches their complete parsed control flow.
Only declared integer parameters may vary within a skill contract.
"""

from dataclasses import dataclass
import re
from textwrap import dedent


VERSION = "gota-bassy/2026-09-21"
GAME_VERSION = "2026.9.21.5"
# This isolated binding targets the Bassy migration; old-week compilers stay frozen.
GAME_VERSIONS = ("2026.9.21.5",)


@dataclass(frozen=True)
class Contract:
    template: str
    parameters: dict[str, tuple[int, int, int]]  # default, minimum, maximum
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    actions: tuple[str, ...]
    meaning: str
    memory: tuple[str, ...] = ()

    def defaults(self):
        return {name: spec[0] for name, spec in self.parameters.items()}

    def source(self, parameters):
        if set(parameters) != set(self.parameters):
            raise ValueError("skill parameters must exactly match its binding contract")
        for name, value in parameters.items():
            _, low, high = self.parameters[name]
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer in {low}..{high}")
        return re.sub(r"\bparam_(\w+)\b", lambda m: str(parameters[m[1]]), self.template)


def contract(source, parameters, reads, writes, actions, meaning, memory=()):
    return Contract(dedent(source).strip(), parameters, tuple(reads), tuple(writes),
                    tuple(actions), meaning, tuple(memory))


def guarded(condition, body):
    return f"if {condition} then\n" + "\n".join("  " + line for line in body.splitlines()) + "\nend if"



CONTRACTS = {}
PREDICATES = {}

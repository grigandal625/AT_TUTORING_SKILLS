from dataclasses import dataclass
from typing import Dict


@dataclass
class Coefficients:
    syntax_fine: float
    logic_fine: float
    lexic_fine: float

    entity_fines: Dict[str, float]


SIMULATION_COEFFICIENTS = Coefficients(
    syntax_fine=3,
    logic_fine=2,
    lexic_fine=1,
    entity_fines={
        "resource_type": 1,
        "resource": 2,
        "template": 3,
        "template_usage": 4,
        "func": 5,
    },
)

KNOWLEDGE_COEFFICIENTS = Coefficients(
    syntax_fine=3,
    logic_fine=2,
    lexic_fine=1,
    entity_fines={
        "event": 1,
        "interval": 2,
        "object": 3,
        "rule": 4,
        "type": 5,
    },
)

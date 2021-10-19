from dataclasses import dataclass


@dataclass()
class Goal:
    name: str
    description: str
    topic: str
    periodic: bool

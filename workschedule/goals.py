from dataclasses import dataclass, field



@dataclass(order=True)
class Goal:
    """A goal can be a task or note."""
    name: str = field(repr=True, compare=True)
    description: str = field(repr=False, compare=False)
    periodic: bool = field(repr=False, compare=False)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return self.name == other
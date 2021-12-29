from dataclasses import dataclass, field



@dataclass(order=True)
class Goal:
    """A goal can be a task or note."""
    name: str = field(compare=True)
    description: str
    periodic: bool

    def __repr__(self) -> str:
        return self.name
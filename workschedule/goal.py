from dataclasses import dataclass


@dataclass(eq=False)
class Goal:
    """A goal can be a task or note."""
    name: str
    description: str
    periodic: bool
    done: bool = False

    def __eq__(self, other):
        return self.name == other

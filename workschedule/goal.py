from dataclasses import dataclass


@dataclass(eq=False)
class Goal:
    """A goal can be a task or note."""
    name: str
    description: str
    done: bool = False

    def __eq__(self, other) -> bool:
        return self.name == other

    def __repr__(self) -> str:
        return self.name


def get_not_dones(goals: list[Goal]) -> list[Goal]:
    """Retursn all done goals."""
    return _get_goals(goals, "done", False)


def _get_goals(goals: list[Goal], attrib: str, value) -> list[Goal]:
    to_return = []
    for goal_ in goals:
        if Goal.__getattribute__(goal_, attrib) == value:
            to_return.append(goal_)
    return to_return

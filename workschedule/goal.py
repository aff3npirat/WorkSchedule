from dataclasses import dataclass


@dataclass(order=True)
class Goal:
    """A goal can be a task or note."""
    name: str
    description: str
    done: bool = False

    def __eq__(self, other) -> bool:
        return self.name == other

    def __repr__(self) -> str:
        return self.name


def sort(goals: list[Goal]) -> list[Goal]:
    """Sorts a list of goals.

    Goals are first sorted by done (goals that are done are put at end of list)
    and then alphabetical.
    """
    done_goals = get_dones(goals)
    notdone_goals = get_not_dones(goals)
    return sorted(notdone_goals) + sorted(done_goals)


def get_not_dones(goals: list[Goal]) -> list[Goal]:
    return _get_goals(goals, "done", False)


def get_dones(goals: list[Goal]) -> list[Goal]:
    return _get_goals(goals, "done", True)


def _get_goals(goals: list[Goal], attrib: str, value) -> list[Goal]:
    to_return = []
    for goal_ in goals:
        if Goal.__getattribute__(goal_, attrib) == value:
            to_return.append(goal_)
    return to_return

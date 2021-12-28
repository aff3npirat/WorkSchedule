import pickle
import prettytable
import textwrap
import os

import goal
import helpers
import history
import timer

GREEN = '\033[32m'
YELLOW = '\033[33m'
ENDC = '\033[0m'

_to_work: dict
_remaining: dict
_goals: dict
_history: list[history.Period]
_work_timer: timer.Timer


class InvalidNameException(Exception): pass
class DuplicateNameException(Exception): pass
class NoScheduleException(Exception): pass


def _valid_topic_name(name: str) -> bool:
    if name in ["", "add", "work", "overview", "Period", "goal", "set", "list", "new", "view"]:
        return False
    return True

def _valid_goal_name(name: str) -> bool:
    if name in [""]:
        return False
    return True

def _valid_schedule_name(name: str) -> bool:
    if name in [""]:
        return False
    return True


def add_topic(new_topic: str, hours: float) -> None:
    """Adds a new topic to current schedule"""
    if not _valid_topic_name(new_topic):
        raise InvalidNameException(f"'{new_topic}' is not a valid topic name!")

    if new_topic in _to_work:
        raise DuplicateNameException(f"Topic '{new_topic}' already exists in schedule!")

    _to_work[new_topic] = hours
    _remaining[new_topic] = 0.0
    _goals[new_topic] = []


def remove_topic(topic: str) -> None:
    """Remove a topic from current schedule."""
    if topic in _to_work:
        del _to_work[topic]
        del _remaining[topic]
        del _goals[topic]
    else:
        raise InvalidNameException(f"Could not find '{topic}' in schedule!")


def new_schedule(name: str) -> None:
    if not _valid_schedule_name(name):
        raise InvalidNameException(f"'{name}' is not a valid name for a schedule!")
    _save(name, {}, {}, {}, timer.Timer(), [history.Period()])


def reset(carry_hours: list[str] = None) -> None:
    """Starts a new period.

    Parameters
    ----------
    carry_hours
        List of topics for which unworked time is carried to new period.
    """
    if carry_hours is None:
        carry_hours = []

    try:
        stop_worktimer()
    except: pass

    for topic in _to_work:
        if topic in carry_hours:
            _remaining = _to_work[topic] + _remaining[topic] - _history[-1].get_hours(topic)
            _remaining[topic] = _remaining
        else:
            _remaining[topic] = 0.0
    _history.append(history.Period())


def work(topic: str, hours: float) -> None:
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    _history[-1].add_entry(history.Entry(topic, hours))


def start_worktimer(topic: str) -> None:
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    _work_timer.start(topic)


def stop_worktimer() -> float:
    """Stops working timer and adds worked hours."""
    topic, hours = _work_timer.stop()
    work(topic, hours)
    return topic, hours


def add_goal(topic: str, name: str, description: str, periodic: bool) -> None:
    """Adds a goal to current period.

    Parameters
    ----------
    topic
        Topic goal is added to.
    name
        Used to adress goal, e.g. mark as done.
    description
        A description of the goal.
    periodic
        Goal is added after each reset.
    """
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name in _goals[topic]:
        raise DuplicateNameException(f"Goal names must be unique!")
    if not _valid_goal_name(name):
        raise InvalidNameException(f"'{name}' is not a valid goal name!")

    new_goal = goal.Goal(name, description, periodic)
    _goals[topic].append(new_goal)


def remove_goal(topic: str, name: str) -> None:
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name not in _goals[topic]:
        raise InvalidNameException(f"Could not find goal '{name}'!")
    _goals[topic].remove(name)


def mark_done(topic: str, name: str) -> None:
    """Mark a goal as done."""
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name not in _goals[topic]:
        raise InvalidNameException(f"Could not find goal '{name}'!")

    idx = _goals[topic].index(name)
    _goals[topic][idx].done = True


def load(name: str, root_dir: str = None) -> None:
    """Load a schedule.
    
    Parameters
    ----------
    name
        Name of schedule to load.
    schedules_dir
        Directory containing files to load from. Should contain name.schedule, name.history files."""
    if root_dir is None:
        root_dir = os.path.join(helpers.get_top_directory(), "schedules")

    try:
        with open(root_dir / f"{name}.schedule", "rb") as file:
            schedule_, remaining_, goals_, work_timer_ = pickle.load(file)
        with open(root_dir / f"{name}.history", "rb") as file:
            worked_ = pickle.load(file)
    except FileNotFoundError:
        raise InvalidNameException(f"There is no schedule named '{name}'!")

    global _to_work, _history, _remaining, _goals, _work_timer
    _to_work = schedule_
    _history = worked_
    _remaining = remaining_
    _goals = goals_
    _work_timer = work_timer_


def save(name: str) -> None:
    _save(name, _to_work, _remaining, _goals, _work_timer, _history)


def _save(name: str, schedule: dict, remaining: dict, goals: dict, work_timer: timer.Timer, worked: list) -> None:
    root_dir = os.path.join(helpers.get_top_directory(), "schedules")
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule, remaining, goals, work_timer], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump(worked, file)


def get_active_schedule(path: str = None) -> str:
    """Returns name of active schedule."""
    if path is None:
        path = os.path.join(helpers.get_top_directory(), "curr_schedule")

    with open(path, "rt") as file:
        lines = file.readlines()
    if len(lines) == 0:
        raise NoScheduleException("There is no active schedule!")
    return lines[0]


def set_as_active(name: str, path: str = None) -> None:
    if path is None:
        path = os.path.join(helpers.get_top_directory(), "curr_schedule")

    with open(path, "wt") as file:
        file.write(name)


def overview() -> str:
    rows = [["Topic"], ["Worked"], ["toWork"], ["Notes"]]
    rows[0].append("Period")
    rows[1].append(f"{_history[-1].get_hours():.2g}")
    rows[2].append(f"{sum(_to_work.values()):.2g}({sum(_remaining.values()):+.2g})")
    rows[3].append("")

    for topic in _to_work:
        rows[0].append(topic)
        rows[1].append(f"{_history[-1].get_hours(topic):.2g}")
        rows[2].append(f"{_to_work[topic]:.2g}({_remaining[topic]:+.2g})")

        goal_cell_text = ""
        for goal_ in goal.sort(_goals[topic]):
            if goal_.done:
                goal_cell_text += f"{GREEN}{goal_}{ENDC}\n"
            elif goal_.periodic:
                goal_cell_text += f"{YELLOW}{goal_}{ENDC}\n"
            else:
                goal_cell_text += f"{goal_}\n"
        goal_cell_text = goal_cell_text.rstrip("\n")
        rows[3].append(goal_cell_text)

    table = prettytable.PrettyTable()
    table.align = "c"
    table.header = False
    table.hrules = prettytable.ALL
    table.add_rows(rows)
    return table.get_string()


def topic_overview(topic: str, line_length: int) -> str:
    """Get an overview of one topic.

    Parameters
    ----------
    topic
        Name of topic.
    detailed
        Expand goal descriptions.
    line_length
        Number of chars in single line.

    Examples
    --------
    >>> topic_overview("CogScie", True, 60)
    CogScie: 10/20(+3)
    ------------------
    Goal#1
        This was my first goal.
   Goal#2
        This is my second goal. I would rather never fulfill it.

    >>> topic_overview("CogScie", False, 60)
    CogScie: 10/20(+3)
    ------------------
    Goal#1 - This was my first goal.
    Goal#2 - This is my second goal. I would rather never...
    """
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}'!")

    header = f"{topic}: {_history[-1].get_hours(topic):.2g}/{_to_work[topic]:.2g}" \
             f"({_remaining[topic]:+.2g})"
    header += "\n" + len(header) * "-" + "\n"

    goal_overview = ""
    for goal_ in goal.sort(_goals[topic]):
            goal_text = f"{goal_.name}\n"
            goal_text += textwrap.indent(
                helpers.split_lines(goal_.description, line_length - 4),
                " " * 4)
            if goal_.done:
                goal_overview += f"{GREEN}{goal_text}{ENDC}\n"
            elif goal_.periodic:
                goal_overview += f"{YELLOW}{goal_text}{ENDC}\n"
            else:
                goal_overview += f"{goal_text}\n"
    return header + goal_overview[:-1]

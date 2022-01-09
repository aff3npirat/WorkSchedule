import pickle
import prettytable
import textwrap
import os

import goals
import helpers
import history
import timer
from history import GoalDoneEntry, GoalFailEntry, WorkEntry

GREEN = '\033[32m'
YELLOW = '\033[33m'
ENDC = '\033[0m'


class InvalidNameException(Exception): pass
class DuplicateNameException(Exception): pass
class NoScheduleException(Exception): pass

_to_work: dict
_remaining: dict
_goals: dict
_history: list[history.Period]
_work_timer: timer.Timer
_todo: list


def _valid_topic_name(name: str) -> bool:
    if name in ["", "Period", "add", "work", "overview", "goal", "set", "list", "new", "view", "reset"]:
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


def add_todo(topic:str, goal:str, pos:int=-1) -> None:
    """Adds a goal to todo-list.
    
    Parameters
    ----------
    topic
        Name of topic which contains goal.
    goal
        Name of goal.
    pos
        Index (0-indexed) on todo-list. When pos equals -1 goal is added to end of list.
    """
    if topic not in _goals:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if goal not in _goals[topic]:
        raise InvalidNameException(f"Could not find goal '{goal}'!")

    if pos >= 0:
        _todo.insert(pos, (topic, goal))
    else:
        _todo.append((topic, goal))


def remove_todo(pos:int) -> None:
    """Remove a goal form todo-list.
    
    Parameters
    ----------
    pos
        Index of goal to remove.
    """
    if pos >= len(_todo) or pos < 0:
        raise IndexError(f"Position '{pos+1}' does not exist in todo-list!")

    _todo.pop(pos)


def reset_todo(done:bool=False) -> None:
    """Clear todo-list.
    
    Parameters
    ----------
    done
        If True, all goals on tood-list will be marked as done.
    """
    if done:
        for topic, goal in _todo:
            mark_done(topic, goal)
    _todo.clear()


def todo_as_str() -> str:
    """Get current todo-list as printable string."""


def add_topic(new_topic: str, hours: float) -> None:
    """Adds a new topic to current schedule"""
    if not _valid_topic_name(new_topic):
        raise InvalidNameException(f"'{new_topic}' is not a valid topic name!")

    if new_topic not in _to_work:
        _goals[new_topic] = []
    _to_work[new_topic] = hours
    _remaining[new_topic] = 0.0


def remove_topic(topic: str) -> None:
    """Remove a topic from current schedule."""
    if topic == "Period":
        raise InvalidNameException(f"Can not remove 'Period' from schedule!")
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find '{topic}' in schedule!")

    del _to_work[topic]
    del _remaining[topic]
    del _goals[topic]
    for topic_, goal in _todo:
        if topic_ == topic:
            _todo.remove((topic_, goal))


def new_schedule(name: str) -> None:
    if not _valid_schedule_name(name):
        raise InvalidNameException(f"'{name}' is not a valid name for a schedule!")
    new_schedule_ = (
        {},  # to_work
        {},  # remaining
        {"Period": []},  # goals
        timer.Timer(),
        [history.Period()]
    )
    _save(name, *new_schedule_)


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
            new_remaining = _to_work[topic] + _remaining[topic] - _history[-1].get_hours(topic)
            _remaining[topic] = new_remaining
        else:
            _remaining[topic] = 0.0
    _history.append(history.Period())


def work(topic: str, hours: float) -> None:
    if topic not in _to_work:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    _history[-1].add_entry(WorkEntry(topic, hours))


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
    if not _valid_goal_name(name):
        raise InvalidNameException(f"'{name}' is not a valid goal name!")
    if topic not in _goals:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name in _goals[topic]:
        raise DuplicateNameException(f"Goal names must be unique!")

    new_goal = goals.Goal(name, description, periodic)
    _goals[topic].append(new_goal)
    _goals[topic] = sorted(_goals[topic])  # sort goals alphabetically


def remove_goal(topic: str, name: str) -> None:
    if topic not in _goals:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name not in _goals[topic]:
        raise InvalidNameException(f"Could not find goal '{name}'!")
    _goals[topic].remove(name)
    
    for entry in _todo:
        if (topic, name) == entry:
            _todo.remove(entry)


def mark_done(topic: str, name: str) -> None:
    """Mark a goal as done.
    
    Adds a new entry to history, containing name and description
    of goal marked as done.
    """
    if topic not in _goals:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name not in _goals[topic]:
        raise InvalidNameException(f"Could not find goal '{name}' in topic '{topic}'!")

    idx = _goals[topic].index(name)
    goal = _goals[topic].pop(idx)
    _history[-1].add_entry(GoalDoneEntry(topic, name, goal.description, goal.periodic))


def load(name:str, root_dir:str = None) -> None:
    """Load a schedule.
    
    Parameters
    ----------
    name
        Name of schedule to load.
    schedules_dir
        Directory containing name.schedule file."""
    if root_dir is None:
        root_dir = os.path.join(helpers.get_top_directory(), "schedules")

    try:
        with open(os.path.join(root_dir, f"{name}.schedule"), "rb") as file:
            loaded = pickle.load(file)
    except FileNotFoundError:
        raise InvalidNameException(f"There is no schedule named '{name}'!")

    global _to_work, _history, _remaining, _goals, _work_timer, _todo
    _to_work, _remaining, _goals, _work_timer, _history, _todo = loaded


def save(name:str, root_dir:str=None) -> None:
    _save(name, _to_work, _remaining, _goals, _work_timer, _history, _todo, root_dir=root_dir)


def _save(name:str, schedule_:dict, remaining:dict, goals_:dict, work_timer:timer.Timer, history_:list, _todo:list, root_dir:str=None) -> None:
    if root_dir is None:
        root_dir = os.path.join(helpers.get_top_directory(), "schedules")

    with open(os.path.join(root_dir, f"{name}.schedule"), "w+b") as file:
        pickle.dump([schedule_, remaining, goals_, work_timer, history_, _todo], file)


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
    rows = [["Topic"], ["Worked"], ["toWork"], ["Goals"]]

    rows[0].append("Period")
    rows[1].append(f"{_history[-1].get_hours():.2g}")
    rows[2].append(f"{sum(_to_work.values()):.2g}({sum(_remaining.values()):+.2g})")
    goal_cell_text = ""
    for goal_ in _goals["Period"]:
        if goal_.periodic:
            goal_cell_text += f"{YELLOW}{goal_}{ENDC}\n"
        else:
            goal_cell_text += f"{goal_}\n"
    rows[3].append(goal_cell_text.rstrip("\n"))

    for topic in _to_work:
        rows[0].append(topic)
        rows[1].append(f"{_history[-1].get_hours(topic):.2g}")
        rows[2].append(f"{_to_work[topic]:.2g}({_remaining[topic]:+.2g})")

        goal_cell_text = ""
        for goal_ in _goals[topic]:
            if goal_.periodic:
                goal_cell_text += f"{YELLOW}{goal_}{ENDC}\n"
            else:
                goal_cell_text += f"{goal_}\n"
        rows[3].append(goal_cell_text.rstrip("\n"))

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
    line_length
        Number of chars in single line.

    Examples
    --------
    >>> topic_overview("CogScie", 60)
    CogScie: 10/20(+3)
    ------------------
    Goal#1
        This was my first goal.
   Goal#2
        This is my second goal. I would rather never fulfill it.
    """
    if topic not in _goals:
        raise InvalidNameException(f"Could not find topic '{topic}'!")

    if topic == "Period":
        header = f"{topic}: {_history[-1].get_hours():.2g}/{sum(_to_work.values())}({sum(_remaining.values()):+.2g})"
        header += "\n" + len(header) * "-" + "\n"
    else:
        header = f"{topic}: {_history[-1].get_hours(topic):.2g}/{_to_work[topic]:.2g}({_remaining[topic]:+.2g})"
        header += "\n" + len(header) * "-" + "\n"

    goal_overview = ""
    for goal_ in _goals[topic]:
            goal_text = f"{goal_.name}\n"
            goal_text += textwrap.indent(
                helpers.split_lines(goal_.description, line_length - 4),
                " " * 4)
            if goal_.periodic:
                goal_overview += f"{YELLOW}{goal_text}{ENDC}\n"
            else:
                goal_overview += f"{goal_text}\n"
    return header + goal_overview[:-1]

import pickle
import prettytable
import textwrap

import goal
import helpers
import history
import work_timer

GREEN = '\033[32m'
YELLOW = '\033[33m'
ENDC = '\033[0m'

# topic -> hours to work
curr_schedule: dict = {}
# topic -> hours remaining
curr_remaining: dict = {}
# topic -> Goal
curr_goals = {}
curr_timer = work_timer.WorkTimer()


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

    if new_topic in curr_schedule:
        raise DuplicateNameException(f"Topic '{new_topic}' already exists in schedule!")

    curr_schedule[new_topic] = hours
    curr_remaining[new_topic] = 0.0
    curr_goals[new_topic] = []


def remove_topic(topic: str) -> None:
    """Remove a topic from current schedule."""
    if topic in curr_schedule:
        del curr_schedule[topic]
        del curr_remaining[topic]
        del curr_goals[topic]
    else:
        raise InvalidNameException(f"Could not find '{topic}' in schedule!")


def new_schedule(name: str) -> None:
    if not _valid_schedule_name(name):
        raise InvalidNameException(f"'{name}' is not a valid name for a schedule!")
    _save(name, {}, {}, {}, work_timer.WorkTimer(), [history.Period()])


def reset(carry_hours: list[str] = None, carry_goals: list[str] = None) -> None:
    """Starts a new period.

    Resets worked hours, remaining and removes all done goals, stops running
    work timers and adds periodic goals.

    Parameters
    ----------
    carry_hours
        List of topics, keep remaining hours for each topic.
    carry_goals
        List of topics, keep undone goals for each topic.
    """
    if carry_hours is None:
        carry_hours = []
    if carry_goals is None:
        carry_goals = []

    try:
        stop_working()
    except:
        pass

    for topic in curr_schedule:
        if topic in carry_hours:
            curr_remaining[topic] += curr_schedule[topic] - history.get_hours(topic)
        else:
            curr_remaining[topic] = 0.0

        if topic in carry_goals:
            for goal_ in goal.get_periodics(curr_goals[topic]):
                goal_.done = False
            curr_goals[topic] = goal.get_not_dones(curr_goals[topic])
        else:
            curr_goals[topic] = goal.get_periodics(curr_goals[topic])
    history.history.append(history.Period())


def work(topic: str, hours: float) -> None:
    if topic not in curr_schedule:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    history.add_entry(history.Entry(topic, round(hours, 2)))


def start_working(topic: str) -> None:
    if topic not in curr_schedule:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    curr_timer.start(topic)


def stop_working() -> float:
    """Stops working timer and adds worked hours."""
    topic = curr_timer.topic
    hours = curr_timer.stop()
    work(topic, hours)
    return hours


def add_goal(topic: str, name: str, description: str, periodic: bool) -> None:
    """Adds a goal to current period.

    Parameters
    ----------
    topic
    name
        Used to adress goal, e.g. mark as done.
    description
        A description of the goal
    periodic
        Goal is added again on reset.
    """
    if topic not in curr_schedule:
        raise InvalidNameException(f"Could not find topic '{topic}' in schedule!")
    if name in curr_goals[topic]:
        raise DuplicateNameException(f"Goal names must be unique!")
    if not _valid_goal_name(name):
        raise InvalidNameException(f"'{name}' is not a valid goal name!")

    new_goal = goal.Goal(name, description, periodic)
    curr_goals[topic].append(new_goal)


def remove_goal(topic: str, name: str) -> None:
    if name not in curr_goals[topic]:
        raise InvalidNameException(f"Could not find goal '{name}'!")
    curr_goals[topic].remove(name)


def mark_done(topic: str, goal_name: str) -> None:
    """Mark a goal as done."""
    if goal_name not in curr_goals[topic]:
        raise InvalidNameException(f"Could not find goal '{goal_name}'!")

    idx = curr_goals[topic].index(goal_name)
    curr_goals[topic][idx].done = True


def load(name: str) -> None:
    """Loads schedule and history."""
    root_dir = helpers.get_top_directory() / "schedules"
    try:
        with open(root_dir / f"{name}.schedule", "rb") as file:
            schedule_, remaining_, goals_, timer = pickle.load(file)
        with open(root_dir / f"{name}.history", "rb") as file:
            history_ = pickle.load(file)
    except FileNotFoundError:
        raise InvalidNameException(f"There is no schedule named '{name}'!")

    history.history = history_
    global curr_schedule, curr_remaining, curr_goals, curr_timer
    curr_schedule = schedule_
    curr_remaining = remaining_
    curr_goals = goals_
    curr_timer = timer


def save(name: str) -> None:
    _save(name, curr_schedule, curr_remaining, curr_goals, curr_timer, history.history)


def _save(name: str, schedule: dict, remaining: dict, goals: dict, timer: work_timer.WorkTimer, history: list):
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule, remaining, goals, timer], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump(history, file)


def get_active_schedule() -> str:
    """Returns name of active schedule."""
    with open(helpers.get_top_directory() / "curr_schedule", "rt") as file:
        lines = file.readlines()
    if len(lines) == 0:
        raise NoScheduleException("There is no active schedule!")
    return lines[0]


def set_as_active(name: str) -> None:
    with open(helpers.get_top_directory() / "curr_schedule", "wt") as file:
        file.write(name)


def overview() -> str:
    rows = [["Topic"], ["Worked"], ["toWork"], ["Notes"]]
    rows[0].append("Period")
    rows[1].append(f"{history.get_hours():.2g}")
    hours_towork = sum(curr_schedule.values())
    hours_remaining = sum(curr_remaining.values())    
    rows[2].append(f"{hours_towork:.2g}({hours_remaining:+.2g})")
    rows[3].append("")

    for topic in curr_schedule:
        rows[0].append(topic)
        rows[1].append(f"{history.get_hours(topic):.2g}")
        rows[2].append(f"{curr_schedule[topic]:.2g}({curr_remaining[topic]:+.2g})")

        goal_text = ""
        for goal_ in goal.sort(curr_goals[topic]):
            if goal_.done:
                goal_text += f"{GREEN}{goal_}{ENDC}\n"
            elif goal_.periodic:
                goal_text += f"{YELLOW}{goal_}{ENDC}\n"
            else:
                goal_text += f"{goal_}\n"
        goal_text = goal_text.rstrip("\n")
        rows[3].append(goal_text)

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
    if topic not in curr_schedule:
        raise InvalidNameException(f"Could not find topic '{topic}'!")

    header = f"{topic}: {history.get_hours(topic):.2g}/{curr_schedule[topic]:.2g}" \
             f"({curr_remaining[topic]:+.2g})"
    header += "\n" + len(header) * "-" + "\n"

    goal_overview = ""
    for goal_ in goal.sort(curr_goals[topic]):
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

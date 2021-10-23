import ntpath
import pickle
import prettytable
import textwrap
from pathlib import Path

import goal
import helpers
import history
import work_timer

DONE_CLR = '\033[32m'
ENDC = '\033[0m'

# topic -> hours to work
schedule: dict = {}
# topic -> hours remaining
remaining: dict = {}
# topic -> Goal
goals = {}
work_timer_ = work_timer.WorkTimer()


class NoSuchTopic(Exception):
    pass


class NoSuchGoal(Exception):
    pass


class DuplicateGoal(Exception):
    pass


def add_topic(new_topic: str, hours: float) -> None:
    """Adds a new topic to current schedule"""
    schedule[new_topic] = hours
    remaining[new_topic] = 0.0
    goals[new_topic] = []


def remove_topic(topic: str) -> None:
    """Remove a topic from current schedule."""
    if topic in schedule:
        del schedule[topic]
        del remaining[topic]
        del goals[topic]
    else:
        raise NoSuchTopic(topic)


def from_file(fpath: str, name: str = None) -> None:
    """Builds a new schedule.

    Schedule must be loaded before used.

    Parameters
    ----------
    fpath
        Path to file.
    name
        Name assigned to schedule. If None file name will be used.
    """
    fpath = Path(fpath)
    if not fpath.is_file():
        raise FileNotFoundError(f"could not find file {fpath.absolute()}")

    schedule_ = {}
    remaining_ = {}
    goals_ = {}
    with open(fpath, "r") as file:
        lines = file.readlines()
        for line in lines:
            topic, hours = line.split(": ")
            hours = hours.rstrip("\n")
            schedule_[topic] = float(hours)
            remaining_[topic] = 0.0
            goals_[topic] = []

    if name is None:
        name = ntpath.basename(fpath)
        if "." in name:
            name = name.split(".")[0]
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule_, remaining_, goals_, work_timer.WorkTimer()],
                    file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump([history.Period()], file)


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

    for topic in schedule:
        if topic in carry_hours:
            remaining[topic] += schedule[topic] - history.get_hours(topic)
        else:
            remaining[topic] = 0.0

        if topic in carry_goals:
            for goal_ in goal.get_periodics(goals[topic]):
                goal_.done = False
            goals[topic] = goal.get_not_dones(goals[topic])
        else:
            goals[topic] = goal.get_periodics(goals[topic])
    history.history.append(history.Period())


def work(topic: str, hours: float) -> None:
    if topic not in schedule:
        raise NoSuchTopic(topic)
    history.add_entry(history.Entry(topic, round(hours, 2)))


def start_working(topic: str) -> None:
    if topic not in schedule:
        raise NoSuchTopic(topic)
    work_timer_.start(topic)


def stop_working() -> float:
    """Stops working timer and adds worked hours."""
    topic = work_timer_.topic
    hours = work_timer_.stop()
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
        The goal will be readded every period.
    periodic
        Goal is added again on reset.
    """
    if topic not in schedule:
        raise NoSuchTopic(topic)
    if name in [goal_ for goal_list in goals.values() for goal_ in goal_list]:
        raise DuplicateGoal(name)

    new_goal = goal.Goal(name, description, periodic)
    goals[topic].append(new_goal)


def mark_done(goal_name: str) -> None:
    """Mark a goal as done."""
    topic = None
    for topic_ in goals:
        if goal_name in goals[topic_]:
            topic = topic_
            break
    if topic is None:
        raise NoSuchGoal(goal_name)

    idx = goals[topic].index(goal_name)
    goals[topic][idx].done = True


def load(name: str) -> None:
    """Loads schedule and history."""
    if name is None:
        return

    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "rb") as file:
        schedule_, remaining_, goals_, timer = pickle.load(file)
    with open(root_dir / f"{name}.history", "rb") as file:
        history_ = pickle.load(file)

    history.history = history_
    global schedule, remaining, goals, work_timer_
    schedule = schedule_
    remaining = remaining_
    goals = goals_
    work_timer_ = timer


def save(name: str) -> None:
    """Saves current schedule.

    Parameters
    ----------
    name
        Name used to load schedule.
    """
    if name is None:
        return

    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule, remaining, goals, work_timer_], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump(history.history, file)


def get_active_schedule() -> str:
    """Returns name of active schedule."""
    with open(helpers.get_top_directory() / "curr_schedule", "rt") as file:
        lines = file.readlines()
    return lines[0] if len(lines) >= 1 else None


def set_as_active(name: str) -> None:
    with open(helpers.get_top_directory() / "curr_schedule", "wt") as file:
        file.write(name)


def overview(detailed: bool) -> str:
    """Get current period in printable format.

    Parameters
    ----------
    detailed
        Seperate remaining hours from hours to work.

    Returns
    -------
    Returns table with following rows:
        'Topic'
        'Worked'
        'toWork'
        'Notes'
    """
    rows = [["Topic"], ["Worked"], ["toWork"], ["Notes"]]
    rows[0].append("Period")
    rows[1].append(f"{history.get_hours():.2g}")
    hours_towork = sum(schedule.values())
    hours_remaining = sum(remaining.values())
    if detailed:
        rows[2].append(f"{hours_towork:.2g}({hours_remaining:+.2g})")
    else:
        rows[2].append(f"{hours_towork + hours_remaining:.2g}")
    rows[3].append("")

    for topic in schedule:
        rows[0].append(topic)
        rows[1].append(f"{history.get_hours(topic):.2g}")

        if detailed:
            rows[2].append(f"{schedule[topic]:.2g}({remaining[topic]:+.2g})")
        else:
            rows[2].append(f"{schedule[topic] + remaining[topic]:.2g}")

        goal_text = ""
        for goal_ in goal.sort(goals[topic]):
            if goal_.done:
                goal_text += f"{DONE_CLR}{goal_}{ENDC}\n"
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


def topic_overview(topic: str, detailed: bool, line_length: int) -> str:
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
    if topic not in schedule:
        raise NoSuchTopic(topic)

    header = f"{topic}: {history.get_hours(topic):.2g}/{schedule[topic]:.2g}" \
             f"({remaining[topic]:+.2g})"
    header += "\n" + len(header) * "-" + "\n"

    goal_overview = ""
    if detailed:
        for goal_ in goal.sort(goals[topic]):
            goal_text = f"{goal_.name}\n"
            goal_text += textwrap.indent(
                helpers.split_lines(goal_.description, line_length - 4),
                " " * 4)
            if goal_.done:
                goal_overview += f"{DONE_CLR}{goal_text}{ENDC}\n"
            else:
                goal_overview += f"{goal_text}\n"
    else:
        for goal_ in goal.sort(goals[topic]):
            line = goal_.name + " - " + goal_.description
            if goal_.done:
                line = f"{DONE_CLR}{line}{ENDC}"
            goal_overview += f"{helpers.cutoff(line, line_length)}\n"
    return header + goal_overview[:-1]

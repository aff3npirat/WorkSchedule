import ntpath
import pickle
import texttable
import textwrap
from pathlib import Path

import goal
import helpers
import history
import work_timer

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


class DuplicateGoalName(Exception):
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
        raise NoSuchTopic


def from_file(fpath: str) -> None:
    """Builds a new schedule.

    Schedule must be loaded before used.

    Parameters
    ----------
    fpath
        Path to file.
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

    name = ntpath.basename(fpath)
    if "." in name:
        name = name.split(".")[0]
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule_, remaining_, goals_], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump([history.Period()], file)


def reset(carry_on: list[str] = None) -> None:
    """Starts a new period.

    Resets worked hours, remaining and removes all done goals, stops running
    work timers and adds periodic goals.

    Parameters
    ----------
    carry_on
        Keep remaining hours from each given topic.
    """
    if carry_on is None:
        carry_on = []

    try:
        stop_working()
    except:
        pass

    for topic in schedule:
        if topic in carry_on:
            remaining[topic] += schedule[topic] - history.get_hours(topic)
        else:
            remaining[topic] = 0.0

        for goal_ in goal.get_periodics(goals[topic]):
            goal_.done = False
        goals[topic] = goal.get_not_dones(goals[topic])
    history.history.append(history.Period())


def work(topic: str, hours: float) -> None:
    if topic not in schedule:
        raise NoSuchTopic
    history.add_entry(history.Entry(topic, hours))


def start_working(topic: str) -> None:
    if topic not in schedule:
        raise NoSuchTopic
    work_timer_.start(topic)


def stop_working() -> None:
    """Stops working timer and adds worked hours."""
    topic = work_timer_.topic
    work_timer_.stop()
    work(topic, round(work_timer_.hours(), 1))


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
        raise NoSuchTopic
    if name in [goal_ for goal_list in goals.values() for goal_ in goal_list]:
        raise DuplicateGoalName

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
        raise NoSuchGoal

    idx = goals[topic].index(goal_name)
    goals[topic][idx].done = True


def load(name: str) -> None:
    """Loads schedule and history."""
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "rb") as file:
        schedule_, remaining_, goals_ = pickle.load(file)
    with open(root_dir / f"{name}.history", "rb") as file:
        history_ = pickle.load(file)

    history.history = history_
    global schedule, remaining, goals
    schedule = schedule_
    remaining = remaining_
    goals = goals_


def save(name: str) -> None:
    """Saves current schedule.

    Parameters
    ----------
    name
        Name used to load schedule.
    """
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule, remaining, goals], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump(history.history, file)


# TODO: highligt done goals
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
    rows[1].append(f"{history.get_hours():g}")
    hours_towork = sum(schedule.values())
    hours_remaining = sum(remaining.values())
    if detailed:
        rows[2].append(f"{hours_towork:g}({hours_remaining:+g})")
    else:
        rows[2].append(f"{hours_towork + hours_remaining:g}")
    rows[3].append("")

    for topic in schedule:
        rows[0].append(topic)
        rows[1].append(f"{history.get_hours(topic):g}")

        if detailed:
            rows[2].append(f"{schedule[topic]:g}({remaining[topic]:+g})")
        else:
            rows[2].append(f"{schedule[topic] + remaining[topic]:g}")

        notes_cell = ""
        for goal_ in goal.sort(goals[topic]):
            notes_cell += f"{goal_}\n"
        notes_cell = notes_cell.rstrip("\n")
        rows[3].append(notes_cell)

    table = texttable.Texttable()
    table.set_header_align(["l" for _ in range(len(schedule) + 2)])
    table.set_cols_align(["l"] + ["c" for _ in range(len(schedule) + 1)])
    table.set_cols_dtype(["t" for _ in range(len(schedule) + 2)])
    table.set_chars(['-', '|', '+', '='])
    # Texttable.BORDER | Texttable.HEADER | Texttable.VLINES
    table.set_deco(15)
    table.add_rows(rows, header=False)
    return table.draw()


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
        raise NoSuchTopic

    header = f"{topic}: {history.get_hours(topic):g}/{schedule[topic]:g}" \
             f"({remaining[topic]:+g})"
    header += "\n" + len(header) * "-" + "\n"

    goal_descriptions = ""
    if detailed:
        for goal_ in goal.sort(goals[topic]):
            goal_descriptions += goal_.name + "\n"
            goal_descriptions += textwrap.indent(
                helpers.split_lines(goal_.description, line_length - 4),
                " " * 4) + "\n"
    else:
        for goal_ in goal.sort(goals[topic]):
            line = goal_.name + " - " + goal_.description
            goal_descriptions += helpers.cutoff(line, line_length) + "\n"
    return header + goal_descriptions

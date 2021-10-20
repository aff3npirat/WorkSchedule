import ntpath
import pickle
import texttable
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

    Resets worked hours, remaining and removes all done goals. Stops running
    work timers.

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


def add_goal(topic: str, name: str, description: str) -> None:
    """Adds a goal to current period.

    Parameters
    ----------
    topic
    name
        Used to adress goal, e.g. mark as done.
    description
        The goal will be readded every period.
    """
    if topic not in schedule:
        raise NoSuchTopic
    new_goal = goal.Goal(name, description)
    goals[topic].append(new_goal)


def mark_done(topic: str, goal_name: str) -> None:
    """Mark a goal as done."""
    if topic not in schedule:
        raise NoSuchTopic
    try:
        idx = goals[topic].index(goal_name)
    except ValueError:
        raise NoSuchGoal
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
        rows[2].append(f"{hours_towork:g}({hours_remaining:g})")
    else:
        rows[2].append(f"{hours_towork + hours_remaining:g}")
    rows[3].append("")
    for topic in schedule:
        rows[0].append(topic)
        rows[1].append(f"{history.get_hours(topic):g}")
        if detailed:
            rows[2].append(f"{schedule[topic]:g}({remaining[topic]:g})")
        else:
            rows[2].append(f"{schedule[topic] + remaining[topic]:g}")
        notes_cell = ""
        for goal_ in goals[topic]:
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


# TODO
def topic_overview(topic: str, detailed: bool) -> str:
    """Get an overview of one topic.

    Parameters
    ----------
    topic
    detailed
        Show goal descriptions and seperate remaining from worked hours.
    """

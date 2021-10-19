import ntpath
import pickle
import texttable
from pathlib import Path

import goal
import helpers
import history
import work_timer

# TODO: sub-goals
#       add a goal to a topic. A goal can be marked as done. Is marked as done
#       eitehr when resetting (if enabled) or by user.

# topic -> hours to work
schedule: dict = {}
# topic -> hours remaining
remaining: dict = {}
# topic -> Goal
goals = {}
work_timer = work_timer.WorkTimer()


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

    Resets worked hours, remaining and removes all done goals.

    Parameters
    ----------
    carry_on
        Keep remaining hours from each given topic.
    """
    if carry_on is None:
        carry_on = []

    for topic in schedule:
        if topic in carry_on:
            remaining[topic] += schedule[topic] - history.get_hours(topic)
        else:
            remaining[topic] = 0.0
        goals[topic] = goal.get_not_dones(goals[topic])
    history.history.append(history.Period())


def work(topic: str, hours: float) -> None:
    history.add_entry(history.Entry(topic, hours))


def start_working(topic: str) -> None:
    work_timer.start(topic)


def stop_working() -> None:
    """Stops working timer and adds worked hours."""
    work_timer.stop()
    work(work_timer.topic, round(work_timer.hours(), 1))


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
    new_goal = goal.Goal(name, description)
    goals[topic].append(new_goal)


def mark_done(topic: str, goal_name: str) -> None:
    """Mark a goal as done."""
    # TODO: ValueError handle, if goal_name is not found in list
    goals[topic][goals[topic].index(goal_name)].done = True


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

    Expects a .scheule and .history file already exists.

    Parameters
    ----------
    name
        Name used to load schedule.
    """
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "wb") as file:
        pickle.dump([schedule, remaining, goals], file)
    with open(root_dir / f"{name}.history", "wb") as file:
        pickle.dump(history.history, file)


def as_string(detailed: bool) -> str:
    """Get current period in printable format.

    Parameters
    ----------
    detailed
        Seperate remaining hours from hours to work.
    """
    rows = [["Topic"], ["Worked"], ["toWork"]]
    for topic in schedule:
        rows[0].append(topic)
        rows[1].append(f"{history.get_hours(topic):g}")
        if detailed:
            rows[2].append(f"{schedule[topic]:g}|{remaining[topic]:g}")
        else:
            rows[2].append(f"{schedule[topic] + remaining[topic]:g}")

    table = texttable.Texttable()
    table.set_header_align(["l" for _ in range(len(schedule) + 1)])
    table.set_cols_align(["l"] + ["c" for _ in range(len(schedule))])
    table.set_cols_dtype(["t" for _ in range(len(schedule) + 1)])
    table.set_chars(['-', '\\', '+', '-'])
    # Texttable.BORDER | Texttable.HEADER | Texttable.VLINES
    table.set_deco(11)
    table.add_rows(rows)
    return table.draw()

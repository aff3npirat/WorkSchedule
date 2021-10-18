import ntpath
import pickle
from pathlib import Path

import helpers
import history
import work_timer

# TODO: output
# TODO: sub-goals
#       add a goal to a topic. A goal can be marked as done. Is marked as done
#         eitehr when resetting (if enabled) or by user.

# topic -> hours to work
schedule: dict = {}
# topic -> hours remaining
remaining: dict = {}
work_timer = work_timer.WorkTimer()


def from_file(fpath: str) -> None:
    """Initializes schedule and history files.

    Creates a schedule and a history file. Files are saved under
    ./schedules from project root.

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
    with open(fpath, "r") as file:
        lines = file.readlines()
        for line in lines:
            topic, hours = line.split(": ")
            hours = hours.rstrip("\n")
            schedule_[topic] = float(hours)
            remaining_[topic] = 0.0

    name = ntpath.basename(fpath)
    if "." in name:
        name = name.split(".")[0]
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule_, remaining_], file)
    with open(root_dir / f"{name}.history", "w+b") as file:
        pickle.dump([history.Period()], file)


def reset(carry_on: list[str] = None) -> None:
    """
    Parameters
    ----------
    carry_on
        Keep remaining hours for each given topic.
    """
    if carry_on is None:
        carry_on = []

    for topic in schedule:
        if topic in carry_on:
            remaining[topic] += schedule[topic] - history.get_hours(topic)
        else:
            remaining[topic] = 0
    history.history.append(history.Period())


def work(topic: str, hours: float) -> None:
    history.add_entry(history.Entry(topic, hours))


def start_working(topic: str) -> None:
    work_timer.start(topic)


def stop_working() -> None:
    """Stops working timer and adds worked hours."""
    work_timer.stop()
    work(work_timer.topic, round(work_timer.hours(), 1))


def load(name: str) -> None:
    """Loads schedule and history."""
    root_dir = helpers.get_top_directory() / "schedules"
    with open(root_dir / f"{name}.schedule", "rb") as file:
        schedule_, remaining_ = pickle.load(file)
    with open(root_dir / f"{name}.history", "rb") as file:
        history_ = pickle.load(file)

    history.history = history_
    global schedule, remaining
    schedule = schedule_
    remaining = remaining_


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
        pickle.dump([schedule, remaining], file)
    with open(root_dir / f"{name}.history", "wb") as file:
        pickle.dump(history.history, file)

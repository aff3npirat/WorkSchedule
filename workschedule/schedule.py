import ntpath
import pickle
from pathlib import Path

import history
import work_timer

# TODO: output
# topic -> hours to work
schedule: dict = {}
# topic -> hours remaining
remaining: dict = {}
work_timer = work_timer.WorkTimer()


def from_file(fpath: str) -> None:
    """Initializes schedule and history files.

    Creates a .schedule and a .history file, with same name as given file.

    Parameters
    ----------
    fpath
        Path to file.
    """
    fpath = Path(fpath)
    if not fpath.is_file():
        raise FileNotFoundError(f"could not find file {fpath.absolute()}")

    schedule = {}
    remaining = {}
    with open(fpath, "r") as file:
        lines = file.readlines()
        for line in lines:
            topic, hours = line.split(": ")
            hours = hours.rstrip("\n")
            schedule[topic] = float(hours)
            remaining[topic] = 0

    name = ntpath.basename(fpath)
    if "." in name:
        name = name.split(".")[0]
    with open(fpath.parent / f"{name}.schedule", "w+b") as file:
        pickle.dump([schedule, remaining], file)
    with open(fpath.parent / f"{name}.history", "w+b") as file:
        pickle.dump([[]], file)


def reset(carry_on: list[str] = None) -> None:
    """
    Parameters
    ----------
    carry_on
        Add remaining hours to work for each topic given as string. Elements
        which do not correspond to a topic have no effect.
    """
    if carry_on is None:
        carry_on = []

    for topic in schedule:
        if topic in carry_on:
            remaining[topic] += schedule[topic] - history.get_hours(topic)
        else:
            remaining[topic] = 0
    history.start_new_period()


def work(topic: str, hours: float) -> None:
    history.add_entry(history.Entry(topic, hours))


def start_working(topic: str) -> None:
    work_timer.start(topic)


def stop_working() -> None:
    """Stops working timer and adds worked hours."""
    work_timer.stop()
    work(work_timer.topic, round(work_timer.hours(), 1))


def take_break() -> None: pass


def load(name: str) -> None: pass


def save() -> None: pass

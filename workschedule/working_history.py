from dataclasses import dataclass, field
from datetime import datetime

history = [[]]


def add_entry(entry):
    """Adds entry to history.

    Two entries with same date and topic will be merged, so that each topic can
    only occur once in current period.
    """
    curr_period = history[-1]
    if entry in curr_period:
        curr_period[curr_period.index(entry)].hours += entry.hours
    else:
        curr_period.append(entry)
    curr_period.sort()


def get_hours(topic: str) -> float:
    """Returns number of hours worked in current period on topic."""
    curr_period = history[-1]
    hours = 0
    for entry in curr_period:
        if entry.topic == topic:
            hours += entry.hours
    return hours


@dataclass(order=True)
class Entry:
    sec_sort_index: str = field(init=False, repr=False)
    topic: str
    hours: float = field(compare=False)
    date: str = field(init=False)

    def __post_init__(self):
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.sec_sort_index = self.topic

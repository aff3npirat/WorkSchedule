from dataclasses import dataclass, field
from datetime import datetime


@dataclass(order=True)
class Entry:
    date: str = field(init=False)
    sec_sort_index: str = field(init=False, repr=False)
    topic: str
    hours: float = field(compare=False)

    def __post_init__(self):
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.sec_sort_index = self.topic


class Period:

    def __init__(self):
        self.start = datetime.now()
        self.entries = []

    def add_entry(self, entry: Entry) -> None:
        """Adds entry to period.

        Two entries with same date and topic will be merged.
        """
        if entry in self.entries:
            self.entries[self.entries.index(entry)].hours += entry.hours
        else:
            self.entries.append(entry)
        self.entries.sort()

    def get_hours(self, topic: str = None) -> float:
        """Returns number of hours worked on topic."""
        hours = 0
        for entry in self.entries:
            if topic is None or entry.topic == topic:
                hours += entry.hours
        return hours


history: list[Period] = []


def add_entry(entry: Entry) -> None:
    history[-1].add_entry(entry)


def get_hours(topic: str = None) -> float:
    return history[-1].get_hours(topic)

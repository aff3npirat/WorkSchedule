from dataclasses import dataclass, field
from datetime import datetime


@dataclass(order=True)
class Entry:
    date: str = field(init=False)
    sec_sort_index: str = field(init=False, repr=False)
    topic: str
    hours: float = field(compare=False)

    def __post_init__(self):
        self.date = datetime.now().strftime("%d/%m/%Y//%H/%M/%S")
        self.sec_sort_index = self.topic



class Period:

    def __init__(self):
        self.start = datetime.now().strftime("%d/%m/%Y//%H/%M/%S")
        self.entries = []

    def add_entry(self, entry: Entry) -> None:
        """Adds an entry to period."""
        self.entries.append(entry)

    def get_hours(self, topic: str = None) -> float:
        """Returns number of hours worked on topic.
        
        When topic is None all hours worked are returned."""
        hours = 0
        for entry in self.entries:
            if topic is None or entry.topic == topic:
                hours += entry.hours
        return hours
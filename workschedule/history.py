from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Entry:
    topic: str
    date: str = field(init=False)

    def __post_init__(self):
        self.date = datetime.now().strftime("%d/%m/%Y//%H/%M/%S")

@dataclass
class WorkEntry(Entry):
    hours: float

@dataclass
class GoalEntry(Entry):
    goal_name: str
    description: str
    periodic: bool

@dataclass
class GoalDoneEntry(GoalEntry): pass

@dataclass
class GoalFailEntry(GoalEntry): pass



class Period:

    def __init__(self):
        self.start = datetime.now().strftime("%d/%m/%Y//%H/%M/%S")
        self.work_entries = []
        self.goal_entries = []

    def add_entry(self, entry: Entry) -> None:
        """Adds an entry to period."""
        if isinstance(entry, WorkEntry):
            self.work_entries.append(entry)
        elif isinstance(entry, GoalEntry):
            self.goal_entries.append(entry)

    def get_hours(self, topic: str = None) -> float:
        """Returns number of hours worked.
        
        Parameters
        ----------
        topic
            Topic for which worked hours are returned. If None all hours worked are returned."""
        hours = 0
        for entry in self.work_entries:
            if topic is None or entry.topic == topic:
                hours += entry.hours
        return hours
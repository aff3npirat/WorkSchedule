from dataclasses import dataclass, field

history = []


def add_entry(entry):
    if entry in history:
        history[history.index(entry)].hours += entry.hours
    else:
        history.append(entry)
    history.sort()


@dataclass(order=True)
class Entry:
    prim_sort_index: str = field(init=False, repr=False)
    sec_sort_index: str = field(init=False, repr=False)
    topic: str
    hours: float = field(compare=False)
    date: str

    def __post_init__(self):
        self.prim_sort_index = self.date
        self.sec_sort_index = self.topic

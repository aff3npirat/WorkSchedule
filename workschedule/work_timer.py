from datetime import datetime


class TimerRunningException(Exception): pass


class WorkTimer:
    """Measures working time on a topic."""

    def __init__(self):
        self.tic: datetime = None
        self.toc: datetime = None
        self.topic: str = None

    def start(self, topic):
        if self.topic is not None:
            raise TimerRunningException(f"There is already a timer running on topic '{self.topic}'!")
        self.topic = topic
        self.tic = datetime.now()

    def stop(self):
        if self.topic is None:
            raise TimerRunningException(f"There is no active timer!")
        self.toc = datetime.now()
        self.topic = None
        return self._hours()

    def _hours(self):
        diff = self.toc - self.tic
        seconds_in_hour = 60 * 60
        return diff.seconds / seconds_in_hour

from datetime import datetime


class TimerAlreadyRunning(Exception):
    pass


class NoTimerActive(Exception):
    pass


class WorkTimer:
    """Measures working time on a topic."""

    def __init__(self):
        self.tic: datetime = None
        self.toc: datetime = None
        self.topic: str = None

    def start(self, topic):
        if self.topic is not None:
            raise TimerAlreadyRunning(self.topic)
        self.topic = topic
        self.tic = datetime.now()

    def stop(self):
        if self.topic is None:
            raise NoTimerActive
        self.toc = datetime.now()
        self.topic = None
        return self._hours()

    def _hours(self):
        diff = self.toc - self.tic
        seconds_in_hour = 60 * 60
        return diff.seconds / seconds_in_hour

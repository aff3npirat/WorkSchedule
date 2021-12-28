from datetime import datetime


class TimerRunningException(Exception): pass


class Timer:

    def __init__(self):
        self.tic = None
        self.toc = None
        self.topic = None

    def start(self, topic):
        if self.topic is not None:
            raise TimerRunningException(f"There is already a timer running on topic '{self.topic}'!")
        self.topic = topic
        self.tic = datetime.now()

    def stop(self):
        if self.topic is None:
            raise TimerRunningException(f"There is no active timer!")
        self.toc = datetime.now()
        hours = (self.toc - self.tic).seconds / 3600
        topic = self.topic
        self.topic = None
        return topic, hours

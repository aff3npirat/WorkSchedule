from datetime import datetime


class TimerAlreadyRunning(Exception):
    pass


class NoTimerActive(Exception):
    pass


class WorkTimer:
    """Measures working time on a topic.

    Can only stop time for one topic. Before starting a time on new topic stop
    has to be called.
    """

    tic: datetime
    toc: datetime
    topic: str = None

    @staticmethod
    def start(topic):
        if WorkTimer.topic is not None:
            raise TimerAlreadyRunning(WorkTimer.topic)
        WorkTimer.topic = topic
        WorkTimer.tic = datetime.now()

    @staticmethod
    def stop():
        if WorkTimer.topic is None:
            raise NoTimerActive
        WorkTimer.toc = datetime.now()
        WorkTimer.topic = None

    @staticmethod
    def hours():
        diff = WorkTimer.toc - WorkTimer.tic
        seconds_in_hour = 60 * 60
        return diff.seconds / seconds_in_hour

from datetime import datetime


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
            raise ValueError(f"there is already a timer running on topic"
                             f"{WorkTimer.topic}")
        WorkTimer.topic = topic
        WorkTimer.tic = datetime.now()

    @staticmethod
    def stop():
        if WorkTimer.topic is None:
            raise ValueError("there is no active timer")
        WorkTimer.toc = datetime.now()
        WorkTimer.topic = None

    @staticmethod
    def pause():
        # TODO
        pass

    @staticmethod
    def resume(self):
        # TODO
        pass

    @staticmethod
    def hours():
        diff = WorkTimer.toc - WorkTimer.tic
        seconds_in_hour = 60 * 60
        return diff.seconds / seconds_in_hour

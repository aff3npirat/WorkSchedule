from datetime import datetime


class WorkTimer:

    def start(self, topic):
        self.topic = topic
        self.tic = datetime.now()

    def stop(self):
        self.toc = datetime.now()

    def hours(self):
        diff = self.toc - self.tic
        seconds_in_hour = 60 * 60
        return diff.seconds / seconds_in_hour

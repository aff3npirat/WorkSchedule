from pathlib import Path

import helpers
import timer

# topic -> hours to work
schedule = {}
# topic -> hours worked
worked = {}
# topic -> hours to work, remaining since last reset
carry = {}

work_timer = timer.WorkTimer()


def build_schedule(fpath) -> None:
    """Creates schedule from txt file.

    Each topic is on single line and topic name and hours are seperated by
    colon followed by a whitespace.

    Parameters
    ----------
    fpath : str
        Relative path to file.
    """
    fpath = helpers.get_top_directory() / fpath
    if not fpath.is_file():
        raise ValueError(f"could not find schedule at {Path(fpath).absolute()}")

    with open(fpath, "r") as file:
        for line in file.readlines():
            name, hours = [x.rstrip("\n ") for x in line.split(": ")]
            schedule[name] = float(hours)
            worked[name] = 0
            carry[name] = 0


def reset(hard=True, negative_carry=False) -> None:
    """Sets worked hours to 0.

    Parameters
    ----------
    hard : bool or list of str, optional
        If False carry on hours.
        If list of strings carry on hours for given topics.
    negative_carry : bool, optional
        Allow negative values for carry on.
    """
    for topic in schedule:
        if isinstance(hard, list):
            reset_hard = topic not in hard
        else:
            reset_hard = hard
        if not reset_hard:
            carry[topic] = schedule[topic] - worked[topic]
            if carry[topic] < 0 and not negative_carry:
                carry[topic] = 0
        else:
            carry[topic] = 0
        worked[topic] = 0


def work(topic, hours) -> None:
    """
    Parameters
    ----------
    topic : str
        Topic worked on.
    hours : float
        Number of hours. 1.5 hours correspond to 90 minutes.
    """
    worked[topic] += hours


def start_working(topic):
    """

    Parameters
    ----------
    topic : str
        Start timer for current topic.
    """
    work_timer.start(topic)


def stop_working():
    """Stops working timer and adds worked hours."""
    work_timer.stop()
    work(work_timer.topic, round(work_timer.hours(), 1))


# TODO: output, history
if __name__ == '__main__':
    build_schedule("test.txt")
    work("Kacken", 10)
    work("CogScie", 20)
    work("Pipi", 5)
    reset(False, True)
    pass

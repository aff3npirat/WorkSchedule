import unittest

from workschedule import working_history as history


class TestHistory(unittest.TestCase):

    def test_add_entry(self):
        # same topic, same day
        # same topic, not same day
        # not same topic, same day
        a = history.Entry("a", 1)
        b = history.Entry("")

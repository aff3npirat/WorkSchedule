import unittest

from workschedule import working_history as history


class TestHistory(unittest.TestCase):

    def test_add_entry(self) -> None:
        # same topic, same day
        # same topic, not same day
        # not same topic, same day
        a = history.Entry("b", 1)
        b = history.Entry("b", 2)
        c = history.Entry("a", 3)
        c.date = "01/02/0001"
        d = history.Entry("a", 4)

        history.add_entry(a)
        history.add_entry(b)
        self.assertEqual(len(history.history[-1]), 1)
        history.add_entry(c)
        self.assertEqual(len(history.history[-1]), 2)
        history.add_entry(d)
        self.assertEqual(history.history[-1][0], c)
        self.assertEqual(history.history[-1][1], d)
        self.assertEqual(history.history[-1][2].hours, 3)

    def test_get_hours(self) -> None:
        history.add_entry(history.Entry("b", 1))
        history.add_entry(history.Entry("c", 2))
        history.add_entry(history.Entry("a", 3))
        history.add_entry(history.Entry("a", 4))

        self.assertEqual(history.get_hours("a"), 7)
        self.assertEqual(history.get_hours("b"), 1)
        self.assertEqual(history.get_hours("c"), 2)

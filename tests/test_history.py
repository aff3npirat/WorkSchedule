import unittest

import context
import history


class TestHistory(unittest.TestCase):

    def setUp(self) -> None:
        history.history = []
        history.history.append(history.Period())

    def test_add_entry(self) -> None:
        # same topic, same day
        # same topic, not same day
        # not same topic, same day
        a = history.Entry("b", 1)
        b = history.Entry("b", 2)
        c = history.Entry("a", 3)
        c.date = "01/02/0001"
        d = history.Entry("a", 4)

        period = history.history[-1]
        history.add_entry(a)
        history.add_entry(b)
        self.assertEqual(len(period.entries), 1)
        history.add_entry(c)
        self.assertEqual(len(period.entries), 2)
        history.add_entry(d)
        self.assertEqual(period.entries[0], c)
        self.assertEqual(period.entries[1], d)
        self.assertEqual(period.entries[2].hours, 3)

    def test_get_hours(self) -> None:
        history.add_entry(history.Entry("b", 1))
        history.add_entry(history.Entry("c", 2))
        history.add_entry(history.Entry("a", 3))
        history.add_entry(history.Entry("a", 4))

        self.assertEqual(history.get_hours("a"), 7)
        self.assertEqual(history.get_hours("b"), 1)
        self.assertEqual(history.get_hours("c"), 2)
        self.assertEqual(history.get_hours(), 10)


if __name__ == '__main__':
    unittest.main()

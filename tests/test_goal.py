import unittest

import context
import goal


class TestGoal(unittest.TestCase):

    def test_sort(self):
        goals = [
            goal.Goal("A", "", False),
            goal.Goal("C", "", True),
            goal.Goal("B", "", False),
            goal.Goal("E", "", True),
            goal.Goal("D", "", False),
            ]
        goals[0].done = True
        goals[1].done = True
        goals[2].done = True
        expected = [
            goal.Goal("D", "", False),
            goal.Goal("E", "", True),
            goal.Goal("A", "", False),
            goal.Goal("B", "", False),
            goal.Goal("C", "", True),
            ]
        self.assertEqual(goal.sort(goals), expected)

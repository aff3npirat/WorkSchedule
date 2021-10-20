import unittest

import context
import goal


class TestGoal(unittest.TestCase):

    def test_sort(self):
        goals = [
            goal.Goal("A", ""),
            goal.Goal("C", ""),
            goal.Goal("B", ""),
            goal.Goal("E", ""),
            goal.Goal("D", ""),
            ]
        goals[0].done = True
        goals[1].done = True
        goals[2].done = True
        expected = [
            goal.Goal("D", ""),
            goal.Goal("E", ""),
            goal.Goal("A", ""),
            goal.Goal("B", ""),
            goal.Goal("C", ""),
            ]
        self.assertEqual(goal.sort(goals), expected)

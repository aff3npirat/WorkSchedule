import unittest

import context
import goal
import history
import schedule
import work_timer


class TestSchedule(unittest.TestCase):
    in_file = "./test_schedule.txt"

    def setUp(self) -> None:
        schedule.work_timer = work_timer.WorkTimer()
        schedule.from_file(self.in_file)
        schedule.load("test_schedule")

    def test_remaining_hours_after_reset(self):
        schedule.work("Lernen", 6.5)
        schedule.work("Arbeiten", 14)
        schedule.work("LustigeSachen", 17)
        schedule.reset(["Arbeiten", "Lernen"])

        actual = schedule.remaining
        expected = {"Lernen": -1.5, "Arbeiten": 6.0, "LustigeSachen": 0.0}
        self.assertEqual(actual, expected)
        self.assertEqual(len(history.history), 2)

    def test_overview(self):
        schedule.work("Lernen", 6.5)
        schedule.work("Arbeiten", 14)
        schedule.reset(["Lernen", "Arbeiten"])
        schedule.work("Lernen", 4)
        schedule.add_goal("Lernen", "Goal#1", "really useless here!")
        schedule.add_goal("Lernen", "Goal#2", "")
        schedule.add_goal("Lernen", "Goal#3", "")
        schedule.add_goal("Lernen", "Goal#4", "")
        schedule.add_goal("Lernen", "Goal#5", "")
        schedule.add_goal("Arbeiten", "Wirklicheinelange-notiz", "")
        print("---Without detail---")
        print(schedule.overview(False), end="\n\n")
        print("--With detail---")
        print(schedule.overview(True), end="\n\n")

    def test_goals(self):
        # test add_goal
        schedule.add_goal("Lernen", "Goal#1", "Do some really important stuff!")
        expected = {
            "Lernen": [goal.Goal("Goal#1", "Do some really important stuff!")],
            "Arbeiten": [],
            "LustigeSachen": [],
            }
        self.assertEqual(schedule.goals, expected)

        # test mark_done
        schedule.mark_done("Lernen", "Goal#1")
        self.assertEqual(schedule.goals["Lernen"][0].done, True)

        # test goals after reset
        schedule.add_goal("Lernen", "Goal#2", "not so important!")
        schedule.add_goal("Arbeiten", "Goal#3", "really stupid!")
        schedule.mark_done("Arbeiten", "Goal#3")
        schedule.reset()
        expected = {"Lernen": [goal.Goal("Goal#2", "not so important!")],
                    "Arbeiten": [],
                    "LustigeSachen": []}
        self.assertEqual(schedule.goals, expected)


if __name__ == '__main__':
    unittest.main()

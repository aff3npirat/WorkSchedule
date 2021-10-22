import unittest

import context
import goal
import history
import schedule
import work_timer


class TestSchedule(unittest.TestCase):
    in_file = "./test_schedule.txt"

    def setUp(self) -> None:
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
        schedule.add_goal("Lernen", "Goal#1", "really useless here!", False)
        schedule.add_goal("Lernen", "Goal#2", "", False)
        schedule.add_goal("Lernen", "Goal#3", "", False)
        schedule.add_goal("Lernen", "Goal#4", "", False)
        schedule.add_goal("Lernen", "Goal#5", "", False)
        schedule.add_goal("Arbeiten", "Wirklicheinelange-notiz", "", False)
        schedule.mark_done("Goal#1")
        print("---Without detail---")
        print(schedule.overview(False), end="\n\n")
        print("--With detail---")
        print(schedule.overview(True), end="\n\n")

    def test_topic_overview(self):
        schedule.work("Lernen", 6.5)
        schedule.work("Arbeiten", 14)
        schedule.reset(["Lernen", "Arbeiten"])
        schedule.work("Lernen", 4)
        schedule.add_goal("Lernen", "Goal#1", "a" * 50, False)
        schedule.add_goal("Lernen", "Goal#2", "b" * 60, True)
        schedule.add_goal("Lernen", "Goal#3", "c" * 100, False)
        schedule.add_goal("Lernen", "Goal#4", "d" * 48 + " " + "e" * 20, False)
        schedule.add_goal("Arbeiten",
                          "Goal#5",
                          "hoffentlich sieht man mich nicht.",
                          False)
        schedule.mark_done("Goal#1")
        print("---Without detail---")
        print(schedule.topic_overview("Lernen", False, 60), end="\n\n")
        print("--With detail---")
        print(schedule.topic_overview("Lernen", True, 60), end="\n\n")

    def test_goals(self):
        # test add_goal
        schedule.add_goal("Lernen",
                          "Goal#1",
                          "Do some really important stuff!",
                          False)
        expected = {
            "Lernen":
                [goal.Goal("Goal#1", "Do some really important stuff!", False)],
            "Arbeiten": [],
            "LustigeSachen": [],
            }
        self.assertEqual(schedule.goals, expected)
        self.assertRaises(schedule.DuplicateGoal,
                          schedule.add_goal,
                          "Arbeiten",
                          "Goal#1",
                          "Something else",
                          True)

        # test mark_done
        schedule.mark_done("Goal#1")
        self.assertEqual(schedule.goals["Lernen"][0].done, True)
        self.assertRaises(schedule.NoSuchGoal,
                          schedule.mark_done,
                          "Goal#-1")

        # test goals after reset
        schedule.add_goal("Lernen", "Goal#2", "not so important!", False)
        schedule.add_goal("Arbeiten", "Goal#3", "really stupid!", False)
        schedule.add_goal("Arbeiten", "Goal#4", "really really stupid!", True)
        schedule.mark_done("Goal#3")
        schedule.mark_done("Goal#4")
        schedule.reset()
        expected = {"Lernen": [goal.Goal("Goal#2", "not so important!", False)],
                    "Arbeiten":
                        [goal.Goal("Goal#4", "really really stupid!", True)],
                    "LustigeSachen": []}
        self.assertEqual(schedule.goals, expected)

    def test_add_topic(self):
        schedule.add_topic("Skaten", 20.5)
        schedule.add_topic("Lernen", 12)
        expected = {"Lernen": 12.0,
                    "Arbeiten": 20.0,
                    "LustigeSachen": 15.5,
                    "Skaten": 20.5}
        self.assertEqual(schedule.schedule, expected)
        expected = {"Lernen": 0.0,
                    "Arbeiten": 0.0,
                    "LustigeSachen": 0.0,
                    "Skaten": 0.0}
        self.assertEqual(schedule.remaining, expected)
        expected = {"Lernen": [],
                    "Arbeiten": [],
                    "LustigeSachen": [],
                    "Skaten": []}
        self.assertEqual(schedule.goals, expected)

    def test_remove_topic(self):
        schedule.remove_topic("LustigeSachen")
        self.assertEqual(schedule.schedule, {"Lernen": 5.0, "Arbeiten": 20.0})
        self.assertEqual(schedule.remaining, {"Lernen": 0.0, "Arbeiten": 0.0})
        self.assertEqual(schedule.goals, {"Lernen": [], "Arbeiten": []})
        self.assertRaises(schedule.NoSuchTopic,
                          schedule.remove_topic,
                          "Schwimmen")

    def test_start_working(self):
        schedule.start_working("Lernen")
        self.assertRaises(schedule.NoSuchTopic,
                          schedule.start_working,
                          "")
        self.assertRaises(work_timer.TimerAlreadyRunning,
                          schedule.start_working,
                          "Lernen")
        schedule.stop_working()

    def test_stop_working(self):
        self.assertRaises(work_timer.NoTimerActive, schedule.stop_working)

    def test_load(self):
        self.assertRaises(FileNotFoundError, schedule.load, "nixda")
        self.assertRaises(FileNotFoundError, schedule.load, "test_load")
        expected = {"Lernen": 5.0, "Arbeiten": 20.0, "LustigeSachen": 15.5}
        self.assertEqual(schedule.schedule, expected)
        self.assertIsNone(schedule.load("test_schedule"))


if __name__ == '__main__':
    unittest.main()

import unittest

import context
import history
import schedule
import work_timer


class TestSchedule(unittest.TestCase):
    in_file = "./test_schedule.txt"

    def setUp(self) -> None:
        schedule.schedule = {}
        schedule.remaining = {}
        schedule.work_timer = work_timer.WorkTimer()
        schedule.from_file(self.in_file)
        schedule.load("test_schedule")

    def test_reset(self):
        schedule.work("Lernen", 6.5)
        schedule.work("Arbeiten", 14)
        schedule.work("LustigeSachen", 17)
        schedule.reset(["Arbeiten", "Lernen"])

        actual = schedule.remaining
        expected = {"Lernen": -1.5, "Arbeiten": 6.0, "LustigeSachen": 0.0}
        self.assertEqual(actual, expected)
        self.assertEqual(len(history.history), 2)

    def test_as_string(self):
        schedule.work("Lernen", 6.5)
        schedule.work("Arbeiten", 14)
        schedule.reset(["Lernen", "Arbeiten"])
        schedule.work("Lernen", 4)
        print("---Without detail---")
        print(schedule.as_string(False), end="\n\n")
        print("--With detail---")
        print(schedule.as_string(True), end="\n\n")


if __name__ == '__main__':
    unittest.main()

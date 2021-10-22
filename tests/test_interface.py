import argparse
import unittest
import sys
from contextlib import contextmanager
import io
from unittest import mock

import context
import schedule
import terminal_interface as interface
from schedule import NoSuchTopic, NoSuchGoal, DuplicateGoal
from work_timer import NoTimerActive, TimerAlreadyRunning


@contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestTerminalInterface(unittest.TestCase):
    in_file = "./test_schedule.txt"

    def setUp(self) -> None:
        schedule.from_file(self.in_file)
        schedule.load("test_schedule")

    def test_work(self):
        parser_work = interface.parser_work

        args = parser_work.parse_args(["", "4"])
        self.assertRaises(NoSuchTopic, interface.work, args)

        args = parser_work.parse_args(["Schwimmen", "5"])
        self.assertRaises(NoSuchTopic, interface.work, args)

        with captured_output() as (out, err):
            args = parser_work.parse_args("Lernen -s".split())
            interface.work(args)
            self.assertEqual("Invalid use of -s.",
                             out.getvalue().splitlines()[0])

            args = parser_work.parse_args("'' 5 -s".split())
            interface.work(args)
            self.assertEqual("Invalid use of -s.",
                             out.getvalue().splitlines()[1])

            args = parser_work.parse_args([])
            interface.work(args)
            self.assertEqual("At least one argument is required.",
                             out.getvalue().splitlines()[2])

    def test_add_topic(self):
        parser_add_topic = interface.parser_add_topic

        with captured_output() as (out, err):
            args = parser_add_topic.parse_args("'' 5".split())
            interface.add_topic(args)
            self.assertEqual("'' is not a valid name.",
                             out.getvalue().splitlines()[0])

    def test_remove_topic(self):
        parser_remove_topic = interface.parser_remove_topic

        args = parser_remove_topic.parse_args(["Schwimmen"])
        self.assertRaises(NoSuchTopic, interface.remove_topic, args)

    def test_overview(self):
        parser_overview = interface.parser_overview

        with captured_output() as (out, err):
            args = parser_overview.parse_args([])
            interface.overview(args)
            self.assertEqual(schedule.overview(False),
                             out.getvalue()[:-1])  # remove newline from print

        with captured_output() as (out, err):
            args = parser_overview.parse_args(["-d"])
            interface.overview(args)
            self.assertEqual(schedule.overview(True),
                             out.getvalue()[:-1])

        with captured_output() as (out, err):
            args = parser_overview.parse_args("Lernen".split())
            interface.overview(args)
            self.assertEqual(schedule.topic_overview("Lernen", False, 60),
                             out.getvalue()[:-1])

        with captured_output() as (out, err):
            args = parser_overview.parse_args("Lernen -d".split())
            interface.overview(args)
            self.assertEqual(schedule.topic_overview("Lernen", True, 60),
                             out.getvalue()[:-1])

        args = parser_overview.parse_args("Schwimmen -d".split())
        self.assertRaises(NoSuchTopic, interface.overview, args)

    @mock.patch("terminal_interface.input", create=True)
    def test_goal_cmd(self, mocked_input):
        parser_goal = interface.parser_goal

        with captured_output() as (out, err):
            # test invalid command
            args = parser_goal.parse_args("remove Lernen".split())
            interface.goal_cmd(args)
            self.assertEqual("There is no command 'remove'.",
                             out.getvalue().splitlines()[0])

        # test goal add
        with captured_output() as (out, err):
            mocked_input.side_effect = ["", "an invalid goal name."]
            args = parser_goal.parse_args("add Lernen".split())
            interface.goal_cmd(args)
            self.assertEqual("'' is not a valid name.",
                             out.getvalue().splitlines()[0])

        mocked_input.side_effect = ["Goal#1", "a valid goal."]
        args = parser_goal.parse_args("add Schwimmen".split())
        self.assertRaises(NoSuchTopic, interface.goal_cmd, args)

        args = parser_goal.parse_args("add Lernen".split())
        mocked_input.side_effect = ["Goal#1", "a valid goal."]
        interface.goal_cmd(args)
        mocked_input.side_effect = ["Goal#1", "a valid goal."]
        self.assertRaises(DuplicateGoal, interface.goal_cmd, args)

        # test done
        args = parser_goal.parse_args("done Goal#2".split())
        self.assertRaises(NoSuchGoal, interface.goal_cmd, args)

        with captured_output() as (out, err):
            args = parser_goal.parse_args("done Goal#2 -p".split())
            interface.goal_cmd(args)
            self.assertEqual("Invalid use of -p.",
                             out.getvalue().splitlines()[0])

            args = parser_goal.parse_args("done Goal#1 -p".split())
            interface.goal_cmd(args)
            self.assertEqual("Invalid use of -p.",
                             out.getvalue().splitlines()[1])


if __name__ == '__main__':
    unittest.main()

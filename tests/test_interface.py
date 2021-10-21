import argparse
import unittest
import sys
from contextlib import contextmanager
import io
from unittest import mock

import context
import schedule
import terminal_interface as interface


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
        parser_work = argparse.ArgumentParser()
        parser_work.add_argument("topic",
                                 type=str,
                                 help="topic help")
        parser_work.add_argument("hours",
                                 type=float,
                                 help="hours help")

        with captured_output() as (out, err):
            args = parser_work.parse_args(["", "4"])
            interface.work(args)
            self.assertEqual("'' is not a valid topic name.",
                             out.getvalue().splitlines()[0])

            args = parser_work.parse_args(["Schwimmen", "5"])
            interface.work(args)
            self.assertEqual("Could not find topic Schwimmen.",
                             out.getvalue().splitlines()[1])

    def test_workt(self):
        parser_workt = argparse.ArgumentParser()
        parser_workt.add_argument("-t",
                                  "--topic",
                                  default="",
                                  type=str,
                                  help="-t help")

        with captured_output() as (out, err):
            args = parser_workt.parse_args([])
            interface.workt(args)
            self.assertEqual("There is no active timer.",
                             out.getvalue().splitlines()[0])

            args = parser_workt.parse_args("-t Lernen".split())
            interface.workt(args)
            args = parser_workt.parse_args("-t Schwimmen".split())
            interface.workt(args)
            self.assertEqual("Could not find topic Schwimmen.",
                             out.getvalue().splitlines()[1])

            args = parser_workt.parse_args("-t Lernen".split())
            interface.workt(args)
            self.assertEqual("There is already a timer running.",
                             out.getvalue().splitlines()[2])

    def test_add_topic(self):
        parser_add_topic = argparse.ArgumentParser()
        parser_add_topic.add_argument("topic", type=str, help="topic help")
        parser_add_topic.add_argument("hours", type=float, help="hours help")

        with captured_output() as (out, err):
            args = parser_add_topic.parse_args("'' 5".split())
            interface.add_topic(args)
            self.assertEqual("'' is not a valid topic name.",
                             out.getvalue().splitlines()[0])

    def test_remove_topic(self):
        parser_remove_topic = argparse.ArgumentParser()
        parser_remove_topic.add_argument("topic", type=str, help="topic help")

        with captured_output() as (out, err):
            args = parser_remove_topic.parse_args(["Schwimmen"])
            interface.remove_topic(args)
            self.assertEqual("Could not find Schwimmen in current schedule.",
                             out.getvalue().splitlines()[0])

    def test_overview(self):
        parser_overview = argparse.ArgumentParser()
        parser_overview.add_argument("-t",
                                     "--topic",
                                     default="",
                                     type=str,
                                     help="t help")
        parser_overview.add_argument("-d",
                                     "--detail",
                                     default=False,
                                     action="store_true",
                                     help="d help")

        with captured_output() as (out, err):
            args = parser_overview.parse_args([])
            interface.overview(args)
            self.assertEqual(schedule.overview(False),
                             out.getvalue().rstrip("\n"))

        with captured_output() as (out, err):
            args = parser_overview.parse_args(["-d"])
            interface.overview(args)
            self.assertEqual(schedule.overview(True),
                             out.getvalue().rstrip("\n"))

        with captured_output() as (out, err):
            args = parser_overview.parse_args("-t Lernen".split())
            interface.overview(args)
            self.assertEqual(schedule.topic_overview("Lernen", False),
                             out.getvalue().rstrip("\n"))

        with captured_output() as (out, err):
            args = parser_overview.parse_args("-t Lernen -d".split())
            interface.overview(args)
            self.assertEqual(schedule.topic_overview("Lernen", True),
                             out.getvalue().rstrip("\n"))

    @mock.patch("terminal_interface.input", create=True)
    def test_goal(self, mocked_input):
        parser_goal = argparse.ArgumentParser()
        parser_goal.add_argument("cmd", type=str, help="cmd help")
        parser_goal.add_argument("topic", type=str, help="topic help")
        parser_goal.add_argument("-p",
                                 "--periodic",
                                 default=False,
                                 action="store_true",
                                 help="-p help")

        with captured_output() as (out, err):
            # test invalid command
            args = parser_goal.parse_args("remove Lernen".split())
            interface.goal_cmd(args)
            self.assertEqual("There is no command 'remove'.",
                             out.getvalue().splitlines()[0])

            # test goal add
            mocked_input.side_effect = ["", "an invalid goal name."]
            args = parser_goal.parse_args("add Lernen".split())
            interface.goal_cmd(args)
            self.assertEqual("'' is not a valid name.",
                             out.getvalue().splitlines()[1])

            mocked_input.side_effect = ["Goal#1", "a valid goal."]
            args = parser_goal.parse_args("add Schwimmen".split())
            interface.goal_cmd(args)
            self.assertEqual("Could not find topic Schwimmen.",
                             out.getvalue().splitlines()[2])

            args = parser_goal.parse_args("add Lernen".split())
            mocked_input.side_effect = ["Goal#1", "a valid goal."]
            interface.goal_cmd(args)
            mocked_input.side_effect = ["Goal#1", "a valid goal."]
            interface.goal_cmd(args)
            self.assertEqual("Goal name must be unique.",
                             out.getvalue().splitlines()[3])

            # test done
            args = parser_goal.parse_args("done Goal#2".split())
            interface.goal_cmd(args)
            self.assertEqual("Could not find goal Goal#2.",
                             out.getvalue().splitlines()[4])

            args = parser_goal.parse_args("done Goal#2 -p".split())
            interface.goal_cmd(args)
            self.assertEqual("Invalid use of -p.",
                             out.getvalue().splitlines()[5])

            args = parser_goal.parse_args("done Goal#1 -p".split())
            interface.goal_cmd(args)
            self.assertEqual("Invalid use of -p.",
                             out.getvalue().splitlines()[5])


if __name__ == '__main__':
    unittest.main()

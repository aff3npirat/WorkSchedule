import argparse
import unittest
import sys
from contextlib import contextmanager
import io

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

    def test_work_invalid_input(self):
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

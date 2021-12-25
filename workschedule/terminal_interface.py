import argparse
import ctypes
import sys

import schedule
from schedule import InvalidNameException, DuplicateNameException, NoScheduleException
from work_timer import TimerRunningException

LINE_LENGTH = 60


def handle_exceptions(err: Exception) -> None:
    if type(err) in [InvalidNameException, DuplicateNameException, TimerRunningException, NoScheduleException]:
        print(str(err))
    else:
        raise err

def add_topic_handler(args) -> None:
    schedule.add_topic(args.topic, args.hours)


def remove_topic_handler(args) -> None:
    schedule.remove_topic(args.topic)


def work_parser_handler(args) -> None:
    if args.topic is args.hours is None:
        topic = schedule.curr_timer.topic
        hours = schedule.curr_timer.stop()
        now = schedule.curr_timer.toc.strftime("%H:%M")
        schedule.work(topic, hours)
        print(f"[{now}] Stoped work-timer. Worked {hours:.1f} hours on {topic}.")
    elif args.hours is None:
        schedule.start_working(args.topic)
        now = schedule.curr_timer.tic.strftime("%H:%M")
        print(f"[{now}] Started work-timer.")
    else:
        schedule.work(args.topic, args.hours)


def goal_add_handler(args) -> None:
    if len(args.name) > LINE_LENGTH:
        print(f"Name can not be longer than {LINE_LENGTH} chars.")
        return

    description = input("Enter description: ").rstrip()
    schedule.add_goal(args.topic, args.name, description, args.periodic)


def done_goal_handler(args):
    schedule.mark_done(args.topic, args.name)


def remove_goal_handler(args) -> None:
    schedule.remove_goal(args.topic, args.name)


def reset_parser_handler(args):
    if args.reset_goals:
        schedule.reset(args.topics)
    else:
        schedule.reset(args.topics, schedule.goals.keys())


def new_schedule(name: str):
    schedule.from_file(name)


def set_active(name: str):
    schedule.set_as_active(name)
    print(f"Set {name} as active.")


def main_parser_handler(args):
    nargs = len(args.cmd_args)
    if nargs == 0:
        print(f"Active schedule is '{schedule.get_active_schedule()}'")
    elif nargs == 1 and args.cmd_args[0] in ["overview", "Period", "view"]:
        # enable virtual terminal sequences
        # Reference: https://docs.microsoft.com/en-us/windows/console/getstdhandle
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        print(schedule.overview())
    elif nargs == 1 and schedule._valid_topic_name(args.cmd_args[0]):
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        print(schedule.topic_overview(args.cmd_args[0], LINE_LENGTH))
    else:
        args = main_parser.parse_args(args.cmd_args)
        args.func(args)


overview_parser = argparse.ArgumentParser(description="main parser")
overview_parser.add_argument("cmd_args", nargs="*", default=[])
overview_parser.set_defaults(func=main_parser_handler)

main_parser = argparse.ArgumentParser(description="subparsers")
subparsers = main_parser.add_subparsers(dest="parser_name")

work_parser = subparsers.add_parser("work")
work_parser.add_argument("topic", type=str, default=None, nargs="?")
work_parser.add_argument("hours", type=float, default=None, nargs="?")
work_parser.set_defaults(func=work_parser_handler)

add_topic_parser = subparsers.add_parser("add")
add_topic_parser.add_argument("topic", type=str)
add_topic_parser.add_argument("hours", type=float)
add_topic_parser.set_defaults(func=add_topic_handler)

remove_topic_parser = subparsers.add_parser("remove")
remove_topic_parser.add_argument("topic", type=str)
remove_topic_parser.set_defaults(func=remove_topic_handler)

reset_parser = subparsers.add_parser("reset")
reset_parser.add_argument("topics", type=str, nargs="*")
reset_parser.add_argument("-g", "--reset_goals", default=False, action="store_true")
reset_parser.set_defaults(func=reset_parser_handler)

load_parser = subparsers.add_parser("set")
load_parser.add_argument("name", type=str)

new_schedule_parser = subparsers.add_parser("new")
new_schedule_parser.add_argument("name", type=str)

goal_parser = subparsers.add_parser("goal")
goal_subparsers = goal_parser.add_subparsers()

goal_add_parser = goal_subparsers.add_parser("add")
goal_add_parser.add_argument("topic", type=str)
goal_add_parser.add_argument("name", type=str)
goal_add_parser.add_argument("-p", "--periodic", default=False, action="store_true")
goal_add_parser.set_defaults(func=goal_add_handler)

goal_remove_parser = goal_subparsers.add_parser("remove")
goal_remove_parser.add_argument("topic", type=str)
goal_remove_parser.add_argument("name", type=str)
goal_remove_parser.set_defaults(func=remove_goal_handler)

goal_done_parser = goal_subparsers.add_parser("done")
goal_done_parser.add_argument("topic", type=str)
goal_done_parser.add_argument("name", type=str)
goal_done_parser.set_defaults(func=done_goal_handler)


def main():
    try:
        nargs = len(sys.argv)
        if nargs == 3 and sys.argv[1] == "set":
            set_active(sys.argv[2])
        elif nargs == 3 and sys.argv[1] == "new":
            schedule.new_schedule(sys.argv[2])
            set_active(sys.argv[2])
        else:
            args = overview_parser.parse_args()
            name = schedule.get_active_schedule()
            schedule.load(name)
            args.func(args)
            schedule.save(name)
    except Exception as err:
        handle_exceptions(err)


if __name__ == '__main__':
    main()

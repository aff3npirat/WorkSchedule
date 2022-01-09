import argparse
import ctypes
import sys
from datetime import datetime

import schedule
from schedule import InvalidNameException, DuplicateNameException, NoScheduleException
from timer import TimerRunningException

LINE_LENGTH = 60


def exeption_handler(err: Exception) -> None:
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
        topic, hours = schedule.stop_worktimer()
        print(f"[{datetime.now().strftime('%H:%M')}] Stoped work-timer. Worked {hours:.2f} hours on {topic}.")
    elif args.hours is None:
        schedule.start_worktimer(args.topic)
        print(f"[{datetime.now().strftime('%H:%M')}] Started work-timer.")
    else:
        schedule.work(args.topic, args.hours)


def goal_add_handler(args) -> None:
    if len(args.name) > LINE_LENGTH:
        print(f"Name can not be longer than {LINE_LENGTH} chars.")
        return

    description = input("Enter description: ").rstrip()
    schedule.add_goal(args.topic, args.name, description, args.periodic)


def done_goal_handler(args) -> None:
    schedule.mark_done(args.topic, args.name)


def remove_goal_handler(args) -> None:
    schedule.remove_goal(args.topic, args.name)


def reset_parser_handler(args) -> None:
    schedule.reset(args.topics)


def new_schedule(name: str) -> None:
    schedule.from_file(name)


def set_active(name: str) -> None:
    schedule.set_as_active(name)
    print(f"Set {name} as active.")


def view_parser_handler(args) -> None:
    # enable virtual terminal sequences
    # Reference: https://docs.microsoft.com/en-us/windows/console/getstdhandle
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    if args.topic is None:
        print(schedule.overview())
    else:
        print(schedule.topic_overview(args.topic, LINE_LENGTH))


def view_todo_handler(args) -> None:
    print(schedule.todo_as_str())


def add_todo_handler(args) -> None:
    if args.pos is None:
        pos = -1
    else:
        pos = args.pos -1

    schedule.add_todo(args.topic, args.goal, pos)


def remove_todo_handler(args) -> None:
    if args.pos is None:
        schedule.reset_todo(False)
    else:
        schedule.remove_todo(args.pos - 1)


def done_todo_handler(args) -> None:
    schedule.reset_todo(True)


main_parser = argparse.ArgumentParser(description="subparsers")
main_parser.set_defaults(func=lambda x: print(f"Active schedule is '{schedule.get_active_schedule()}'"))
subparsers = main_parser.add_subparsers()

overview_parser = subparsers.add_parser("view")
overview_parser.add_argument("topic", default=None, type=str, nargs="?")
overview_parser.set_defaults(func=view_parser_handler)

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

todo_main_parser = subparsers.add_parser("todo")
todo_main_parser.set_defaults(func=view_todo_handler)
todo_subparsers = todo_main_parser.add_subparsers()

todo_add_parser = todo_subparsers.add_parser("add")
todo_add_parser.add_argument("topic", type=str)
todo_add_parser.add_argument("goal", type=str)
todo_add_parser.add_argument("-i", "--pos", type=int, default=None)
todo_add_parser.set_defaults(func=add_todo_handler)

todo_remove_parser = todo_subparsers.add_parser("rm")
todo_remove_parser.add_argument("-i", "--pos", type=int, default=None)
todo_remove_parser.set_defaults(func=remove_todo_handler)

todo_done_parser = todo_subparsers.add_parser("done")
todo_done_parser.set_defaults(func=done_todo_handler)


def main() -> None:
    try:
        nargs = len(sys.argv)
        if nargs == 3 and sys.argv[1] == "set":
            set_active(sys.argv[2])
        elif nargs == 3 and sys.argv[1] == "new":
            schedule.new_schedule(sys.argv[2])
            set_active(sys.argv[2])
        else:
            args = main_parser.parse_args()
            name = schedule.get_active_schedule()
            schedule.load(name)
            args.func(args)
            schedule.save(name)
    except Exception as err:
        exeption_handler(err)


if __name__ == '__main__':
    main()

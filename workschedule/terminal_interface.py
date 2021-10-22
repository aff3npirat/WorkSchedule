import argparse

import schedule
from schedule import NoSuchTopic, NoSuchGoal, DuplicateGoal
from work_timer import NoTimerActive, TimerAlreadyRunning

LINE_LENGTH = 60


# TODO: add .bat files, that call python.exe in workschedule env
def handle(err: Exception) -> None:
    if type(err) is NoSuchTopic:
        print(f"Could not find topic '{err}'.")
    elif type(err) is NoSuchGoal:
        print(f"Could not find goal '{err}'.")
    elif type(err) is DuplicateGoal:
        print(f"Goal name must be unique.")
    elif type(err) is NoTimerActive:
        print("Can not stop work-timer: no timer active.")
    elif type(err) is TimerAlreadyRunning:
        print("Can not start work-timer: timer is already active.")
    else:
        raise err


def overview(args) -> None:
    if args.topic is None:
        print(schedule.overview(args.detail))
    else:
        print(schedule.topic_overview(args.topic, args.detail, LINE_LENGTH))


def add_topic(args) -> None:
    if args.topic == "''":
        print("'' is not a valid name.")
    else:
        schedule.add_topic(args.topic, args.hours)


def remove_topic(args) -> None:
    schedule.remove_topic(args.topic)


# TODO: output time when starting timer, output duraton when stopping timer
def work(args) -> None:
    if args.stop and not (args.topic is None and args.hours is None):
        print("Invalid use of -s.")
        return
    if not any([args.stop, args.topic, args.hours]):
        print("At least one argument is required.")
        return

    if args.stop:
        schedule.stop_working()
        print("Stopping work-timer.")
    else:
        if args.hours is None:
            schedule.start_working(args.topic)
            print("Starting work-timer.")
        else:
            schedule.work(args.topic, args.hours)


def goal_cmd(args) -> None:
    """Selects function to call based on args.cmd."""
    if args.cmd == "add":
        add_goal_cmd(args.topic, args.periodic)
    elif args.cmd == "done":
        if args.periodic:
            print("Invalid use of -p.")
            return
        mark_done_cmd(args.topic)
    else:
        print(f"There is no command '{args.cmd}'.")


def add_goal_cmd(topic: str, periodic: bool) -> None:
    name = input("Enter name: ").rstrip()
    if name == "":
        print("'' is not a valid name.")
        return
    if len(name) > LINE_LENGTH:
        print(f"Name can not be longer than {LINE_LENGTH} chars.")
        return
    description = input("Enter description: ").rstrip()

    schedule.add_goal(topic, name, description, periodic)


def mark_done_cmd(name: str):
    schedule.mark_done(name)


def reset(args):
    schedule.reset(args.topics)


def new_schedule(args):
    schedule.from_file(args.file, args.name)


def as_active(args):
    schedule.set_as_active(args.name)
    print(f"Set {args.name} as active.")


def get_active(args):
    name = schedule.get_active_schedule()
    print(f"Active schedule is: {name}")


parser = argparse.ArgumentParser(description="main parser")
parser.set_defaults(func=get_active)
subparsers = parser.add_subparsers(description="subparsers")

parser_overview = subparsers.add_parser("overview", help="overview help")
parser_overview.add_argument("topic",
                             nargs="?",
                             default=None,
                             type=str,
                             help="topic help")
parser_overview.add_argument("-d",
                             "--detail",
                             default=False,
                             action="store_true",
                             help="d help")
parser_overview.set_defaults(func=overview)

parser_add_topic = subparsers.add_parser("add", help="add_topic help")
parser_add_topic.add_argument("topic", type=str, help="topic help")
parser_add_topic.add_argument("hours", type=float, help="hours help")
parser_add_topic.set_defaults(func=add_topic)

parser_remove_topic = subparsers.add_parser("remove", help="remove_topic help")
parser_remove_topic.add_argument("topic", type=str, help="topic help")
parser_remove_topic.set_defaults(func=remove_topic)

parser_work = subparsers.add_parser("work", help="work help")
parser_work.add_argument("topic",
                         type=str,
                         nargs="?",
                         default=None,
                         help="topic help")
parser_work.add_argument("hours",
                         type=float,
                         nargs="?",
                         default=None,
                         help="hours help")
parser_work.add_argument("-s",
                         "--stop",
                         default=False,
                         action="store_true",
                         help="-s help")
parser_work.set_defaults(func=work)

parser_goal = subparsers.add_parser("goal", help="goal help")
parser_goal.add_argument("cmd", type=str, help="cmd help")
parser_goal.add_argument("topic", type=str, help="topic help")
parser_goal.add_argument("-p",
                         "--periodic",
                         default=False,
                         action="store_true",
                         help="-p help")
parser_goal.set_defaults(func=goal_cmd)

parser_reset = subparsers.add_parser("reset", help="reset help")
parser_reset.add_argument("topics", nargs="*", type=str, help="topics help")
parser_reset.set_defaults(func=reset)

parser_new = subparsers.add_parser("new", help="new help")
parser_new.add_argument("-f", "--file", required=True, type=str, help="-f help")
parser_new.add_argument("-n", "--name", required=True, type=str, help="-n help")
parser_new.set_defaults(func=new_schedule)

parser_load = subparsers.add_parser("load", help="load help")
parser_load.add_argument("name", type=str, help="name help")
parser_load.set_defaults(func=as_active)


def main():
    args = parser.parse_args()
    try:
        name = schedule.get_active_schedule()
        schedule.load(name)
        args.func(args)
        schedule.save(name)
    except Exception as err:
        handle(err)


if __name__ == '__main__':
    main()

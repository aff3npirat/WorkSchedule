import argparse

import schedule
from schedule import NoSuchTopic, NoSuchGoal
from work_timer import NoTimerRunning, TimerAlreadyRunning


def overview(args) -> None:
    if args.topic == "":
        print(schedule.overview(args.detail))
    else:
        print(schedule.topic_overview(args.topic, args.detail))


def add_topic(args) -> None:
    if args.topic == "":
        print("'' is not a valid topic name.")
    else:
        schedule.add_topic(args.topic, args.hours)


def remove_topic(args) -> None:
    if args.topic == "":
        print("'' is not a valid topic name.")
    else:
        try:
            schedule.remove_topic(args.topic)
        except NoSuchTopic:
            print(f"Could not find {args.topic} in current schedule.")


def work(args) -> None:
    if args.topic == "":
        print("'' is not a valid topic name.")
    else:
        try:
            schedule.work(args.topic, args.hours)
        except NoSuchTopic:
            print(f"Could not find topic {args.topic}.")


def workt(args) -> None:
    if args.stop:
        try:
            schedule.stop_working()
        except NoTimerRunning:
            print("There is no timer running.")
    elif args.topic != "":
        try:
            schedule.start_working(args.topic)
        except TimerAlreadyRunning:
            print("There is already a timer running.")
        except NoSuchTopic:
            print(f"Could not find topic {args.topic}.")
    else:
        print("'' is not a valid topic name.")


def goal_cmd(args) -> None:
    """Selects function to call based on args.cmd."""


def add_goal(topic: str, name: str, description: str) -> None: pass


def done(topic: str, periodic: bool) -> None: pass


def load(args) -> None: pass


def new(args) -> None: pass


# TODO: add_topic, remove_topic, goal add/done


parser = argparse.ArgumentParser(description="main parser")
subparsers = parser.add_subparsers(description="subparsers")

parser_overview = subparsers.add_parser("overview", help="overview help")
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
parser_overview.set_defaults(func=overview)

parser_add_topic = subparsers.add_parser("add", help="add_topic help")
parser_add_topic.add_argument("topic", type=str, help="topic help")
parser_add_topic.add_argument("hours", type=float, help="hours help")
parser_add_topic.set_defaults(func=add_topic)

parser_remove_topic = subparsers.add_parser("remove", help="remove_topic help")
parser_remove_topic.add_argument("topic", type=str, help="topic help")
parser_remove_topic.set_defaults(func=remove_topic)

parser_work = subparsers.add_parser("work", help="work help")
parser_work.add_argument("topic", type=str, help="topic help")
parser_work.add_argument("hours", type=float, help="hours help")
parser_work.set_defaults(func=work)

parser_workt = subparsers.add_parser("workt", help="workt help")
parser_workt.add_argument("-t", "--topic", default="", type=str, help="-t help")
parser_workt.add_argument("-s",
                          "--stop",
                          default=False,
                          action="store_true",
                          help="-s help")
parser_workt.set_defaults(func=workt)

parser_goal = subparsers.add_parser("goal", help="goal help")
parser_goal.add_argument("cmd", type=str, help="cmd help")
parser_goal.add_argument("topic", type=str, help="topic help")
parser_goal.add_argument("-p",
                         "--periodic",
                         default=False,
                         action="store_true",
                         help="-p help")
parser_goal.set_defaults(func=goal_cmd)

parser_load = subparsers.add_parser("load", help="load help")
parser_load.add_argument("name", type=str, help="name help")
parser_load.add_argument("-s",
                         "--no-saving",
                         default=False,
                         action="store_true",
                         help="-s help")
parser_load.set_defaults(func=load)

parser_new = subparsers.add_parser("new", help="new help")
parser_new.add_argument("-l",
                        "--no-loading",
                        default=False,
                        action="store_true",
                        help="-l help")
parser_new.set_defaults(func=new)

args = parser.parse_args()
# args.func(args)

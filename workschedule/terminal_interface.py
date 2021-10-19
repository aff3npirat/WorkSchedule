import argparse


def overview(args) -> None: pass


def work(args) -> None: pass


def done(args) -> None: pass


def load(args) -> None: pass


def new(args) -> None: pass


parser = argparse.ArgumentParser(description="main parser")
subparsers = parser.add_subparsers(description="subparsers")

parser_overview = subparsers.add_parser("overview", help="overview help")
parser_overview.add_argument("-t", "--topic", type=str, help="t help")
parser_overview.add_argument("-d",
                             "--detail",
                             default=False,
                             action="store_true",
                             help="d help")
parser_overview.set_defaults(func=overview)

parser_work = subparsers.add_parser("work", help="work help")
parser_work.add_argument("topic", type=str, help="topic help")
parser_work.add_argument("hours", type=float, help="hours help")
parser_work.add_argument("-s",
                         "--stop",
                         default=False,
                         action="store_true",
                         help="-s help")
parser_work.set_defaults(func=overview)

parser_done = subparsers.add_parser("done", help="done help")
parser_done.add_argument("goal", type=str, help="goal help")
parser_done.add_argument("-p",
                         "--periodic",
                         defaul=False,
                         action="store_true",
                         help="-p help")
parser_done.set_defaults(func=done)

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
args.func(args)

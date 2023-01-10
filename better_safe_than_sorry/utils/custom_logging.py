import logging
import argparse
from typing import Sequence

_loglevels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def available_loglevels() -> Sequence[str]:
    return list(_loglevels.keys())


def add_loglevel_argument(parser: argparse.ArgumentParser, default_loglevel="warning"):
    parser.add_argument(
        "--loglevel",
        default=default_loglevel,
        choices=available_loglevels(),
        help="Specify the desired loglevel. (choices: %(choices)s)",
    )


def get_log_level(args: argparse.Namespace) -> int:
    return _loglevels[args.loglevel]

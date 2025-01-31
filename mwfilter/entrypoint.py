# -*- coding: utf-8 -*-

from argparse import Namespace
from logging import getLogger
from sys import exit as sys_exit
from typing import List, Optional

from mwfilter.arguments import get_default_arguments

logger = getLogger()


def app(args: Namespace) -> None:
    logger.debug(args)


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)
    try:
        app(args)
    except BaseException as e:
        logger.exception(e)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys_exit(main())

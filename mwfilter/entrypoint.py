# -*- coding: utf-8 -*-

from copy import copy
from sys import exit as sys_exit
from sys import stderr
from typing import List, Optional

from mwfilter.apps import run_app
from mwfilter.arguments import CMDS, get_default_arguments
from mwfilter.logging.logging import (
    SEVERITY_NAME_DEBUG,
    add_default_colored_logging,
    add_default_logging,
    add_simple_logging,
    logger,
    set_root_level,
    silent_unnecessary_loggers,
)


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)

    if not args.cmd:
        print("Empty command error", file=stderr)
        return 1

    assert args.cmd in CMDS

    assert isinstance(args.settings_page, str)
    assert isinstance(args.mkdocs_yml, str)
    assert isinstance(args.cache_dir, str)
    assert isinstance(args.colored_logging, bool)
    assert isinstance(args.default_logging, bool)
    assert isinstance(args.simple_logging, bool)
    assert isinstance(args.severity, str)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)
    assert isinstance(args.D, bool)

    if args.D:
        args.colored_logging = True
        args.default_logging = False
        args.simple_logging = False
        args.debug = True
        args.verbose = 1

    cmd = args.cmd
    colored_logging = args.colored_logging
    default_logging = args.default_logging
    simple_logging = args.simple_logging
    severity = args.severity
    debug = args.debug
    verbose = args.verbose

    if colored_logging:
        add_default_colored_logging()
    elif default_logging:
        add_default_logging()
    elif simple_logging:
        add_simple_logging()

    if debug:
        set_root_level(SEVERITY_NAME_DEBUG)
    else:
        set_root_level(severity)
        if verbose < 2:
            silent_unnecessary_loggers()

    if 2 <= verbose:
        ns = copy(args)
        if getattr(ns, "password", None):
            setattr(ns, "password", "****")
        logger.debug(f"The command line argument is {ns}")

    return run_app(cmd, args)


if __name__ == "__main__":
    sys_exit(main())

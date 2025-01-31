# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import environ
from typing import Final, List, Optional

from dotenv import load_dotenv

PROG: Final[str] = "mwfilter"
DESCRIPTION: Final[str] = "MediaWiki Filter"


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from mwfilter import __version__

    return __version__


def default_argument_parser() -> ArgumentParser:
    load_dotenv()

    parser = ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument("--output", "-o", default=environ.get("OUTPUT_DIR"))
    parser.add_argument("--cache", default=environ.get("CACHE_DIR"))
    parser.add_argument("--username", "-u", default=environ.get("MEDIAWIKI_USERNAME"))
    parser.add_argument("--password", "-p", default=environ.get("MEDIAWIKI_PASSWORD"))
    parser.add_argument("--settings-page", default=environ.get("SETTINGS_PAGE"))
    parser.add_argument("--version", "-V", action="version", version=version())
    parser.add_argument(
        "hostname",
        nargs="?",
        default=environ.get("MEDIAWIKI_HOSTNAME"),
    )
    return parser


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> Namespace:
    parser = default_argument_parser()
    return parser.parse_known_args(cmdline, namespace)[0]

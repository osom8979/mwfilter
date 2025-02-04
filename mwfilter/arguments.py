# -*- coding: utf-8 -*-

from argparse import REMAINDER, ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import R_OK, access, getcwd
from os.path import expanduser, isfile, join
from typing import Final, List, Optional, Sequence

from mwfilter.logging.logging import SEVERITIES, SEVERITY_NAME_INFO
from mwfilter.system.environ import get_typed_environ_value as get_eval

PROG: Final[str] = "mwfilter"
DESCRIPTION: Final[str] = "MediaWiki Filter"
EPILOG = f"""
Apply general debugging options:
  {PROG} -D ...
"""

CMD_PAGE: Final[str] = "page"
CMD_PAGE_HELP: Final[str] = "Download MediaWiki pages"
CMD_PAGE_EPILOG = """
List of namespace numbers:
  -2: Media
  -1: Special
  0: (Main)
  1: Talk
  2: User
  3: User talk
  4: Project
  5: Project talk
  6: File
  7: File talk
  8: MediaWiki
  9: MediaWiki talk
  10: Template
  11: Template talk
  12: Help
  13: Help talk
  14: Category
  15: Category talk
"""

CMD_PICKLE: Final[str] = "pickle"
CMD_PICKLE_HELP: Final[str] = "Pickle the downloaded MediaWiki files"

CMD_CONVERT: Final[str] = "convert"
CMD_CONVERT_HELP: Final[str] = "Convert the pickled MediaWiki files"

CMD_CLEAR: Final[str] = "clear"
CMD_CLEAR_HELP: Final[str] = "Clear cached files"

CMDS: Final[Sequence[str]] = (CMD_PAGE, CMD_PICKLE, CMD_CONVERT, CMD_CLEAR)

LOCAL_DOTENV_FILENAME: Final[str] = ".env.local"
DEFAULT_CACHE_DIRNAME: Final[str] = ".mwfilter"
DEFAULT_MKDOCS_YML: Final[str] = "mkdocs.yml"
DEFAULT_MEDIAWIKI_PATH: Final[str] = "/w/"
DEFAULT_SETTINGS_PAGE: Final[str] = "Mwfilter:Settings"
DEFAULT_MEDIAWIKI_NAMESPACE: Final[int] = 0


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from mwfilter import __version__

    return __version__


@lru_cache
def cache_dir() -> str:
    return join(expanduser("~"), DEFAULT_CACHE_DIRNAME)


def add_dotenv_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-dotenv",
        action="store_true",
        default=get_eval("NO_DOTENV", False),
        help="Do not use dot-env file",
    )
    parser.add_argument(
        "--dotenv-path",
        default=get_eval("DOTENV_PATH", join(getcwd(), LOCAL_DOTENV_FILENAME)),
        metavar="file",
        help=f"Specifies the dot-env file (default: '{LOCAL_DOTENV_FILENAME}')",
    )


def add_page_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_PAGE,
        help=CMD_PAGE_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--hostname",
        default=get_eval("MEDIAWIKI_HOSTNAME"),
        help=(
            "The hostname of a MediaWiki instance. "
            "Must *NOT* include a scheme (e.g. 'https://')"
        ),
    )
    parser.add_argument(
        "--endpoint-path",
        default=get_eval("ENDPOINT_PATH", DEFAULT_MEDIAWIKI_PATH),
        help=(
            "The API endpoint location on a MediaWiki site depends on the "
            "configurable $wgScriptPath. Must contain a trailing slash ('/'). "
            f"Defaults to '{DEFAULT_MEDIAWIKI_PATH}'"
        ),
    )
    parser.add_argument(
        "--username",
        "-u",
        default=get_eval("MEDIAWIKI_USERNAME"),
        help="If API authentication is required, this is a UTF-8 encoded username.",
    )
    parser.add_argument(
        "--password",
        "-p",
        default=get_eval("MEDIAWIKI_PASSWORD"),
        help="If API authentication is required, this is a UTF-8 encoded password.",
    )
    parser.add_argument(
        "--namespace",
        type=int,
        default=get_eval("MEDIAWIKI_NAMESPACE", DEFAULT_MEDIAWIKI_NAMESPACE),
        help="The namespace number of the MediaWiki page to download.",
    )
    parser.add_argument(
        "pages",
        nargs=REMAINDER,
        help="Names of downloaded pages.",
    )


def add_pickle_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_PICKLE,
        help=CMD_PICKLE_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)


def add_convert_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_CONVERT,
        help=CMD_CONVERT_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)


def add_clear_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_CLEAR,
        help=CMD_CLEAR_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    add_dotenv_arguments(parser)

    parser.add_argument(
        "--settings-page",
        default=get_eval("SETTINGS_PAGE", DEFAULT_SETTINGS_PAGE),
        help=(
            "The name of the MediaWiki page containing project settings information. "
            f"(default: '{DEFAULT_SETTINGS_PAGE}')"
        ),
    )
    parser.add_argument(
        "--mkdocs-yml",
        default=get_eval("MKDOCS_YML", DEFAULT_MKDOCS_YML),
        help=f"Provide a specific MkDocs config. (default: '{DEFAULT_MKDOCS_YML}')",
    )
    parser.add_argument(
        "--cache-dir",
        default=get_eval("CACHE_DIR", cache_dir()),
        help=f"Cache directory path. (default: '{cache_dir()}')",
    )

    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "--colored-logging",
        "-c",
        action="store_true",
        default=get_eval("COLORED_LOGGING", False),
        help="Use colored logging",
    )
    logging_group.add_argument(
        "--default-logging",
        action="store_true",
        default=get_eval("DEFAULT_LOGGING", False),
        help="Use default logging",
    )
    logging_group.add_argument(
        "--simple-logging",
        "-s",
        action="store_true",
        default=get_eval("SIMPLE_LOGGING", False),
        help="Use simple logging",
    )

    parser.add_argument(
        "--severity",
        choices=SEVERITIES,
        default=get_eval("SEVERITY", SEVERITY_NAME_INFO),
        help=f"Logging severity (default: '{SEVERITY_NAME_INFO}')",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=get_eval("DEBUG", False),
        help="Enable debugging mode and change logging severity to 'DEBUG'",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=get_eval("VERBOSE", 0),
        help="Be more verbose/talkative during the operation",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=version(),
    )

    parser.add_argument(
        "-D",
        action="store_true",
        default=False,
        help="Same as [''-c', '-d', '-v'] flags",
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_page_parser(subparsers)
    add_pickle_parser(subparsers)
    add_convert_parser(subparsers)
    add_clear_parser(subparsers)

    return parser


def _load_dotenv(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> None:
    parser = ArgumentParser(add_help=False, allow_abbrev=False, exit_on_error=False)
    add_dotenv_arguments(parser)
    args = parser.parse_known_args(cmdline, namespace)[0]

    assert isinstance(args.no_dotenv, bool)
    assert isinstance(args.dotenv_path, str)

    if args.no_dotenv:
        return
    if not isfile(args.dotenv_path):
        return
    if not access(args.dotenv_path, R_OK):
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(args.dotenv_path)
    except ModuleNotFoundError:
        pass


def _remove_dotenv_attrs(namespace: Namespace) -> Namespace:
    assert isinstance(namespace.no_dotenv, bool)
    assert isinstance(namespace.dotenv_path, str)

    del namespace.no_dotenv
    del namespace.dotenv_path

    assert not hasattr(namespace, "no_dotenv")
    assert not hasattr(namespace, "dotenv_path")

    return namespace


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> Namespace:
    # [IMPORTANT] Dotenv related options are processed first.
    _load_dotenv(cmdline, namespace)

    parser = default_argument_parser()
    args = parser.parse_known_args(cmdline, namespace)[0]

    # Remove unnecessary dotenv attrs
    return _remove_dotenv_attrs(args)

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

Download all main pages:
  {PROG} -y -D down -a

Download all template pages:
  {PROG} -y -D down -N 10 -a

Download settings pages:
  {PROG} -y -D down -E

Build all wiki files:
  {PROG} -y -D build
"""

CMD_DOWN: Final[str] = "down"
CMD_DOWN_HELP: Final[str] = "Download MediaWiki pages"
CMD_DOWN_EPILOG = """
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

CMD_BUILD: Final[str] = "build"
CMD_BUILD_HELP: Final[str] = "Convert MediaWiki files to Markdown files"

CMD_CLEAN: Final[str] = "clean"
CMD_CLEAN_HELP: Final[str] = "Clean cached files"

CMDS: Final[Sequence[str]] = (CMD_DOWN, CMD_BUILD, CMD_CLEAN)

LOCAL_DOTENV_FILENAME: Final[str] = ".env.local"
DEFAULT_CACHE_DIRNAME: Final[str] = ".mwfilter"
DEFAULT_MKDOCS_YML: Final[str] = "mkdocs.yml"
DEFAULT_MEDIAWIKI_HOSTNAME: Final[str] = "localhost"
DEFAULT_MEDIAWIKI_PATH: Final[str] = "/w/"
DEFAULT_SETTINGS_PAGE_NAME: Final[str] = "Mwfilter:Settings"
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


def add_down_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_DOWN,
        help=CMD_DOWN_HELP,
        epilog=CMD_DOWN_EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--endpoint-path",
        default=get_eval("ENDPOINT_PATH", DEFAULT_MEDIAWIKI_PATH),
        help=(
            "The API endpoint location on a MediaWiki site depends on the "
            "configurable $wgScriptPath. Must contain a trailing slash ('/'). "
            f"(default: '{DEFAULT_MEDIAWIKI_PATH}')"
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
        "-N",
        type=int,
        default=get_eval("MEDIAWIKI_NAMESPACE", DEFAULT_MEDIAWIKI_NAMESPACE),
        help=(
            "The namespace number of the MediaWiki page to download. "
            f"(default: {DEFAULT_MEDIAWIKI_NAMESPACE})"
        ),
    )
    parser.add_argument(
        "--no-expand-templates",
        action="store_true",
        default=get_eval("NO_EXPAND_TEMPLATES", False),
        help="Expand templates.",
    )
    parser.add_argument(
        "--export-settings",
        "-E",
        action="store_true",
        default=False,
        help="Export settings file.",
    )
    parser.add_argument(
        "--settings-page-name",
        default=get_eval("SETTINGS_PAGE_NAME", DEFAULT_SETTINGS_PAGE_NAME),
        help=(
            "The name of the MediaWiki page containing project settings information. "
            f"(default: '{DEFAULT_SETTINGS_PAGE_NAME}')"
        ),
    )
    parser.add_argument(
        "--all",
        "-a",
        "-A",
        action="store_true",
        default=False,
        help="Selects all pages in the specified namespace.",
    )
    parser.add_argument(
        "pages",
        nargs=REMAINDER,
        help="Names of downloaded pages.",
    )


def add_build_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_BUILD,
        help=CMD_BUILD_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--mkdocs-yml",
        default=get_eval("MKDOCS_YML", DEFAULT_MKDOCS_YML),
        help=f"Provide a specific MkDocs config. (default: '{DEFAULT_MKDOCS_YML}')",
    )
    parser.add_argument(
        "--all",
        "-a",
        "-A",
        action="store_true",
        default=False,
        help="Build all cache files and directories.",
    )
    parser.add_argument(
        "pages",
        nargs=REMAINDER,
        help="Names of build pages.",
    )


def add_clean_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_CLEAN,
        help=CMD_CLEAN_HELP,
        formatter_class=RawDescriptionHelpFormatter,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--all",
        "-a",
        "-A",
        action="store_true",
        default=False,
        help="Remove all cache files and directories.",
    )


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    add_dotenv_arguments(parser)

    parser.add_argument(
        "--hostname",
        "-H",
        default=get_eval("MEDIAWIKI_HOSTNAME", str()),
        help=(
            "The hostname of a MediaWiki instance. "
            "Must *NOT* include a scheme (e.g. 'https://')"
        ),
    )
    parser.add_argument(
        "--cache-dir",
        "-C",
        default=get_eval("CACHE_DIR", cache_dir()),
        help=f"Root cache directory path. (default: '{cache_dir()}')",
    )
    parser.add_argument(
        "--no-create-cache-dir",
        action="store_true",
        default=get_eval("NO_CREATE_CACHE_DIR", False),
        help="Do not automatically create the cache directory if it does not exist.",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        default=False,
        help="Automatic yes to prompts.",
    )
    parser.add_argument(
        "--ignore-errors",
        "-I",
        action="store_true",
        default=get_eval("IGNORE_ERRORS", False),
        help="Do not raise even if an error occurs.",
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
        help="Same as ['-c', '-d', '-v'] flags",
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_down_parser(subparsers)
    add_build_parser(subparsers)
    add_clean_parser(subparsers)

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

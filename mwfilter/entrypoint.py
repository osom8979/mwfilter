# -*- coding: utf-8 -*-

import os
from logging import DEBUG, Formatter, StreamHandler, getLogger
from sys import exit as sys_exit
from sys import stderr, stdout
from typing import List, Optional

from mwclient import Site
from mwclient.page import Page

from mwfilter.arguments import get_default_arguments


def default_logger():
    logger = getLogger()
    formatter = Formatter("{levelname[0]} {asctime} {name} {message}", style="{")
    handler = StreamHandler(stdout)
    handler.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    return logger


def app(
    hostname: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    output: Optional[str] = None,
    settings_page: Optional[str] = None,
) -> None:
    if not hostname:
        raise ValueError("url is required")

    site = Site(hostname, path="/")
    if username and password:
        site.login(username, password)

    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)

    if not os.path.isdir(output):
        raise NotADirectoryError("Output directory is not a directory")

    logger = default_logger()

    if settings_page:
        settings_page = site.pages[settings_page]
        logger.info(settings_page.text())

    for page in site.allpages():
        assert isinstance(page, Page)
        title = page.name
        content = page.text()

        assert isinstance(title, str)
        assert isinstance(content, str)
        logger.info(title)


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)
    try:
        app(
            hostname=args.hostname,
            username=args.username,
            password=args.password,
            output=args.output,
            settings_page=args.settings_page,
        )
    except BaseException as e:
        print(e, file=stderr)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys_exit(main())

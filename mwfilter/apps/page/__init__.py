# -*- coding: utf-8 -*-

from argparse import Namespace


def page_main(args: Namespace) -> None:
    from mwfilter.apps.page.app import PageApp

    app = PageApp(args)
    app.run()

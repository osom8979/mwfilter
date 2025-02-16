# -*- coding: utf-8 -*-

from argparse import Namespace


def index_main(args: Namespace) -> None:
    from mwfilter.apps.index.app import IndexApp

    app = IndexApp(args)
    app.run()

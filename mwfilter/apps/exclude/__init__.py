# -*- coding: utf-8 -*-

from argparse import Namespace


def exclude_main(args: Namespace) -> None:
    from mwfilter.apps.exclude.app import ExcludeApp

    app = ExcludeApp(args)
    app.run()

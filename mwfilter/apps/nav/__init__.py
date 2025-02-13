# -*- coding: utf-8 -*-

from argparse import Namespace


def nav_main(args: Namespace) -> None:
    from mwfilter.apps.nav.app import NavApp

    app = NavApp(args)
    app.run()

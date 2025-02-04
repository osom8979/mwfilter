# -*- coding: utf-8 -*-

from argparse import Namespace


def down_main(args: Namespace) -> None:
    from mwfilter.apps.down.app import DownApp

    app = DownApp(args)
    app.run()

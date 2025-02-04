# -*- coding: utf-8 -*-

from argparse import Namespace


def clear_main(args: Namespace) -> None:
    from mwfilter.apps.clear.app import ClearApp

    app = ClearApp(args)
    app.run()

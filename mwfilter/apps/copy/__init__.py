# -*- coding: utf-8 -*-

from argparse import Namespace


def copy_main(args: Namespace) -> None:
    from mwfilter.apps.copy.app import CopyApp

    app = CopyApp(args)
    app.run()

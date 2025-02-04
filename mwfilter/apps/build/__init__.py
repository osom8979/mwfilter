# -*- coding: utf-8 -*-

from argparse import Namespace


def build_main(args: Namespace) -> None:
    from mwfilter.apps.build.app import BuildApp

    app = BuildApp(args)
    app.run()

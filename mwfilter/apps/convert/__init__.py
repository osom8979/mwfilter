# -*- coding: utf-8 -*-

from argparse import Namespace


def convert_main(args: Namespace) -> None:
    from mwfilter.apps.convert.app import ConvertApp

    app = ConvertApp(args)
    app.run()

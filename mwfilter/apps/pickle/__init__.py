# -*- coding: utf-8 -*-

from argparse import Namespace


def pickle_main(args: Namespace) -> None:
    from mwfilter.apps.pickle.app import PickleApp

    app = PickleApp(args)
    app.run()

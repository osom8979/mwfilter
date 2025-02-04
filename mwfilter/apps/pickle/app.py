# -*- coding: utf-8 -*-

from argparse import Namespace


class PickleApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)
        self._debug = args.debug
        self._verbose = args.verbose

    def run(self) -> None:
        pass

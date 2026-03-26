# -*- coding: utf-8 -*-

from argparse import Namespace


def image_main(args: Namespace) -> None:
    from mwfilter.apps.image.app import ImageApp

    app = ImageApp(args)
    app.run()

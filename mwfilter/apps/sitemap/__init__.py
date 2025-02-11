# -*- coding: utf-8 -*-

from argparse import Namespace


def sitemap_main(args: Namespace) -> None:
    from mwfilter.apps.sitemap.app import SitemapApp

    app = SitemapApp(args)
    app.run()

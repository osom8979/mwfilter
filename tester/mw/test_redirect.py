# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.mw.redirect import parse_redirect_pagename


class RedirectTestCase(TestCase):
    def test_default(self):
        link0 = parse_redirect_pagename("#넘겨주기 [[Link]]")  # noqa
        self.assertEqual("Link", link0)

        link1 = parse_redirect_pagename("#REDIRECT [[Link]]")
        self.assertEqual("Link", link1)


if __name__ == "__main__":
    main()

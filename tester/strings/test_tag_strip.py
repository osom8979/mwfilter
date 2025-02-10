# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.strings.tag_strip import strip_tags


class TagStripTestCase(TestCase):
    def test_default(self):
        self.assertEqual("T1_T2", strip_tags("<a><pre>T1</pre>_<br>T2<hr/></a>"))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.mediawiki.converter import mediawiki_to_markdown

_MEDIAWIKI_CONTENT = """
NAPALM Network Automation and Programmability Abstraction Layer

== See also ==
* [[python]]
* [[Netmiko]]

== Favorite site ==
* [https://github.com/napalm-automation/napalm Github - napalm]
"""

_MARKDOWN_CONTENT = """
NAPALM Network Automation and Programmability Abstraction Layer

## See also {#see_also}

-   [python](python.md "wikilink")
-   [Netmiko](Netmiko.md "wikilink")

## Favorite site {#favorite_site}

-   [Github - napalm](https://github.com/napalm-automation/napalm)
"""


class ConvertTestCase(TestCase):
    def test_mediawiki_to_markdown(self):
        self.assertEqual(_MARKDOWN_CONTENT, mediawiki_to_markdown(_MEDIAWIKI_CONTENT))


if __name__ == "__main__":
    main()

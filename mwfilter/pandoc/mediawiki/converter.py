# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

import json

from pypandoc import convert_text


def default_pandoc_filter(e):
    assert isinstance(e, dict)
    return e


def mediawiki_to_markdown(mediawiki_context: str) -> str:
    pandoc_json = convert_text(mediawiki_context, to="json", format="mediawiki")
    modified_json = json.dumps(default_pandoc_filter(json.loads(pandoc_json)))
    return convert_text(modified_json, to="markdown", format="json")

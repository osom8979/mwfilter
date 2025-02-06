# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

import json

from pypandoc import convert_text


def on_block(block: dict):
    block_type = block["t"]
    block_content = block["c"]
    assert isinstance(block_type, str)
    assert isinstance(block_content, list)

    match block_type:
        case "Plain":
            pass
        case "Para":
            pass
        case "LineBlock":
            pass
        case "CodeBlock":
            pass
        case "RawBlock":
            pass
        case "BlockQuote":
            pass
        case "OrderedList":
            pass
        case "BulletList":
            pass
        case "DefinitionList":
            pass
        case "Header":
            pass
        case "HorizontalRule":
            pass
        case "Table":
            pass
        case "Figure":
            pass
        case "Div":
            pass
        case _:
            raise ValueError(f"Unexpected block type: {block_type}")


def default_pandoc_filter(obj):
    assert isinstance(obj, dict)

    pandoc_api_version = obj["pandoc-api-version"]
    assert isinstance(pandoc_api_version, list)
    assert len(pandoc_api_version) == 3
    major, minor, patch = pandoc_api_version

    meta = obj["meta"]  # Metadata for the document: title, authors, date.
    assert isinstance(meta, dict)
    assert len(meta) == 0

    blocks = obj["blocks"]
    assert isinstance(blocks, list)

    for block in blocks:
        assert isinstance(block, dict)
        on_block(block)


def mediawiki_to_markdown(mediawiki_context: str) -> str:
    pandoc_json = convert_text(mediawiki_context, to="json", format="mediawiki")
    modified_json = json.dumps(default_pandoc_filter(json.loads(pandoc_json)))
    return convert_text(modified_json, to="markdown", format="json")

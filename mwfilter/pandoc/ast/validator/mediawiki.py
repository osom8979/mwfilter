# -*- coding: utf-8 -*-

from typing import Any, List


def definition_list_validator(e: Any) -> None:
    assert isinstance(e, dict)
    if e_blocks := e.get("blocks"):
        assert isinstance(e_blocks, list)

        pass_blocks: List[Any] = list()

        for i, e_block in enumerate(e_blocks):
            assert isinstance(e_block, dict)
            t = e_block["t"]
            assert isinstance(t, str)

            if pass_blocks and t == "Para":
                c = e_block["c"]
                assert isinstance(c, list)

                last = pass_blocks[-1]
                assert isinstance(last, dict)
                t_last = last["t"]
                assert isinstance(t_last, str)

                if c and t_last == "DefinitionList":
                    c0 = c[0]
                    assert isinstance(c0, dict)
                    c0t = c0["t"]
                    assert isinstance(c0t, str)

                    if c0t == "Str":
                        c0c = c0["c"]
                        assert isinstance(c0c, str)

                        if c0c.startswith(":*"):
                            raise ValueError(
                                "MediaWiki syntax error. "
                                "The first DescriptionDetails in a DefinitionList "
                                "should not start with ':*'."
                            )

            pass_blocks.append(e_block)


def mediawiki_validator(e: Any) -> None:
    definition_list_validator(e)

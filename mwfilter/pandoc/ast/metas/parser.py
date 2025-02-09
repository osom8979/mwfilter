# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Dict, Sequence, Type

from mwfilter.pandoc.ast.metas.meta_value import MetaValue


@lru_cache
def meta_value_classes() -> Sequence[Type[MetaValue]]:
    # [IMPORTANT] Avoid 'circular import' issues
    from mwfilter.pandoc.ast.metas.meta_blocks import MetaBlocks
    from mwfilter.pandoc.ast.metas.meta_bool import MetaBool
    from mwfilter.pandoc.ast.metas.meta_inlines import MetaInlines
    from mwfilter.pandoc.ast.metas.meta_list import MetaList
    from mwfilter.pandoc.ast.metas.meta_map import MetaMap
    from mwfilter.pandoc.ast.metas.meta_string import MetaString

    return (
        MetaBlocks,
        MetaBool,
        MetaInlines,
        MetaList,
        MetaMap,
        MetaString,
    )


@lru_cache
def meta_value_map() -> Dict[str, Type[MetaValue]]:
    return {cls.__name__: cls for cls in meta_value_classes()}


def parse_meta_value(e) -> MetaValue:
    assert isinstance(e, dict)
    e_type = e.get("t")
    e_content = e.get("c")
    assert isinstance(e_type, str)
    return meta_value_map()[e_type].parse_object(e_content)

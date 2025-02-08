# -*- coding: utf-8 -*-


class ColSpan(int):
    """The number of columns occupied by a cell; the width of a cell."""

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)

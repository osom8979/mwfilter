# -*- coding: utf-8 -*-


class RowSpan(int):
    """The number of rows occupied by a cell; the height of a cell."""

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)

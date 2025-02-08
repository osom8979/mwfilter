# -*- coding: utf-8 -*-

from unittest import TestCase, main

import mwfilter.pandoc.ast.inlines.str_
from mwfilter.pandoc import ast
from mwfilter.pandoc.ast.enums import Alignment


class TableTestCase(TestCase):
    def test_default(self):
        text = "{|\n|+C\n!H1\n!H2\n|-\n!RH\n|RD\n|}"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.Table)
        self.assertTrue(b0.attr.is_empty)
        self.assertIsNone(b0.caption.short_caption)
        self.assertEqual(1, len(b0.caption.blocks))

        b0cb0 = b0.caption.blocks[0]
        self.assertIsInstance(b0cb0, ast.Plain)
        self.assertEqual(1, len(b0cb0.inlines))

        b0cb0i0 = b0cb0.inlines[0]
        self.assertIsInstance(b0cb0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("C", b0cb0i0.text)

        self.assertEqual(2, len(b0.col_specs))
        b0cs0 = b0.col_specs[0]
        self.assertIsInstance(b0cs0, ast.ColSpec)
        self.assertEqual(Alignment.AlignDefault, b0cs0.alignment)
        self.assertTrue(b0cs0.col_width.is_default)

        b0cs1 = b0.col_specs[1]
        self.assertIsInstance(b0cs1, ast.ColSpec)
        self.assertEqual(Alignment.AlignDefault, b0cs1.alignment)
        self.assertTrue(b0cs1.col_width.is_default)

        b0th = b0.table_head
        self.assertIsInstance(b0th, ast.TableHead)
        self.assertTrue(b0th.attr.is_empty)
        self.assertEqual(1, len(b0th.rows))

        b0thr0 = b0th.rows[0]
        self.assertIsInstance(b0thr0, ast.Row)
        self.assertTrue(b0thr0.attr.is_empty)
        self.assertEqual(2, len(b0thr0.cells))

        b0thr0c0 = b0thr0.cells[0]
        self.assertIsInstance(b0thr0c0, ast.Cell)
        self.assertTrue(b0thr0c0.attr.is_empty)
        self.assertEqual(Alignment.AlignDefault, b0thr0c0.alignment)
        self.assertEqual(1, b0thr0c0.col_span)
        self.assertEqual(1, b0thr0c0.row_span)
        self.assertEqual(1, len(b0thr0c0.blocks))
        b0thr0c0b0 = b0thr0c0.blocks[0]
        self.assertIsInstance(b0thr0c0b0, ast.Para)
        self.assertEqual(1, len(b0thr0c0b0.inlines))
        b0thr0c0b0i0 = b0thr0c0b0.inlines[0]
        self.assertIsInstance(b0thr0c0b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("H1", b0thr0c0b0i0.text)

        b0thr0c1 = b0thr0.cells[1]
        self.assertIsInstance(b0thr0c1, ast.Cell)
        self.assertTrue(b0thr0c1.attr.is_empty)
        self.assertEqual(Alignment.AlignDefault, b0thr0c1.alignment)
        self.assertEqual(1, b0thr0c1.col_span)
        self.assertEqual(1, b0thr0c1.row_span)
        self.assertEqual(1, len(b0thr0c1.blocks))
        b0thr0c1b0 = b0thr0c1.blocks[0]
        self.assertIsInstance(b0thr0c1b0, ast.Para)
        self.assertEqual(1, len(b0thr0c1b0.inlines))
        b0thr0c1b0i0 = b0thr0c1b0.inlines[0]
        self.assertIsInstance(b0thr0c1b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("H2", b0thr0c1b0i0.text)

        self.assertEqual(1, len(b0.table_body))
        b0tb0 = b0.table_body[0]
        self.assertIsInstance(b0tb0, ast.TableBody)
        self.assertTrue(b0tb0.attr.is_empty)
        self.assertEqual(0, b0tb0.row_head_columns)
        self.assertEqual(0, len(b0tb0.header_rows))
        self.assertEqual(1, len(b0tb0.body_rows))

        b0tb0br0 = b0tb0.body_rows[0]
        self.assertIsInstance(b0tb0br0, ast.Row)
        self.assertTrue(b0tb0br0.attr.is_empty)
        self.assertEqual(2, len(b0tb0br0.cells))

        b0tb0br0c0 = b0tb0br0.cells[0]
        self.assertIsInstance(b0tb0br0c0, ast.Cell)
        self.assertTrue(b0tb0br0c0.attr.is_empty)
        self.assertEqual(1, len(b0tb0br0c0.blocks))
        b0tb0br0c0b0 = b0tb0br0c0.blocks[0]
        self.assertIsInstance(b0tb0br0c0b0, ast.Para)
        self.assertEqual(1, len(b0tb0br0c0b0.inlines))
        b0tb0br0c0b0i0 = b0tb0br0c0b0.inlines[0]
        self.assertIsInstance(b0tb0br0c0b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("RH", b0tb0br0c0b0i0.text)

        b0tb0br0c1 = b0tb0br0.cells[1]
        self.assertIsInstance(b0tb0br0c1, ast.Cell)
        self.assertTrue(b0tb0br0c1.attr.is_empty)
        self.assertEqual(1, len(b0tb0br0c1.blocks))
        b0tb0br0c1b0 = b0tb0br0c1.blocks[0]
        self.assertIsInstance(b0tb0br0c1b0, ast.Para)
        self.assertEqual(1, len(b0tb0br0c1b0.inlines))
        b0tb0br0c1b0i0 = b0tb0br0c1b0.inlines[0]
        self.assertIsInstance(b0tb0br0c1b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("RD", b0tb0br0c1b0i0.text)

        b0tf = b0.table_foot
        self.assertTrue(b0tf.attr.is_empty)
        self.assertFalse(b0tf.rows)


if __name__ == "__main__":
    main()

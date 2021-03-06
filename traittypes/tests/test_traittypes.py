# encoding: utf-8
"""Tests for traittypes.traittypes."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from unittest import TestCase
from traitlets import HasTraits, TraitError, observe
from traitlets.tests.test_traitlets import TraitTestBase
from traittypes import Array, DataFrame, Series
import numpy as np
import pandas as pd


# Good / Bad value trait test cases


class IntArrayTrait(HasTraits):
    value = Array().tag(dtype=np.int)


class TestIntArray(TraitTestBase):
    """
    Test dtype validation with a ``dtype=np.int``
    """
    obj = IntArrayTrait()

    _good_values = [1, [1, 2, 3], [[1, 2, 3], [4, 5, 6]], np.array([1])]
    _bad_values = [[1, [0, 0]]]

    def assertEqual(self, v1, v2):
        return np.testing.assert_array_equal(v1, v2)


# Other test cases


class TestArray(TestCase):

    def test_array_equal(self):
        notifications = []
        class Foo(HasTraits):
            bar = Array([1, 2])
            @observe('bar')
            def _(self, change):
                notifications.append(change)
        foo = Foo()
        foo.bar = [1, 2]
        self.assertFalse(len(notifications))
        foo.bar = [1, 1]
        self.assertTrue(len(notifications))

    def test_initial_values(self):
        class Foo(HasTraits):
            a = Array()
            b = Array(dtype='int')
            c = Array(None, allow_none=True)
            d = Array([])
        foo = Foo()
        self.assertTrue(np.array_equal(foo.a, np.array(0)))
        self.assertTrue(np.array_equal(foo.b, np.array(0)))
        self.assertTrue(foo.c is None)
        self.assertTrue(np.array_equal(foo.d, []))

    def test_allow_none(self):
        class Foo(HasTraits):
            bar = Array()
            baz = Array(allow_none=True)
        foo = Foo()
        with self.assertRaises(TraitError):
            foo.bar = None
        foo.baz = None

    def test_custom_validators(self):
        # Test with a squeeze coercion
        def squeeze(trait, value):
            if 1 in value.shape:
                value = np.squeeze(value)
            return value

        class Foo(HasTraits):
            bar = Array().valid(squeeze)

        foo = Foo(bar=[[1], [2]])
        self.assertTrue(np.array_equal(foo.bar, [1, 2]))
        foo.bar = [[1], [2], [3]]
        self.assertTrue(np.array_equal(foo.bar, [1, 2, 3]))

        # Test with a shape constraint
        def shape(*dimensions):
            def validator(trait, value):
                if value.shape != dimensions:
                    raise TraitError('Expected an of shape %s and got and array with shape %s' % (dimensions, value.shape))
                else:
                    return value
            return validator

        class Foo(HasTraits):
            bar = Array(np.identity(2)).valid(shape(2, 2))
        foo = Foo()
        with self.assertRaises(TraitError):
            foo.bar = [1]
        new_value = [[0, 1], [1, 0]]
        foo.bar = new_value
        self.assertTrue(np.array_equal(foo.bar, new_value))


class TestDataFrame(TestCase):

    def test_df_equal(self):
        notifications = []
        class Foo(HasTraits):
            bar = DataFrame([1, 2])
            @observe('bar')
            def _(self, change):
                notifications.append(change)
        foo = Foo()
        foo.bar = [1, 2]
        self.assertFalse(len(notifications))
        foo.bar = [1, 1]
        self.assertTrue(len(notifications))

    def test_initial_values(self):
        class Foo(HasTraits):
            a = DataFrame()
            b = DataFrame(None, allow_none=True)
            c = DataFrame([])
        foo = Foo()
        self.assertTrue(foo.a.equals(pd.DataFrame()))
        self.assertTrue(foo.b is None)
        self.assertTrue(foo.c.equals(pd.DataFrame([])))

    def test_allow_none(self):
        class Foo(HasTraits):
            bar = DataFrame()
            baz = DataFrame(allow_none=True)
        foo = Foo()
        with self.assertRaises(TraitError):
            foo.bar = None
        foo.baz = None


class TestSeries(TestCase):

    def test_sereis_equal(self):
        notifications = []
        class Foo(HasTraits):
            bar = Series([1, 2])
            @observe('bar')
            def _(self, change):
                notifications.append(change)
        foo = Foo()
        foo.bar = [1, 2]
        self.assertFalse(len(notifications))
        foo.bar = [1, 1]
        self.assertTrue(len(notifications))

    def test_initial_values(self):
        class Foo(HasTraits):
            a = Series()
            b = Series(None, allow_none=True)
            c = Series([])
        foo = Foo()
        self.assertTrue(foo.a.equals(pd.Series()))
        self.assertTrue(foo.b is None)
        self.assertTrue(foo.c.equals(pd.Series([])))

    def test_allow_none(self):
        class Foo(HasTraits):
            bar = Series()
            baz = Series(allow_none=True)
        foo = Foo()
        with self.assertRaises(TraitError):
            foo.bar = None
        foo.baz = None
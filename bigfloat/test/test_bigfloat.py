# Copyright 2009--2019 Mark Dickinson.
#
# This file is part of the bigfloat package.
#
# The bigfloat package is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat package.  If not, see <http://www.gnu.org/licenses/>.

# Standard library imports
import contextlib
import doctest
import fractions
import io
import math
import operator
import random
import struct
import sys
import types
import unittest
import warnings

# 3rd party imports
import pkg_resources
import six

import bigfloat.core

from bigfloat import (
    # version number
    __version__,

    # main class
    BigFloat,

    # contexts
    Context,

    # limits on emin, emax and precision
    EMIN_MIN, EMAX_MAX,

    # context constants...
    half_precision, single_precision,
    double_precision, quadruple_precision,
    RoundTiesToEven, RoundTowardZero,
    RoundTowardPositive, RoundTowardNegative,
    RoundAwayFromZero,
    ROUND_TIES_TO_EVEN,

    # ... and functions
    IEEEContext, precision,

    # get and set current context
    getcontext,
    setcontext,

    # flags
    Inexact, Overflow, ZeroDivision,
    set_flagstate, get_flagstate,

    # standard arithmetic functions
    add, sub, mul, div, fmod, pow,
    sqrt, floordiv, mod,

    # 5.4 Conversion Functions
    frexp,

    # 5.5 Basic Arithmetic Functions
    root, rootn,

    # 5.6 Comparison Functions
    cmp, cmpabs, is_nan, is_inf, is_finite, is_zero, is_regular, sgn,
    notequal, lessgreater, unordered,

    # 5.7 Special Functions
    exp,
    factorial,
    zeta_ui,
    lgamma,
    j0, j1, jn,
    y0, y1, yn,
    const_log2, const_pi, const_euler, const_catalan,
    sum,

    # 5.10 Integer and Remainder Related Functions
    is_integer,

    # 5.12 Miscellaneous Functions
    min, max,
    is_negative,
    copysign,
)

from bigfloat.core import _all_flags

all_rounding_modes = [RoundTowardZero, RoundTowardNegative,
                      RoundTowardPositive, RoundTiesToEven, RoundAwayFromZero]

if sys.version_info < (3,):
    long_integer_type = long  # noqa
else:
    long_integer_type = int


# Context at the start of each test method.
DefaultTestContext = Context(
    precision=53,
    rounding=ROUND_TIES_TO_EVEN,
    emax=EMAX_MAX,
    emin=EMIN_MIN,
    subnormalize=False,
)


def diffBigFloat(x, y, match_precisions=True):
    """Determine whether two BigFloat instances can be considered
    identical.  Returns None on sucess (indicating that the two
    BigFloats *are* identical), and an appropriate error message on
    failure."""

    if not (isinstance(x, BigFloat) and isinstance(y, BigFloat)):
        raise ValueError("Expected x and y to be BigFloat instances "
                         "in assertIdenticalBigFloat")

    # precisions should match
    if match_precisions:
        if x.precision != y.precision:
            return "Precisions of %r and %r differ." % (x, y)

    # if one of x or y is a nan then both should be
    if is_nan(x) or is_nan(y):
        if not (is_nan(x) and is_nan(y)):
            return ("One of %r and %r is a nan, but the other is not." %
                    (x, y))
        else:
            return None

    # if both x and y are zeros then their signs should be identical
    if is_zero(x) and is_zero(y):
        if is_negative(x) != is_negative(y):
            return "Zeros %r and %r have different signs." % (x, y)

    # otherwise, it's enough that x and y have equal value
    if x != y:
        return "%r and %r have unequal value." % (x, y)

    # no essential difference between x and y
    return None


class MockBinaryOperation(object):
    """
    Mock binary operation, for testing purposes.

    """
    def __init__(self, returns=None):
        self.call = lambda self, other: returns

    def __get__(self, obj, objtype=None):
        return self.call if obj is None else types.MethodType(self.call, obj)


# Dummy class with mock implementations of relevant special methods.

class RichObject(object):
    pass


dummy_ops = [
    'eq', 'ne', 'le', 'lt', 'ge', 'gt',
    'add', 'sub', 'mul', 'truediv', 'floordiv', 'mod', 'divmod', 'pow',
    'lshift', 'rshift', 'and', 'xor', 'or',
    'radd', 'rsub', 'rmul', 'rtruediv', 'rfloordiv', 'rmod', 'rdivmod', 'rpow',
    'rlshift', 'rrshift', 'rand', 'rxor', 'ror',
]
if sys.version_info < (3,):
    dummy_ops.extend(["div", "rdiv"])
if sys.version_info >= (3,):
    dummy_ops.extend(["matmul", "rmatmul"])

for op in dummy_ops:
    setattr(RichObject, '__{op}__'.format(op=op),
            MockBinaryOperation(op))


# Dummy class with *no* implementations of special methods.

class PoorObject(object):
    pass


class BigFloatTests(unittest.TestCase):
    def setUp(self):
        self._original_context = getcontext()
        setcontext(DefaultTestContext)

    def tearDown(self):
        setcontext(self._original_context)
        del self._original_context

    def test_version(self):
        self.assertIsInstance(__version__, str)

    def assertIdenticalFloat(self, x, y):
        if not (isinstance(x, float) and isinstance(y, float)):
            raise ValueError("Expected x and y to be floats "
                             "in assertIdenticalFloat")

        # if either x or y is a nan...
        if x != x or y != y:
            # and one of x and y is not a nan...
            if x == x or y == y:
                self.fail("One of x and y is a nan, but the other is not.")
        elif x == y == 0.0:
            # check signs are the same.  Can't use copysign since that
            # isn't available until Python 2.6;  comparing stringified
            # versions should work on most platforms.
            if str(x) != str(y):
                self.fail("Zeros have different signs")
        else:
            self.assertEqual(x, y)

    def assertIdenticalBigFloat(self, x, y):
        """Fail unless BigFloats x and y are identical.

        x and y are considered identical if they have the
        same precision, and:

        - both x and y are nans, or
        - neither x nor y is a nan, x == y, and if x and y
          are both zero then their signs match.

        """
        # Note that any two nans with the same precision are always
        # regarded as identical, even though it's sometimes possible to
        # distinguish nans with different signs (for example, using
        # copysign).

        if not (isinstance(x, BigFloat) and isinstance(y, BigFloat)):
            raise ValueError("Expected x and y to be BigFloat instances "
                             "in assertIdenticalBigFloat")

        # precisions should match
        if x.precision != y.precision:
            self.fail("Precisions of x and y differ.")

        if is_nan(x) or is_nan(y):
            if not is_nan(x) or not is_nan(y):
                self.fail("One of x and y is a nan, but the other is not.")
        elif is_zero(x) and is_zero(y):
            # check signs are identical
            if is_negative(x) != is_negative(y):
                self.fail("Zeros have different signs")
        else:
            self.assertEqual(x, y)

    def test_arithmetic_functions(self):
        # test add, mul, div, sub, pow, mod
        test_precisions = [2, 10, 23, 24, 52, 53, 54, 100]
        fns = [add, sub, mul, div, pow, floordiv, fmod]

        values = [2, 3, 1.234, BigFloat('0.678'), BigFloat('nan'),
                  float('0.0'), float('inf'), True]

        # functions should accept operands of any integer, float or BigFloat
        # type.
        for v in values:
            for w in values:
                for p in test_precisions:
                    with precision(p):
                        for fn in fns:
                            # test without rounding mode
                            res = fn(v, w)
                            self.assertIs(type(res), BigFloat)
                            self.assertEqual(res.precision, p)
                            # test with rounding mode
                            for rnd in all_rounding_modes:
                                res = fn(v, w, context=rnd)
                                self.assertIs(type(res), BigFloat)
                                self.assertEqual(res.precision, p)

        # should be able to specify rounding mode directly,
        # and it overrides the current context rounding mode
        for p in test_precisions:
            with precision(p):
                for rnd in all_rounding_modes:
                    with rnd:
                        x = div(1, 3, context=RoundTowardPositive)
                        y = div(1, 3, context=RoundTowardNegative)
                        self.assertLess(y, x)
                        x3 = mul(3, x, context=RoundTowardPositive)
                        y3 = mul(y, 3, context=RoundTowardNegative)
                        self.assertLess(y3, 1)
                        self.assertLess(1, x3)

    def test_mod(self):
        # Compare with Python's % operation.
        for _ in range(10000):
            x = struct.unpack(
                '<d', struct.pack('<Q', random.randrange(2**64)))[0]
            y = struct.unpack(
                '<d', struct.pack('<Q', random.randrange(2**64)))[0]

            bigfloat_result = mod(x, y)
            python_result = x % y
            self.assertIdenticalBigFloat(bigfloat_result,
                                         BigFloat(python_result))

    def test_floordiv(self):
        x = BigFloat(2.3)
        y = BigFloat(1.2)
        self.assertIdenticalBigFloat(floordiv(x, y), BigFloat(1))

        # Check some random floats; compare with Python's operation.
        test_pairs = [
            ('-0x1.5921f71f3a8b7p-407', '0x1.4c71c92d27a31p-460'),
            ('-0x1.884ea5a94b5f5p+513', '0x1.c058519564476p+460'),
            ('-0x1.b71ef34af0215p-459', '-0x1.d7c7b08970e2dp-514'),
            ('-0x1.55b19f5f1eaf4p+888', '-0x1.eab0f46fc89fcp+834'),
            ('0x1.c655a7928d80ap-148', '0x1.ed6b2d073dbaap-202'),
            ('0x1.80574cc232b58p+407', '0x1.8017ad6a5cd65p+247'),
            # Cases where the fast method doesn't quite apply
            ('0x1.29dbe528a1eddp+158', '0x1.ab3bd461baacfp+52'),
            ('0x1.f0cd027b645e8p+157', '0x1.afc4d2171de7fp+52'),
            ('0x1.49c34cd7726e3p+158', '0x1.b16193d9ac917p+52'),
            ('0x1.499cd0115b703p+158', '0x1.ecb8a19525c13p+52'),
            ('0x1.c042a3dd22594p+157', '0x1.9d26c3340d073p+52'),
            ('0x1.085e2c60727e6p+158', '0x1.4ab6dab81c08bp+52'),
            ('0x1.085e2c60727e6p+158', '0x1.945a8d6633e67p+52'),
            ('0x1.bfed7fed4e317p+158', '0x1.e677da37e992bp+52'),
            ('0x1.bfed7fed4e317p+158', '0x1.fbb37fe2fe157p+52'),
            ('0x1.d551fa1318722p+157', '0x1.993e3b11333cbp+52'),
        ]

        with double_precision:
            # Some troublesome values.
            for xhex, yhex in test_pairs:
                x = float.fromhex(xhex)
                y = float.fromhex(yhex)
                x_frac = fractions.Fraction(*x.as_integer_ratio())
                y_frac = fractions.Fraction(*y.as_integer_ratio())
                expected_result = BigFloat(x_frac // y_frac)
                actual_result = floordiv(x, y)
                self.assertEqual(actual_result, expected_result)

            # Check a selection of random values.
            for _ in range(10000):
                x = struct.unpack(
                    '<d', struct.pack('<Q', random.randrange(2**64)))[0]
                y = struct.unpack(
                    '<d', struct.pack('<Q', random.randrange(2**64)))[0]
                if math.isnan(x) or math.isinf(x) or x == 0.0:
                    continue
                if math.isnan(y) or math.isinf(y) or y == 0.0:
                    continue

                actual_result = floordiv(x, y)
                try:
                    x_frac = fractions.Fraction(*x.as_integer_ratio())
                    y_frac = fractions.Fraction(*y.as_integer_ratio())
                    # float-to-int conversion is correctly rounded on Python >=
                    # 2.7.
                    expected_result = float(x_frac // y_frac)
                except OverflowError:
                    if x_frac / y_frac > 0:
                        expected_result = float('inf')
                    else:
                        expected_result = float('-inf')

                self.assertEqual(
                    actual_result, expected_result,
                    msg="failure for x = {0!r}, y = {1!r}".format(x, y)
                )

    def test_binary_operations(self):
        # check that BigFloats can be combined with themselves,
        # and with integers and floats, using the standard
        # arithmetic operators:  +, -, *, /, **, %, //

        x = BigFloat('17.29')
        other_values = [2, 3, 1.234, BigFloat('0.678'), False]
        test_precisions = [2, 20, 53, 2000]
        operations = [operator.add, operator.mul, operator.floordiv,
                      operator.sub, operator.pow, operator.truediv,
                      operator.mod]
        # operator.div only defined for Python 2
        if sys.version_info < (3,):
            operations.append(operator.div)

        operations.append(operator.mod)

        for value in other_values:
            for p in test_precisions:
                with precision(p):
                    for op in operations:
                        bf = op(x, value)
                        self.assertIs(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)
                        bf = op(value, x)
                        self.assertIs(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)

    def test_binary_operations_return_not_implemented(self):
        # Check that the binary operations behave well with
        # respect to third-party types.
        bf = BigFloat(123)
        other = RichObject()

        # Comparisons
        self.assertEqual(bf == other, "eq")
        self.assertEqual(bf != other, "ne")
        self.assertEqual(bf < other, "gt")
        self.assertEqual(bf > other, "lt")
        self.assertEqual(bf <= other, "ge")
        self.assertEqual(bf >= other, "le")

        # Arithmetic: +, -, *, /, //, %, divmod, **, %
        self.assertEqual(bf + other, "radd")
        self.assertEqual(bf - other, "rsub")
        self.assertEqual(bf * other, "rmul")
        self.assertEqual(operator.truediv(bf, other), "rtruediv")
        self.assertEqual(bf // other, "rfloordiv")
        self.assertEqual(bf % other, "rmod")
        self.assertEqual(divmod(bf, other), "rdivmod")
        self.assertEqual(bf ** other, "rpow")
        if sys.version_info < (3,):
            self.assertEqual(operator.div(bf, other), "rdiv")
        if sys.version_info >= (3,):
            self.assertEqual(operator.matmul(bf, other), "rmatmul")

        # Bitwise: &, ^, |, <<, >>
        self.assertEqual(bf << other, "rlshift")
        self.assertEqual(bf >> other, "rrshift")
        self.assertEqual(bf & other, "rand")
        self.assertEqual(bf ^ other, "rxor")
        self.assertEqual(bf | other, "ror")

    def test_binary_operations_raise_type_error(self):
        # Check that binary operations correctly raise TypeError,
        # either way around, with an unsupported type.  Excludes
        # == and !=, which need their own checks.
        binary_ops = [
            operator.add, operator.sub, operator.mul, operator.pow,
            operator.truediv, operator.floordiv, operator.mod, divmod,
            operator.lshift, operator.rshift,
            operator.and_, operator.xor, operator.or_,
        ]
        if sys.version_info < (3,):
            binary_ops.append(operator.div)
        else:
            # These only raise on Python 3; on Python 2 we get the
            # usual arbitrary ordering.
            binary_ops.extend(
                [operator.gt, operator.lt, operator.ge, operator.le])

        if sys.version_info >= (3,):
            binary_ops.append(operator.matmul)

        bf = BigFloat(123)
        other = PoorObject()
        for op in binary_ops:
            with self.assertRaises(TypeError):
                op(bf, other)
            with self.assertRaises(TypeError):
                op(other, bf)
        self.assertFalse(bf == other)
        self.assertFalse(other == bf)
        self.assertTrue(bf != other)
        self.assertTrue(other != bf)

        if sys.version_info < (3,):
            # Check that comparisons don't raise.
            self.assertIsInstance(bf < other, bool)
            self.assertIsInstance(bf <= other, bool)
            self.assertIsInstance(bf > other, bool)
            self.assertIsInstance(bf >= other, bool)
            self.assertIsInstance(other < bf, bool)
            self.assertIsInstance(other <= bf, bool)
            self.assertIsInstance(other > bf, bool)
            self.assertIsInstance(other >= bf, bool)

    def test_bool(self):
        # test __nonzero__ / __bool__
        self.assertIs(bool(BigFloat(0)), False)
        self.assertIs(bool(BigFloat('-0')), False)
        self.assertIs(bool(BigFloat(1.0)), True)
        self.assertIs(bool(BigFloat(-123)), True)
        self.assertIs(bool(BigFloat('nan')), True)
        self.assertIs(bool(BigFloat('inf')), True)
        self.assertIs(bool(BigFloat('-inf')), True)

    def test_classifications(self):
        # test classification functions (is_nan, is_inf, is_zero,
        # is_finite, is_integer, is_negative)

        nans = [
            float('nan'), BigFloat('nan'), float('-nan'), -BigFloat('nan'),
        ]
        for x in nans:
            self.assertIs(is_nan(x), True)
            self.assertIs(is_inf(x), False)
            self.assertIs(is_zero(x), False)
            self.assertIs(is_finite(x), False)
            self.assertIs(is_integer(x), False)
            self.assertIs(is_regular(x), False)

        infinities = [
            float('inf'), float('-inf'), BigFloat('inf'), BigFloat('-inf'),
        ]
        for x in infinities:
            self.assertIs(is_nan(x), False)
            self.assertIs(is_inf(x), True)
            self.assertIs(is_zero(x), False)
            self.assertIs(is_finite(x), False)
            self.assertIs(is_integer(x), False)
            self.assertIs(is_regular(x), False)

        zeros = [
            0,
            float('0.0'), float('-0.0'),
            BigFloat('0.0'), BigFloat('-0.0'),
        ]
        for x in zeros:
            self.assertIs(is_nan(x), False)
            self.assertIs(is_inf(x), False)
            self.assertIs(is_zero(x), True)
            self.assertIs(is_finite(x), True)
            self.assertIs(is_integer(x), True)
            self.assertIs(is_regular(x), False)

        for x in [-31, -5.13, BigFloat('-2.34e1000')]:
            self.assertIs(is_nan(x), False)
            self.assertIs(is_inf(x), False)
            self.assertIs(is_zero(x), False)
            self.assertIs(is_finite(x), True)
            self.assertIs(is_regular(x), True)
            self.assertIs(is_negative(x), True)

        for x in [2, 24.0, BigFloat('1e-1000')]:
            self.assertIs(is_nan(x), False)
            self.assertIs(is_inf(x), False)
            self.assertIs(is_zero(x), False)
            self.assertIs(is_finite(x), True)
            self.assertIs(is_regular(x), True)
            self.assertIs(is_negative(x), False)

        # test is_integer for finite nonzero values
        for x in [2, -31, 24.0, BigFloat('1e100'), sqrt(BigFloat('2e100'))]:
            self.assertIs(is_integer(x), True)

        for x in [2.1, BigFloat(-1.345), sqrt(BigFloat(2))]:
            self.assertIs(is_integer(x), False)

        # test is_negative
        negatives = [
            float('-inf'), float('-0.0'),
            BigFloat('-inf'), BigFloat('-0.0'),
            BigFloat(-2.3), -31, -1,
        ]
        for x in negatives:
            self.assertIs(is_negative(x), True)

        for x in [float('inf'), BigFloat('inf'), float('0.0'), 0, 2, 123,
                  BigFloat(1.23)]:
            self.assertIs(is_negative(x), False)

        # test signs of NaNs.  (Warning: the MPFR library doesn't guarantee
        # much here; these tests may break.)
        self.assertIs(is_negative(BigFloat('nan')), False)
        self.assertIs(is_negative(-BigFloat('nan')), True)

    def test_comparisons(self):
        # here's a list of lists of values; within each sublist all

        # entries have the same value; sublists are ordered by increasing value
        values = [
            [BigFloat('-inf'), float('-inf')],
            [-1, -1.0, BigFloat(-1.0)],
            [
                0,
                float('0.0'), float('-0.0'),
                BigFloat('0.0'), BigFloat('-0.0'),
            ],
            [BigFloat('4e-324')],
            [4e-324],
            [1e-320, BigFloat(1e-320)],
            [1, 1.0, BigFloat(1.0)],
            [BigFloat(2 ** 53 + 1)],
            [2 ** 53 + 1],
            [BigFloat('inf'), float('inf')],
        ]

        nans = [
            BigFloat('nan'), -BigFloat('-nan'), float('nan'), -float('nan')
        ]

        LT_PAIRS = []
        EQ_PAIRS = []
        GT_PAIRS = []
        UN_PAIRS = []
        for i, v1 in enumerate(values):
            for x in v1:
                for j, v2 in enumerate(values):
                    for y in v2:
                        if i < j:
                            LT_PAIRS.append((x, y))
                        elif i == j:
                            EQ_PAIRS.append((x, y))
                        else:
                            GT_PAIRS.append((x, y))

        for i, v1 in enumerate(values):
            for x in v1:
                for n in nans:
                    UN_PAIRS.append((x, n))
                    UN_PAIRS.append((n, x))
        for n1 in nans:
            for n2 in nans:
                UN_PAIRS.append((n1, n2))

        for x, y in LT_PAIRS:
            self.assertIs(x < y, True)
            self.assertIs(x <= y, True)
            self.assertIs(x != y, True)
            self.assertIs(x > y, False)
            self.assertIs(x >= y, False)
            self.assertIs(x == y, False)
            self.assertIs(notequal(x, y), True)
            self.assertIs(lessgreater(x, y), True)
            self.assertIs(unordered(x, y), False)

        for x, y in EQ_PAIRS:
            self.assertIs(x <= y, True)
            self.assertIs(x >= y, True)
            self.assertIs(x == y, True)
            self.assertIs(x < y, False)
            self.assertIs(x > y, False)
            self.assertIs(x != y, False)
            self.assertIs(notequal(x, y), False)
            self.assertIs(lessgreater(x, y), False)
            self.assertIs(unordered(x, y), False)

        for x, y in GT_PAIRS:
            self.assertIs(x > y, True)
            self.assertIs(x >= y, True)
            self.assertIs(x != y, True)
            self.assertIs(x < y, False)
            self.assertIs(x <= y, False)
            self.assertIs(x == y, False)
            self.assertIs(notequal(x, y), True)
            self.assertIs(lessgreater(x, y), True)
            self.assertIs(unordered(x, y), False)

        for x, y in UN_PAIRS:
            self.assertIs(x < y, False)
            self.assertIs(x <= y, False)
            self.assertIs(x > y, False)
            self.assertIs(x >= y, False)
            self.assertIs(x == y, False)
            self.assertIs(x != y, True)
            self.assertIs(notequal(x, y), True)
            self.assertIs(lessgreater(x, y), False)
            self.assertIs(unordered(x, y), True)

    def test_creation_from_integer(self):
        test_values = [-23, 0, 100, 7 ** 100]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertIs(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

    def test_creation_from_float(self):
        test_values = [-12.3456, float('-0.0'), float('0.0'), 5e-310, -1e308,
                       float('nan'), float('inf'), float('-inf')]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertIs(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

        # check directly-supplied rounding mode
        lower = BigFloat(1.1, precision(24) + RoundTowardNegative)
        upper = BigFloat(1.1, RoundTowardPositive + precision(24))
        self.assertLess(lower, upper)

        # check directly-supplied exponent, subnormalize:
        nearest_half = BigFloat(123.456, Context(emin=0, subnormalize=True))
        self.assertEqual(nearest_half, 123.5)

    def test_creation_from_string(self):
        test_values = ['123.456',
                       '-1.23',
                       '1e456',
                       '+nan',
                       'inf',
                       '-inf',
                       '-451.001']
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertIs(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

        # check that rounding mode affects the conversion
        with RoundTowardNegative:
            lower = BigFloat('1.1')
        with RoundTowardPositive:
            upper = BigFloat('1.1')
        self.assertLess(lower, upper)

        # alternative version, without with statements
        lower = BigFloat('1.1', RoundTowardNegative)
        upper = BigFloat('1.1', RoundTowardPositive)
        self.assertLess(lower, upper)

        self.assertTrue(is_nan(BigFloat('nan')))
        self.assertTrue(is_inf(BigFloat('inf')))
        self.assertFalse(is_negative(BigFloat('inf')))
        self.assertTrue(is_inf(BigFloat('-inf')))
        self.assertTrue(is_negative(BigFloat('-inf')))
        self.assertTrue(is_zero(BigFloat('0')))
        self.assertFalse(is_negative(BigFloat('0')))
        self.assertTrue(is_zero(BigFloat('-0')))
        self.assertTrue(is_negative(BigFloat('-0')))

    if sys.version_info < (3,):
        def test_creation_from_unicode(self):
            test_values = map(six.text_type,
                              ['123.456',
                               '-1.23',
                               '1e456',
                               '+nan',
                               'inf',
                               '-inf',
                               '-451.001'])
            test_precisions = [2, 20, 53, 2000]
            for value in test_values:
                for p in test_precisions:
                    with precision(p):
                        bf = BigFloat(value)
                        self.assertIs(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)
                    # check directly-supplied context
                    bf = BigFloat(value, precision(p))
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)

    def test_creation_from_BigFloat(self):
        test_values = [BigFloat(1.0),
                       BigFloat('nan'),
                       BigFloat('inf'),
                       const_pi()]
        # add a few extra values at other precisions
        with precision(200):
            test_values.append(const_catalan())
        with precision(15):
            test_values.append(sqrt(3))
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertIs(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

    def test_creation_from_incompatible_object(self):
        with self.assertRaises(TypeError):
            BigFloat([1, 2, 3])
        with self.assertRaises(TypeError):
            BigFloat(1j)

    def test_divmod(self):
        x = BigFloat.exact(1729)
        y = BigFloat.exact(53)

        q, r = divmod(x, y)
        self.assertIsInstance(q, BigFloat)
        self.assertIsInstance(r, BigFloat)
        self.assertEqual(q, BigFloat.exact(1729 // 53))
        self.assertEqual(r, BigFloat.exact(1729 % 53))

        q, r = divmod(-x, y)
        self.assertIsInstance(q, BigFloat)
        self.assertIsInstance(r, BigFloat)
        self.assertEqual(q, BigFloat.exact(-1729 // 53))
        self.assertEqual(r, BigFloat.exact(-1729 % 53))

    def test_exact_context_independent(self):
        with Context(emin=-1, emax=1):
            x = BigFloat.exact(123456)
        self.assertEqual(x, 123456)

    def test_exact_overflow(self):
        # exact conversion should raise ValueError for values that are
        # too large or too small to represent.  (Clearly, floats can
        # never be too large or too small, and integers can't ever
        # be too small.  Here we test with strings.)
        too_large = '1e%d' % (EMAX_MAX // 3)
        too_small = '1e%d' % (EMIN_MIN // 3)
        self.assertRaises(ValueError, BigFloat.exact, too_large, 53)
        self.assertRaises(ValueError, BigFloat.exact, too_small, 53)

        # the exception raising goes via flag detection.  Check that
        # it's independent of the currently-set flags.

        # Set all flags...
        set_flagstate(_all_flags)
        self.assertEqual(BigFloat.exact(12345), 12345)
        self.assertEqual(BigFloat.exact(1e-72), 1e-72)

        # check that flags aren't affected by a BigFloat.exact call
        set_flagstate(set())
        BigFloat.exact('123.45', precision=200)  # shouldn't set inexact flag
        flags = get_flagstate()
        self.assertEqual(flags, set())

    def test_exact_creation_from_integer(self):
        test_values = [-23, 0, 100, 7 ** 100]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value)
                    self.assertIs(type(bf), BigFloat)
                    # check that conversion back to an int recovers
                    # the same value, regardless of the precision of
                    # the current context
                    self.assertEqual(int(bf), value)

        self.assertRaises(TypeError, BigFloat.exact, 1, precision=200)
        self.assertRaises(TypeError, BigFloat.exact, -13, precision=53)

    def test_exact_creation_from_float(self):
        test_values = [-12.3456, float('-0.0'), float('0.0'), 5e-310, -1e308,
                       float('nan'), float('inf'), float('-inf')]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value)
                    self.assertIs(type(bf), BigFloat)
                    # check that conversion back to float recovers
                    # the same value
                    self.assertIdenticalFloat(float(bf), value)

        self.assertRaises(TypeError, BigFloat.exact, 1.0, precision=200)
        self.assertRaises(
            TypeError,
            BigFloat.exact, float('nan'), precision=53,
        )

    def test_exact_creation_from_string(self):
        test_values = ['123.456',
                       '-1.23',
                       '1e456',
                       '+nan',
                       'inf',
                       '-inf',
                       '-451.001']
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value, precision=p)
                    self.assertIs(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)

        # Check that rounding-mode doesn't affect the conversion
        with RoundTowardNegative:
            lower = BigFloat.exact('1.1', precision=20)
        with RoundTowardPositive:
            upper = BigFloat.exact('1.1', precision=20)
        self.assertEqual(lower, upper)

        # Check that TypeError is raised if precision not passed.
        with self.assertRaises(TypeError):
            BigFloat.exact('1.1')

    if sys.version_info < (3,):
        def test_exact_creation_from_unicode(self):
            test_values = map(six.text_type,
                              ['123.456',
                               '-1.23',
                               '1e456',
                               '+nan',
                               'inf',
                               '-inf',
                               '-451.001'])
            test_precisions = [2, 20, 53, 2000]
            for value in test_values:
                for p in test_precisions:
                    with precision(p):
                        bf = BigFloat.exact(value, precision=p)
                        self.assertIs(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)

            # check that rounding-mode doesn't affect the conversion
            with RoundTowardNegative:
                lower = BigFloat.exact('1.1', precision=20)
            with RoundTowardPositive:
                upper = BigFloat.exact('1.1', precision=20)
            self.assertEqual(lower, upper)

    def test_exact_creation_from_BigFloat(self):
        for test_precision in [2, 20, 53, 2000]:
            for test_rounding in all_rounding_modes:
                with precision(test_precision):
                    with test_rounding:
                        x = sqrt(2)
                y = BigFloat.exact(x)
                self.assertEqual(x, y)

        self.assertRaises(TypeError, BigFloat.exact, BigFloat(23), 100)

    def test_exact_creation_from_incompatible_object(self):
        with self.assertRaises(TypeError):
            BigFloat.exact([1, 2, 3])
        with self.assertRaises(TypeError):
            BigFloat.exact(1j, precision=20)

    def test_exponent_limits(self):
        with Context(emin=-1000, emax=0):
            x = add(123, 456)
        self.assertEqual(x, BigFloat('infinity'))

    def test_float(self):
        # test conversion to float
        with precision(200):
            x = BigFloat(2 ** 100 + 1) / 2 ** 100
            y = BigFloat(2 ** 100 - 1) / 2 ** 100

        # just double check that they're not equal as BigFloats
        self.assertNotEqual(x, y)

        # rounding mode shouldn't affect conversion
        for rnd in all_rounding_modes:
            with rnd:
                self.assertEqual(float(x), 1.)
                self.assertEqual(float(y), 1.)

    def test_hash(self):
        # equal values should hash equal
        pos0 = BigFloat('0')
        neg0 = BigFloat('-0')
        self.assertEqual(hash(pos0), hash(neg0))

        # hash shouldn't depend on precision
        with precision(200):
            x1 = BigFloat(123456)
        with precision(11):
            x2 = BigFloat(123456)
        with precision(53):
            x3 = BigFloat(123456)
        self.assertEqual(hash(x1), hash(x2))
        self.assertEqual(hash(x1), hash(x3))

        # check that hash values match those of floats
        test_values = [
            float('inf'),
            float('nan'),
            0.0,
            1.0,
            1.625,
            1.1,
            1e100,
            1.456789123123e10,
            1.9876543456789e-10,
            1e-100,
            3.1415926535,
        ]
        test_values += [-x for x in test_values]
        for test_value in test_values:
            self.assertEqual(
                hash(BigFloat.exact(test_value)),
                hash(test_value)
            )

        # check that hash(n) matches hash(BigFloat(n)) for integers n
        for n in range(-50, 50):
            self.assertEqual(hash(n), hash(BigFloat.exact(n)))

        # values near powers of 2
        for e in [30, 31, 32, 33, 34, 62, 63, 64, 65, 66]:
            for n in range(2 ** e - 50, 2 ** e + 50):
                self.assertEqual(hash(n), hash(BigFloat.exact(n)),
                                 "hash(n) != hash(BigFloat.exact(n)) "
                                 "for n = %s" % n)
                self.assertEqual(hash(BigFloat(n)), hash(int(BigFloat(n))),
                                 "hash(BigFloat(n)) != hash(int(BigFloat(n))) "
                                 "for n = %s" % n)

        n = 7**100
        self.assertEqual(hash(BigFloat.exact(n)), hash(n))

    if sys.version_info >= (3,):
        # Only Python 3 has consistent hashing for all numeric types,
        # so we can't expect these tests to pass on Python 2.
        def test_hash_compatibility_with_fraction(self):
            n = 7**100
            d = 2**999
            f = fractions.Fraction(n, d)
            with precision(1000):
                bigfloat_f = BigFloat.exact(n) / BigFloat.exact(d)
            self.assertEqual(hash(bigfloat_f), hash(f))
            self.assertEqual(hash(bigfloat_f), hash(f))

    def test_hex(self):
        # test conversion to a hex string

        test_values = [
            # (input, precision, output)
            ('NaN', 2, 'nan'),
            ('NaN', 24, 'nan'),
            ('NaN', 53, 'nan'),
            ('NaN', 100, 'nan'),
            # ('-NaN', 10, '-NaN'),
            ('Inf', 2, 'inf'),
            ('-Inf', 10, '-inf'),
            ('0', 53, '0'),
            ('-0', 24, '-0'),

            ('0.25', 4, '0x0.8p-1'),
            ('0.25', 5, '0x0.80p-1'),

            ('0.5', 2, '0x0.8p+0'),
            ('0.5', 3, '0x0.8p+0'),
            ('0.5', 4, '0x0.8p+0'),
            ('0.5', 5, '0x0.80p+0'),
            ('0.5', 8, '0x0.80p+0'),
            ('0.5', 9, '0x0.800p+0'),

            ('1', 2, '0x0.8p+1'),
            ('1', 3, '0x0.8p+1'),
            ('1', 4, '0x0.8p+1'),
            ('1', 5, '0x0.80p+1'),
            ('1', 8, '0x0.80p+1'),
            ('1', 9, '0x0.800p+1'),

            ('1.5', 24, '0x0.c00000p+1'),
            ('-1.5', 24, '-0x0.c00000p+1'),
            ('3.14159265358979323846264', 52, '0x0.c90fdaa22168cp+2'),
            ('3.14159265358979323846264', 53, '0x0.c90fdaa22168c0p+2'),

        ]

        for strarg, precision_in, expected in test_values:
            arg = BigFloat.exact(strarg, precision=precision_in)
            got = arg.hex()
            self.assertEqual(expected, got)

    def test_int(self):
        # test conversion to int
        self.assertEqual(int(BigFloat(13.7)), 13)
        self.assertEqual(int(BigFloat(2.3)), 2)
        self.assertEqual(int(BigFloat(1729)), 1729)

        self.assertEqual(int(BigFloat(-1e-50)), 0)
        self.assertEqual(int(BigFloat('-2.99999')), -2)
        self.assertEqual(int(BigFloat(-5.0)), -5)

        self.assertEqual(int(BigFloat('0.0')), 0)
        self.assertEqual(int(BigFloat('-0.0')), 0)

        self.assertRaises(ValueError, int, BigFloat('inf'))
        self.assertRaises(ValueError, int, BigFloat('-inf'))
        self.assertRaises(ValueError, int, BigFloat('nan'))

    if sys.version_info < (3,):
        def test_long(self):
            self.assertIsInstance(
                long_integer_type(BigFloat(13.7)), long_integer_type)
            self.assertEqual(long_integer_type(BigFloat(13.7)), 13)
            self.assertIsInstance(
                long_integer_type(BigFloat(13.7)), long_integer_type)
            self.assertEqual(long_integer_type(BigFloat(2.3)), 2)
            self.assertIsInstance(
                long_integer_type(BigFloat(1729)), long_integer_type)
            self.assertEqual(long_integer_type(BigFloat(1729)), 1729)

            self.assertIsInstance(
                long_integer_type(BigFloat('0.0')), long_integer_type)
            self.assertEqual(long_integer_type(BigFloat('0.0')), 0)
            self.assertIsInstance(
                long_integer_type(BigFloat('-0.0')), long_integer_type)
            self.assertEqual(long_integer_type(BigFloat('-0.0')), 0)

            self.assertRaises(ValueError, long_integer_type, BigFloat('inf'))
            self.assertRaises(ValueError, long_integer_type, BigFloat('-inf'))
            self.assertRaises(ValueError, long_integer_type, BigFloat('nan'))

    def test_integer_ratio(self):

        ir = BigFloat.as_integer_ratio

        test_values = [
            (
                sqrt(BigFloat(2), context=RoundTowardPositive),
                (6369051672525773, 4503599627370496)
            ),
            (
                sqrt(BigFloat(2), context=RoundTowardNegative),
                (1592262918131443, 1125899906842624)
            ),
            (const_pi(), (884279719003555, 281474976710656)),
            (BigFloat('2.0'), (2, 1)),
            (BigFloat('0.5'), (1, 2)),
            (BigFloat('-1.125'), (-9, 8)),
        ]

        for arg, expected in test_values:
            self.assertEqual(ir(arg), expected)

        self.assertEqual(ir(BigFloat('0.0')), (0, 1))
        self.assertEqual(ir(BigFloat('-0.0')), (0, 1))

        self.assertRaises(ValueError, ir, BigFloat('inf'))
        self.assertRaises(ValueError, ir, BigFloat('-inf'))
        self.assertRaises(ValueError, ir, BigFloat('nan'))

    def test_repr(self):
        # eval(repr(x)) should recover the BigFloat x, with
        # the same precision and value.

        test_values = [const_pi(), BigFloat(12345),
                       BigFloat('inf'), BigFloat('-inf'), BigFloat('nan'),
                       BigFloat('0'), BigFloat('-0')]
        with precision(5):
            test_values.append(BigFloat(-1729))
        with precision(200):
            test_values.append(sqrt(3))

        for x in test_values:
            # current precision shouldn't affect the repr or the eval
            for p in [2, 30, 53, 100, 1000]:
                with precision(p):
                    self.assertIdenticalBigFloat(eval(repr(x)), x)

    def test_str(self):
        # check special values
        self.assertEqual(str(BigFloat('0.0')), '0')
        self.assertEqual(str(BigFloat('-0.0')), '-0')
        self.assertEqual(str(BigFloat('inf')), 'inf')
        self.assertEqual(str(BigFloat('-inf')), '-inf')
        self.assertEqual(str(BigFloat('nan')), 'nan')

        self.assertEqual(str(BigFloat('1e100')), '1.0000000000000000e+100')

        # check switch from fixed-point to exponential notation
        self.assertEqual(str(BigFloat('1e-5')), '1.0000000000000001e-05')
        self.assertEqual(str(BigFloat('9.999e-5')), '9.9989999999999996e-05')
        self.assertEqual(str(BigFloat('1e-4')), '0.00010000000000000000')
        self.assertEqual(str(BigFloat('1e14')), '100000000000000.00')
        self.assertEqual(str(BigFloat('1e15')), '1000000000000000.0')
        self.assertEqual(str(BigFloat('1e16')), '10000000000000000')
        self.assertEqual(str(BigFloat('9.999e16')), '99990000000000000')
        self.assertEqual(str(BigFloat('1e17')), '1.0000000000000000e+17')

    def test_subnormalization(self):
        # check that subnormalization doesn't result in
        # double rounding
        with double_precision:
            self.assertEqual(div(2 ** 53 + 1, 2 ** 1128), pow(2, -1074))

        # check that results are integer multiples of
        # 2**-1074
        with double_precision:
            self.assertEqual(BigFloat('3e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.4e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.5e-324'), pow(2, -1073))

    def test_const_log2(self):
        with double_precision:
            self.assertEqual(
                const_log2(),
                BigFloat.exact('0.69314718055994531', precision=53),
            )

    def test_const_pi(self):
        with double_precision:
            self.assertEqual(
                const_pi(),
                BigFloat.exact('3.14159265358979323', precision=53)
            )
        with double_precision + RoundTowardNegative:
            pi_lower = const_pi()
        with double_precision + RoundTowardPositive:
            pi_upper = const_pi()

        self.assertLess(pi_lower, pi_upper)
        # Test passing context argument.
        with double_precision:
            self.assertEqual(
                const_pi(),
                BigFloat.exact('3.1415926535897932', precision=53),
            )
            self.assertEqual(
                const_pi(context=RoundTowardNegative),
                pi_lower
            )
            self.assertEqual(
                const_pi(context=RoundTowardPositive),
                pi_upper
            )

    def test_const_euler(self):
        with double_precision:
            self.assertEqual(
                const_euler(),
                BigFloat.exact('0.57721566490153286', precision=53),
            )

    def test_const_catalan(self):
        with double_precision:
            self.assertEqual(
                const_catalan(),
                BigFloat.exact('0.91596559417721902', precision=53),
            )

    def test_sum(self):
        with double_precision:
            inputs = [1.0/n**2 for n in range(1, 1000)]
            bf_sum = sum(inputs)
            self.assertIsInstance(bf_sum, BigFloat)
            self.assertEqual(bf_sum, math.fsum(inputs))

        # Check the documented behaviours.

        # Check sign of zero when summing zeros.
        pz, nz = BigFloat("0.0"), BigFloat("-0.0")

        for rounding_mode in all_rounding_modes:
            with rounding_mode:
                self.assertFalse(is_negative(sum([])))
                self.assertFalse(is_negative(sum([pz])))
                self.assertFalse(is_negative(sum([pz, pz])))
                self.assertFalse(is_negative(sum([pz, pz, pz])))

                self.assertTrue(is_negative(sum([nz])))
                self.assertTrue(is_negative(sum([nz, nz])))
                self.assertTrue(is_negative(sum([nz, nz, nz])))

                if rounding_mode == RoundTowardNegative:
                    self.assertTrue(is_negative(sum([pz, nz])))
                else:
                    self.assertFalse(is_negative(sum([pz, nz])))

        # Check sign of a zero result from non-zero summands.
        args = [10, -10]
        for rounding_mode in all_rounding_modes:
            with rounding_mode:
                bf_sum = sum(args)
                self.assertEqual(bf_sum, 0.0)
                if rounding_mode == RoundTowardNegative:
                    self.assertTrue(is_negative(bf_sum))
                else:
                    self.assertFalse(is_negative(bf_sum))

    def test_copy(self):
        x = BigFloat.exact(
            '1234091801830413840192384102394810329481324.3',
            precision=200,
        )
        y = x.copy()
        self.assertEqual(x, y)
        self.assertIsNot(x, y)

    def test_copy_abs(self):
        x = BigFloat.exact(
            '1234091801830413840192384102394810329481324.3',
            precision=200,
        )
        neg_x = BigFloat.exact(
            '-1234091801830413840192384102394810329481324.3',
            precision=200,
        )
        self.assertEqual(x.copy_abs(), x)
        self.assertEqual(neg_x.copy_abs(), x)

        inf = BigFloat('infinity')
        ninf = BigFloat('-infinity')
        self.assertEqual(inf.copy_abs(), inf)
        self.assertEqual(ninf.copy_abs(), inf)

    def test_copy_neg(self):
        x = BigFloat.exact(
            '1234091801830413840192384102394810329481324.3',
            precision=200,
        )
        neg_x = BigFloat.exact(
            '-1234091801830413840192384102394810329481324.3',
            precision=200,
        )
        self.assertEqual(x.copy_neg(), neg_x)
        self.assertEqual(neg_x.copy_neg(), x)

        inf = BigFloat('infinity')
        ninf = BigFloat('-infinity')
        self.assertEqual(inf.copy_neg(), ninf)
        self.assertEqual(ninf.copy_neg(), inf)

    def test_unary_operations(self):
        # test __pos__, __neg__ and __abs__

        # unary operations should round to the current context
        with precision(150):
            x = sqrt(2)

        test_precisions = [2, 20, 53, 2000]
        for p in test_precisions:
            with precision(p):
                posx = +x
                self.assertEqual(posx.precision, p)
                if p < 150:
                    self.assertNotEqual(x, posx)
                else:
                    self.assertEqual(x, posx)

                negx = -x
                self.assertEqual(negx.precision, p)
                if p < 150:
                    self.assertNotEqual(x, -negx)
                else:
                    self.assertEqual(x, -negx)

                absx = operator.abs(x)
                self.assertEqual(absx.precision, p)
                if p < 150:
                    self.assertNotEqual(x, absx)
                else:
                    self.assertEqual(x, absx)

    @unittest.skipUnless(sys.version_info >= (3,),
                         "round tests only applicable to Python 3")
    def test_single_argument_round(self):
        # Rounding with a single argument.
        test_values = [
            (BigFloat('-2.0'), -2),
            (BigFloat('-1.5'), -2),
            (BigFloat('-1.4999'), -1),
            (BigFloat('-0.6'), -1),
            (BigFloat('-0.5'), 0),
            (BigFloat('-0.1'), 0),
            (BigFloat('-0.0'), 0),
            (BigFloat('0.0'), 0),
            (BigFloat('0.1'), 0),
            (BigFloat('0.5'), 0),
            (BigFloat('0.6'), 1),
            (BigFloat('1.4999'), 1),
            (BigFloat('1.5'), 2),
            (BigFloat('2.0'), 2),
        ]
        for value, expected_result in test_values:
            result = round(value)
            self.assertIsInstance(result, int)
            self.assertEqual(result, expected_result)

        with self.assertRaises(ValueError):
            round(BigFloat('inf'))
        with self.assertRaises(ValueError):
            round(BigFloat('nan'))

    @unittest.skipUnless(sys.version_info >= (3,),
                         "round tests only applicable to Python 3")
    def test_two_argument_round(self):
        test_triples = [
            # n = -1 (round to nearest 10)
            (BigFloat(-35), -1, BigFloat(-40)),
            (BigFloat(-25), -1, BigFloat(-20)),
            (BigFloat(-15), -1, BigFloat(-20)),
            (BigFloat(-5), -1, BigFloat('-0')),
            (BigFloat(5), -1, BigFloat(0)),
            (BigFloat(15), -1, BigFloat(20)),
            (BigFloat(25), -1, BigFloat(20)),
            (BigFloat(35), -1, BigFloat(40)),

            # n = 0
            (BigFloat(-1.5), 0, BigFloat('-2')),
            (BigFloat(-0.5), 0, BigFloat('-0')),
            (BigFloat(0.49999999999999994), 0, BigFloat('0')),
            (BigFloat(0.5), 0, BigFloat('0')),
            (BigFloat(1.5), 0, BigFloat('2')),
            (BigFloat(2.5), 0, BigFloat('2')),
            (BigFloat('4503599627370495.5'), 0, BigFloat('4503599627370496')),
            (BigFloat('4503599627370497'), 0, BigFloat('4503599627370497')),

            # n = 1
            (BigFloat('0.05'), 1, BigFloat('0.1')),
            (BigFloat('0.1'), 1, BigFloat('0.1')),
            (BigFloat('0.15'), 1, BigFloat('0.1')),
            (BigFloat('0.2'), 1, BigFloat('0.2')),
            (BigFloat('0.25'), 1, BigFloat('0.2')),
            (BigFloat('0.3'), 1, BigFloat('0.3')),
            (BigFloat('0.35'), 1, BigFloat('0.3')),
            (BigFloat('0.4'), 1, BigFloat('0.4')),
            (BigFloat('0.45'), 1, BigFloat('0.5')),
            (BigFloat('0.5'), 1, BigFloat('0.5')),
            (BigFloat('0.55'), 1, BigFloat('0.6')),
            (BigFloat('0.6'), 1, BigFloat('0.6')),
            (BigFloat('0.75'), 1, BigFloat('0.8')),

            # Various n.
            (BigFloat('314159.265358979323'), -6, BigFloat('0')),
            (BigFloat('314159.265358979323'), -5, BigFloat('300000')),
            (BigFloat('314159.265358979323'), -4, BigFloat('310000')),
            (BigFloat('314159.265358979323'), -3, BigFloat('314000')),
            (BigFloat('314159.265358979323'), -2, BigFloat('314200')),
            (BigFloat('314159.265358979323'), -1, BigFloat('314160')),
            (BigFloat('314159.265358979323'), 0, BigFloat('314159')),
            (BigFloat('314159.265358979323'), 1, BigFloat('314159.3')),
            (BigFloat('314159.265358979323'), 2, BigFloat('314159.27')),
            (BigFloat('314159.265358979323'), 3, BigFloat('314159.265')),
            (BigFloat('314159.265358979323'), 4, BigFloat('314159.2654')),
            (BigFloat('314159.265358979323'), 5, BigFloat('314159.26536')),
            (BigFloat('314159.265358979323'), 6, BigFloat('314159.265359')),

            # Special values.
            (BigFloat('0'), 0, BigFloat('0')),
            (BigFloat('-0'), 0, BigFloat('-0')),
            (BigFloat('0'), 10, BigFloat('0')),
            (BigFloat('-0'), 10, BigFloat('-0')),
            (BigFloat('0'), -10, BigFloat('0')),
            (BigFloat('-0'), -10, BigFloat('-0')),
            (BigFloat('inf'), 0, BigFloat('inf')),
            (BigFloat('-inf'), 0, BigFloat('-inf')),
            (BigFloat('nan'), 0, BigFloat('nan')),
            (BigFloat('inf'), 10, BigFloat('inf')),
            (BigFloat('-inf'), 10, BigFloat('-inf')),
            (BigFloat('nan'), 10, BigFloat('nan')),
            (BigFloat('inf'), -10, BigFloat('inf')),
            (BigFloat('-inf'), -10, BigFloat('-inf')),
            (BigFloat('nan'), -10, BigFloat('nan')),
        ]
        for bf, n, expected in test_triples:
            actual = round(bf, n)
            self.assertIsInstance(actual, BigFloat)
            self.assertIdenticalBigFloat(actual, expected)

        # Check round-ties-to-even behaviour.
        result = round(BigFloat(-1.5), 0)
        self.assertIsInstance(result, BigFloat)
        self.assertEqual(result, BigFloat(-2))

        result = round(BigFloat(-0.5), 0)
        self.assertIsInstance(result, BigFloat)
        self.assertEqual(result, BigFloat(0))

        result = round(BigFloat(0.5), 0)
        self.assertIsInstance(result, BigFloat)
        self.assertEqual(result, BigFloat(0))

        result = round(BigFloat(1.5), 0)
        self.assertIsInstance(result, BigFloat)
        self.assertEqual(result, BigFloat(2))

        result = round(BigFloat(2.5), 0)
        self.assertIsInstance(result, BigFloat)
        self.assertEqual(result, BigFloat(2))

        # Check that rounding mode only affects the conversion of
        # the rounded result from decimal back to binary, and not
        # the round-ties-to-even used for the binary to decimal round.
        with RoundTowardNegative:
            # Exact halfway case; should round down.
            lower = round(BigFloat('1.125'), 2)
            expected = BigFloat('1.12')
            self.assertEqual(lower, expected)
        with RoundTowardPositive:
            upper = round(BigFloat('1.125'), 2)
            expected = BigFloat('1.12')
            self.assertEqual(upper, expected)
        self.assertLess(lower, upper)

        with RoundTowardNegative:
            lower = round(BigFloat('1.875'), 2)
            expected = BigFloat('1.88')
            self.assertEqual(lower, expected)
        with RoundTowardPositive:
            upper = round(BigFloat('1.875'), 2)
            expected = BigFloat('1.88')
            self.assertEqual(upper, expected)
        self.assertLess(lower, upper)

    @unittest.skipUnless(sys.version_info >= (3,),
                         "math.ceil tests only applicable to Python 3")
    def test_math_ceil(self):
        x = BigFloat('9.55')
        y = math.ceil(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 10)

        x = BigFloat('-9.55')
        y = math.ceil(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, -9)

        x = BigFloat('-0.00')
        y = math.ceil(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat('0.00')
        y = math.ceil(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat.exact(7**100)
        y = math.ceil(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 7**100)

        with self.assertRaises(ValueError):
            y = math.ceil(BigFloat('inf'))
        with self.assertRaises(ValueError):
            y = math.ceil(BigFloat('nan'))

    @unittest.skipUnless(sys.version_info >= (3,),
                         "math.floor tests only applicable to Python 3")
    def test_math_floor(self):
        x = BigFloat('-9.55')
        y = math.floor(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, -10)

        x = BigFloat('9.55')
        y = math.floor(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 9)

        x = BigFloat('-0.00')
        y = math.floor(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat('0.00')
        y = math.floor(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat.exact(7**100)
        y = math.floor(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 7**100)

        with self.assertRaises(ValueError):
            y = math.floor(BigFloat('inf'))
        with self.assertRaises(ValueError):
            y = math.floor(BigFloat('nan'))

    @unittest.skipUnless(sys.version_info >= (3,),
                         "math.trunc tests only applicable to Python 3")
    def test_math_trunc(self):
        x = BigFloat('-9.55')
        y = math.trunc(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, -9)

        x = BigFloat('9.55')
        y = math.trunc(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 9)

        x = BigFloat('-0.00')
        y = math.trunc(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat('0.00')
        y = math.trunc(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 0)

        x = BigFloat.exact(7**100)
        y = math.trunc(x)
        self.assertIsInstance(y, int)
        self.assertEqual(y, 7**100)

        with self.assertRaises(ValueError):
            y = math.trunc(BigFloat('inf'))
        with self.assertRaises(ValueError):
            y = math.trunc(BigFloat('nan'))

    def test__format_to_floating_precision(self):
        # Formatting to precision 1.  We need extra testing for this, since
        # it's not supported by the MPFR library itself.

        x = BigFloat('9.55')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '1', 1),
        )

        x = BigFloat('9.7')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '1', 1),
        )

        # Halfway cases
        x = BigFloat('-0.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (True, '5', -1),
        )
        x = BigFloat('-1.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (True, '2', 0),
        )
        x = BigFloat('-2.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (True, '2', 0),
        )
        x = BigFloat('-3.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (True, '4', 0),
        )
        x = BigFloat('0.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '5', -1),
        )
        x = BigFloat('1.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '2', 0),
        )
        x = BigFloat('2.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '2', 0),
        )
        x = BigFloat('3.5')
        self.assertEqual(
            x._format_to_floating_precision(1),
            (False, '4', 0),
        )

    def test__format_to_fixed_precision(self):
        # Zeros
        x = BigFloat('0')
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (False, '0', -5),
        )

        x = BigFloat('-0')
        self.assertEqual(
            x._format_to_fixed_precision(-3),
            (True, '0', 3),
        )

        # Specials
        x = BigFloat('inf')
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (False, 'inf', None),
        )
        x = BigFloat('-inf')
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (True, 'inf', None),
        )
        x = BigFloat('nan')
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (False, 'nan', None),
        )

        x = BigFloat('4567.892391555555')
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (False, '456789239', -5),
        )

        x = BigFloat('-0.000123456')
        self.assertEqual(
            x._format_to_fixed_precision(10),
            (True, '1234560', -10),
        )
        self.assertEqual(
            x._format_to_fixed_precision(6),
            (True, '123', -6),
        )
        self.assertEqual(
            x._format_to_fixed_precision(5),
            (True, '12', -5),
        )

        self.assertEqual(
            x._format_to_fixed_precision(4),
            (True, '1', -4),
        )

        self.assertEqual(
            x._format_to_fixed_precision(3),
            (True, '0', -3),
        )

        # Cases where we end up computing zero significant digits.
        self.assertEqual(
            BigFloat('0.0999999999')._format_to_fixed_precision(0),
            (False, '0', 0),
        )
        self.assertEqual(
            BigFloat('0.1000000001')._format_to_fixed_precision(0),
            (False, '0', 0),
        )
        self.assertEqual(
            BigFloat('0.47')._format_to_fixed_precision(0),
            (False, '0', 0),
        )
        self.assertEqual(
            BigFloat('0.499999999')._format_to_fixed_precision(0),
            (False, '0', 0),
        )
        self.assertEqual(
            BigFloat('0.5')._format_to_fixed_precision(0),
            (False, '0', 0),
        )
        self.assertEqual(
            BigFloat('0.500000001')._format_to_fixed_precision(0),
            (False, '1', 0),
        )
        self.assertEqual(
            BigFloat('0.53')._format_to_fixed_precision(0),
            (False, '1', 0),
        )
        self.assertEqual(
            BigFloat('0.9')._format_to_fixed_precision(0),
            (False, '1', 0),
        )
        self.assertEqual(
            BigFloat('0.99')._format_to_fixed_precision(0),
            (False, '1', 0),
        )
        self.assertEqual(
            BigFloat('0.999999999')._format_to_fixed_precision(0),
            (False, '1', 0),
        )

        self.assertEqual(
            BigFloat('-0.0999999999')._format_to_fixed_precision(0),
            (True, '0', 0),
        )
        self.assertEqual(
            BigFloat('-0.1000000001')._format_to_fixed_precision(0),
            (True, '0', 0),
        )
        self.assertEqual(
            BigFloat('-0.499999999')._format_to_fixed_precision(0),
            (True, '0', 0),
        )
        self.assertEqual(
            BigFloat('-0.5')._format_to_fixed_precision(0),
            (True, '0', 0),
        )
        self.assertEqual(
            BigFloat('-0.500000001')._format_to_fixed_precision(0),
            (True, '1', 0),
        )
        self.assertEqual(
            BigFloat('-0.9')._format_to_fixed_precision(0),
            (True, '1', 0),
        )
        self.assertEqual(
            BigFloat('-0.99')._format_to_fixed_precision(0),
            (True, '1', 0),
        )
        self.assertEqual(
            BigFloat('-0.999999999')._format_to_fixed_precision(0),
            (True, '1', 0),
        )

        # Values close to powers of 10; checking exponent calculation
        x = BigFloat('1.000000000001')
        self.assertEqual(
            x._format_to_fixed_precision(3),
            (False, '1000', -3),
        )

        x = BigFloat('0.999999999999')
        self.assertEqual(
            x._format_to_fixed_precision(3),
            (False, '1000', -3),
        )

        x = BigFloat('1.0000000000000001')
        self.assertEqual(
            x._format_to_fixed_precision(3),
            (False, '1000', -3),
        )

        x = BigFloat('0.9999999999999999')
        self.assertEqual(
            x._format_to_fixed_precision(3),
            (False, '1000', -3),
        )

    # 5.4 Conversion Functions
    def test_frexp(self):
        x = BigFloat(float.fromhex('0x1.921fb54442d18p+1'))
        significand, exponent = frexp(x)
        self.assertIsInstance(exponent, int)
        self.assertEqual(exponent, 2)

        expected_significand = BigFloat(float.fromhex('0x1.921fb54442d18p-1'))
        self.assertEqual(significand, expected_significand)

    # 5.5 Basic Arithmetic Functions
    def test_root(self):

        this_module = __name__.split(".")[-1]

        def quiet_root(x, n):
            with self.assertIssuesDeprecationWarning(filename=this_module):
                return root(x, n)

        self.assertEqual(quiet_root(BigFloat(23), 1), BigFloat(23))
        self.assertEqual(quiet_root(BigFloat(49), 2), BigFloat(7))
        self.assertEqual(quiet_root(BigFloat(27), 3), BigFloat(3))
        self.assertEqual(quiet_root(BigFloat(-27), 3), BigFloat(-3))
        self.assertEqual(quiet_root(BigFloat(16), 4), BigFloat(2))
        with self.assertRaises(ValueError):
            quiet_root(BigFloat(23), -1)
        self.assertTrue(is_nan(quiet_root(BigFloat(2), 0)))
        self.assertTrue(is_nan(quiet_root(BigFloat(-2), 2)))

        self.assertIsNegativeZero(quiet_root(-BigFloat(0), 2))
        self.assertIsPositiveZero(quiet_root(BigFloat(0), 2))
        self.assertIsNegativeZero(quiet_root(-BigFloat(0), 3))
        self.assertIsPositiveZero(quiet_root(BigFloat(0), 3))

    def test_rootn(self):
        self.assertEqual(rootn(BigFloat(23), 1), BigFloat(23))
        self.assertEqual(rootn(BigFloat(49), 2), BigFloat(7))
        self.assertEqual(rootn(BigFloat(27), 3), BigFloat(3))
        self.assertEqual(rootn(BigFloat(-27), 3), BigFloat(-3))
        self.assertEqual(rootn(BigFloat(16), 4), BigFloat(2))
        with self.assertRaises(ValueError):
            rootn(BigFloat(23), -1)
        self.assertTrue(is_nan(rootn(BigFloat(2), 0)))
        self.assertTrue(is_nan(rootn(BigFloat(-2), 2)))

        self.assertIsPositiveZero(rootn(-BigFloat(0), 2))
        self.assertIsPositiveZero(rootn(BigFloat(0), 2))
        self.assertIsNegativeZero(rootn(-BigFloat(0), 3))
        self.assertIsPositiveZero(rootn(BigFloat(0), 3))

    # 5.6 Comparison Functions
    def test_cmp(self):
        self.assertGreater(cmp(BigFloat(2), BigFloat(1)), 0)
        self.assertEqual(cmp(BigFloat(3.5), 3.5), 0)
        self.assertLess(cmp(-3.5, -1), 0)

        # Comparisons involving NaNs should raise an exception
        with self.assertRaises(ValueError):
            cmp(BigFloat('nan'), 0)
        with self.assertRaises(ValueError):
            cmp(0, BigFloat('nan'))
        with self.assertRaises(ValueError):
            cmp(BigFloat('-nan'), BigFloat('nan'))

    def test_cmpabs(self):
        self.assertGreater(cmpabs(BigFloat(2), BigFloat(1)), 0)
        self.assertEqual(cmpabs(BigFloat(3.5), 3.5), 0)
        self.assertGreater(cmpabs(-3.5, -1), 0)

        # Comparisons involving NaNs should raise an exception
        with self.assertRaises(ValueError):
            cmpabs(BigFloat('nan'), 0)
        with self.assertRaises(ValueError):
            cmpabs(0, BigFloat('nan'))
        with self.assertRaises(ValueError):
            cmpabs(BigFloat('-nan'), BigFloat('nan'))

    def test_sgn(self):
        self.assertEqual(sgn(BigFloat(2.6)), 1)
        self.assertEqual(sgn(BigFloat(-3.5)), -1)

        # Special values
        self.assertEqual(sgn(BigFloat('-inf')), -1)
        self.assertEqual(sgn(BigFloat('inf')), 1)
        self.assertEqual(sgn(BigFloat('0')), 0)
        self.assertEqual(sgn(BigFloat('-0')), 0)

        # NaNs should raise an exception
        with self.assertRaises(ValueError):
            sgn(BigFloat('nan'))

    # 5.7 Special Functions
    def test_factorial(self):
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
        self.assertEqual(factorial(2), 2)
        self.assertEqual(factorial(3), 6)
        self.assertEqual(factorial(4), 24)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(6), 720)

        with self.assertRaises((OverflowError, ValueError)):
            factorial(-1)

    def test_zeta_ui(self):
        self.assertEqual(zeta_ui(0), -0.5)
        self.assertEqual(zeta_ui(1), float('inf'))
        self.assertEqual(zeta_ui(2), 1.6449340668482264)

    def test_lgamma(self):
        self.assertEqual(lgamma(0.5), 0.57236494292470008)
        self.assertEqual(lgamma(-0.5), 1.2655121234846454)

    def test_jn(self):
        self.assertEqual(j0(1.2345), jn(0, 1.2345))
        self.assertEqual(j1(1.2345), jn(1, 1.2345))

    def test_yn(self):
        self.assertEqual(y0(1.2345), yn(0, 1.2345))
        self.assertEqual(y1(1.2345), yn(1, 1.2345))

    # 5.12 Miscellaneous Functions
    def test_min(self):
        self.assertEqual(min(2, 3), 2)

    def test_max(self):
        self.assertEqual(max(2, 3), 3)

    def test_copysign(self):
        self.assertEqual(copysign(5, -7), -5)
        self.assertEqual(copysign(5, 7), 5)
        self.assertEqual(copysign(-5, 7), 5)
        self.assertEqual(copysign(-5, -7), -5)

    # Testcase helper assertions

    @contextlib.contextmanager
    def assertIssuesDeprecationWarning(self, filename=None):
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            try:
                yield
            finally:
                self.assertEqual(len(ws), 1)
                w = ws[-1]
                self.assertTrue(issubclass(w.category, DeprecationWarning))
                self.assertIn("deprecated", str(w.message))
                if filename is not None:
                    self.assertIn(filename, w.filename)

    def assertIsPositiveZero(self, x):
        self.assertEqual(x, 0)
        self.assertFalse(is_negative(x))

    def assertIsNegativeZero(self, x):
        self.assertEqual(x, 0)
        self.assertTrue(is_negative(x))


class IEEEContextTests(unittest.TestCase):
    def test_IEEEContext(self):
        self.assertEqual(IEEEContext(16), half_precision)
        self.assertEqual(IEEEContext(32), single_precision)
        self.assertEqual(IEEEContext(64), double_precision)
        self.assertEqual(IEEEContext(128), quadruple_precision)

        c = IEEEContext(256)
        self.assertEqual(c.precision, 237)
        self.assertEqual(c.emax, 262144)
        self.assertEqual(c.emin, -262377)
        self.assertEqual(c.subnormalize, True)
        self.assertEqual(c.rounding, None)


class FlagTests(unittest.TestCase):
    def test_overflow(self):
        set_flagstate(set())  # clear flags
        exp(BigFloat(1e308))
        self.assertEqual(get_flagstate(), {Inexact, Overflow})

    def test_divide_by_zero(self):
        # Clear all flags.
        set_flagstate(set())
        self.assertEqual(get_flagstate(), set())
        BigFloat(2) / BigFloat(0)
        self.assertEqual(get_flagstate(), {ZeroDivision})
        # Flag should be sticky, so after a simple exact operation, it
        # should still be set.
        BigFloat(1) * BigFloat(3)
        self.assertEqual(get_flagstate(), {ZeroDivision})


class ABCTests(unittest.TestCase):
    def setUp(self):
        self._original_context = getcontext()
        setcontext(DefaultTestContext)

    def tearDown(self):
        setcontext(self._original_context)
        del self._original_context


def mpfr_set_str2(rop, s, base, rnd):
    """Set value of rop from the string s, using given base and rounding mode.

    If s is a valid string for the given base, set the Mpfr variable
    rop from s, rounding in the direction given by 'rnd', and return
    the usual ternary value.

    If s is not a valid string for the given base, raise ValueError.

    """
    import mpfr

    if s == s.strip():
        ternary, endindex = mpfr.mpfr_strtofr(rop, s, base, rnd)
        if not s[endindex:]:
            return ternary
    raise ValueError("not a valid numeric string")


def _fromhex_exact(value):
    """Private function used in testing"""
    # private low-level version of fromhex that always does an exact
    # conversion.  Avoids using any heavy machinery (contexts, function
    # wrapping), since its main use is in the testing of that machinery.
    import mpfr
    from bigfloat.core import ROUND_TIES_TO_EVEN

    precision = len(value) * 4
    bf = mpfr.Mpfr_t.__new__(BigFloat)
    mpfr.mpfr_init2(bf, precision)
    ternary = mpfr_set_str2(bf, value, 16, ROUND_TIES_TO_EVEN)
    if ternary:
        # conversion should have been exact, except possibly if
        # value overflows or underflows
        raise ValueError("_fromhex_exact failed to do an exact "
                         "conversion.  This shouldn't happen. "
                         "Please report.")
    return bf


def process_lines(lines):
    def test_fn(self):

        for line in lines:
            # any portion of the line after '#' is a comment; leading
            # and trailing whitespace are ignored
            comment_pos = line.find('#')
            if comment_pos != -1:
                line = line[:comment_pos]
            line = line.strip()
            if not line:
                continue

            # now we've got a line that should be processed; possibly
            # a directive
            if line.startswith('context '):
                context = getattr(bigfloat, line[8:])
                setcontext(context)
                continue

            # not a directive, so it takes the form lhs -> rhs, where
            # the lhs is a function name followed by arguments, and
            # the rhs is an expected result followed by expected flags
            lhs_pieces, rhs_pieces = map(str.split, line.split('->'))
            fn = getattr(bigfloat, lhs_pieces[0])
            args = [_fromhex_exact(arg) for arg in lhs_pieces[1:]]
            expected_result = _fromhex_exact(rhs_pieces[0])
            expected_flags = set(
                getattr(bigfloat, flag) for flag in rhs_pieces[1:]
            )

            # reset flags, and compute result
            set_flagstate(set())
            actual_result = fn(*args)
            actual_flags = get_flagstate()

            # compare actual with expected results
            diff = diffBigFloat(actual_result, expected_result,
                                match_precisions=False)
            if diff is not None:
                self.fail("{}: {}".format(diff, line))
            self.assertEqual(actual_flags, expected_flags, msg=line)

    return test_fn


def tests_from_data(basename):
    """
    Return test processing data from a given file.

    Given the basename of a *.bft file in the test_data directory,
    return a test method that runs the tests for that file.
    """
    test_file = pkg_resources.resource_filename(
        "bigfloat.test",
        "test_data/{basename}.bft".format(basename=basename),
    )
    with io.open(test_file, encoding="utf-8") as f:
        test_data = f.readlines()
    return process_lines(test_data)


ABCTests.test_next_up = tests_from_data("next_up")
ABCTests.test_next_down = tests_from_data("next_down")
ABCTests.test_pos = tests_from_data("pos")
ABCTests.test_mod = tests_from_data("mod")
ABCTests.test_floordiv = tests_from_data("floordiv")
ABCTests.test_various = tests_from_data("various")


def load_tests(loader, tests, ignore):
    """ Add bigfloat.core doctests to test suite. """
    tests.addTests(doctest.DocTestSuite(bigfloat.core))
    return tests


if __name__ == '__main__':
    unittest.main()

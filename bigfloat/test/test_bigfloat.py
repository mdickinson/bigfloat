from __future__ import with_statement # for Python 2.5

from test.test_support import run_unittest
import unittest
import operator
from bigfloat import *
from bigfloat import _all_flags
import math
import __builtin__

all_rounding_modes = [RoundTowardZero, RoundTowardNegative,
                      RoundTowardPositive, RoundTiesToEven]
all_rounding_mode_strings = ['RoundTowardZero', 'RoundTowardNegative',
                             'RoundTowardPositive', 'RoundTiesToEven']


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


class BigFloatTests(unittest.TestCase):
    def setUp(self):
        setcontext(DefaultContext)

    def assertIdenticalFloat(self, x, y):
        if not (isinstance(x, float) and isinstance(y, float)):
            raise ValueError("Expected x and y to be floats "
                             "in assertIdenticalFloat")
        if x != x or y != y: # if either x or y is a nan...
            if x == x or y == y:  # and one of x and y is not a nan...
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
        fns = [add, sub, mul, div, pow, mod]
        values = [2, 3L, 1.234, BigFloat('0.678'), BigFloat('nan'),
                  float('0.0'), float('inf'), True]

        # functions should accept operands of any integer, float or BigFloat type.
        for v in values:
            for w in values:
                for p in test_precisions:
                    with precision(p):
                        for fn in fns:
                            # test without rounding mode
                            res = fn(v, w)
                            self.assertEqual(type(res), BigFloat)
                            self.assertEqual(res.precision, p)
                            # test with rounding mode
                            for rnd in all_rounding_modes:
                                res = fn(v, w, context=rnd)
                                self.assertEqual(type(res), BigFloat)
                                self.assertEqual(res.precision, p)

        # should be able to specify rounding mode directly,
        # and it overrides the current context rounding mode
        for p in test_precisions:
            with precision(p):
                for rnd in all_rounding_modes:
                    with rnd:
                        x = div(1, 3, context=RoundTowardPositive)
                        y = div(1, 3, context=RoundTowardNegative)
                        self.assert_(y < x)
                        x3 = mul(3, x, context=RoundTowardPositive)
                        y3 = mul(y, 3, context=RoundTowardNegative)
                        self.assert_(y3 < 1 < x3)

    def test_binary_operations(self):
        # check that BigFloats can be combined with themselves,
        # and with integers and floats, using the 6 standard
        # arithmetic operators:  +, -, *, /, **, %

        x = BigFloat('17.29')
        other_values = [2, 3L, 1.234, BigFloat('0.678'), False]
        test_precisions = [2, 20, 53, 2000]
        # note that division using '/' should work (giving true division)
        # whether or not 'from __future__ import division' is enabled.
        # So we test both operator.div and operator.truediv.
        operations = [operator.add, operator.mul, operator.div,
                      operator.sub, operator.pow, operator.truediv,
                      operator.mod]
        for value in other_values:
            for p in test_precisions:
                with precision(p):
                    for op in operations:
                        bf = op(x, value)
                        self.assertEqual(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)
                        bf = op(value, x)
                        self.assertEqual(type(bf), BigFloat)
                        self.assertEqual(bf.precision, p)

    def test_bool(self):
        # test __nonzero__ / __bool__
        self.assertEqual(bool(BigFloat(0)), False)
        self.assertEqual(bool(BigFloat('-0')), False)
        self.assertEqual(bool(BigFloat(1.0)), True)
        self.assertEqual(bool(BigFloat(-123)), True)
        self.assertEqual(bool(BigFloat('nan')), True)
        self.assertEqual(bool(BigFloat('inf')), True)
        self.assertEqual(bool(BigFloat('-inf')), True)

    def test_classifications(self):
        # test classification functions (is_nan, is_inf, is_zero,
        # is_finite, is_integer, is_negative)

        for x in [float('nan'), BigFloat('nan'), float('-nan'), -BigFloat('nan')]:
            self.assertEqual(is_nan(x), True)
            self.assertEqual(is_inf(x), False)
            self.assertEqual(is_zero(x), False)
            self.assertEqual(is_finite(x), False)
            self.assertEqual(is_integer(x), False)

        for x in [float('inf'), float('-inf'), BigFloat('inf'), BigFloat('-inf')]:
            self.assertEqual(is_nan(x), False)
            self.assertEqual(is_inf(x), True)
            self.assertEqual(is_zero(x), False)
            self.assertEqual(is_finite(x), False)
            self.assertEqual(is_integer(x), False)

        for x in [0, 0L, float('0.0'), float('-0.0'), BigFloat('0.0'), BigFloat('-0.0')]:
            self.assertEqual(is_nan(x), False)
            self.assertEqual(is_inf(x), False)
            self.assertEqual(is_zero(x), True)
            self.assertEqual(is_finite(x), True)
            self.assertEqual(is_integer(x), True)

        for x in [2, -31L, 24.0, -5.13, BigFloat('1e-1000'), BigFloat('-2.34e1000')]:
            self.assertEqual(is_nan(x), False)
            self.assertEqual(is_inf(x), False)
            self.assertEqual(is_zero(x), False)
            self.assertEqual(is_finite(x), True)

        # test is_integer for finite nonzero values
        for x in [2, -31L, 24.0, BigFloat('1e100'), sqrt(BigFloat('2e100'))]:
            self.assertEqual(is_integer(x), True)

        for x in [2.1, BigFloat(-1.345), sqrt(BigFloat(2))]:
            self.assertEqual(is_integer(x), False)

        # test is_negative
        for x in [float('-inf'), float('-0.0'), BigFloat('-inf'), BigFloat('-0.0'),
                  BigFloat(-2.3), -31, -1L]:
            self.assertEqual(is_negative(x), True)

        for x in [float('inf'), BigFloat('inf'), float('0.0'), 0, 0L, 2L, 123,
                  BigFloat(1.23)]:
            self.assertEqual(is_negative(x), False)


    def test_comparisons(self):
        # here's a list of lists of values; within each sublist all
        # entries have the same value;  sublists are ordered by increasing value
        values = [
            [BigFloat('-Infinity'), float('-inf')],
            [-1L, -1, -1.0, BigFloat(-1.0)],
            [0L, 0, float('0.0'), float('-0.0'), BigFloat('0.0'), BigFloat('-0.0')],
            [BigFloat('4e-324')],
            [4e-324],
            [1e-320, BigFloat(1e-320)],
            [1L, 1, 1.0, BigFloat(1.0)],
            [BigFloat(2**53+1)],
            [2**53+1],
            [BigFloat('Infinity'), float('inf')],
            ]

        nans = [BigFloat('nan'), -BigFloat('-nan'), float('nan'), -float('nan')]

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
            self.assertEqual(x < y, True)
            self.assertEqual(x <= y, True)
            self.assertEqual(x != y, True)
            self.assertEqual(x > y, False)
            self.assertEqual(x >= y, False)
            self.assertEqual(x == y, False)
            self.assertEqual(lessgreater(x, y), True)
            self.assertEqual(unordered(x, y), False)

        for x, y in EQ_PAIRS:
            self.assertEqual(x <= y, True)
            self.assertEqual(x >= y, True)
            self.assertEqual(x == y, True)
            self.assertEqual(x < y, False)
            self.assertEqual(x > y, False)
            self.assertEqual(x != y, False)
            self.assertEqual(lessgreater(x, y), False)
            self.assertEqual(unordered(x, y), False)

        for x, y in GT_PAIRS:
            self.assertEqual(x > y, True)
            self.assertEqual(x >= y, True)
            self.assertEqual(x != y, True)
            self.assertEqual(x < y, False)
            self.assertEqual(x <= y, False)
            self.assertEqual(x == y, False)
            self.assertEqual(lessgreater(x, y), True)
            self.assertEqual(unordered(x, y), False)

        for x, y in UN_PAIRS:
            self.assertEqual(x < y, False)
            self.assertEqual(x <= y, False)
            self.assertEqual(x > y, False)
            self.assertEqual(x >= y, False)
            self.assertEqual(x == y, False)
            self.assertEqual(x != y, True)
            self.assertEqual(lessgreater(x, y), False)
            self.assertEqual(unordered(x, y), True)

    def test_creation_from_integer(self):
        test_values = [-23, 0, 100, 7**100, -23L, 0L, 100L]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertEqual(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

    def test_creation_from_float(self):
        test_values = [-12.3456, float('-0.0'), float('0.0'), 5e-310, -1e308,
                        float('nan'), float('inf'), float('-inf')]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertEqual(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

        # check directly-supplied rounding mode
        lower = BigFloat(1.1, precision(24) + RoundTowardNegative)
        upper = BigFloat(1.1, RoundTowardPositive + precision(24))
        self.assert_(lower < upper)

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
                       u'-451.001']
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertEqual(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

        # check that rounding mode affects the conversion
        with RoundTowardNegative:
            lower = BigFloat('1.1')
        with RoundTowardPositive:
            upper = BigFloat('1.1')
        self.assert_(lower < upper)

        # alternative version, without with statements
        lower = BigFloat('1.1', RoundTowardNegative)
        upper = BigFloat('1.1', RoundTowardPositive)
        self.assert_(lower < upper)

        self.assert_(is_nan(BigFloat('nan')))
        self.assert_(is_inf(BigFloat('inf')))
        self.assert_(not is_negative(BigFloat('inf')))
        self.assert_(is_inf(BigFloat('-inf')))
        self.assert_(is_negative(BigFloat('-inf')))
        self.assert_(is_zero(BigFloat('0')))
        self.assert_(not is_negative(BigFloat('0')))
        self.assert_(is_zero(BigFloat('-0')))
        self.assert_(is_negative(BigFloat('-0')))

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
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)
                # check directly-supplied context
                bf = BigFloat(value, precision(p))
                self.assertEqual(type(bf), BigFloat)
                self.assertEqual(bf.precision, p)

    def test_exact_context_independent(self):
        with Context(emin=-1, emax=1):
            x = BigFloat.exact(123456)
        self.assertEqual(x, 123456)

    def test_exact_overflow(self):
        # exact conversion should raise ValueError for values that are
        # too large or too small to represent.  (Clearly, floats can
        # never be too large or too small, and integers can't ever
        # be too small.  Here we test with strings.)
        too_large = '1e%d' % (EMAX_MAX//3)
        too_small = '1e%d' % (EMIN_MIN//3)
        too_large_neg = '-1e%d' % (EMAX_MAX//3)
        too_small_neg = '-1e%d' % (EMIN_MIN//3)
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
        test_values = [-23, 0, 100, 7**100, -23L, 0L, 100L]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value)
                    self.assertEqual(type(bf), BigFloat)
                    # check that conversion back to an int recovers
                    # the same value, regardless of the precision of
                    # the current context
                    self.assertEqual(int(bf), value)

        self.assertRaises(TypeError, BigFloat.exact, 1, precision=200)
        self.assertRaises(TypeError, BigFloat.exact, -13L, precision=53)

    def test_exact_creation_from_float(self):
        test_values = [-12.3456, float('-0.0'), float('0.0'), 5e-310, -1e308,
                        float('nan'), float('inf'), float('-inf')]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value)
                    self.assertEqual(type(bf), BigFloat)
                    # check that conversion back to float recovers
                    # the same value
                    self.assertIdenticalFloat(float(bf), value)

        self.assertRaises(TypeError, BigFloat.exact, 1.0, precision=200)
        self.assertRaises(TypeError, BigFloat.exact, float('nan'), precision=53)

    def test_exact_creation_from_string(self):
        test_values = ['123.456',
                       '-1.23',
                       '1e456',
                       '+nan',
                       'inf',
                       '-inf',
                       u'-451.001']
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat.exact(value, precision=p)
                    self.assertEqual(type(bf), BigFloat)
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

    def test_exponent_limits(self):
        with Context(emin=-1000, emax=0):
            x = add(123, 456)
        self.assertEqual(x, BigFloat('infinity'))

    def test_float(self):
        # test conversion to float
        with precision(200):
            x = BigFloat(2**100+1)/2**100
            y = BigFloat(2**100-1)/2**100

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

        # check that hash(n) matches hash(BigFloat(n)) for integers n
        for n in range(-50, 50):
            self.assertEqual(hash(n), hash(BigFloat.exact(n)))

        #   values near powers of 2
        for e in [30, 31, 32, 33, 34, 62, 63, 64, 65, 66]:
            for n in range(2**e-50, 2**e+50):
                self.assertEqual(hash(n), hash(BigFloat.exact(n)))
                self.assertEqual(hash(BigFloat(n)), hash(int(BigFloat(n))))

        # check that hash values match those of floats
        self.assertEqual(hash(BigFloat('inf')), hash(float('inf')))
        self.assertEqual(hash(BigFloat('-inf')), hash(float('-inf')))
        self.assertEqual(hash(BigFloat('0')), hash(float('0')))
        self.assertEqual(hash(BigFloat('-0')), hash(float('-0')))
        self.assertEqual(hash(BigFloat('1')), hash(float('1')))
        self.assertEqual(hash(BigFloat('-1')), hash(float('-1')))
        self.assertEqual(hash(BigFloat('1.625')), hash(float('1.625')))
        self.assertEqual(hash(BigFloat.exact(1.1)), hash(1.1))

    def test_hex(self):
        # test conversion to a hex string

        test_values = [
            # (input, precision, output)
            ('NaN', 2, 'NaN'),
            ('NaN', 24, 'NaN'),
            ('NaN', 53, 'NaN'),
            ('NaN', 100, 'NaN'),
            #('-NaN', 10, '-NaN'),
            ('Inf', 2, 'Infinity'),
            ('-Inf', 10, '-Infinity'),
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

        for strarg, precision, expected in test_values:
            arg = BigFloat.exact(strarg, precision=precision)
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

    def test_integer_ratio(self):

        ir = BigFloat.as_integer_ratio

        test_values = [
            (sqrt(BigFloat(2), context=RoundTowardPositive), (6369051672525773, 4503599627370496)),
            (sqrt(BigFloat(2), context=RoundTowardNegative), (1592262918131443, 1125899906842624)),
            (const_pi(), (884279719003555L, 281474976710656L)),
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
        self.assertEqual(str(BigFloat('inf')), 'Infinity')
        self.assertEqual(str(BigFloat('-inf')), '-Infinity')
        self.assertEqual(str(BigFloat('nan')), 'NaN')

        self.assertEqual(str(BigFloat('1e100')), '1.0000000000000000e+100')

        # check switch from fixed-point to exponential notation
        self.assertEqual(str(BigFloat('1e-5')), '1.0000000000000001e-5')
        self.assertEqual(str(BigFloat('9.999e-5')), '9.9989999999999996e-5')
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
            self.assertEqual(div(2**53+1, 2**1128), pow(2, -1074))

        # check that results are integer multiples of
        # 2**-1074
        with double_precision:
            self.assertEqual(BigFloat('3e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.4e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.5e-324'), pow(2, -1073))

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

                absx = __builtin__.abs(x)
                self.assertEqual(absx.precision, p)
                if p < 150:
                    self.assertNotEqual(x, absx)
                else:
                    self.assertEqual(x, absx)


class ContextTests(unittest.TestCase):
    def setUp(self):
        setcontext(DefaultContext)

    def test_attributes(self):
        c = DefaultContext
        self.assert_(isinstance(c.precision, (int, long)))
        self.assert_(isinstance(c.emax, (int, long)))
        self.assert_(isinstance(c.emin, (int, long)))
        self.assert_(isinstance(c.subnormalize, bool))
        self.assert_(c.rounding in all_rounding_mode_strings)

    #def test_callable(self):
    #    # check that self is callable
    #    c = Context(emin = -123, emax=456, precision=1729,
    #                subnormalize=True, rounding=RoundTowardPositive)
    #    d = c(precision=400)
    #    self.assertEqual(d.precision, 400)
    #    self.assertEqual(d.emax, c.emax)
    #    self.assertEqual(d.emin, c.emin)
    #    self.assertEqual(d.subnormalize, c.subnormalize)
    #    self.assertEqual(d.rounding, c.rounding)
    #
    #    e = c(emax=16384, rounding=RoundTowardZero)
    #    self.assertEqual(e.precision, c.precision)
    #    self.assertEqual(e.emax, 16384)
    #    self.assertEqual(e.emin, c.emin)
    #    self.assertEqual(e.rounding, RoundTowardZero)
    #    self.assertEqual(e.subnormalize, c.subnormalize)

    def test_hashable(self):
        # create equal but non-identical contexts
        c1 = Context(emin=-999, emax=999, precision=100,
                     subnormalize=True, rounding='RoundTowardPositive')
        c2 = (Context(emax=999, emin=-999, rounding='RoundTowardPositive') + 
              Context(precision=100, subnormalize=True))
        self.assertEqual(hash(c1), hash(c2))

    def test_with(self):
        # check use of contexts in with statements
        c = Context(emin = -123, emax=456, precision=1729,
                    subnormalize=True, rounding='RoundTowardPositive')
        d = Context(emin = 0, emax=10585, precision=20,
                    subnormalize=False, rounding='RoundTowardNegative')

        with c:
            # check nested with
            with d:
                self.assertEqual(getcontext().precision, d.precision)
                self.assertEqual(getcontext().emin, d.emin)
                self.assertEqual(getcontext().emax, d.emax)
                self.assertEqual(getcontext().subnormalize, d.subnormalize)
                self.assertEqual(getcontext().rounding, d.rounding)

            # check context is restored on normal exit
            self.assertEqual(getcontext().precision, c.precision)
            self.assertEqual(getcontext().emin, c.emin)
            self.assertEqual(getcontext().emax, c.emax)
            self.assertEqual(getcontext().subnormalize, c.subnormalize)
            self.assertEqual(getcontext().rounding, c.rounding)

            # check context is restored on abnormal exit, and that exceptions
            # raised within the with block are propagated
            try:
                with d:
                    raise ValueError
            except ValueError:
                pass
            else:
                self.fail('ValueError not propagated from with block')

            self.assertEqual(getcontext().precision, c.precision)
            self.assertEqual(getcontext().emin, c.emin)
            self.assertEqual(getcontext().emax, c.emax)
            self.assertEqual(getcontext().subnormalize, c.subnormalize)
            self.assertEqual(getcontext().rounding, c.rounding)

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
        result = exp(BigFloat(1e308))
        self.assertEqual(get_flagstate(), set([Inexact, Overflow]))


class ABCTests(unittest.TestCase):
    def setUp(self):
        setcontext(DefaultContext)

def process_lines(lines):
    def test_fn(self):

        for l in lines:
            # any portion of the line after '#' is a comment; leading
            # and trailing whitespace are ignored
            comment_pos = l.find('#')
            if comment_pos != -1:
                l = l[:comment_pos]
            l = l.strip()
            if not l:
                continue

            # now we've got a line that should be processed; possibly
            # a directive
            if l.startswith('context '):
                context = globals()[l[8:]]
                setcontext(context)
                continue

            # not a directive, so it takes the form lhs -> rhs, where
            # the lhs is a function name followed by arguments, and
            # the rhs is an expected result followed by expected flags
            lhs_pieces, rhs_pieces = map(str.split, l.split('->'))
            fn = globals()[lhs_pieces[0]]
            args = [BigFloat._fromhex_exact(arg) for arg in lhs_pieces[1:]]
            expected_result = BigFloat._fromhex_exact(rhs_pieces[0])
            expected_flags = set(globals()[flag] for flag in rhs_pieces[1:])

            # reset flags, and compute result
            set_flagstate(set())
            actual_result = fn(*args)
            actual_flags = get_flagstate()

            # compare actual with expected results
            diff = diffBigFloat(actual_result, expected_result,
                                match_precisions=False)
            if diff is not None:
                self.fail(diff)
            self.assertEqual(actual_flags, expected_flags)

    return test_fn

ABCTests.test_next_up = process_lines("""\
context double_precision

next_up -inf -> -1.fffffffffffffp+1023
next_up -1p-1074 -> -0
next_up -0.8p-1075 -> -0
next_up -0.4p-1075 -> -0
next_up -0.000000000000000000000000001p-1075 -> -0
next_up -1p-999999999 -> -0
next_up -0 -> 1p-1074
next_up 0 -> 1p-1074
next_up 1p-999999999 -> 1p-1074
next_up 0.8p-1074 -> 1p-1074
next_up 0.ffffffffffffffffffffp-1074 -> 1p-1074
next_up 1p-1074 -> 2p-1074
next_up 1p-1023 -> 1.0000000000002p-1023
next_up 1p-1022 -> 1.0000000000001p-1022
next_up 1.ffffffffffffep+1023 -> 1.fffffffffffffp+1023
next_up 1.ffffffffffffeffffp+1023 -> 1.fffffffffffffp+1023
next_up 1.fffffffffffffp+1023 -> inf
next_up inf -> inf

next_up nan -> nan

""".split('\n'))



ABCTests.test_pos = process_lines("""\
context double_precision
context RoundTiesToEven

pos 0 -> 0
pos -0 -> -0
pos inf -> inf
pos -inf -> -inf
pos nan -> nan NanFlag

# smallest representable positive value is 1p-1074
# values in (0, 0.8p-1074] -> 0 Inexact Underflow

# exactly representable with precision 53 and unbounded exponent,
# but not exactly representable with precision 53 and bounded exponent
pos 0.8p-1075 -> 0 Inexact Underflow
pos 0.cp-1075 -> 0 Inexact Underflow
pos 0.ffffffffffffp-1075 -> 0 Inexact Underflow

# not exactly representable with precision 53 and unbounded exponent
pos 0.ffffffffffffffffffffp-1075 -> 0 Inexact Underflow
pos 1p-1075 -> 0 Inexact Underflow

# values in (0.8p-1075, 1p-1074) -> 1p-1074 Inexact Underflow

pos 1.00000000000000000001p-1075 -> 1p-1074 Inexact Underflow
pos 1.000000001p-1075 -> 1p-1074 Inexact Underflow
pos 1.8p-1075 -> 1p-1074 Inexact Underflow
pos 0.ffffffffffff8p-1074 -> 1p-1074 Inexact Underflow
pos 0.ffffffffffffffffffffp-1074 -> 1p-1074 Inexact Underflow

# 1p-1074 exactly representable
pos 1p-1074 -> 1p-1074 Underflow

# values in (1p-1074, 1.8p-1074) -> 1p-1074 Inexact Underflow
pos 1.7p-1074 -> 1p-1074 Inexact Underflow
pos 1.7ffffffffffffp-1074 -> 1p-1074 Inexact Underflow
pos 1.7ffffffffffff8p-1074 -> 1p-1074 Inexact Underflow

# values in [1.8p-1074, 2p-1074) -> 2p-1074 Inexact Underflow
pos 1.8p-1074 -> 2p-1074 Inexact Underflow
pos 1.80000000000008p-1074 -> 2p-1074 Inexact Underflow
pos 1.8000000000001p-1074 -> 2p-1074 Inexact Underflow
pos 2p-1074 -> 2p-1074 Underflow

# test round-half-to-even at some mid-range subnormal values
pos 123456p-1074 -> 123456p-1074 Underflow
pos 123456.7p-1074 -> 123456p-1074 Inexact Underflow
pos 123456.7ffffffffffffp-1074 -> 123456p-1074 Inexact Underflow
pos 123456.8p-1074 -> 123456p-1074 Inexact Underflow
pos 123456.8000000000001p-1074 -> 123457p-1074 Inexact Underflow
pos 123456.9p-1074 -> 123457p-1074 Inexact Underflow
pos 123456.ap-1074 -> 123457p-1074 Inexact Underflow
pos 123456.bp-1074 -> 123457p-1074 Inexact Underflow
pos 123456.cp-1074 -> 123457p-1074 Inexact Underflow
pos 123456.dp-1074 -> 123457p-1074 Inexact Underflow
pos 123456.ep-1074 -> 123457p-1074 Inexact Underflow
pos 123456.fp-1074 -> 123457p-1074 Inexact Underflow
pos 123457.0p-1074 -> 123457p-1074 Underflow
pos 123457.1p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.2p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.3p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.4p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.5p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.6p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.7p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.7fffffffp-1074 -> 123457p-1074 Inexact Underflow
pos 123457.7fffffff8p-1074 -> 123457p-1074 Inexact Underflow
pos 123457.8p-1074 -> 123458p-1074 Inexact Underflow
pos 123457.800000008p-1074 -> 123458p-1074 Inexact Underflow
pos 123457.80000001p-1074 -> 123458p-1074 Inexact Underflow
pos 123457.9p-1074 -> 123458p-1074 Inexact Underflow

# values near smallest representable normal value, 1p-1022
pos 0.8p-1022 -> 0.8p-1022 Underflow

# write e for 2**-53, t for 1p-1022, then:
#
#  (1-2e)t -> Underflow  # exactly representable
#  ((1-2e)t, (1-e)t) -> (1-2e)t Inexact Underflow
#  [(1-e)t, (1-e/2)t) -> t Inexact Underflow
#  [(1-e/2)t, t) -> t Inexact  # no underflow!  after rounding at work

pos 0.fffffffffffffp-1022 -> 0.fffffffffffffp-1022            Underflow
pos 0.fffffffffffff00000000001p-1022 -> 0.fffffffffffffp-1022 Inexact Underflow
pos 0.fffffffffffff4p-1022 -> 0.fffffffffffffp-1022           Inexact Underflow
pos 0.fffffffffffff7ffffffffffp-1022 -> 0.fffffffffffffp-1022 Inexact Underflow
pos 0.fffffffffffff8p-1022 -> 1p-1022                         Inexact Underflow
pos 0.fffffffffffffbffffffffffp-1022 -> 1p-1022               Inexact Underflow
pos 0.fffffffffffffcp-1022 -> 1p-1022                         Inexact
pos 0.ffffffffffffffffffffffffp-1022 -> 1p-1022               Inexact
pos 1p-1022 -> 1p-1022
pos 1p+1024 -> Infinity Inexact Overflow

""".split('\n'))

def test_main():
    run_unittest(BigFloatTests, ContextTests, FlagTests, ABCTests)

if __name__ == '__main__':
    test_main()

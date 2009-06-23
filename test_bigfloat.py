from __future__ import with_statement # for Python 2.5

import unittest
import operator
from bigfloat import *
import math

all_rounding_modes = [RoundTowardZero, RoundTowardNegative,
                      RoundTowardPositive, RoundTiesToEven]

class ContextTests(unittest.TestCase):
    pass

class BigFloatTests(unittest.TestCase):
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
                                res = fn(v, w, rounding=rnd)
                                self.assertEqual(type(res), BigFloat)
                                self.assertEqual(res.precision, p)

        # should be able to specify rounding mode directly,
        # and it overrides the current context rounding mode
        for p in test_precisions:
            with precision(p):
                for rnd in all_rounding_modes:
                    with rounding(rnd):
                        x = div(1, 3, rounding=RoundTowardPositive)
                        y = div(1, 3, rounding=RoundTowardNegative)
                        self.assert_(y < x)
                        x3 = mul(3, x, rounding=RoundTowardPositive)
                        y3 = mul(y, 3, rounding=RoundTowardNegative)
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

        # check that rounding mode affects the conversion
        with rounding(RoundTowardNegative):
            lower = BigFloat('1.1')
        with rounding(RoundTowardPositive):
            upper = BigFloat('1.1')
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

    def test_exact_context_independent(self):
        with exponent_limits(0, 0):
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
        set_flagstate(all_flags)
        self.assertEqual(BigFloat.exact(12345), 12345)
        self.assertEqual(BigFloat.exact(1e-72), 1e-72)

        # check that flags aren't affected by a BigFloat.exact call
        set_flagstate(set())
        BigFloat.exact('123.45', precision=200)  # shouldn't set inexact flag
        flags = get_flagstate()
        self.assertEqual(flags, set())

    def test_exponent_limits(self):
        with exponent_limits(-1000, 0):
            x = add(123, 456)
        self.assertEqual(x, BigFloat('infinity'))

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
        with rounding(RoundTowardNegative):
            lower = BigFloat.exact('1.1', precision=20)
        with rounding(RoundTowardPositive):
            upper = BigFloat.exact('1.1', precision=20)
        self.assertEqual(lower, upper)

    def test_exact_creation_from_BigFloat(self):
        for test_precision in [2, 20, 53, 2000]:
            for test_rounding in all_rounding_modes:
                with precision(test_precision):
                    with rounding(test_rounding):
                        x = sqrt(2)
                y = BigFloat.exact(x)
                self.assertEqual(x, y)

        self.assertRaises(TypeError, BigFloat.exact, BigFloat(23), 100)

    def test_float(self):
        # test conversion to float
        with precision(200):
            x = BigFloat(2**100+1)/2**100
            y = BigFloat(2**100-1)/2**100

        self.assertNotEqual(x, y)

        # rounding mode shouldn't affect conversion
        for rnd in all_rounding_modes:
            with rounding(rnd):
                self.assertEqual(float(x), 1.)
                self.assertEqual(float(y), 1.)

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
            (sqrt(BigFloat(2), rounding=RoundTowardPositive), (6369051672525773, 4503599627370496)),
            (sqrt(BigFloat(2), rounding=RoundTowardNegative), (1592262918131443, 1125899906842624)),
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

                absx = __builtins__.abs(x)
                self.assertEqual(absx.precision, p)
                if p < 150:
                    self.assertNotEqual(x, absx)
                else:
                    self.assertEqual(x, absx)


def test_main():
    unittest.main()

if __name__ == '__main__':
    test_main()

import unittest
import operator
from bigfloat import *
import math

class BigFloatTests(unittest.TestCase):
    def assertIdenticalFloat(self, x, y):
        if not (isinstance(x, float) and isinstance(y, float)):
            raise ValueError("Expected x and y to be floats "
                             "in assertIdenticalFloat")
        if math.isnan(x) or math.isnan(y):
            if not math.isnan(x) and math.isnan(y):
                self.fail("One of x and y is a nan, but the other is not.")
        elif x == y == 0.0:
            if not math.copysign(1.0, x) == math.copysign(1.0, y):
                self.fail("Zeros have different signs")
        else:
            self.assertEqual(x, y)

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
        test_values = [-12.3456, -0.0, 0.0, 5e-310, -1e308,
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

        self.assert_(nan_p(BigFloat('nan')))
        self.assert_(inf_p(BigFloat('inf')))
        self.assert_(not signbit(BigFloat('inf')))
        self.assert_(inf_p(BigFloat('-inf')))
        self.assert_(signbit(BigFloat('-inf')))

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
        test_values = [-12.3456, -0.0, 0.0, 5e-310, -1e308,
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
            for test_rounding in [RoundTowardZero, RoundTowardNegative,
                                  RoundTowardPositive, RoundTiesToEven]:
                with precision(test_precision):
                    with rounding(test_rounding):
                        x = sqrt(2)
                y = BigFloat.exact(x)
                self.assertEqual(x, y)

        self.assertRaises(TypeError, BigFloat.exact, BigFloat(23), 100)

    def test_binary_operations(self):
        # check that BigFloats can be combined with themselves,
        # and with integers and floats, using the 6 standard
        # arithmetic operators:  +, -, *, /, **, %

        x = BigFloat('17.29')
        other_values = [2, 3L, 1.234, BigFloat('0.678')]
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

    def test_str(self):
        # check special values
        self.assertEqual(str(BigFloat(0)), '0')
        self.assertEqual(str(-BigFloat(0)), '-0')
        self.assertEqual(str(BigFloat('inf')), 'Infinity')
        self.assertEqual(str(BigFloat('-inf')), '-Infinity')
        self.assertEqual(str(BigFloat('nan')), 'NaN')


def test_main():
    unittest.main()

if __name__ == '__main__':
    test_main()

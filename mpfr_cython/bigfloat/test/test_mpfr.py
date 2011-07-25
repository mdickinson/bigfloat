# Copyright 2009--2011 Mark Dickinson.
#
# This file is part of the bigfloat module.
#
# The bigfloat module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat module is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat module.  If not, see <http://www.gnu.org/licenses/>.

import sys
import unittest

from bigfloat.mpfr import (
    MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD, MPFR_RNDA,

    Mpfr,

    mpfr_get_prec,
    mpfr_set_prec,

    mpfr_const_pi,
    mpfr_get_str,
    mpfr_set,
    mpfr_set_d,
    mpfr_get_d,
    mpfr_get_d_2exp,
    mpfr_set_si,
    mpfr_set_si_2exp,
    mpfr_get_si,
    mpfr_set_str,
    mpfr_strtofr,

    mpfr_set_nan,
    mpfr_set_inf,
    mpfr_set_zero,

    mpfr_swap,

    mpfr_fits_slong_p,

    mpfr_neg,

    mpfr_add,
    mpfr_sub,
    mpfr_mul,
    mpfr_sqr,
    mpfr_sqrt,
    mpfr_rec_sqrt,
    mpfr_cbrt,

    mpfr_div,
    mpfr_fmod,
    mpfr_pow,

    mpfr_inf_p,
    mpfr_nan_p,
    mpfr_zero_p,
    mpfr_signbit,
    
    mpfr_equal_p,
    mpfr_less_p,
    mpfr_lessequal_p,
    mpfr_greater_p,
    mpfr_greaterequal_p,

    mpfr_get_emin,
    mpfr_get_emin_min,
    mpfr_get_emin_max,
    mpfr_get_emax,
    mpfr_get_emax_min,
    mpfr_get_emax_max,

    mpfr_set_emin,
    mpfr_set_emax,

    mpfr_clear_underflow,
    mpfr_clear_overflow,
    mpfr_clear_nanflag,
    mpfr_clear_inexflag,
    mpfr_clear_erangeflag,

    mpfr_clear_flags,

    mpfr_set_underflow,
    mpfr_set_overflow,
    mpfr_set_nanflag,
    mpfr_set_inexflag,
    mpfr_set_erangeflag,

    mpfr_underflow_p,
    mpfr_overflow_p,
    mpfr_nanflag_p,
    mpfr_inexflag_p,
    mpfr_erangeflag_p,
)


class TestMpfr(unittest.TestCase):
    def setUp(self):
        mpfr_clear_flags()


    def test_bad_constructor(self):
        with self.assertRaises(TypeError):
            Mpfr()

        with self.assertRaises(TypeError):
            Mpfr("not a number")

        with self.assertRaises(TypeError):
            Mpfr(10, 11)

        with self.assertRaises(ValueError):
            Mpfr(1)

    def test_constructor(self):
        x = Mpfr(10)
        self.assertIsInstance(x, Mpfr)
        y = Mpfr(20L)
        self.assertIsInstance(y, Mpfr)

    def test_get_and_set_prec(self):
        x = Mpfr(10)
        self.assertEqual(mpfr_get_prec(x), 10)
        mpfr_set_prec(x, 20)
        self.assertEqual(mpfr_get_prec(x), 20)

    def test_get_d_and_set_d(self):
        x = Mpfr(53)
        mpfr_set_d(x, 1.2345, MPFR_RNDN)
        self.assertEqual(mpfr_get_d(x, MPFR_RNDN), 1.2345)

    def test_set_si_2exp(self):
        x = Mpfr(64)
        mpfr_set_si_2exp(x, 11, 5, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 352)

    def test_swap(self):
        x = Mpfr(17)
        y = Mpfr(23)
        mpfr_set_si(x, 56789, MPFR_RNDN)
        mpfr_set_si(y, 12345, MPFR_RNDN)
        mpfr_swap(x, y)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 12345)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 56789)
        self.assertEqual(mpfr_get_prec(x), 23)
        self.assertEqual(mpfr_get_prec(y), 17)

    def test_fits_slong_p(self):
        x = Mpfr(64)
        mpfr_set_si(x, sys.maxint, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), True)

        x = Mpfr(64)
        mpfr_set_si(x, -sys.maxint-1, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), True)

        x = Mpfr(28)
        mpfr_set_si(x, sys.maxint, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), False)

    def test_get_si_and_set_si(self):
        x = Mpfr(64)
        # Check roundtrip.
        mpfr_set_si(x, 2367, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 2367)

        # Check set_si from long
        mpfr_set_si(x, 5789L, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 5789)

        # Check set_si from out-of-range arguments.
        with self.assertRaises(OverflowError):
            mpfr_set_si(x, sys.maxint+1, MPFR_RNDN)

        with self.assertRaises(OverflowError):
            mpfr_set_si(x, -sys.maxint-2, MPFR_RNDN)

        # None of the above should have set the erange flag.
        self.assertIs(mpfr_erangeflag_p(), False)

        # Check get_si with out-of-range values.
        mpfr_set_inf(x, 0)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), sys.maxint)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_inf(x, -1)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), -sys.maxint-1)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_d(x, 1e100, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), sys.maxint)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_d(x, -1e100, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), -sys.maxint-1)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

    def test_none_argument(self):
        with self.assertRaises(TypeError):
            mpfr_const_pi(None, MPFR_RNDN)

    def test_const_pi(self):
        pi = Mpfr(10)
        mpfr_const_pi(pi, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, pi, MPFR_RNDN),
            ('31406', 1),
        )

    def test_set(self):
        x = Mpfr(30)
        y = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        mpfr_set(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            mpfr_get_str(10, 0, y, MPFR_RNDN),
        )
        # Invalid rounding mode.
        with self.assertRaises(ValueError):
            mpfr_set(y, x, -1)

    def test_neg(self):
        x = Mpfr(30)
        y = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        mpfr_neg(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, y, MPFR_RNDN),
            ('-31415926553', 1),
        )

    def test_add(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_add(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('18000000000', 2),
        )

    def test_sub(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_sub(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('-40000000000', 1),
        )

    def test_mul(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_mul(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('77000000000', 2),
        )

    def test_sqr(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23, MPFR_RNDN)
        mpfr_sqr(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23**2)

    def test_div(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_div(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('63636363670', 0),
        )

    def test_sqrt(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23**2, MPFR_RNDN)
        mpfr_sqrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23)

    def test_rec_sqrt(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23**2, MPFR_RNDN)
        mpfr_rec_sqrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_d(y, MPFR_RNDN), 0.043478260869565216)

    def test_cbrt(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23**3, MPFR_RNDN)
        mpfr_cbrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23)

    def test_fmod(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_fmod(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('70000000000', 1),
        )

    def test_pow(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_pow(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, z, MPFR_RNDN),
            ('19773267440', 10),
        )

    def test_equal_p(self):
        x = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertIs(
            mpfr_equal_p(x, x),
            True,
        )

    def test_lessequal_p(self):
        x = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertIs(
            mpfr_lessequal_p(x, x),
            True,
        )

    def test_less_p(self):
        x = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertIs(
            mpfr_less_p(x, x),
            False,
        )

    def test_greaterequal_p(self):
        x = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertIs(
            mpfr_greaterequal_p(x, x),
            True,
        )

    def test_greater_p(self):
        x = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertIs(
            mpfr_greater_p(x, x),
            False,
        )

    def test_set_d(self):
        x = Mpfr(30)
        mpfr_set_d(x, 0.1, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            ('99999999977', -1),
        )

    def test_set_nan(self):
        x = Mpfr(53)
        mpfr_set_nan(x)
        self.assertIs(mpfr_nan_p(x), True)

    def test_set_inf(self):
        x = Mpfr(53)
        mpfr_set_inf(x, 0)
        self.assertIs(mpfr_inf_p(x), True)
        self.assertIs(mpfr_signbit(x), False)

        mpfr_set_inf(x, 1)
        self.assertIs(mpfr_inf_p(x), True)
        self.assertIs(mpfr_signbit(x), False)

        mpfr_set_inf(x, -1)
        self.assertIs(mpfr_inf_p(x), True)
        self.assertIs(mpfr_signbit(x), True)

    def test_set_zero(self):
        x = Mpfr(53)
        mpfr_set_zero(x, 0)
        self.assertIs(mpfr_zero_p(x), True)
        self.assertIs(mpfr_signbit(x), False)

        mpfr_set_zero(x, 1)
        self.assertIs(mpfr_zero_p(x), True)
        self.assertIs(mpfr_signbit(x), False)

        mpfr_set_zero(x, -1)
        self.assertIs(mpfr_zero_p(x), True)
        self.assertIs(mpfr_signbit(x), True)

    def test_set_str(self):
        x = Mpfr(30)
        mpfr_set_str(x, '1.2345', 10, MPFR_RNDU)
        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            ('12345000003', 1),
        )
        mpfr_set_str(x, '1.2345', 10, MPFR_RNDD)
        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            ('12344999984', 1),
        )
        # Invalid base
        with self.assertRaises(ValueError):
            mpfr_set_str(x, '1.2345', 1, MPFR_RNDN)
        with self.assertRaises(ValueError):
            mpfr_set_str(x, '1.2345', 63, MPFR_RNDN)

    def test_strtofr(self):
        x = Mpfr(30)

        result, endindex = mpfr_strtofr(x, '135.6 789', 10, MPFR_RNDN)
        self.assertIn(result, (-1, 0, 1))
        self.assertEqual(endindex, 5)

        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            ('13559999990', 3),
        )

    def test_get_d_2exp(self):
        x = Mpfr(53)
        mpfr_set_d(x, 3.141592653589793, MPFR_RNDN)
        y, exp = mpfr_get_d_2exp(x, MPFR_RNDN)
        self.assertEqual(exp, 2)
        self.assertEqual(y, 0.7853981633974483)

    def test_get_str(self):
        x = Mpfr(20)
        mpfr_const_pi(x, MPFR_RNDN)

        # Invalid base
        with self.assertRaises(ValueError):
            print mpfr_get_str(1, 0, x, MPFR_RNDN)
        with self.assertRaises(ValueError):
            print mpfr_get_str(63, 0, x, MPFR_RNDN)

        # Invalid number of digits
        with self.assertRaises(ValueError):
            print mpfr_get_str(10, 1, x, MPFR_RNDN)
        with self.assertRaises((ValueError, OverflowError)):
            print mpfr_get_str(10, -1, x, MPFR_RNDN)

        # Bases other than 10
        x = Mpfr(20)
        mpfr_set_str(x, '64', 10, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(10, 2, x, MPFR_RNDN),
            ('64', 2),
        )
        self.assertEqual(
            mpfr_get_str(10, 0, x, MPFR_RNDN),
            ('64000000', 2),
        )
        self.assertEqual(
            mpfr_get_str(2, 0, x, MPFR_RNDN),
            ('10000000000000000000', 7),
        )
        self.assertEqual(
            mpfr_get_str(3, 0, x, MPFR_RNDN),
            ('21010000000000', 4),
        )
        self.assertEqual(
            mpfr_get_str(62, 0, x, MPFR_RNDN),
            ('12000', 2),
        )

    def test_rounding_modes(self):
        self.assertEqual(MPFR_RNDN, 0)
        self.assertIsInstance(MPFR_RNDZ, int)
        self.assertIsInstance(MPFR_RNDU, int)
        self.assertIsInstance(MPFR_RNDD, int)
        self.assertIsInstance(MPFR_RNDA, int)

    def test_exponent_bounds(self):
        # Just exercise the exponent bound functions.
        self.assertIsInstance(mpfr_get_emin(), (int, long))
        self.assertIsInstance(mpfr_get_emin_min(), (int, long))
        self.assertIsInstance(mpfr_get_emin_max(), (int, long))
        self.assertIsInstance(mpfr_get_emax(), (int, long))
        self.assertIsInstance(mpfr_get_emax_min(), (int, long))
        self.assertIsInstance(mpfr_get_emax_max(), (int, long))

        # Setting exponent bounds
        mpfr_set_emin(-56)
        self.assertEqual(mpfr_get_emin(), -56)

        mpfr_set_emax(777)
        self.assertEqual(mpfr_get_emax(), 777)

    def test_flags(self):
        # Exercise flag getting and setting methods.
        mpfr_set_overflow()
        self.assertIs(mpfr_overflow_p(), True)
        mpfr_clear_overflow()
        self.assertIs(mpfr_overflow_p(), False)

        mpfr_set_underflow()
        self.assertIs(mpfr_underflow_p(), True)
        mpfr_clear_underflow()
        self.assertIs(mpfr_underflow_p(), False)

        mpfr_set_nanflag()
        self.assertIs(mpfr_nanflag_p(), True)
        mpfr_clear_nanflag()
        self.assertIs(mpfr_nanflag_p(), False)

        mpfr_set_inexflag()
        self.assertIs(mpfr_inexflag_p(), True)
        mpfr_clear_inexflag()
        self.assertIs(mpfr_inexflag_p(), False)

        mpfr_set_erangeflag()
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()
        self.assertIs(mpfr_erangeflag_p(), False)




if __name__ == '__main__':
    unittest.main()

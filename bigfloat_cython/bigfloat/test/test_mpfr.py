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

    # Base extension type
    Mpfr_t,

    mpfr_initialized_p,

    # 5.1 Initialization Functions
    mpfr_init2,
    mpfr_inits2,
    mpfr_clear,
    mpfr_clears,
    mpfr_init,
    mpfr_inits,
    mpfr_set_default_prec,
    mpfr_get_default_prec,
    mpfr_set_prec,
    mpfr_get_prec,

    # 5.2 Assignment Functions
    mpfr_set,
    mpfr_set_si,
    mpfr_set_d,
    mpfr_set_si_2exp,
    mpfr_set_str,
    mpfr_strtofr,
    mpfr_set_nan,
    mpfr_set_inf,
    mpfr_set_zero,
    mpfr_swap,

    # 5.4 Conversion Functions
    mpfr_get_d,
    mpfr_get_si,
    mpfr_get_d_2exp,
    mpfr_get_str,
    mpfr_fits_slong_p,

    # 5.5 Basic Arithmetic Functions
    mpfr_add,
    mpfr_sub,
    mpfr_mul,
    mpfr_sqr,
    mpfr_div,
    mpfr_sqrt,
    mpfr_rec_sqrt,
    mpfr_cbrt,
    mpfr_root,
    mpfr_pow,
    mpfr_neg,
    mpfr_abs,
    mpfr_dim,

    # 5.6 Comparison Functions
    mpfr_cmp,
    mpfr_cmpabs,
    mpfr_nan_p,
    mpfr_inf_p,
    mpfr_number_p,
    mpfr_zero_p,
    mpfr_regular_p,
    mpfr_sgn,
    mpfr_greater_p,
    mpfr_greaterequal_p,
    mpfr_less_p,
    mpfr_lessequal_p,
    mpfr_equal_p,
    mpfr_lessgreater_p,
    mpfr_unordered_p,

    # 5.7 Special Functions
    mpfr_log,
    mpfr_log2,
    mpfr_log10,

    mpfr_exp,
    mpfr_exp2,
    mpfr_exp10,

    mpfr_cos,
    mpfr_sin,
    mpfr_tan,
    mpfr_sin_cos,
    mpfr_sec,
    mpfr_csc,
    mpfr_cot,
    mpfr_acos,
    mpfr_asin,
    mpfr_atan,

    mpfr_atan2,

    mpfr_cosh,
    mpfr_sinh,
    mpfr_tanh,
    mpfr_sinh_cosh,
    mpfr_sech,
    mpfr_csch,
    mpfr_coth,
    mpfr_acosh,
    mpfr_asinh,
    mpfr_atanh,

    mpfr_log1p,
    mpfr_expm1,
    mpfr_eint,
    mpfr_li2,
    mpfr_gamma,
    mpfr_lngamma,
    mpfr_digamma,
    mpfr_zeta,
    mpfr_erf,
    mpfr_erfc,
    mpfr_j0,
    mpfr_j1,
    mpfr_y0,
    mpfr_y1,

    mpfr_fma,
    mpfr_fms,
    mpfr_agm,
    mpfr_hypot,

    mpfr_ai,

    mpfr_const_log2,
    mpfr_const_pi,
    mpfr_const_euler,
    mpfr_const_catalan,
    mpfr_free_cache,

    # 5.10 Integer and Remainder Related Functions
    mpfr_rint,
    mpfr_ceil,
    mpfr_floor,
    mpfr_round,
    mpfr_trunc,

    mpfr_rint_ceil,
    mpfr_rint_floor,
    mpfr_rint_round,
    mpfr_rint_trunc,

    mpfr_frac,
    mpfr_modf,

    mpfr_fmod,
    mpfr_remainder,
    mpfr_remquo,
    mpfr_integer_p,

    # 5.11 Rounding Related Functions
    mpfr_set_default_rounding_mode,
    mpfr_get_default_rounding_mode,
    mpfr_prec_round,
    mpfr_can_round,
    mpfr_min_prec,
    mpfr_print_rnd_mode,

    mpfr_signbit,

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


# Factory function for creating and initializing Mpfr_t instances.
def Mpfr(precision):
    self = Mpfr_t()
    mpfr_init2(self, precision)
    return self


class TestMpfr(unittest.TestCase):
    def setUp(self):
        mpfr_clear_flags()

    def test_initialized_p(self):
        x = Mpfr_t()
        self.assertIs(mpfr_initialized_p(x), False)
        mpfr_init2(x, 53)
        self.assertIs(mpfr_initialized_p(x), True)
        mpfr_clear(x)
        self.assertIs(mpfr_initialized_p(x), False)

    def test_clear_on_uninitialized_instance(self):
        x = Mpfr_t()
        with self.assertRaises(ValueError):
            mpfr_clear(x)

        mpfr_init2(x, 53)
        mpfr_clear(x)
        with self.assertRaises(ValueError):
            mpfr_clear(x)

    def test_init2_on_already_initialized_instance(self):
        x = Mpfr_t()
        mpfr_init2(x, 53)
        with self.assertRaises(ValueError):
            mpfr_init2(x, 53)

    def test_init2_bad_precision(self):
        x = Mpfr_t()
        with self.assertRaises(ValueError):
            mpfr_init2(x, -2)

    def test_init(self):
        x = Mpfr_t()
        mpfr_init(x)
        self.assertEqual(
            mpfr_get_prec(x),
            mpfr_get_default_prec(),
        )

    def test_init_on_already_initialized_instance(self):
        x = Mpfr_t()
        mpfr_init(x)
        with self.assertRaises(ValueError):
            mpfr_init(x)

    def test_inits2_and_clears(self):
        args = [Mpfr_t() for _ in range(3)]
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), False)
        mpfr_inits2(123, *args)
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), True)
            self.assertEqual(mpfr_get_prec(arg), 123)
        mpfr_clears(*args)
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), False)

        # check bad precision
        with self.assertRaises(ValueError):
            mpfr_inits2(-2, *args)
        with self.assertRaises(ValueError):
            mpfr_inits2(-2)


    def test_inits_and_clears(self):
        args = [Mpfr_t() for _ in range(3)]
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), False)
        mpfr_inits(*args)
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), True)
            self.assertEqual(mpfr_get_prec(arg), mpfr_get_default_prec())
        mpfr_clears(*args)
        for arg in args:
            self.assertIs(mpfr_initialized_p(arg), False)

    def test_get_and_set_default_prec(self):
        old_default_prec = mpfr_get_default_prec()
        mpfr_set_default_prec(200)
        try:
            self.assertEqual(mpfr_get_default_prec(), 200)
        finally:
            mpfr_set_default_prec(old_default_prec)
        self.assertEqual(mpfr_get_default_prec(), old_default_prec)

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
        self.assertIsInstance(x, Mpfr_t)
        y = Mpfr(20L)
        self.assertIsInstance(y, Mpfr_t)

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

    def test_abs(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, -0.567, MPFR_RNDN)
        mpfr_abs(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.567,
        )
        mpfr_set_d(x, 0.123, MPFR_RNDN)
        mpfr_abs(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.123,
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

    def test_dim(self):
        x = Mpfr(30)
        y = Mpfr(30)
        z = Mpfr(30)
        mpfr_set_d(x, 7.0, MPFR_RNDN)
        mpfr_set_d(y, 11.0, MPFR_RNDN)
        mpfr_dim(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(z, MPFR_RNDN),
            0.0,
        )
        mpfr_dim(z, y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(z, MPFR_RNDN),
            4.0,
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

    def test_root(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, -(23**5), MPFR_RNDN)
        mpfr_root(y, x, 5, MPFR_RNDN)
        self.assertEqual(mpfr_get_d(y, MPFR_RNDN), -23.0)

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

    # 5.6 Comparison Functions

    def test_cmp(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 12, MPFR_RNDN)
        mpfr_set_si(y, 13, MPFR_RNDN)
        self.assertLess(mpfr_cmp(x, y), 0)
        self.assertEqual(mpfr_cmp(x, x), 0)
        self.assertGreater(mpfr_cmp(y, x), 0)

    def test_cmpabs(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 12, MPFR_RNDN)
        mpfr_set_si(y, -13, MPFR_RNDN)
        self.assertLess(mpfr_cmpabs(x, y), 0)
        self.assertEqual(mpfr_cmpabs(x, x), 0)
        self.assertGreater(mpfr_cmpabs(y, x), 0)

    def test_sgn(self):
        x = Mpfr(53)
        mpfr_set_si(x, 12, MPFR_RNDN)
        self.assertGreater(mpfr_sgn(x), 0)
        mpfr_set_si(x, -12, MPFR_RNDN)
        self.assertLess(mpfr_sgn(x), 0)
        mpfr_set_si(x, 0, MPFR_RNDN)
        self.assertEqual(mpfr_sgn(x), 0)

    def test_regular_p(self):
        x = Mpfr(53)
        mpfr_set_nan(x)
        self.assertIs(mpfr_regular_p(x), False)
        mpfr_set_inf(x, 1)
        self.assertIs(mpfr_regular_p(x), False)
        mpfr_set_zero(x, 1)
        self.assertIs(mpfr_regular_p(x), False)
        mpfr_set_si(x, 1, MPFR_RNDN)
        self.assertIs(mpfr_regular_p(x), True)

    def test_number_p(self):
        x = Mpfr(53)
        mpfr_set_nan(x)
        self.assertIs(mpfr_number_p(x), False)
        mpfr_set_inf(x, 1)
        self.assertIs(mpfr_number_p(x), False)
        mpfr_set_zero(x, 1)
        self.assertIs(mpfr_number_p(x), True)
        mpfr_set_si(x, 1, MPFR_RNDN)
        self.assertIs(mpfr_number_p(x), True)

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

    def test_lessgreater_p(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_si(x, 2, MPFR_RNDN)
        mpfr_set_nan(y)
        mpfr_set_inf(z, 1)
        self.assertIs(
            mpfr_lessgreater_p(x, x),
            False,
        )
        self.assertIs(
            mpfr_lessgreater_p(x, y),
            False,
        )
        self.assertIs(
            mpfr_lessgreater_p(x, z),
            True,
        )
        self.assertIs(
            mpfr_lessgreater_p(y, y),
            False,
        )
        self.assertIs(
            mpfr_lessgreater_p(y, z),
            False,
        )
        self.assertIs(
            mpfr_lessgreater_p(z, z),
            False,
        )

    def test_unordered_p(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_si(x, 2, MPFR_RNDN)
        mpfr_set_nan(y)
        mpfr_set_inf(z, 1)
        self.assertIs(
            mpfr_unordered_p(x, x),
            False,
        )
        self.assertIs(
            mpfr_unordered_p(x, y),
            True,
        )
        self.assertIs(
            mpfr_unordered_p(x, z),
            False,
        )
        self.assertIs(
            mpfr_unordered_p(y, y),
            True,
        )
        self.assertIs(
            mpfr_unordered_p(y, z),
            True,
        )
        self.assertIs(
            mpfr_unordered_p(z, z),
            False,
        )


    # 5.7 Special Functions
    def test_log(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_log(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.9878743481543455,
        )

    def test_log2(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_log2(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            2.867896463992655,
        )

    def test_log10(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_log10(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.8633228601204559,
        )

    def test_exp(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_exp(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1480.299927584545,
        )

    def test_exp2(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_exp2(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            157.58648490814926,
        )

    def test_exp10(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_exp10(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            19952623.149688788,
        )

    def test_cos(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_cos(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.52607751738110533998,
        )

    def test_sin(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_sin(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.850436620628564424067,
        )

    def test_tan(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_tan(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.616561423993499104376,
        )

    def test_sin_cos(self):
        # Check that sin_cos results are identical to those provided by sin and
        # cos independently (including the ternary values).
        op = Mpfr(53)
        sop = Mpfr(53)
        cop = Mpfr(53)
        sop_single = Mpfr(53)
        cop_single = Mpfr(53)

        # N.B.  All that's guaranteed by the docs about the ternary values is
        # that they're +ve, 0 or -ve as appropriate; the assertEqual below may
        # be a little too strong.
        test_values = [x / 100.0 for x in range(-100, 100)]
        for test_value in test_values:
            mpfr_set_d(op, test_value, MPFR_RNDN)

            st, ct = mpfr_sin_cos(sop, cop, op, MPFR_RNDN)
            st_single = mpfr_sin(sop_single, op, MPFR_RNDN)
            ct_single = mpfr_cos(cop_single, op, MPFR_RNDN)

            # Check ternary values.
            self.assertEqual(st, st_single)
            self.assertEqual(ct, ct_single)

            # Check sin and cos values.
            self.assertTrue(mpfr_equal_p(sop, sop_single))
            self.assertTrue(mpfr_equal_p(cop, cop_single))

    def test_sec(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_sec(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.90086055184063662072,
        )

    def test_csc(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_csc(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.17586657928828617564,
        )

    def test_cot(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_cot(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.6185969708033942509443,
        )

    def test_acos(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 0.625, MPFR_RNDN)
        mpfr_acos(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.895664793857864972022,
        )

    def test_asin(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 0.625, MPFR_RNDN)
        mpfr_asin(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.675131532937031647209,
        )

    def test_atan(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 0.625, MPFR_RNDN)
        mpfr_atan(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.558599315343562435972,
        )

    def test_atan2(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(x, 0.35, MPFR_RNDN)
        mpfr_set_d(y, 0.88, MPFR_RNDN)
        mpfr_atan2(z, y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(z, MPFR_RNDN),
            1.1922507314834034,
        )

    def test_cosh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_cosh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            740.15030156166007686,
        )

    def test_sinh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_sinh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            740.14962602288488302,
        )

    def test_tanh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_tanh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.99999908729514293447,
        )

    def test_sinh_cosh(self):
        # Check that sinh_cosh results are identical to those provided by sinh
        # and cosh independently (including the ternary values).
        op = Mpfr(53)
        sop = Mpfr(53)
        cop = Mpfr(53)
        sop_single = Mpfr(53)
        cop_single = Mpfr(53)

        # N.B.  All that's guaranteed by the docs about the ternary values is
        # that they're +ve, 0 or -ve as appropriate; the assertEqual below may
        # be a little too strong.
        test_values = [x / 100.0 for x in range(-100, 100)]
        for test_value in test_values:
            mpfr_set_d(op, test_value, MPFR_RNDN)

            st, ct = mpfr_sinh_cosh(sop, cop, op, MPFR_RNDN)
            st_single = mpfr_sinh(sop_single, op, MPFR_RNDN)
            ct_single = mpfr_cosh(cop_single, op, MPFR_RNDN)

            # Check ternary values.
            self.assertEqual(st, st_single)
            self.assertEqual(ct, ct_single)

            # Check sinh and cosh values.
            self.assertTrue(mpfr_equal_p(sop, sop_single))
            self.assertTrue(mpfr_equal_p(cop, cop_single))

    def test_sech(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_sech(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.0013510769338201674601516852324956868915,
        )

    def test_csch(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_csch(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.0013510781669557727158793600532906091079,
        )

    def test_coth(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 7.3, MPFR_RNDN)
        mpfr_coth(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.0000009127056900964470593240457667881,
        )

    def test_acosh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 1.3, MPFR_RNDN)
        mpfr_acosh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            0.75643291085695963970413518095370628592,
        )

    def test_asinh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 1.3, MPFR_RNDN)
        mpfr_asinh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.0784510589548970088022680582217889485,
        )

    def test_atanh(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 0.78, MPFR_RNDN)
        mpfr_atanh(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.0453705484668847151702051105754406143,
        )

    def test_miscellaneous_special_functions(self):
        triples = [
            (mpfr_log1p, 2.625, 1.2878542883066381),
            (mpfr_expm1, 2.625, 12.804574186067095),
            (mpfr_eint, 2.625, 7.7065767629369219),
            (mpfr_li2, 2.625, 2.3990452789082216),
            (mpfr_gamma, 2.625, 1.4569332050919717),
            (mpfr_lngamma, 2.625, 0.37633368202490544),
            (mpfr_digamma, 2.625, 0.76267585080804882),
            (mpfr_zeta, 2.625, 1.2972601932163248),
            (mpfr_erf, 2.625, 0.99979462426385878),
            (mpfr_erfc, 2.625, 0.00020537573614121744),
            (mpfr_j0, 2.625, -0.10848780856998129),
            (mpfr_j1, 2.625, 0.46377974664560533),
            (mpfr_y0, 2.625, 0.47649455655720157),
            (mpfr_y1, 2.625, 0.19848583551020473),
            (mpfr_ai, 2.625,  0.012735929874768289),
            ]

        rop = Mpfr(53)
        op = Mpfr(53)
        for fn, input, expected_output in triples:
            mpfr_set_d(op, input, MPFR_RNDN)
            fn(rop, op, MPFR_RNDN)
            actual_output = mpfr_get_d(rop, MPFR_RNDN)
            self.assertEqual(
                actual_output,
                expected_output,
                msg='{}'.format(fn),
            )

    def test_fma(self):
        op1 = Mpfr(53)
        op2 = Mpfr(53)
        op3 = Mpfr(53)
        rop = Mpfr(53)
        mpfr_set_d(op1, 5.0, MPFR_RNDN)
        mpfr_set_d(op2, 7.0, MPFR_RNDN)
        mpfr_set_d(op3, 11.0, MPFR_RNDN)
        mpfr_fma(rop, op1, op2, op3, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(rop, MPFR_RNDN),
            46.0,
        )

    def test_fms(self):
        op1 = Mpfr(53)
        op2 = Mpfr(53)
        op3 = Mpfr(53)
        rop = Mpfr(53)
        mpfr_set_d(op1, 5.0, MPFR_RNDN)
        mpfr_set_d(op2, 7.0, MPFR_RNDN)
        mpfr_set_d(op3, 11.0, MPFR_RNDN)
        mpfr_fms(rop, op1, op2, op3, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(rop, MPFR_RNDN),
            24.0,
        )

    def test_agm(self):
        x = Mpfr(53)
        y = Mpfr(53)
        rop = Mpfr(53)
        mpfr_set_d(x, 1.0, MPFR_RNDN)
        mpfr_set_d(y, 1.625, MPFR_RNDN)
        mpfr_agm(rop, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(rop, MPFR_RNDN),
            1.2935586022927736,
        )

    def test_hypot(self):
        x = Mpfr(53)
        y = Mpfr(53)
        rop = Mpfr(53)
        mpfr_set_d(x, 5.0, MPFR_RNDN)
        mpfr_set_d(y, 12.0, MPFR_RNDN)
        mpfr_hypot(rop, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(rop, MPFR_RNDN),
            13.0,
        )

    def test_const_log2(self):
        x = Mpfr(53)
        mpfr_const_log2(x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            0.69314718055994530941723212145817656808,
        )

    def test_const_pi(self):
        x = Mpfr(53)
        mpfr_const_pi(x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            3.1415926535897932384626433832795028842,
        )

    def test_const_euler(self):
        x = Mpfr(53)
        mpfr_const_euler(x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            0.57721566490153286060651209008240243104,
        )

    def test_const_catalan(self):
        x = Mpfr(53)
        mpfr_const_catalan(x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            0.91596559417721901505460351493238411077,
        )

    def test_free_cache(self):
        # It's awkward to test this; we settle for checking that the function
        # has been exported and is callable.
        mpfr_free_cache()


    # 5.10 Integer and Remainder Related Functions
    def test_rint(self):
        x = Mpfr(2)
        y = Mpfr(53)
        mpfr_set_d(y, 10.5, MPFR_RNDN)
        mpfr_rint(x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            12.0,
        )

    def test_rint_variants(self):
        rop = Mpfr(2)
        op = Mpfr(53)
        test_triples = [
            (mpfr_ceil, 8.5, 12.0),
            (mpfr_ceil, -8.5, -8.0),
            (mpfr_floor, 8.5, 8.0),
            (mpfr_floor, -8.5, -12.0),
            (mpfr_round, 10.0, 12.0),
            (mpfr_round, -10.0, -12.0),
            (mpfr_trunc, 11.5, 8.0),
            (mpfr_trunc, -11.5, -8.0),
        ]
        for fn, input, expected_output in test_triples:
            mpfr_set_d(op, input, MPFR_RNDN)
            fn(rop, op)
            actual_output = mpfr_get_d(rop, MPFR_RNDN)
            self.assertEqual(
                actual_output,
                expected_output,
                msg=(
                    "Unexpected result for {}({}): expected {}, "
                    "got {}.".format(
                        fn.__name__, input, expected_output, actual_output,
                    ),
                ),
            )

    def test_rint_round_variants(self):
        rop = Mpfr(2)
        op = Mpfr(53)
        test_triples = [
            (mpfr_rint_ceil, 8.5, 8.0),
            (mpfr_rint_ceil, -8.5, -8.0),
            (mpfr_rint_floor, 8.5, 8.0),
            (mpfr_rint_floor, -8.5, -8.0),
            (mpfr_rint_round, 10.0, 8.0),
            (mpfr_rint_round, -10.0, -8.0),
            (mpfr_rint_trunc, 11.5, 12.0),
            (mpfr_rint_trunc, -11.5, -12.0),
        ]
        for fn, input, expected_output in test_triples:
            mpfr_set_d(op, input, MPFR_RNDN)
            fn(rop, op, MPFR_RNDN)
            actual_output = mpfr_get_d(rop, MPFR_RNDN)
            self.assertEqual(
                actual_output,
                expected_output,
                msg=(
                    "Unexpected result for {}({}): expected {}, "
                    "got {}.".format(
                        fn.__name__, input, expected_output, actual_output,
                    ),
                ),
            )

    def test_frac(self):
        op = Mpfr(53)
        rop = Mpfr(53)
        mpfr_set_d(op, 123.45678, MPFR_RNDN)
        mpfr_frac(rop, op, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(rop, MPFR_RNDN),
            0.45677999999999486,
        )

    def test_modf(self):
        op = Mpfr(53)
        fracop = Mpfr(53)
        intop = Mpfr(53)
        fracop_single = Mpfr(53)
        intop_single = Mpfr(53)

        test_values = [
            1.0,
            1.23,
            1e-100,
            1e100,
            15.78,
            -1.56,
            float('inf'),
            float('nan'),
        ]
        for test_value in test_values:
            mpfr_set_d(op, test_value, MPFR_RNDN)

            it, ft = mpfr_modf(intop, fracop, op, MPFR_RNDN)
            it_single = mpfr_rint_trunc(intop_single, op, MPFR_RNDN)
            ft_single = mpfr_frac(fracop_single, op, MPFR_RNDN)

            # Check ternary values.
            self.assertEqual(it, it_single)
            self.assertEqual(ft, ft_single)

            # Check trunc and cos values.
            self.assertTrue(mpfr_equal_p(intop, intop_single) or
                            mpfr_nan_p(intop) and mpfr_nan_p(intop_single))
            self.assertTrue(mpfr_equal_p(fracop, fracop_single) or
                            mpfr_nan_p(fracop) and mpfr_nan_p(fracop_single))

    def test_fmod(self):
        r = Mpfr(53)
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 9.0, MPFR_RNDN)
        mpfr_set_d(y, 3.1415926535897931, MPFR_RNDN)
        mpfr_fmod(r, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(r, MPFR_RNDN),
            2.7168146928204138,
        )

    def test_remainder(self):
        r = Mpfr(53)
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 9.0, MPFR_RNDN)
        mpfr_set_d(y, 3.1415926535897931, MPFR_RNDN)
        mpfr_remainder(r, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(r, MPFR_RNDN),
            -0.42477796076937935,
        )

    def test_remquo(self):
        r = Mpfr(53)
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(x, 9.0, MPFR_RNDN)
        mpfr_set_d(y, 3.1415926535897931, MPFR_RNDN)
        ternary, quotient = mpfr_remquo(r, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(r, MPFR_RNDN),
            -0.42477796076937935,
        )
        # Result should be exact.
        self.assertEqual(ternary, 0)
        self.assertEqual(quotient, 3)

    def test_integer_p(self):
        non_integers = [5.3, 1e-100, float('nan'), float('-inf')]
        integers = [2.0, -0.0, 1e100]

        x = Mpfr(53)
        for non_integer in non_integers:
            mpfr_set_d(x, non_integer, MPFR_RNDN)
            self.assertIs(
                mpfr_integer_p(x),
                False,
            )
        for integer in integers:
            mpfr_set_d(x, integer, MPFR_RNDN)
            self.assertIs(
                mpfr_integer_p(x),
                True,
            )

    # 5.11 Rounding Related Functions
    def test_get_and_set_default_rounding_mode(self):
        old_default_rounding_mode = mpfr_get_default_rounding_mode()
        mpfr_set_default_rounding_mode(MPFR_RNDZ)
        try:
            self.assertEqual(mpfr_get_default_rounding_mode(), MPFR_RNDZ)
        finally:
            mpfr_set_default_rounding_mode(old_default_rounding_mode)
        self.assertEqual(
            mpfr_get_default_rounding_mode(),
            old_default_rounding_mode,
        )

    def test_prec_round(self):
        x = Mpfr_t()
        mpfr_init2(x, 100)
        mpfr_set_d(x, 5.123, MPFR_RNDN)
        mpfr_prec_round(x, 200, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            5.123,
        )
        self.assertEqual(mpfr_get_prec(x), 200)
        mpfr_prec_round(x, 3, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            5.0,
        )
        self.assertEqual(mpfr_get_prec(x), 3)

    def test_min_prec(self):
        x = Mpfr_t()
        mpfr_init2(x, 53)
        mpfr_set_d(x, 5.0, MPFR_RNDN)
        self.assertEqual(mpfr_min_prec(x), 3)

    def test_can_round(self):
        # Example: we have an (very good) approximation b = 24.5 of some value
        # x, and we need to know x to 5 bits.
        b = Mpfr_t()
        mpfr_init2(b, 53)
        mpfr_set_d(b, 24.5, MPFR_RNDN)
        # Here we can't round to nearest, since we don't know whether to round
        # to 24 or 25.
        self.assertIs(
            mpfr_can_round(b, 1000, MPFR_RNDN, MPFR_RNDN, 5),
            False,
        )
        # But we can round down safely.
        self.assertIs(
            mpfr_can_round(b, 1000, MPFR_RNDN, MPFR_RNDZ, 5),
            True,
        )
        # We can also round to nearest safely if the original value 24.5 was
        # the result of a rounding up ...
        self.assertIs(
            mpfr_can_round(b, 1000, MPFR_RNDU, MPFR_RNDN, 5),
            True,
        )
        # ... but not if it was the result of a rounding down ...
        self.assertIs(
            mpfr_can_round(b, 1000, MPFR_RNDD, MPFR_RNDN, 5),
            False,
        )

    def test_print_rnd_mode(self):
        self.assertEqual(mpfr_print_rnd_mode(MPFR_RNDN), 'MPFR_RNDN')
        self.assertEqual(mpfr_print_rnd_mode(MPFR_RNDD), 'MPFR_RNDD')
        self.assertEqual(mpfr_print_rnd_mode(MPFR_RNDU), 'MPFR_RNDU')
        self.assertEqual(mpfr_print_rnd_mode(MPFR_RNDZ), 'MPFR_RNDZ')
        self.assertEqual(mpfr_print_rnd_mode(MPFR_RNDA), 'MPFR_RNDA')



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

    def test_get_and_set_emin(self):
        # Setting exponent bounds
        old_emin = mpfr_get_emin()
        mpfr_set_emin(-56)
        try:
            self.assertEqual(mpfr_get_emin(), -56)
        finally:
            mpfr_set_emin(old_emin)
        self.assertEqual(mpfr_get_emin(), old_emin)

    def test_get_and_set_emax(self):
        old_emax = mpfr_get_emax()
        mpfr_set_emax(777)
        try:
            self.assertEqual(mpfr_get_emax(), 777)
        finally:
            mpfr_set_emax(old_emax)
        self.assertEqual(mpfr_get_emax(), old_emax)

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

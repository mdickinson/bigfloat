# Copyright 2009--2014 Mark Dickinson.
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

import contextlib
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mpfr import (
    _LONG_MIN, _LONG_MAX,

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

    mpfr_fac_ui,

    mpfr_log1p,
    mpfr_expm1,
    mpfr_eint,
    mpfr_li2,
    mpfr_gamma,
    mpfr_lngamma,
    mpfr_lgamma,
    mpfr_digamma,
    mpfr_zeta,
    mpfr_zeta_ui,
    mpfr_erf,
    mpfr_erfc,
    mpfr_j0,
    mpfr_j1,
    mpfr_jn,
    mpfr_y0,
    mpfr_y1,
    mpfr_yn,

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

    # 5.12 Miscellaneous Functions
    mpfr_nexttoward,
    mpfr_nextabove,
    mpfr_nextbelow,
    mpfr_min,
    mpfr_max,
    mpfr_get_exp,
    mpfr_set_exp,
    mpfr_signbit,
    mpfr_setsign,
    mpfr_copysign,
    mpfr_get_version,
    MPFR_VERSION,
    MPFR_VERSION_MAJOR,
    MPFR_VERSION_MINOR,
    MPFR_VERSION_PATCHLEVEL,
    MPFR_VERSION_STRING,
    MPFR_VERSION_NUM,
    mpfr_get_patches,
    mpfr_buildopt_tls_p,
    mpfr_buildopt_decimal_p,

    # 5.13 Exception Related Functions
    mpfr_get_emin,
    mpfr_get_emax,

    mpfr_set_emin,
    mpfr_set_emax,

    mpfr_get_emin_min,
    mpfr_get_emin_max,
    mpfr_get_emax_min,
    mpfr_get_emax_max,

    mpfr_check_range,
    mpfr_subnormalize,

    mpfr_clear_underflow,
    mpfr_clear_overflow,
    mpfr_clear_nanflag,
    mpfr_clear_inexflag,
    mpfr_clear_erangeflag,

    mpfr_set_underflow,
    mpfr_set_overflow,
    mpfr_set_nanflag,
    mpfr_set_inexflag,
    mpfr_set_erangeflag,

    mpfr_clear_flags,

    mpfr_underflow_p,
    mpfr_overflow_p,
    mpfr_nanflag_p,
    mpfr_inexflag_p,
    mpfr_erangeflag_p,
)


# Context manager for making a temporary change to emin.
@contextlib.contextmanager
def temporary_emin(emin):
    old_emin = mpfr_get_emin()
    mpfr_set_emin(emin)
    try:
        yield
    finally:
        mpfr_set_emin(old_emin)


# Context manager for making a temporary change to emax.
@contextlib.contextmanager
def temporary_emax(emax):
    old_emax = mpfr_get_emax()
    mpfr_set_emax(emax)
    try:
        yield
    finally:
        mpfr_set_emax(old_emax)


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
        y = Mpfr(20)
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
        mpfr_set_si(x, _LONG_MAX, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), True)

        x = Mpfr(64)
        mpfr_set_si(x, _LONG_MIN, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), True)

        x = Mpfr(28)
        mpfr_set_si(x, _LONG_MAX, MPFR_RNDN)
        self.assertIs(mpfr_fits_slong_p(x, MPFR_RNDN), False)

    def test_get_si_and_set_si(self):
        x = Mpfr(64)
        # Check roundtrip.
        mpfr_set_si(x, 2367, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 2367)

        # Check set_si from long
        mpfr_set_si(x, 5789, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), 5789)

        # Check set_si from out-of-range arguments.
        with self.assertRaises(OverflowError):
            mpfr_set_si(x, _LONG_MAX + 1, MPFR_RNDN)

        with self.assertRaises(OverflowError):
            mpfr_set_si(x, _LONG_MIN - 1, MPFR_RNDN)

        # None of the above should have set the erange flag.
        self.assertIs(mpfr_erangeflag_p(), False)

        # Check get_si with out-of-range values.
        mpfr_set_inf(x, 0)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), _LONG_MAX)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_inf(x, -1)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), _LONG_MIN)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_d(x, 1e100, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), _LONG_MAX)
        self.assertIs(mpfr_erangeflag_p(), True)
        mpfr_clear_erangeflag()

        mpfr_set_d(x, -1e100, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(x, MPFR_RNDN), _LONG_MIN)
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
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23 ** 2)

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
        mpfr_set_si(x, 23 ** 2, MPFR_RNDN)
        mpfr_sqrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23)

    def test_rec_sqrt(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23 ** 2, MPFR_RNDN)
        mpfr_rec_sqrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_d(y, MPFR_RNDN), 0.043478260869565216)

    def test_cbrt(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, 23 ** 3, MPFR_RNDN)
        mpfr_cbrt(y, x, MPFR_RNDN)
        self.assertEqual(mpfr_get_si(y, MPFR_RNDN), 23)

    def test_root(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_si(x, -(23 ** 5), MPFR_RNDN)
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

    def test_fac_ui(self):
        x = Mpfr(53)
        mpfr_fac_ui(x, 4, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            24.0,
        )
        mpfr_fac_ui(x, 5, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            120.0,
        )
        mpfr_fac_ui(x, 6, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            720.0,
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
                msg='{0}'.format(fn),
            )

    def test_lgamma(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(x, 2.625, MPFR_RNDN)
        ternary, sign = mpfr_lgamma(y, x, MPFR_RNDN)
        mpfr_lngamma(z, x, MPFR_RNDN)
        self.assertEqual(sign, 1)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            mpfr_get_d(z, MPFR_RNDN),
        )

        # Negative value
        mpfr_set_d(x, -0.5, MPFR_RNDN)
        ternary, sign = mpfr_lgamma(y, x, MPFR_RNDN)
        self.assertEqual(sign, -1)
        self.assertEqual(
            mpfr_get_d(y, MPFR_RNDN),
            1.2655121234846454,  # log(2 * sqrt(pi))
        )

    def test_zeta_ui(self):
        x = Mpfr(53)
        mpfr_zeta_ui(x, 0, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            -0.5,
        )
        mpfr_zeta_ui(x, 1, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            float('inf'),
        )
        mpfr_zeta_ui(x, 2, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            1.6449340668482264,
        )

    def test_jn(self):
        # Just check that n = 0 and n = 1 cases correspond to what we already
        # have.
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(z, 2.3456, MPFR_RNDN)

        mpfr_j0(x, z, MPFR_RNDN)
        mpfr_jn(y, 0, z, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            mpfr_get_d(y, MPFR_RNDN),
        )
        mpfr_j1(x, z, MPFR_RNDN)
        mpfr_jn(y, 1, z, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            mpfr_get_d(y, MPFR_RNDN),
        )

    def test_yn(self):
        # Just check that n = 0 and n = 1 cases correspond to what we already
        # have.
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(z, 2.3456, MPFR_RNDN)

        mpfr_y0(x, z, MPFR_RNDN)
        mpfr_yn(y, 0, z, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            mpfr_get_d(y, MPFR_RNDN),
        )
        mpfr_y1(x, z, MPFR_RNDN)
        mpfr_yn(y, 1, z, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            mpfr_get_d(y, MPFR_RNDN),
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
                    "Unexpected result for {0}({1}): expected {2}, "
                    "got {3}.".format(
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
                    "Unexpected result for {0}({1}): expected {2}, "
                    "got {3}.".format(
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
        with self.assertRaises(ValueError):
            mpfr_print_rnd_mode(-1)

        # Check that we get a 'str' instance on both Python 2 and Python 3.
        self.assertIsInstance(mpfr_print_rnd_mode(MPFR_RNDN), str)

    # 5.12 Miscellaneous Functions
    def test_nexttoward(self):
        x = Mpfr(4)
        y = Mpfr(53)

        mpfr_set_d(x, 2.0, MPFR_RNDN)
        mpfr_set_d(y, 2.001, MPFR_RNDN)
        mpfr_nexttoward(x, y)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            2.25,
        )

        mpfr_set_d(x, 2.0, MPFR_RNDN)
        mpfr_set_d(y, -1.3, MPFR_RNDN)
        mpfr_nexttoward(x, y)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            1.875,
        )

    def test_nextabove(self):
        x = Mpfr(4)
        mpfr_set_d(x, 1.0, MPFR_RNDN)
        mpfr_nextabove(x)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            1.125,
        )

    def test_nextbelow(self):
        x = Mpfr(4)
        mpfr_set_d(x, 1.0, MPFR_RNDN)
        mpfr_nextbelow(x)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            0.9375,
        )

    def test_get_exp(self):
        x = Mpfr(34)
        mpfr_set_d(x, 0.516, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_exp(x),
            0,
        )
        mpfr_set_d(x, 8.0, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_exp(x),
            4,
        )
        mpfr_set_d(x, 1e-9, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_exp(x),
            -29,
        )

    def test_set_exp(self):
        x = Mpfr(53)
        mpfr_set_d(x, 48.0, MPFR_RNDN)
        old_exp = mpfr_get_exp(x)
        mpfr_set_exp(x, -1)
        self.assertEqual(
            mpfr_get_exp(x),
            -1,
        )
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            0.375,
        )
        mpfr_set_exp(x, old_exp)
        self.assertEqual(
            mpfr_get_exp(x),
            old_exp,
        )
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            48.0,
        )

    def test_min_and_max(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(x, 1.2, MPFR_RNDN)
        mpfr_set_d(y, 1.3, MPFR_RNDN)
        mpfr_min(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(z, MPFR_RNDN),
            1.2,
        )
        mpfr_max(z, x, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(z, MPFR_RNDN),
            1.3,
        )

    def test_signbit(self):
        x = Mpfr(53)
        mpfr_set_d(x, 24.5, MPFR_RNDN)
        self.assertIs(mpfr_signbit(x), False)
        mpfr_set_d(x, -12.3, MPFR_RNDN)
        self.assertIs(mpfr_signbit(x), True)

    def test_setsign(self):
        x = Mpfr(53)
        y = Mpfr(53)
        mpfr_set_d(y, 24.5, MPFR_RNDN)

        mpfr_setsign(x, y, False, MPFR_RNDN)
        self.assertIs(mpfr_signbit(x), False)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            24.5,
        )
        mpfr_setsign(x, y, True, MPFR_RNDN)
        self.assertIs(mpfr_signbit(x), True)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            -24.5,
        )

    def test_copysign(self):
        x = Mpfr(53)
        y = Mpfr(53)
        z = Mpfr(53)
        mpfr_set_d(y, 24.5, MPFR_RNDN)
        mpfr_set_d(z, -12.3, MPFR_RNDN)
        mpfr_copysign(x, y, z, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            -24.5,
        )
        mpfr_copysign(x, z, y, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_d(x, MPFR_RNDN),
            12.3,
        )

    def test_MPFR_VERSION(self):
        major = MPFR_VERSION_MAJOR
        minor = MPFR_VERSION_MINOR
        patchlevel = MPFR_VERSION_PATCHLEVEL
        num = MPFR_VERSION_NUM(major, minor, patchlevel)
        self.assertEqual(num, MPFR_VERSION)

    def test_MPFR_VERSION_STRING(self):
        self.assertIsInstance(MPFR_VERSION_STRING, str)

    def test_get_version(self):
        self.assertIsInstance(mpfr_get_version(), str)
        self.assertEqual(mpfr_get_version(), MPFR_VERSION_STRING)

    def test_get_patches(self):
        self.assertIsInstance(mpfr_get_patches(), list)
        for patch in mpfr_get_patches():
            self.assertIsInstance(patch, str)

    def test_buildopt_tls_p(self):
        self.assertIsInstance(mpfr_buildopt_tls_p(), bool)

    def test_buildopt_decimal_p(self):
        self.assertIsInstance(mpfr_buildopt_decimal_p(), bool)

    # 5.13 Exception Related Functions
    def test_check_range(self):
        # Make some tests with precision 3 and exponent range (0, 4).  With
        # this format, the largest representable finite number is 14, and the
        # smallest is 0.5.
        inf = float('inf')
        test_data = [
            ((14.0, 1, MPFR_RNDN), (14.0, 1, 'inexflag')),
            ((14.0, 0, MPFR_RNDN), (14.0, 0, '')),
            ((14.0, -1, MPFR_RNDN), (14.0, -1, 'inexflag')),
            ((16.0, 1, MPFR_RNDN), (inf, 1, 'inexflag overflow')),
            ((16.0, 0, MPFR_RNDN), (inf, 1, 'inexflag overflow')),
            ((16.0, -1, MPFR_RNDN), (inf, 1, 'inexflag overflow')),
            ((20.0, 1, MPFR_RNDN), (inf, 1, 'inexflag overflow')),

            ((14.0, 1, MPFR_RNDU), (14.0, 1, 'inexflag')),
            ((14.0, 0, MPFR_RNDU), (14.0, 0, '')),
            ((16.0, 1, MPFR_RNDU), (inf, 1, 'inexflag overflow')),
            ((16.0, 0, MPFR_RNDU), (inf, 1, 'inexflag overflow')),
            ((20.0, 1, MPFR_RNDU), (inf, 1, 'inexflag overflow')),

            ((12.0, -1, MPFR_RNDD), (12.0, -1, 'inexflag')),
            ((14.0, 0, MPFR_RNDD), (14.0, 0, '')),
            ((14.0, -1, MPFR_RNDD), (14.0, -1, 'inexflag')),
            ((16.0, 0, MPFR_RNDD), (14.0, -1, 'inexflag overflow')),
            ((16.0, -1, MPFR_RNDD), (14.0, -1, 'inexflag overflow')),

            ((0.25, 1, MPFR_RNDN), (0, -1, 'underflow inexflag')),
            ((0.25, 0, MPFR_RNDN), (0, -1, 'underflow inexflag')),
            ((0.25, -1, MPFR_RNDN), (0.5, 1, 'underflow inexflag')),
            ((0.4375, 1, MPFR_RNDN), (0.5, 1, 'underflow inexflag')),
            ((0.4375, 0, MPFR_RNDN), (0.5, 1, 'underflow inexflag')),
            ((0.4375, -1, MPFR_RNDN), (0.5, 1, 'underflow inexflag')),
            ((0.5, 1, MPFR_RNDN), (0.5, 1, 'inexflag')),
            ((0.5, 0, MPFR_RNDN), (0.5, 0, '')),
            ((0.5, -1, MPFR_RNDN), (0.5, -1, 'inexflag')),

            ((0.4375, 1, MPFR_RNDU), (0.5, 1, 'underflow inexflag')),
            ((0.4375, 0, MPFR_RNDU), (0.5, 1, 'underflow inexflag')),
            ((0.5, 1, MPFR_RNDU), (0.5, 1, 'inexflag')),
            ((0.5, 0, MPFR_RNDU), (0.5, 0, '')),

            ((0.4375, 0, MPFR_RNDD), (0, -1, 'underflow inexflag')),
            ((0.4375, -1, MPFR_RNDD), (0, -1, 'underflow inexflag')),
            ((0.5, 0, MPFR_RNDD), (0.5, 0, '')),
            ((0.5, -1, MPFR_RNDD), (0.5, -1, 'inexflag')),
        ]

        flag_testers = {
            'underflow': mpfr_underflow_p,
            'inexflag': mpfr_inexflag_p,
            'overflow': mpfr_overflow_p,
            'nanflag': mpfr_nanflag_p,
            'erangeflag': mpfr_erangeflag_p,
        }

        def get_current_flags():
            flags = set()
            for flag, tester in flag_testers.items():
                if tester():
                    flags.add(flag)
            return flags

        x = Mpfr(3)
        for inputs, outputs in test_data:
            val_in, ternary_in, rnd = inputs
            val_out, ternary_out, flags = outputs
            # All test values should be exactly representable in 4 bits.
            t = mpfr_set_d(x, val_in, MPFR_RNDN)
            assert t == 0
            with temporary_emax(4):
                with temporary_emin(0):
                    mpfr_clear_flags()
                    actual_ternary_out = mpfr_check_range(x, ternary_in, rnd)
                    actual_flags = get_current_flags()
                    actual_val_out = mpfr_get_d(x, MPFR_RNDN)
            self.assertEqual(actual_val_out, val_out)
            self.assertEqual(actual_ternary_out, ternary_out)
            self.assertEqual(actual_flags, set(flags.split()))

    def test_subnormalize(self):
        # Tests with precision 3 and emin 0.

        # With this precision and exponent range, and gradual underflow, the
        # representable finite positive numbers are, in order:
        #
        #   0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0,
        #   8.0, 10.0, 12.0, 14.0, ...
        #
        # Here only 0.5, 1.0 and 1.5 are subnormal.

        # Note that mpfr_subnormalize expects that the exponent of the
        # given number is already in the range [emin, emax].

        # Underflow flag should be set for all values that would round to
        # something less than 2 with unbounded exponent range; that's
        # everything that's strictly less than 1.875.

        test_data = [
            # Exact result in the range [0, 0.25]
            ((0.0, 0, MPFR_RNDN), (0.0, 0, '')),
            # Hmm.  Apparently MPFR doesn't set the underflow flag for the case
            # below.  Bug?  Probably not a problem in practice, since a normal
            # function producing the result 0.0 with ternary value -1 will
            # already have set the underflow flag.
            ((0.0, -1, MPFR_RNDN), (0.0, -1, 'inexflag')),

            # Exact result in the range (0.25, 0.5625]
            ((0.5, 1, MPFR_RNDN), (0.5, 1, 'inexflag underflow')),
            ((0.5, 0, MPFR_RNDN), (0.5, 0, 'underflow')),
            ((0.5, -1, MPFR_RNDN), (0.5, -1, 'inexflag underflow')),

            # Exact result in the range (0.5625, 0.6875)
            ((0.625, 1, MPFR_RNDN), (0.5, -1, 'inexflag underflow')),
            ((0.625, 0, MPFR_RNDN), (0.5, -1, 'inexflag underflow')),
            ((0.625, -1, MPFR_RNDN), (0.5, -1, 'inexflag underflow')),

            # Exact result in the range [0.6875, 0.8125]
            ((0.75, 1, MPFR_RNDN), (0.5, -1, 'inexflag underflow')),
            ((0.75, 0, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),
            ((0.75, -1, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),

            # Exact result in the range (0.8125, 0.9375)
            ((0.875, 1, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),
            ((0.875, 0, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),
            ((0.875, -1, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),

            # Exact result in the range [0.9375, 1.125]
            ((1.0, 1, MPFR_RNDN), (1.0, 1, 'inexflag underflow')),
            ((1.0, 0, MPFR_RNDN), (1.0, 0, 'underflow')),
            ((1.0, -1, MPFR_RNDN), (1.0, -1, 'inexflag underflow')),

            # Exact result in the range (1.125, 1.375)
            ((1.25, 1, MPFR_RNDN), (1.0, -1, 'inexflag underflow')),
            ((1.25, 0, MPFR_RNDN), (1.0, -1, 'inexflag underflow')),
            ((1.25, -1, MPFR_RNDN), (1.5, 1, 'inexflag underflow')),

            # Exact result in the range [1.375, 1.625]
            ((1.25, 1, MPFR_RNDN), (1.0, -1, 'inexflag underflow')),
            ((1.25, 0, MPFR_RNDN), (1.0, -1, 'inexflag underflow')),
            ((1.25, -1, MPFR_RNDN), (1.5, 1, 'inexflag underflow')),

            # Exact result in the range (1.625, 1.875)
            ((1.75, 1, MPFR_RNDN), (1.5, -1, 'inexflag underflow')),
            ((1.75, 0, MPFR_RNDN), (2.0, 1, 'inexflag underflow')),
            ((1.75, -1, MPFR_RNDN), (2.0, 1, 'inexflag underflow')),

            # Exact result in the range [1.875, 2.25]
            ((2.0, 1, MPFR_RNDN), (2.0, 1, 'inexflag')),
            ((2.0, 0, MPFR_RNDN), (2.0, 0, '')),
            ((2.0, -1, MPFR_RNDN), (2.0, -1, 'inexflag')),
        ]

        flag_testers = {
            'underflow': mpfr_underflow_p,
            'inexflag': mpfr_inexflag_p,
            'overflow': mpfr_overflow_p,
            'nanflag': mpfr_nanflag_p,
            'erangeflag': mpfr_erangeflag_p,
        }

        def get_current_flags():
            flags = set()
            for flag, tester in flag_testers.items():
                if tester():
                    flags.add(flag)
            return flags

        x = Mpfr(3)
        for inputs, outputs in test_data:
            val_in, ternary_in, rnd = inputs
            val_out, ternary_out, flags = outputs
            # All test values should be exactly representable in 4 bits.
            t = mpfr_set_d(x, val_in, MPFR_RNDN)
            assert t == 0
            with temporary_emin(0):
                mpfr_clear_flags()
                actual_ternary_out = mpfr_subnormalize(x, ternary_in, rnd)
                # Normalize return value from mpfr_subnormalize to -1, 0 or 1.
                if actual_ternary_out < 0:
                    actual_ternary_out = -1
                elif actual_ternary_out > 0:
                    actual_ternary_out = 1
                actual_flags = get_current_flags()
                actual_val_out = mpfr_get_d(x, MPFR_RNDN)
            self.assertEqual(actual_val_out, val_out)
            self.assertEqual(actual_ternary_out, ternary_out)
            self.assertEqual(actual_flags, set(flags.split()))

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
            mpfr_get_str(1, 0, x, MPFR_RNDN)
        with self.assertRaises(ValueError):
            mpfr_get_str(63, 0, x, MPFR_RNDN)

        # Invalid number of digits
        with self.assertRaises(ValueError):
            mpfr_get_str(10, 1, x, MPFR_RNDN)
        with self.assertRaises((ValueError, OverflowError)):
            mpfr_get_str(10, -1, x, MPFR_RNDN)

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

        # Type of result.
        digits, exp = mpfr_get_str(10, 0, x, MPFR_RNDN)
        self.assertIsInstance(digits, str)
        self.assertIsInstance(exp, int)

    def test_rounding_modes(self):
        self.assertEqual(MPFR_RNDN, 0)
        self.assertIsInstance(MPFR_RNDZ, int)
        self.assertIsInstance(MPFR_RNDU, int)
        self.assertIsInstance(MPFR_RNDD, int)
        self.assertIsInstance(MPFR_RNDA, int)

    def test_exponent_bounds(self):
        # Just exercise the exponent bound functions.
        self.assertIsInstance(mpfr_get_emin(), int)
        self.assertIsInstance(mpfr_get_emin_min(), int)
        self.assertIsInstance(mpfr_get_emin_max(), int)
        self.assertIsInstance(mpfr_get_emax(), int)
        self.assertIsInstance(mpfr_get_emax_min(), int)
        self.assertIsInstance(mpfr_get_emax_max(), int)

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

    def test_limits(self):
        # Regression test for badly-defined LONG_MAX and LONG_MIN.
        self.assertGreaterEqual(_LONG_MAX, 2**31-1)
        self.assertLessEqual(_LONG_MIN, -2**31)


if __name__ == '__main__':
    unittest.main()

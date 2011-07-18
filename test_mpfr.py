import unittest

from mpfr import (
    MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD,
    MPFR_RNDA, MPFR_RNDF, MPFR_RNDNA,

    Mpfr,

    mpfr_const_pi,
    mpfr_get_str,
    mpfr_set,
    mpfr_set_d,
    mpfr_set_str,
    mpfr_strtofr,

    mpfr_neg,

    mpfr_add,
    mpfr_sub,
    mpfr_mul,
    mpfr_div,
    mpfr_fmod,

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
        self.assertEqual(MPFR_RNDNA, -1)
        self.assertIsInstance(MPFR_RNDZ, int)
        self.assertIsInstance(MPFR_RNDU, int)
        self.assertIsInstance(MPFR_RNDD, int)
        self.assertIsInstance(MPFR_RNDA, int)
        self.assertIsInstance(MPFR_RNDF, int)

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

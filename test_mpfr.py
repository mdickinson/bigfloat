import unittest

from mpfr import (
    MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD,
    MPFR_RNDA, MPFR_RNDF, MPFR_RNDNA,

    Mpfr,

    mpfr_const_pi,
    mpfr_get_str,
    mpfr_set,
    mpfr_set_d,
)


class TestMpfr(unittest.TestCase):
    def test_bad_constructor(self):
        with self.assertRaises(TypeError):
            Mpfr()

        with self.assertRaises(TypeError):
            Mpfr("not a number")

        with self.assertRaises(TypeError):
            Mpfr(10, 11)


    def test_none_argument(self):
        with self.assertRaises(TypeError):
            mpfr_const_pi(None, 0)

    def test_const_pi(self):
        pi = Mpfr(10)
        mpfr_const_pi(pi, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(pi),
            ('31406', 1),
        )

    def test_set(self):
        x = Mpfr(30)
        y = Mpfr(30)
        mpfr_const_pi(x, MPFR_RNDN)
        mpfr_set(y, x, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(x),
            mpfr_get_str(y),
        )

    def test_set_d(self):
        x = Mpfr(30)
        mpfr_set_d(x, 0.1, MPFR_RNDN)
        self.assertEqual(
            mpfr_get_str(x),
            ('99999999977', -1),
        )

    def test_rounding_modes(self):
        self.assertEqual(MPFR_RNDN, 0)
        self.assertEqual(MPFR_RNDNA, -1)
        self.assertIsInstance(MPFR_RNDZ, int)
        self.assertIsInstance(MPFR_RNDU, int)
        self.assertIsInstance(MPFR_RNDD, int)
        self.assertIsInstance(MPFR_RNDA, int)
        self.assertIsInstance(MPFR_RNDF, int)

if __name__ == '__main__':
    unittest.main()

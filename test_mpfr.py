import unittest

from mpfr import (
    MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD,
    MPFR_RNDA, MPFR_RNDF, MPFR_RNDNA,

    Mpfr, mpfr_const_pi, mpfr_get_str,
)


class TestMpfr(unittest.TestCase):
    def test_none_argument(self):
        with self.assertRaises(TypeError):
            mpfr_const_pi(None, 0)

    def test_const_pi(self):
        pi = Mpfr(10)
        mpfr_const_pi(pi, 0)
        self.assertEqual(
            mpfr_get_str(pi),
            ('31406', 1),
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

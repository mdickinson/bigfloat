import unittest

import bigfloat.mpfr as mpfr
from bigfloat.rounding_mode import (
    RoundingMode,
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_AWAY_FROM_ZERO,
)


class TestRoundingMode(unittest.TestCase):
    def test_rounding_mode_from_int(self):
        rm = RoundingMode(mpfr.MPFR_RNDN)
        self.assertEqual(rm, ROUND_TIES_TO_EVEN)
        self.assertIsInstance(rm, RoundingMode)

    def test_rounding_mode_from_rounding_mode(self):
        rm = RoundingMode(ROUND_TOWARD_POSITIVE)
        self.assertEqual(rm, ROUND_TOWARD_POSITIVE)
        self.assertIsInstance(rm, RoundingMode)

    def test_str(self):
        self.assertEqual(str(ROUND_TIES_TO_EVEN), 'ROUND_TIES_TO_EVEN')
        self.assertEqual(str(ROUND_TOWARD_ZERO), 'ROUND_TOWARD_ZERO')
        self.assertEqual(str(ROUND_TOWARD_POSITIVE), 'ROUND_TOWARD_POSITIVE')
        self.assertEqual(str(ROUND_TOWARD_NEGATIVE), 'ROUND_TOWARD_NEGATIVE')
        self.assertEqual(str(ROUND_AWAY_FROM_ZERO), 'ROUND_AWAY_FROM_ZERO')

    def test_repr(self):
        self.assertEqual(repr(ROUND_TIES_TO_EVEN), 'ROUND_TIES_TO_EVEN')
        self.assertEqual(repr(ROUND_TOWARD_ZERO), 'ROUND_TOWARD_ZERO')
        self.assertEqual(repr(ROUND_TOWARD_POSITIVE), 'ROUND_TOWARD_POSITIVE')
        self.assertEqual(repr(ROUND_TOWARD_NEGATIVE), 'ROUND_TOWARD_NEGATIVE')
        self.assertEqual(repr(ROUND_AWAY_FROM_ZERO), 'ROUND_AWAY_FROM_ZERO')

    def test_int(self):
        self.assertEqual(int(ROUND_TIES_TO_EVEN), mpfr.MPFR_RNDN)
        self.assertEqual(int(ROUND_TOWARD_ZERO), mpfr.MPFR_RNDZ)
        self.assertEqual(int(ROUND_TOWARD_POSITIVE), mpfr.MPFR_RNDU)
        self.assertEqual(int(ROUND_TOWARD_NEGATIVE), mpfr.MPFR_RNDD)
        self.assertEqual(int(ROUND_AWAY_FROM_ZERO), mpfr.MPFR_RNDA)

    def test_type(self):
        self.assertTrue(issubclass(RoundingMode, int))
        self.assertIs(type(ROUND_TIES_TO_EVEN), RoundingMode)
        self.assertIs(type(ROUND_TOWARD_ZERO), RoundingMode)
        self.assertIs(type(ROUND_TOWARD_POSITIVE), RoundingMode)
        self.assertIs(type(ROUND_TOWARD_NEGATIVE), RoundingMode)
        self.assertIs(type(ROUND_AWAY_FROM_ZERO), RoundingMode)

    def test_invalid_rounding_mode(self):
        with self.assertRaises(ValueError):
            RoundingMode(-1)


if __name__ == '__main__':
    unittest.main()

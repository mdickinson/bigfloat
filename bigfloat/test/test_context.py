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

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from bigfloat.context import (
    setcontext,
    getcontext,
    Context,
    DefaultContext,

    _temporary_exponent_bounds,
)
import mpfr
from bigfloat.rounding_mode import (
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_AWAY_FROM_ZERO,
)

all_rounding_modes = [
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_AWAY_FROM_ZERO,
]


class ContextTests(unittest.TestCase):
    def setUp(self):
        setcontext(DefaultContext)

    def test__temporary_exponent_bounds(self):
        # Failed calls to _temporary_exponent_bounds shouldn't affect emin or
        # emax.
        original_emin = mpfr.mpfr_get_emin()
        original_emax = mpfr.mpfr_get_emax()

        # Call to _temporary_exponent_bounds should restore original values.
        with _temporary_exponent_bounds(-10, 10):
            self.assertEqual(mpfr.mpfr_get_emin(), -10)
            self.assertEqual(mpfr.mpfr_get_emax(), 10)
        self.assertEqual(mpfr.mpfr_get_emin(), original_emin)
        self.assertEqual(mpfr.mpfr_get_emax(), original_emax)

        # Even erroneous calls should restore originals.
        with self.assertRaises(OverflowError):
            with _temporary_exponent_bounds(-10, 10 ** 100):
                pass
        self.assertEqual(mpfr.mpfr_get_emin(), original_emin)
        self.assertEqual(mpfr.mpfr_get_emax(), original_emax)

        with self.assertRaises(OverflowError):
            with _temporary_exponent_bounds(-10 ** 100, 10):
                pass
        self.assertEqual(mpfr.mpfr_get_emin(), original_emin)
        self.assertEqual(mpfr.mpfr_get_emax(), original_emax)

        with self.assertRaises(OverflowError):
            with _temporary_exponent_bounds(-10 ** 100, 10 ** 100):
                pass
        self.assertEqual(mpfr.mpfr_get_emin(), original_emin)
        self.assertEqual(mpfr.mpfr_get_emax(), original_emax)

    def test_attributes(self):
        c = DefaultContext
        self.assertIsInstance(c.precision, int)
        self.assertIsInstance(c.emax, int)
        self.assertIsInstance(c.emin, int)
        self.assertIsInstance(c.subnormalize, bool)
        self.assertIn(c.rounding, all_rounding_modes)

    def test_bad_rounding_mode(self):
        with self.assertRaises(ValueError):
            Context(rounding=-1)

    def test_hashable(self):
        # create equal but non-identical contexts
        c1 = Context(emin=-999, emax=999, precision=100,
                     subnormalize=True, rounding=mpfr.MPFR_RNDU)
        c2 = (Context(emax=999, emin=-999, rounding=mpfr.MPFR_RNDU) +
              Context(precision=100, subnormalize=True))
        self.assertEqual(hash(c1), hash(c2))
        self.assertEqual(c1, c2)
        self.assertIs(c1 == c2, True)
        self.assertIs(c1 != c2, False)

        # distinct contexts
        d1 = Context(emin=-999, emax=999, precision=100,
                     subnormalize=True, rounding=mpfr.MPFR_RNDU)
        d2 = Context(emin=-999, emax=999, precision=101,
                     subnormalize=True, rounding=mpfr.MPFR_RNDU)
        self.assertIs(d1 != d2, True)
        self.assertIs(d1 == d2, False)

    def test_with(self):
        # check use of contexts in with statements
        c = Context(emin=-123, emax=456, precision=1729,
                    subnormalize=True, rounding=mpfr.MPFR_RNDU)
        d = Context(emin=0, emax=10585, precision=20,
                    subnormalize=False, rounding=mpfr.MPFR_RNDD)

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


if __name__ == '__main__':
    unittest.main()

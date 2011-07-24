import unittest

from bigfloat.context import (
    setcontext,
    getcontext,
    Context,
    DefaultContext,
)
import bigfloat.mpfr as mpfr
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

    def test_attributes(self):
        c = DefaultContext
        self.assert_(isinstance(c.precision, (int, long)))
        self.assert_(isinstance(c.emax, (int, long)))
        self.assert_(isinstance(c.emin, (int, long)))
        self.assert_(isinstance(c.subnormalize, bool))
        self.assert_(c.rounding in all_rounding_modes)

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

    def test_with(self):
        # check use of contexts in with statements
        c = Context(emin = -123, emax=456, precision=1729,
                    subnormalize=True, rounding=mpfr.MPFR_RNDU)
        d = Context(emin = 0, emax=10585, precision=20,
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

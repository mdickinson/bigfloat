# Copyright 2009--2019 Mark Dickinson.
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

import threading
import unittest

from six.moves import queue

import mpfr
from bigfloat.context import (
    getcontext,
    Context,
    DefaultContext,
    precision,
    RoundAwayFromZero,
    RoundTiesToEven,
    RoundTowardNegative,
    RoundTowardPositive,
    RoundTowardZero,
    _temporary_exponent_bounds,
)
from bigfloat.ieee import quadruple_precision
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
        c = Context(
            emin=-999,
            emax=999,
            precision=100,
            subnormalize=True,
            rounding=ROUND_TIES_TO_EVEN,
        )
        self.assertIsInstance(c.precision, int)
        self.assertIsInstance(c.emax, int)
        self.assertIsInstance(c.emin, int)
        self.assertIsInstance(c.subnormalize, bool)
        self.assertIn(c.rounding, all_rounding_modes)

    def test_bad_rounding_mode(self):
        with self.assertRaises(ValueError):
            Context(rounding=-1)

    def test_default_context(self):
        self.assertEqual(
            DefaultContext,
            quadruple_precision + RoundTiesToEven,
        )

    def test_rounding_contexts(self):
        with RoundTiesToEven:
            self.assertEqual(getcontext().rounding, ROUND_TIES_TO_EVEN)
        with RoundTowardPositive:
            self.assertEqual(getcontext().rounding, ROUND_TOWARD_POSITIVE)
        with RoundTowardNegative:
            self.assertEqual(getcontext().rounding, ROUND_TOWARD_NEGATIVE)
        with RoundTiesToEven:
            self.assertEqual(getcontext().rounding, ROUND_TIES_TO_EVEN)
        with RoundAwayFromZero:
            self.assertEqual(getcontext().rounding, ROUND_AWAY_FROM_ZERO)

        # Rounding contexts should not affect existing settings for
        # precision, exponents, etc.
        original_contexts = [
            Context(
                precision=234,
                emin=-9999,
                emax=9999,
                subnormalize=True,
                rounding=ROUND_TOWARD_NEGATIVE,
            ),
            Context(
                precision=5,
                emin=-10,
                emax=10,
                subnormalize=False,
                rounding=ROUND_AWAY_FROM_ZERO,
            ),
        ]
        rounding_contexts = [
            RoundTiesToEven,
            RoundTowardPositive,
            RoundTowardNegative,
            RoundTowardZero,
            RoundAwayFromZero,
        ]

        for original_context in original_contexts:
            for rounding_context in rounding_contexts:
                with original_context:
                    with rounding_context:
                        self.assertEqual(
                            getcontext().precision,
                            original_context.precision,
                        )
                        self.assertEqual(
                            getcontext().emin,
                            original_context.emin,
                        )
                        self.assertEqual(
                            getcontext().emax,
                            original_context.emax,
                        )
                        self.assertEqual(
                            getcontext().subnormalize,
                            original_context.subnormalize,
                        )
                        self.assertEqual(
                            getcontext().rounding,
                            rounding_context.rounding,
                        )

    def test_hashable(self):
        # create equal but non-identical contexts
        c1 = Context(emin=-999, emax=999, precision=100,
                     subnormalize=True, rounding=ROUND_TOWARD_POSITIVE)
        c2 = (Context(emax=999, emin=-999, rounding=ROUND_TOWARD_POSITIVE) +
              Context(precision=100, subnormalize=True))
        self.assertEqual(hash(c1), hash(c2))
        self.assertEqual(c1, c2)
        self.assertIs(c1 == c2, True)
        self.assertIs(c1 != c2, False)

        # distinct contexts
        d1 = Context(emin=-999, emax=999, precision=100,
                     subnormalize=True, rounding=ROUND_TOWARD_POSITIVE)
        d2 = Context(emin=-999, emax=999, precision=101,
                     subnormalize=True, rounding=ROUND_TOWARD_POSITIVE)
        self.assertIs(d1 != d2, True)
        self.assertIs(d1 == d2, False)

    def test_with(self):
        # check use of contexts in with statements
        c = Context(emin=-123, emax=456, precision=1729,
                    subnormalize=True, rounding=ROUND_TOWARD_POSITIVE)
        d = Context(emin=0, emax=10585, precision=20,
                    subnormalize=False, rounding=ROUND_TOWARD_NEGATIVE)

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

    def test_context_initialised_in_background_thread(self):
        # Regression test for mdickinson/bigfloat#78.

        # Timeout for blocking waits, so that a badly written test or
        # an unexpected failure mode doesn't cause the whole test suite
        # to block.
        SAFETY_TIMEOUT = 10.0

        def target(result_queue, precision_changed, continue_event):
            # Change the context in a background thread. Put computed
            # precisions on a results queue for testing in the main thread.
            # We use events to pause execution of the background thread
            # so that we can effectively test that the main thread is
            # unaffected at that point.
            try:
                result_queue.put(("PREC", getcontext().precision))
                with precision(20):
                    result_queue.put(("PREC", getcontext().precision))
                    precision_changed.set()
                    if not continue_event.wait(timeout=SAFETY_TIMEOUT):
                        raise RuntimeError("continue_event not received")

                result_queue.put(("PREC", getcontext().precision))
            except BaseException as e:
                result_queue.put(("EXC", str(e)))
            result_queue.put(("DONE",))

        result_queue = queue.Queue()
        precision_changed = threading.Event()
        continue_event = threading.Event()

        default_precision = DefaultContext.precision

        self.assertEqual(getcontext().precision, default_precision)

        thread = threading.Thread(
            target=target,
            args=(result_queue, precision_changed, continue_event),
        )
        thread.start()
        try:
            precision_changed.wait(timeout=SAFETY_TIMEOUT)
            # At this point, the precision in the background thread has
            # been changed, but our precision should be unaltered.
            self.assertEqual(getcontext().precision, default_precision)
            continue_event.set()
        finally:
            thread.join()

        # Collect messages from the background thread.
        messages = []
        while True:
            message = result_queue.get(timeout=SAFETY_TIMEOUT)
            if message[0] == "DONE":
                break
            messages.append(message)

        self.assertEqual(
            messages,
            [
                ("PREC", DefaultContext.precision),
                ("PREC", 20),
                ("PREC", DefaultContext.precision),
            ],
        )


if __name__ == '__main__':
    unittest.main()

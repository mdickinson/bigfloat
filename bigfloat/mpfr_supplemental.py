# -*- coding: UTF-8

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
"""
Supplementary functions with a similar API to those in the mpfr module.
"""
import mpfr


def _quotient_exponent(x, y):
    """
    Given two positive finite MPFR instances x and y,
    find the exponent of x / y; that is, the unique
    integer e such that 2**(e-1) <= x / y < 2**e.

    """
    assert mpfr.mpfr_regular_p(x)
    assert mpfr.mpfr_regular_p(y)

    # Make copy of x with the exponent of y.
    x2 = mpfr.Mpfr_t()
    mpfr.mpfr_init2(x2, mpfr.mpfr_get_prec(x))
    mpfr.mpfr_set(x2, x, mpfr.MPFR_RNDN)
    mpfr.mpfr_set_exp(x2, mpfr.mpfr_get_exp(y))

    # Compare x2 and y, disregarding the sign.
    extra = mpfr.mpfr_cmpabs(x2, y) >= 0
    return extra + mpfr.mpfr_get_exp(x) - mpfr.mpfr_get_exp(y)


def mpfr_floordiv(rop, x, y, rnd):
    """
    Given two MPFR numbers x and y, compute floor(x / y),
    rounded if necessary using the given rounding mode.
    The result is placed in 'rop'.
    """
    # Algorithm notes
    # ---------------
    # A simple and obvious approach is to compute floor(x / y) exactly, and
    # then round to the nearest representable value using the given rounding
    # mode.  This requires computing x / y to a precision sufficient to ensure
    # that floor(x / y) is exactly representable.  If abs(x / y) < 2**r, then
    # abs(floor(x / y)) <= 2**r, and so r bits of precision is enough.
    # However, for large quotients this is impractical, and we need some other
    # method.  For x / y sufficiently large, it's possible to show that x / y
    # and floor(x / y) are indistinguishable, in the sense that both quantities
    # round to the same value.  More precisely, we have the following theorem:
    #
    # Theorem.  Suppose that x and y are nonzero finite binary floats
    # representable with p and q bits of precision, respectively.  Let R be any
    # of the IEEE 754 standard rounding modes, and choose a target precision r.
    # Write rnd for the rounding operation from Q to precision-r binary floats
    # with rounding mode R.  Write bin(x) for the binade of a nonzero float x.
    #
    # If R is a round-to-nearest rounding mode, and either
    #
    # (1) p <= q + r and |x / y| >= 2^(q + r), or
    # (2) p > q + r and bin(x) - bin(y) >= p
    #
    # then
    #
    #    rnd(floor(x / y)) == rnd(x / y)
    #
    # Conversely, if R is a directed rounding mode, and either
    #
    # (1) p < q + r and |x / y| >= 2^(q + r - 1), or
    # (2) p >= q + r and bin(x) - bin(y) >= p
    #
    # then again
    #
    #    rnd(floor(x / y)) == rnd(x / y).
    #
    # Proof.  See separate notes and Coq proof in the float-proofs
    # repository.
    #
    # Rather than distinguish between the various cases (R directed
    # or not, p large versus p small) above, we use a weaker but
    # simpler amalgamation of the above result:
    #
    # Corollary 1. With x, y, p, q, R, r and rnd as above, if
    #
    #     |x / y| >= 2^max(q + r, p)
    #
    # then
    #
    #     rnd(floor(x / y)) == rnd(x / y).
    #
    # Proof. Note that |x / y| >= 2^p implies bin(x) - bin(y) >= p,
    # so it's enough that |x / y| >= 2^max(p, q + r) in the case of
    # a round-to-nearest mode, and that |x / y| >= 2^max(p, q + r - 1)
    # in the case of a directed rounding mode.

    # In special cases, it's safe to defer to mpfr_div: the result in
    # these cases is always 0, infinity, or nan.
    if not mpfr.mpfr_regular_p(x) or not mpfr.mpfr_regular_p(y):
        return mpfr.mpfr_div(rop, x, y, rnd)

    e = _quotient_exponent(x, y)

    p = mpfr.mpfr_get_prec(x)
    q = mpfr.mpfr_get_prec(y)
    r = mpfr.mpfr_get_prec(rop)

    # If e - 1 >= max(p, q+r) then |x / y| >= 2^(e-1) >= 2^max(p, q+r),
    # so by the above theorem, round(floordiv(x, y)) == round(div(x, y)).
    if e - 1 >= max(p, q + r):
        return mpfr.mpfr_div(rop, x, y, rnd)

    # Slow version: compute to sufficient bits to get integer precision.  Given
    # that 2**(e-1) <= x / y < 2**e, need >= e bits of precision.
    z_prec = max(e, 2)
    z = mpfr.Mpfr_t()
    mpfr.mpfr_init2(z, z_prec)

    # Compute the floor exactly. The division may set the
    # inexact flag, so we save its state first.
    old_inexact = mpfr.mpfr_inexflag_p()
    mpfr.mpfr_div(z, x, y, mpfr.MPFR_RNDD)
    if not old_inexact:
        mpfr.mpfr_clear_inexflag()

    # Floor result should be exactly representable, so any rounding mode will
    # do.
    ternary = mpfr.mpfr_rint_floor(z, z, rnd)
    assert ternary == 0

    # ... and round to the given rounding mode.
    return mpfr.mpfr_set(rop, z, rnd)


def mpfr_mod(rop, x, y, rnd):
    """
    Given two MPRF numbers x and y, compute
    x - floor(x / y) * y, rounded if necessary using the given
    rounding mode.  The result is placed in 'rop'.

    This is the 'remainder' operation, with sign convention
    compatible with Python's % operator (where x % y has
    the same sign as y).
    """
    # There are various cases:
    #
    # 0. If either argument is a NaN, the result is NaN.
    #
    # 1. If x is infinite or y is zero, the result is NaN.
    #
    # 2. If y is infinite, return 0 with the sign of y if x is zero, x if x has
    #    the same sign as y, and infinity with the sign of y if it has the
    #    opposite sign.
    #
    # 3. If none of the above cases apply then both x and y are finite,
    #    and y is nonzero.  If x and y have the same sign, simply
    #    return the result of fmod(x, y).
    #
    # 4. Now both x and y are finite, y is nonzero, and x and y have
    #    differing signs.  Compute r = fmod(x, y) with sufficient precision
    #    to get an exact result.  If r == 0, return 0 with the sign of y
    #    (which will be the opposite of the sign of x).  If r != 0,
    #    return r + y, rounded appropriately.

    if not mpfr.mpfr_number_p(x) or mpfr.mpfr_nan_p(y) or mpfr.mpfr_zero_p(y):
        return mpfr.mpfr_fmod(rop, x, y, rnd)
    elif mpfr.mpfr_inf_p(y):
        x_negative = mpfr.mpfr_signbit(x)
        y_negative = mpfr.mpfr_signbit(y)
        if mpfr.mpfr_zero_p(x):
            mpfr.mpfr_set_zero(rop, -y_negative)
            return 0
        elif x_negative == y_negative:
            return mpfr.mpfr_set(rop, x, rnd)
        else:
            mpfr.mpfr_set_inf(rop, -y_negative)
            return 0

    x_negative = mpfr.mpfr_signbit(x)
    y_negative = mpfr.mpfr_signbit(y)
    if x_negative == y_negative:
        return mpfr.mpfr_fmod(rop, x, y, rnd)
    else:
        p = max(mpfr.mpfr_get_prec(x), mpfr.mpfr_get_prec(y))
        z = mpfr.Mpfr_t()
        mpfr.mpfr_init2(z, p)
        # Doesn't matter what rounding mode we use here; the result
        # should be exact.
        ternary = mpfr.mpfr_fmod(z, x, y, rnd)
        assert ternary == 0
        if mpfr.mpfr_zero_p(z):
            mpfr.mpfr_set_zero(rop, -y_negative)
            return 0
        else:
            return mpfr.mpfr_add(rop, y, z, rnd)

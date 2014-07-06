# -*- coding: UTF-8

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

# Python wrapper for MPFR library


import sys as _sys
import contextlib as _contextlib

import mpfr

from bigfloat.rounding_mode import (
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
)

from bigfloat.context import (
    Context,
    DefaultContext,
    EmptyContext,

    RoundTowardPositive,
    RoundTowardNegative,

    _apply_function_in_current_context,
)


# Alternative names for some builtins that get overwritten by functions created
# in this module.
_builtin_max = max
_builtin_min = min
_builtin_abs = abs
_builtin_pow = pow


if _sys.version_info < (3,):
    INTEGER_TYPES = int, long
    STRING_TYPES = str, unicode

    if _sys.maxsize == 2**31 - 1:
        _PyHASH_MODULUS = 2**31 - 1
    elif _sys.maxsize == 2**63 - 1:
        _PyHASH_MODULUS = 2**61 - 1
    else:
        raise ValueError("Unexpected value for sys.maxsize.")
    _PyHASH_INF = hash(float('inf'))
    _PyHASH_NAN = hash(float('nan'))

    _bit_length_correction = {
        '0': 4, '1': 3, '2': 2, '3': 2, '4': 1, '5': 1, '6': 1, '7': 1,
        '8': 0, '9': 0, 'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0,
        }

    def _bit_length(n):
        """Bit length of an integer"""
        hex_n = '%x' % _builtin_abs(n)
        return 4 * len(hex_n) - _bit_length_correction[hex_n[0]]

else:
    INTEGER_TYPES = int,
    STRING_TYPES = str,

    _PyHASH_MODULUS = _sys.hash_info.modulus
    _PyHASH_INF = _sys.hash_info.inf
    _PyHASH_NAN = _sys.hash_info.nan

    _bit_length = int.bit_length

# _PyHASH_2INV is the inverse of 2 modulo the prime _PyHASH_MODULUS
_PyHASH_2INV = _builtin_pow(2, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)


def _mpfr_get_str2(base, ndigits, op, rounding_mode):
    """
    Variant of mpfr_get_str, for internal use:  simply splits off the '-'
    sign from the digit string, and returns a triple

        (sign, digits, exp)

    Also converts the byte-string produced by mpfr_get_str to Unicode.

    """
    digits, exp = mpfr.mpfr_get_str(base, ndigits, op, rounding_mode)
    negative = digits.startswith('-')
    if negative:
        digits = digits[1:]
    return negative, digits, exp


###############################################################################
# Context manager to give an easy way to change emin and emax temporarily.

try:
    DBL_PRECISION = _sys.float_info.mant_dig
except AttributeError:
    # Python 2.5 and earlier don't have sys.float_info; it's enough for
    # DBL_PRECISION to be an upper bound.  64 bits should always be enough.
    DBL_PRECISION = 64

# Dealing with exponent limits
# ----------------------------
# The MPFR documentation for mpfr_set_emin and mpfr_set_emax says:
#
#   "If the user changes the exponent range, it is her/his
#   responsibility to check that all current floating-point variables
#   are in the new allowed range (for example using mpfr_check_range),
#   otherwise the subsequent behavior will be undefined, in the sense
#   of the ISO C standard."
#
# Some MPFR operations and functions (including at least mpfr_add and
# mpfr_nexttoward) appear to assume that input arguments have
# exponents within the current [emin, emax] range.
#
# This assumption is inconsistent with the way that we'd like the
# bigfloat package to operate: a standard operation on BigFloats
# shouldn't care if the inputs to the operation are outside the
# current context; it should only worry about forcing the output into
# the format specified by the current context.  So we adopt the
# following approach:
#
# We define constants EMAX_MAX and EMIN_MIN representing the min and
# max values we'll allow for both emin and emax (these aren't
# necessarily the same as the values returned by mpfr_emin_min and
# mpfr_emax_max).  When the module is imported, emax and emin are
# set to these values.
#
# After this, the MPFR stored emax and emin aren't touched when the
# context is changed; but for each standard operation or function, the
# function is performed with emax=EMAX_MAX and emin=EMIN_MIN.  *Then*
# the exponents are changed, mpfr_check_range is called (also
# mpfr_subnormalize if necessary), and the exponents stored by MPFR
# are restored to their original state.
#
# Any BigFloat instance that's created *must* have exponent in the
# range [EMIN_MIN, EMAX_MAX] (unless it's a zero, infinity or nan).

EMAX_MAX = mpfr.MPFR_EMAX_DEFAULT
EMIN_MIN = mpfr.MPFR_EMIN_DEFAULT

EMAX_MIN = _builtin_max(mpfr.MPFR_EMIN_DEFAULT, mpfr.mpfr_get_emax_min())
EMIN_MAX = _builtin_min(mpfr.MPFR_EMAX_DEFAULT, mpfr.mpfr_get_emin_max())

mpfr.mpfr_set_emin(EMIN_MIN)
mpfr.mpfr_set_emax(EMAX_MAX)

PRECISION_MIN = mpfr.MPFR_PREC_MIN
PRECISION_MAX = mpfr.MPFR_PREC_MAX


def _format_finite(negative, digits, dot_pos):
    """Given a (possibly empty) string of digits and an integer
    dot_pos indicating the position of the decimal point relative to
    the start of that string, output a formatted numeric string with
    the same value and same implicit exponent."""

    # strip leading zeros
    olddigits = digits
    digits = digits.lstrip('0')
    dot_pos -= len(olddigits) - len(digits)

    # value is 0.digits * 10**dot_pos
    use_exponent = dot_pos <= -4 or dot_pos > len(digits)
    if use_exponent:
        exp = dot_pos - 1 if digits else dot_pos
        dot_pos -= exp

    # left pad with zeros, insert decimal point, and add exponent
    if dot_pos <= 0:
        digits = '0' * (1 - dot_pos) + digits
        dot_pos += 1 - dot_pos
    assert 1 <= dot_pos <= len(digits)
    if dot_pos < len(digits):
        digits = digits[:dot_pos] + '.' + digits[dot_pos:]
    if use_exponent:
        digits += "e%+d" % exp
    return '-' + digits if negative else digits


def next_up(x, context=None):
    """next_up(x): return the least representable float that's
    strictly greater than x.

    This operation is quiet:  flags are not affected.

    """
    x = BigFloat._implicit_convert(x)
    # make sure we don't alter any flags
    with _saved_flags():
        with (context if context is not None else EmptyContext):
            with RoundTowardPositive:
                # nan maps to itself
                if is_nan(x):
                    return +x

                # round to current context; if value changes, we're done
                y = +x
                if y != x:
                    return y

                # otherwise apply mpfr_nextabove
                bf = y.copy()
                mpfr.mpfr_nextabove(bf)
                # apply + one more time to deal with subnormals
                return +bf


def next_down(x, context=None):
    """next_down(x): return the greatest representable float that's
    strictly less than x.

    This operation is quiet:  flags are not affected.

    """
    x = BigFloat._implicit_convert(x)
    # make sure we don't alter any flags
    with _saved_flags():
        with (context if context is not None else EmptyContext):
            with RoundTowardNegative:
                # nan maps to itself
                if is_nan(x):
                    return +x

                # round to current context; if value changes, we're done
                y = +x
                if y != x:
                    return y

                # otherwise apply mpfr_nextabove
                bf = y.copy()
                mpfr.mpfr_nextbelow(bf)
                # apply + one more time to deal with subnormals
                return +bf


def _binop(op):
    def wrapped_op(self, other):
        try:
            result = op(self, other)
        except TypeError:
            result = NotImplemented
        return result
    return wrapped_op


def _rbinop(op):
    def wrapped_op(self, other):
        try:
            result = op(other, self)
        except TypeError:
            result = NotImplemented
        return result
    return wrapped_op


class BigFloat(mpfr.Mpfr_t):
    def __new__(cls, value, context=None):
        """Create BigFloat from integer, float, string or another BigFloat.

        If the context keyword argument is not given, the result
        format and the rounding mode

        Uses the current precision and rounding mode, unless an
        alternative context is given.

        """
        if context is not None:
            with context:
                return cls(value)

        if isinstance(value, float):
            return _set_d(value)
        elif isinstance(value, STRING_TYPES):
            return set_str2(value.strip(), 10)
        elif isinstance(value, INTEGER_TYPES):
            return set_str2('%x' % value, 16)
        elif isinstance(value, BigFloat):
            return pos(value)
        else:
            raise TypeError("Can't convert argument %s of type %s "
                            "to BigFloat" % (value, type(value)))

    @classmethod
    def fromhex(cls, value, context=None):
        with (context if context is not None else EmptyContext):
            return set_str2(value, 16)

    # alternative constructor, that does exact conversions
    @classmethod
    def exact(cls, value, precision=None):
        """Convert an integer, float or BigFloat with no loss of precision.
        Also convert a string with given precision.

        This constructor makes no use of the current context.
        """

        # figure out precision to use
        if isinstance(value, STRING_TYPES):
            if precision is None:
                raise TypeError("precision must be supplied when "
                                "converting from a string")
        else:
            if precision is not None:
                raise TypeError("precision argument should not be "
                                "specified except when converting "
                                "from a string")
            if isinstance(value, float):
                precision = _builtin_max(DBL_PRECISION, PRECISION_MIN)
            elif isinstance(value, INTEGER_TYPES):
                precision = _builtin_max(_bit_length(value), PRECISION_MIN)
            elif isinstance(value, BigFloat):
                precision = value.precision
            else:
                raise TypeError("Can't convert argument %s of type %s "
                                "to BigFloat" % (value, type(value)))

        # use Default context, with given precision
        with _saved_flags():
            set_flagstate(set())  # clear all flags
            with DefaultContext + Context(precision=precision):
                result = BigFloat(value)
            if test_flag(Overflow):
                raise ValueError("value too large to represent as a BigFloat")
            if test_flag(Underflow):
                raise ValueError("value too small to represent as a BigFloat")
            if test_flag(Inexact) and not isinstance(value, STRING_TYPES):
                # since this is supposed to be an exact conversion, the
                # inexact flag should never be set except when converting
                # from a string.
                assert False, ("Inexact conversion in BigFloat.exact. "
                               "This shouldn't ever happen.  Please report.")

        return result

    def __int__(self):
        """BigFloat -> int.

        Rounds using RoundTowardZero, regardless of current rounding mode.

        """
        # convert via hex string; rounding mode doesn't matter here,
        # since conversion should be exact
        if not is_finite(self):
            raise ValueError("Can't convert infinity or nan to integer")

        # Conversion to base 16 is exact, so any rounding mode will do.
        negative, digits, e = _mpfr_get_str2(
            16,
            0,
            self,
            ROUND_TIES_TO_EVEN,
        )
        n = int(digits, 16)
        e = 4 * (e - len(digits))
        if e >= 0:
            n <<= e
        else:
            n >>= -e
        return int(-n) if negative else int(n)

    def __float__(self):
        """BigFloat -> float.

        Rounds using RoundTiesToEven, regardless of current rounding mode.

        """
        return mpfr.mpfr_get_d(self, ROUND_TIES_TO_EVEN)

    def _sign(self):
        return mpfr.mpfr_signbit(self)

    def _significand(self):
        """Return the significand of self, as a BigFloat.

        If self is a nonzero finite number, return a BigFloat m
        with the same precision as self, such that

          0.5 <= m < 1. and
          self = +/-m * 2**e

        for some exponent e.

        If self is zero, infinity or nan, return a copy of self with
        the sign set to 0.

        """
        m = self.copy()
        if self and is_finite(self):
            mpfr.mpfr_set_exp(m, 0)
        mpfr.mpfr_setsign(m, m, False, ROUND_TIES_TO_EVEN)
        return m

    def _exponent(self):
        """Return the exponent of self, as an integer.

        The exponent is defined as the unique integer k such that
        2**(k-1) <= abs(self) < 2**k.

        If self is not finite and nonzero, return a string:  one
        of '0', 'Infinity' or 'NaN'.

        """

        if self and is_finite(self):
            return mpfr.mpfr_get_exp(self)

        if not self:
            return '0'
        elif is_inf(self):
            return 'Infinity'
        elif is_nan(self):
            return 'NaN'
        else:
            assert False, "shouldn't ever get here"

    def copy(self):
        """ Return a copy of self.

        This function does not make use of the context.  The result has the
        same precision as the original.

        """
        result = mpfr.Mpfr_t.__new__(BigFloat)
        mpfr.mpfr_init2(result, self.precision)
        mpfr.mpfr_set(result, self, ROUND_TIES_TO_EVEN)
        return result

    def copy_neg(self):
        """ Return a copy of self with the opposite sign bit.

        Unlike -self, this does not make use of the context:  the result
        has the same precision as the original.

        """
        result = mpfr.Mpfr_t.__new__(BigFloat)
        mpfr.mpfr_init2(result, self.precision)
        new_sign = not self._sign()
        mpfr.mpfr_setsign(result, self, new_sign, ROUND_TIES_TO_EVEN)
        return result

    def copy_abs(self):
        """ Return a copy of self with the sign bit unset.

        Unlike abs(self), this does not make use of the context: the result
        has the same precision as the original.

        """
        result = mpfr.Mpfr_t.__new__(BigFloat)
        mpfr.mpfr_init2(result, self.precision)
        mpfr.mpfr_setsign(result, self, False, ROUND_TIES_TO_EVEN)
        return result

    def hex(self):
        """Return a hexadecimal representation of a BigFloat."""

        sign = '-' if self._sign() else ''
        e = self._exponent()
        if isinstance(e, STRING_TYPES):
            return sign + e

        m = self._significand()
        _, digits, _ = _mpfr_get_str2(
            16,
            0,
            m,
            ROUND_TIES_TO_EVEN,
        )
        # only print the number of digits that are actually necessary
        n = 1 + (self.precision - 1) // 4
        assert all(c == '0' for c in digits[n:])
        result = '%s0x0.%sp%+d' % (sign, digits[:n], e)
        return result

    def as_integer_ratio(self):
        """Return pair n, d of integers such that the value of self is
        exactly equal to n/d, n and d are relatively prime, and d >= 1.

        """
        if not is_finite(self):
            raise ValueError("Can't express infinity or nan as "
                             "an integer ratio")
        elif not self:
            return 0, 1

        # convert to a hex string, and from there to a fraction
        negative, digits, e = _mpfr_get_str2(
            16,
            0,
            self,
            ROUND_TIES_TO_EVEN,
        )
        digits = digits.rstrip('0')

        # find number of trailing 0 bits in last hex digit
        v = int(digits[-1], 16)
        v &= -v
        n, d = int(digits, 16) // v, 1
        e = (e - len(digits) << 2) + {1: 0, 2: 1, 4: 2, 8: 3}[v]

        # abs(number) now has value n * 2**e, and n is odd
        if e >= 0:
            n <<= e
        else:
            d <<= -e

        return (-n if negative else n), d

    def __str__(self):
        if is_zero(self):
            return '-0' if is_negative(self) else '0'
        elif is_finite(self):
            negative, digits, e = _mpfr_get_str2(
                10,
                0,
                self,
                ROUND_TIES_TO_EVEN,
            )
            return _format_finite(negative, digits, e)
        elif is_inf(self):
            return '-Infinity' if is_negative(self) else 'Infinity'
        else:
            assert is_nan(self)
            return 'NaN'

    def __repr__(self):
        return "BigFloat.exact('%s', precision=%d)" % (
            str(self), self.precision)

    def _format_to_precision_one(self):
        """ Format 'self' to one significant figure.

        This is a special case of _format_to_floating_precision, made necessary
        because the mpfr_get_str function doesn't support passing a precision
        smaller than 2 (according to the docs), so we need some trickery to
        make this work.

        Rounding is always round-to-nearest.
        """

        # Start by formatting to 2 digits; we'll then truncate to one digit,
        # rounding appropriately.
        sign, digits, exp = _mpfr_get_str2(
            10,
            2,
            self,
            ROUND_TOWARD_NEGATIVE,
        )

        # If the last digit is 5, we can't tell which way to round; instead,
        # recompute with the opposite rounding direction, and round based on
        # the result of that.
        if digits[-1] == '5':
            sign, digits, exp = _mpfr_get_str2(
                10,
                2,
                self,
                ROUND_TOWARD_POSITIVE,
            )

        if digits[-1] in '01234':
            round_up = False
        elif digits[-1] in '6789':
            round_up = True
        else:
            # Halfway case: round to even.
            round_up = digits[-2] in '13579'

        digits = digits[:-1]
        if round_up:
            digits = str(int(digits) + 1)
            if len(digits) == 2:
                assert digits[-1] == '0'
                digits = digits[:-1]
                exp += 1
        return sign, digits, exp - 1

    def _format_to_floating_precision(self, precision):
        """ Format a nonzero finite BigFloat instance to a given number of
        significant digits.

        Returns a triple (negative, digits, exp) where:

          - negative is a boolean, True for a negative number, else False
          - digits is a string giving the digits of the output
          - exp represents the exponent of the output,

        The normalization of the exponent is such that <digits>E<exp>
        represents the decimal approximation to self.

        Rounding is always round-to-nearest.
        """
        if precision <= 0:
            raise ValueError("precision argument should be at least 1")

        if precision == 1:
            return self._format_to_precision_one()

        sign, digits, exp = _mpfr_get_str2(
            10,
            precision,
            self,
            ROUND_TIES_TO_EVEN,
        )

        return sign, digits, exp - len(digits)

    def _format_to_fixed_precision(self, precision):
        """ Format 'self' to a given number of digits after the decimal point.

        Returns a triple (negative, digits, exp) where:

          - negative is a boolean, True for a negative number, else False
          - digits is a string giving the digits of the output
          - exp represents the exponent of the output

        The normalization of the exponent is such that <digits>E<exp>
        represents the decimal approximation to self.

        """
        # MPFR only provides functions to format to a given number of
        # significant digits.  So we must:
        #
        #   (1) Identify an e such that 10**(e-1) <= abs(x) < 10**e.
        #
        #   (2) Determine the number of significant digits required, and format
        #       to that number of significant digits.
        #
        #   (3) Adjust output if necessary if it's been rounded up to 10**e.

        # Zeros
        if is_zero(self):
            return is_negative(self), '0', -precision

        # Specials
        if is_inf(self):
            return is_negative(self), 'Infinity', None

        if is_nan(self):
            return is_negative(self), 'NaN', None

        # Figure out the exponent by making a call to get_str2.  exp satisfies
        # 10**(exp-1) <= self < 10**exp
        _, _, exp = _mpfr_get_str2(
            10,
            2,
            self,
            ROUND_TOWARD_ZERO,
        )

        sig_figs = exp + precision

        if sig_figs < 0:
            sign = self._sign()
            return sign, '0', -precision

        elif sig_figs == 0:
            # Ex: 0.1 <= x < 1.0, rounding x to nearest multiple of 1.0.
            # Or: 100.0 <= x < 1000.0, rounding x to nearest multiple of 1000.0
            sign, digits, new_exp = _mpfr_get_str2(
                10,
                2,
                self,
                ROUND_TOWARD_NEGATIVE,
            )
            if int(digits) == 50:
                # Halfway case
                sign, digits, new_exp = _mpfr_get_str2(
                    10,
                    2,
                    self,
                    ROUND_TOWARD_POSITIVE,
                )

            digits = '1' if int(digits) > 50 or new_exp == exp + 1 else '0'
            return sign, digits, -precision

        negative, digits, new_exp = self._format_to_floating_precision(
            sig_figs
        )

        # It's possible that the rounding up involved changes the exponent;
        # in that case we have to adjust the digits accordingly.  The only
        # possibility should be that new_exp == exp + 1.
        if new_exp + len(digits) != exp:
            assert new_exp + len(digits) == exp + 1
            digits += '0'

        return negative, digits, -precision

    if _sys.version_info < (3,):
        def __hash__(self):
            # if self is exactly representable as a float, then its hash
            # should match that of the float.  Note that this covers the
            # case where self == 0.
            if self == float(self) or is_nan(self):
                return hash(float(self))

            # now we must ensure that hash(self) == hash(int(self)) in the
            # case where self is integral.  We use the (undocumented) fact
            # that hash(n) == hash(m) for any two nonzero integers n and m
            # that are congruent modulo 2**64-1 and have the same sign:
            # see the source for long_hash in Objects/longobject.c.  An
            # alternative would be to convert an integral self to an
            # integer and take the hash of that, but that would be
            # painfully slow for something like BigFloat('1e1000000000').
            negative, digits, e = _mpfr_get_str2(
                16,
                0,
                self,
                ROUND_TIES_TO_EVEN,
            )
            e -= len(digits)
            # The value of self is (-1)**negative * int(digits, 16) *
            # 16**e.  Compute a strictly positive integer n such that n is
            # congruent to abs(self) modulo 2**64-1 (e.g., in the sense
            # that the numerator of n - abs(self) is divisible by
            # 2**64-1).

            if e >= 0:
                n = int(digits, 16) * _builtin_pow(16, e, 2 ** 64 - 1)
            else:
                n = int(digits, 16) * _builtin_pow(2 ** 60, -e, 2 ** 64 - 1)
            return hash(-n if negative else n)

        # != is automatically inferred from == for Python 3.
        def __ne__(self, other):
            return not (self == other)

        def __nonzero__(self):
            return not is_zero(self)

        def __long__(self):
            return long(int(self))
    else:
        def __hash__(self):
            if is_nan(self):
                return _PyHASH_NAN
            elif is_inf(self):
                return -_PyHASH_INF if is_negative(self) else _PyHASH_INF
            elif is_zero(self):
                return 0

            negative, digits, e = _mpfr_get_str2(
                16,
                0,
                self,
                ROUND_TIES_TO_EVEN,
            )
            # Find binary exponent.
            e = 4 * (e - len(digits))

            # The value of self is (-1)**negative * int(digits, 16) * 2**e.
            if e >= 0:
                exp_hash = _builtin_pow(2, e, _PyHASH_MODULUS)
            else:
                exp_hash = _builtin_pow(_PyHASH_2INV, -e, _PyHASH_MODULUS)
            hash_ = int(digits, 16) * exp_hash % _PyHASH_MODULUS
            ans = -hash_ if negative else hash_
            return -2 if ans == -1 else ans

        def __bool__(self):
            return not is_zero(self)

    @property
    def precision(self):
        return mpfr.mpfr_get_prec(self)

    @classmethod
    def _implicit_convert(cls, arg):
        """Implicit conversion used for binary operations, comparisons,
        functions, etc.  Return value should be an instance of
        BigFloat."""

        # ints, long and floats mix freely with BigFloats, and are
        # converted exactly.
        if isinstance(arg, INTEGER_TYPES) or isinstance(arg, float):
            return cls.exact(arg)
        elif isinstance(arg, BigFloat):
            return arg
        else:
            raise TypeError("Unable to convert argument %s of type %s "
                            "to BigFloat" % (arg, type(arg)))

###############################################################################
# Flags
#
# MPFR has 5 flags available, one of which we shouldn't encounter in
# normal use.  We need functions to save and restore the current flag
# state.

Inexact = 'Inexact'
Overflow = 'Overflow'
Underflow = 'Underflow'
NanFlag = 'NanFlag'
ZeroDivision = 'ZeroDivision'

_all_flags = set([Inexact, Overflow, Underflow, NanFlag, ZeroDivision])

_flag_translate = {
    'underflow': Underflow,
    'overflow': Overflow,
    'nanflag': NanFlag,
    'inexflag': Inexact,
    'divby0': ZeroDivision,
}

_clear_flag_fns = dict(
    (v, getattr(mpfr, 'mpfr_clear_' + k))
    for k, v in _flag_translate.items())
_set_flag_fns = dict(
    (v, getattr(mpfr, 'mpfr_set_' + k))
    for k, v in _flag_translate.items())
_test_flag_fns = dict(
    (v, getattr(mpfr, 'mpfr_' + k + '_p'))
    for k, v in _flag_translate.items())


def test_flag(f):
    """
    Return True if the given flag is set, and False otherwise.

    """
    return _test_flag_fns[f]()


def set_flag(f):
    """
    Set the given flag.

    """
    return _set_flag_fns[f]()


def clear_flag(f):
    """
    Clear the given flag.

    """
    return _clear_flag_fns[f]()


def get_flagstate():
    """
    Return a set containing the flags that are currently set.

    """
    return set(f for f in _all_flags if test_flag(f))


def set_flagstate(flagset):
    """
    Set all flags in ``flagset``, and clear all other flags.

    """
    if not flagset <= _all_flags:
        raise ValueError("unrecognized flags in flagset")

    for f in flagset:
        set_flag(f)
    for f in _all_flags - flagset:
        clear_flag(f)


@_contextlib.contextmanager
def _saved_flags():
    """Save current flags for the duration of a with block.  Restore
    those original flags after the block completes."""

    old_flags = get_flagstate()
    try:
        yield
    finally:
        set_flagstate(old_flags)


def _set_d(x, context=None):
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_set_d,
        (x,),
        context,
    )


def _set_from_whole_string(rop, s, base, rnd):
    """
    Helper function for set_str2: accept a string, set rop, and return the
    appropriate ternary value.  Raise ValueError if ``s`` doesn't represent
    a valid string in the given base.

    """
    s = s.strip()
    ternary, endindex = mpfr.mpfr_strtofr(rop, s, base, rnd)
    if len(s) != endindex:
        raise ValueError("not a valid numeric string")
    return ternary


def set_str2(s, base, context=None):
    """
    Convert the string ``s`` in base ``base`` to a BigFloat instance, rounding
    according to the current context.

    Raise ValueError if ``s`` doesn't represent a valid string in the given
    base.

    """
    return _apply_function_in_current_context(
        BigFloat,
        _set_from_whole_string,
        (s, base),
        context,
    )


###############################################################################
# 5.2 Assignment Functions
###############################################################################

def pos(x, context=None):
    """
    Return ``x``.

    As usual, the result is rounded to the current context.  The ``pos``
    function can be useful for rounding an intermediate result, computed with a
    temporary increase in precision, back to the current context.  For
    example::

        >>> from bigfloat import precision
        >>> pow(3, 20) + 1.234 - pow(3, 20)  # inaccurate due to precision loss
        BigFloat.exact('1.2340002059936523', precision=53)
        >>> with precision(100):  # compute result with extra precision
        ...     x = pow(3, 20) + 1.234 - pow(3, 20)
        ...
        >>> x
        BigFloat.exact('1.2339999999999999857891452847980', precision=100)
        >>> pos(x)  # round back to original precision
        BigFloat.exact('1.2340000000000000', precision=53)

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_set,
        (BigFloat._implicit_convert(x),),
        context,
    )


###############################################################################
# 5.5 Basic Arithmetic Functions
###############################################################################

def add(x, y, context=None):
    """
    Return ``x`` + ``y``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_add,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def sub(x, y, context=None):
    """
    Return ``x`` - ``y``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sub,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def mul(x, y, context=None):
    """
    Return ``x`` times ``y``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_mul,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def sqr(x, context=None):
    """
    Return the square of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sqr,
        (BigFloat._implicit_convert(x),),
        context,
    )


def div(x, y, context=None):
    """
    Return ``x`` divided by ``y``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_div,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def sqrt(x, context=None):
    """
    Return the square root of ``x``.

    Return -0 if x is -0, to be consistent with the IEEE 754 standard.  Return
    NaN if x is negative.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sqrt,
        (BigFloat._implicit_convert(x),),
        context,
    )


def rec_sqrt(x, context=None):
    """
    Return the reciprocal square root of x.

    Return +Inf if x is ±0, +0 if x is +Inf, and NaN if x is negative.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_rec_sqrt,
        (BigFloat._implicit_convert(x),),
        context,
    )


def cbrt(x, context=None):
    """
    Return the cube root of x.

    For x negative, return a negative number.  The cube root of -0 is defined
    to be -0.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_cbrt,
        (BigFloat._implicit_convert(x),),
        context,
    )


def root(x, k, context=None):
    """
    Return the kth root of x.

    For k odd and x negative (including -Inf), return a negative number.
    For k even and x negative (including -Inf), return NaN.

    The kth root of -0 is defined to be -0, whatever the parity of k.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_cbrt,
        (BigFloat._implicit_convert(x),),
        context,
    )


def pow(x, y, context=None):
    """
    Return ``x`` raised to the power ``y``.

    Special values are handled as described in the ISO C99 and IEEE 754-2008
    standards for the pow function.

      * pow(±0, y) returns plus or minus infinity for y a negative odd integer.

      * pow(±0, y) returns plus infinity for y negative and not an odd integer.

      * pow(±0, y) returns plus or minus zero for y a positive odd integer.

      * pow(±0, y) returns plus zero for y positive and not an odd integer.

      * pow(-1, ±Inf) returns 1.

      * pow(+1, y) returns 1 for any y, even a NaN.

      * pow(x, ±0) returns 1 for any x, even a NaN.

      * pow(x, y) returns NaN for finite negative x and finite non-integer y.

      * pow(x, -Inf) returns plus infinity for 0 < abs(x) < 1, and plus zero
        for abs(x) > 1.

      * pow(x, +Inf) returns plus zero for 0 < abs(x) < 1, and plus infinity
        for abs(x) > 1.

      * pow(-Inf, y) returns minus zero for y a negative odd integer.

      * pow(-Inf, y) returns plus zero for y negative and not an odd integer.

      * pow(-Inf, y) returns minus infinity for y a positive odd integer.

      * pow(-Inf, y) returns plus infinity for y positive and not an odd
        integer.

      * pow(+Inf, y) returns plus zero for y negative, and plus infinity for y
        positive.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_pow,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def neg(x, context=None):
    """
    Return -x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_neg,
        (BigFloat._implicit_convert(x),),
        context,
    )


def abs(x, context=None):
    """
    Return abs(x).

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_abs,
        (BigFloat._implicit_convert(x),),
        context,
    )


def dim(x, y, context=None):
    """
    Return max(x - y, 0).

    Return x - y if x > y, +0 if x <= y, and NaN if either x or y is NaN.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_dim,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


###############################################################################
# 5.6 Comparison Functions
###############################################################################

def cmp(op1, op2):
    """
    Perform a three-way comparison of op1 and op2.

    Return a positive value if op1 > op2, zero if op1 = op2, and a negative
    value if op1 < op2. Both op1 and op2 are considered to their full own
    precision, which may differ. If one of the operands is NaN, raise
    ValueError.

    Note: This function may be useful to distinguish the three possible
    cases. If you need to distinguish two cases only, it is recommended to use
    the predicate functions like 'greaterequal'; they behave like the IEEE 754
    comparisons, in particular when one or both arguments are NaN.

    """
    op1 = BigFloat._implicit_convert(op1)
    op2 = BigFloat._implicit_convert(op2)
    if is_nan(op1) or is_nan(op2):
        raise ValueError("Cannot perform comparison with NaN.")
    return mpfr.mpfr_cmp(op1, op2)


def cmpabs(op1, op2):
    """
    Compare the absolute values of op1 and op2.

    Return a positive value if op1 > op2, zero if op1 = op2, and a negative
    value if op1 < op2. Both op1 and op2 are considered to their full own
    precision, which may differ. If one of the operands is NaN, raise
    ValueError.

    Note: This function may be useful to distinguish the three possible
    cases. If you need to distinguish two cases only, it is recommended to use
    the predicate functions like 'greaterequal'; they behave like the IEEE 754
    comparisons, in particular when one or both arguments are NaN.

    """
    op1 = BigFloat._implicit_convert(op1)
    op2 = BigFloat._implicit_convert(op2)
    if is_nan(op1) or is_nan(op2):
        raise ValueError("Cannot perform comparison with NaN.")
    return mpfr.mpfr_cmpabs(op1, op2)


def is_nan(x):
    """ Return True if x is a NaN, else False. """

    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_nan_p(x)


def is_inf(x):
    """ Return True if x is an infinity, else False. """

    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_inf_p(x)


def is_finite(x):
    """ Return True if x is finite, else False.

    A BigFloat instance is considered to be finite if it is neither an
    infinity or a NaN.

    """
    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_number_p(x)


def is_zero(x):
    """ Return True if x is a zero, else False. """

    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_zero_p(x)


def is_regular(x):
    """ Return True if x is finite and nonzero, else False. """

    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_regular_p(x)


def sgn(x):
    """
    Return the sign of x.

    Return a positive integer if x > 0, 0 if x == 0, and a negative integer if
    x < 0.  Raise ValueError if x is a NaN.

    This function is equivalent to cmp(x, 0), but more efficient.

    """
    x = BigFloat._implicit_convert(x)
    if is_nan(x):
        raise ValueError("Cannot take sign of a NaN.")
    return mpfr.mpfr_sgn(x)


def greater(x, y):
    """
    Return True if x > y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_greater_p(x, y)


def greaterequal(x, y):
    """
    Return True if x >= y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_greaterequal_p(x, y)


def less(x, y):
    """
    Return True if x < y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_less_p(x, y)


def lessequal(x, y):
    """
    Return True if x <= y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_lessequal_p(x, y)


def equal(x, y):
    """
    Return True if x == y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_equal_p(x, y)


def lessgreater(x, y):
    """
    Return True if x < y or x > y and False otherwise.

    This function returns False whenever x and/or y is a NaN.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_lessgreater_p(x, y)


def unordered(x, y):
    """
    Return True if x or y is a NaN and False otherwise.

    """
    x = BigFloat._implicit_convert(x)
    y = BigFloat._implicit_convert(y)
    return mpfr.mpfr_unordered_p(x, y)


###############################################################################
# 5.7 Special Functions
###############################################################################

def log(x, context=None):
    """
    Return the natural logarithm of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_log,
        (BigFloat._implicit_convert(x),),
        context,
    )


def log2(x, context=None):
    """
    Return the base-two logarithm of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_log2,
        (BigFloat._implicit_convert(x),),
        context,
    )


def log10(x, context=None):
    """
    Return the base-ten logarithm of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_log10,
        (BigFloat._implicit_convert(x),),
        context,
    )


def exp(x, context=None):
    """
    Return the exponential of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_exp,
        (BigFloat._implicit_convert(x),),
        context,
    )


def exp2(x, context=None):
    """
    Return two raised to the power x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_exp2,
        (BigFloat._implicit_convert(x),),
        context,
    )


def exp10(x, context=None):
    """
    Return ten raised to the power x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_exp10,
        (BigFloat._implicit_convert(x),),
        context,
    )


def cos(x, context=None):
    """
    Return the cosine of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_cos,
        (BigFloat._implicit_convert(x),),
        context,
    )


def sin(x, context=None):
    """
    Return the sine of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sin,
        (BigFloat._implicit_convert(x),),
        context,
    )


def tan(x, context=None):
    """
    Return the tangent of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_tan,
        (BigFloat._implicit_convert(x),),
        context,
    )


def sec(x, context=None):
    """
    Return the secant of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sec,
        (BigFloat._implicit_convert(x),),
        context,
    )


def csc(x, context=None):
    """
    Return the cosecant of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_csc,
        (BigFloat._implicit_convert(x),),
        context,
    )


def cot(x, context=None):
    """
    Return the cotangent of ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_cot,
        (BigFloat._implicit_convert(x),),
        context,
    )


def acos(x, context=None):
    """
    Return the inverse cosine of ``x``.

    The mathematically exact result lies in the range [0, π].  However, note
    that as a result of rounding to the current context, it's possible for the
    actual value returned to be fractionally larger than π::

        >>> from bigfloat import precision
        >>> with precision(12):
        ...     x = acos(-1)
        ...
        >>> print(x)
        3.1416
        >>> x > const_pi()
        True

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_acos,
        (BigFloat._implicit_convert(x),),
        context,
    )


def asin(x, context=None):
    """
    Return the inverse sine of ``x``.

    The mathematically exact result lies in the range [-π/2, π/2].  However,
    note that as a result of rounding to the current context, it's possible
    for the actual value to lie just outside this range.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_asin,
        (BigFloat._implicit_convert(x),),
        context,
    )


def atan(x, context=None):
    """
    Return the inverse tangent of ``x``.

    The mathematically exact result lies in the range [-π/2, π/2].  However,
    note that as a result of rounding to the current context, it's possible
    for the actual value to lie just outside this range.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_atan,
        (BigFloat._implicit_convert(x),),
        context,
    )


def atan2(y, x, context=None):
    """
    Return ``atan(y / x)`` with the appropriate choice of function branch.

    If ``x > 0``, then ``atan2(y, x)`` is mathematically equivalent to ``atan(y
    / x)``.  If ``x < 0`` and ``y > 0``, ``atan(y, x)`` is equivalent to ``π +
    atan(y, x)``.  If ``x < 0`` and ``y < 0``, the result is ``-π + atan(y,
    x)``.

    Geometrically, ``atan2(y, x)`` is the angle (measured counterclockwise, in
    radians) from the positive x-axis to the line segment joining (0, 0) to (x,
    y), in the usual representation of the x-y plane.

    Special values are handled as described in the ISO C99 and IEEE 754-2008
    standards for the atan2 function.  The following examples illustrate the
    rules for positive y; for negative y, apply the symmetry ``atan(-y, x) ==
    -atan(y, x)``.

        >>> finite = positive = 2.3
        >>> negative = -2.3
        >>> inf = BigFloat('inf')

        >>> print(atan2(+0.0, -0.0))     # pi
        3.1415926535897931
        >>> print(atan2(+0.0, +0.0))     # 0
        0
        >>> print(atan2(+0.0, negative)) # pi
        3.1415926535897931
        >>> print(atan2(+0.0, positive)) # 0
        0
        >>> print(atan2(positive, 0.0))  # pi / 2
        1.5707963267948966
        >>> print(atan2(inf, -inf))      # 3*pi / 4
        2.3561944901923448
        >>> print(atan2(inf, inf))       # pi / 4
        0.78539816339744828
        >>> print(atan2(inf, finite))    # pi / 2
        1.5707963267948966
        >>> print(atan2(positive, -inf)) # pi
        3.1415926535897931
        >>> print(atan2(positive, +inf)) # 0
        0

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_atan2,
        (
            BigFloat._implicit_convert(y),
            BigFloat._implicit_convert(x),
        ),
        context,
    )


def cosh(x, context=None):
    """
    Return the hyperbolic cosine of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_cosh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def sinh(x, context=None):
    """
    Return the hyperbolic sine of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sinh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def tanh(x, context=None):
    """
    Return the hyperbolic tangent of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_tanh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def sech(x, context=None):
    """
    Return the hyperbolic secant of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_sech,
        (BigFloat._implicit_convert(x),),
        context,
    )


def csch(x, context=None):
    """
    Return the hyperbolic cosecant of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_csch,
        (BigFloat._implicit_convert(x),),
        context,
    )


def coth(x, context=None):
    """
    Return the hyperbolic cotangent of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_coth,
        (BigFloat._implicit_convert(x),),
        context,
    )


def acosh(x, context=None):
    """
    Return the inverse hyperbolic cosine of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_acosh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def asinh(x, context=None):
    """
    Return the inverse hyperbolic sine of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_asinh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def atanh(x, context=None):
    """
    Return the inverse hyperbolic tangent of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_atanh,
        (BigFloat._implicit_convert(x),),
        context,
    )


def factorial(x, context=None):
    """
    Return the factorial of the nonnegative integer x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_fac_ui,
        (x,),
        context,
    )


def log1p(x, context=None):
    """
    Return the logarithm of one plus x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_log1p,
        (BigFloat._implicit_convert(x),),
        context,
    )


def expm1(x, context=None):
    """
    Return one less than the exponential of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_expm1,
        (BigFloat._implicit_convert(x),),
        context,
    )


def eint(x, context=None):
    """
    Return the exponential integral of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_eint,
        (BigFloat._implicit_convert(x),),
        context,
    )


def li2(x, context=None):
    """
    Return the real part of the dilogarithm of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_li2,
        (BigFloat._implicit_convert(x),),
        context,
    )


def gamma(x, context=None):
    """
    Return the value of the Gamma function of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_gamma,
        (BigFloat._implicit_convert(x),),
        context,
    )


def lngamma(x, context=None):
    """
    Return the value of the logarithm of the Gamma function of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_lngamma,
        (BigFloat._implicit_convert(x),),
        context,
    )


def lgamma(x, context=None):
    """
    Return the logarithm of the absolute value of the Gamma function at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        lambda rop, op, rnd: mpfr.mpfr_lgamma(rop, op, rnd)[0],
        (BigFloat._implicit_convert(x),),
        context,
    )


def digamma(x, context=None):
    """
    Return the value of the digamma (sometimes also called Psi) function on op.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_digamma,
        (BigFloat._implicit_convert(x),),
        context,
    )


def zeta(x, context=None):
    """
    Return the value of the Riemann zeta function on x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_zeta,
        (BigFloat._implicit_convert(x),),
        context,
    )


def zeta_ui(x, context=None):
    """
    Return the value of the Riemann zeta function at the nonnegative integer x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_zeta_ui,
        (x,),
        context,
    )


def erf(x, context=None):
    """
    Return the value of the error function at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_erf,
        (BigFloat._implicit_convert(x),),
        context,
    )


def erfc(x, context=None):
    """
    Return the value of the complementary error function at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_erfc,
        (BigFloat._implicit_convert(x),),
        context,
    )


def j0(x, context=None):
    """
    Return the value of the first kind Bessel function of order 0 at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_j0,
        (BigFloat._implicit_convert(x),),
        context,
    )


def j1(x, context=None):
    """
    Return the value of the first kind Bessel function of order 1 at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_j1,
        (BigFloat._implicit_convert(x),),
        context,
    )


def jn(n, x, context=None):
    """
    Return the value of the first kind Bessel function of order ``n`` at ``x``.

    ``n`` should be a Python integer.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_jn,
        (n, BigFloat._implicit_convert(x)),
        context,
    )


def y0(x, context=None):
    """
    Return the value of the second kind Bessel function of order 0 at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_y0,
        (BigFloat._implicit_convert(x),),
        context,
    )


def y1(x, context=None):
    """
    Return the value of the second kind Bessel function of order 1 at x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_y1,
        (BigFloat._implicit_convert(x),),
        context,
    )


def yn(n, x, context=None):
    """
    Return the value of the second kind Bessel function of order ``n`` at
    ``x``.

    ``n`` should be a Python integer.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_yn,
        (n, BigFloat._implicit_convert(x)),
        context,
    )


def fma(x, y, z, context=None):
    """
    Return (x * y) + z, with a single rounding according to the current
    context.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_fma,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
            BigFloat._implicit_convert(z),
        ),
        context,
    )


def fms(x, y, z, context=None):
    """
    Return (x * y) - z, with a single rounding according to the current
    context.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_fms,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
            BigFloat._implicit_convert(z),
        ),
        context,
    )


def agm(x, y, context=None):
    """
    Return the arithmetic geometric mean of x and y.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_agm,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def hypot(x, y, context=None):
    """
    Return the Euclidean norm of x and y, i.e., the square root of the sum of
    the squares of x and y.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_hypot,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def ai(x, context=None):
    """
    Return the Airy function of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_ai,
        (BigFloat._implicit_convert(x),),
        context,
    )


def const_log2(context=None):
    """
    Return log(2).

    Returns the natural logarithm of 2, 0.6931471805..., with precision and
    rounding mode taken from the current context.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_const_log2,
        (),
        context,
    )


def const_pi(context=None):
    """
    Return π.

    Returns π = 3.1415926535..., with precision and rounding mode taken from
    the current context.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_const_pi,
        (),
        context,
    )


def const_euler(context=None):
    """
    Return Euler's constant.

    Returns the value of the Euler-Mascheroni constant, 0.5772156649..., with
    precision and rounding mode taken from the current context.  The constant
    is equal to the limit of (1 + 1/2 + 1/3 + ... + 1/n) - log(n) as n
    approaches infinity.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_const_euler,
        (),
        context,
    )


def const_catalan(context=None):
    """
    Return Catalan's constant.

    Returns the value of Catalan's constant 0.9159655941..., with precision and
    rounding mode taken from the current context.  The Catalan constant is
    defined as the limit of the series 1 - 1/3**2 + 1/5**2 - 1/7**2 + 1/9**2 -
    ...

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_const_catalan,
        (),
        context,
    )


###############################################################################
# 5.10 Integer and Remainder Related Functions
###############################################################################

def ceil(x, context=None):
    """
    Return the next higher or equal integer to x.

    If the result is not exactly representable, it will be rounded according to
    the current context.  Note that the rounding step means that it's possible
    for the result to be smaller than ``x``.  For example::

        >>> x = 2**100 + 1
        >>> ceil(2**100 + 1) >= x
        False

    One way to be sure of getting a result that's greater than or equal to
    ``x`` is to use the ``RoundTowardPositive`` rounding mode::

        >>> with RoundTowardPositive:
        ...     x = 2**100 + 1
        ...     ceil(x) >= x
        ...
        True

    Similar comments apply to the :func:`floor`, :func:`round` and
    :func:`trunc` functions.

    .. note::

       This function corresponds to the MPFR function ``mpfr_rint_ceil``,
       not to ``mpfr_ceil``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_rint_ceil,
        (BigFloat._implicit_convert(x),),
        context,
    )


def floor(x, context=None):
    """
    Return the next lower or equal integer to x.

    If the result is not exactly representable, it will be rounded according to
    the current context.

    Note that it's possible for the result to be larger than ``x``.  See the
    documentation of the :func:`ceil` function for more information.

    .. note::

       This function corresponds to the MPFR function ``mpfr_rint_floor``,
       not to ``mpfr_floor``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_rint_floor,
        (BigFloat._implicit_convert(x),),
        context,
    )


def round(x, context=None):
    """
    Return the nearest integer to x, rounding halfway cases *away from zero*.

    If the result is not exactly representable, it will be rounded according to
    the current context.

    .. note::

       This function corresponds to the MPFR function ``mpfr_rint_round``, not
       to ``mpfr_round``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_rint_round,
        (BigFloat._implicit_convert(x),),
        context,
    )


def trunc(x, context=None):
    """
    Return the next integer towards zero.

    If the result is not exactly representable, it will be rounded according to
    the current context.

    .. note::

       This function corresponds to the MPFR function ``mpfr_rint_trunc``,
       not to ``mpfr_trunc``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_rint_trunc,
        (BigFloat._implicit_convert(x),),
        context,
    )


def frac(x, context=None):
    """
    Return the fractional part of ``x``.

    The result has the same sign as ``x``.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_frac,
        (BigFloat._implicit_convert(x),),
        context,
    )


def mod(x, y, context=None):
    """
    Return ``x`` reduced modulo ``y``.

    Returns the value of x - n * y, where n is the integer quotient of x
    divided by y, rounded toward zero.

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If x is infinite or y is zero, the result is NaN. If y is
    infinite and x is finite, the result is x rounded to the current context.
    If the result is zero, it has the sign of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_fmod,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def remainder(x, y, context=None):
    """
    Return x reduced modulo y.

    Returns the value of x - n * y, where n is the integer quotient of x
    divided by y, rounded to the nearest integer (ties rounded to even).

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If x is infinite or y is zero, the result is NaN. If y is
    infinite and x is finite, the result is x (rounded to the current
    context). If the result is zero, it has the sign of x.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_remainder,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def is_integer(x):
    """ Return True if x is an exact integer, else False. """

    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_integer_p(x)


###############################################################################
# 5.12 Miscellaneous Functions
###############################################################################

def min(x, y, context=None):
    """
    Return the minimum of x and y.

    If x and y are both NaN, return NaN. If exactly one of x and y is NaN,
    return the non-NaN value. If x and y are zeros of different signs, return
    −0.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_min,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def max(x, y, context=None):
    """
    Return the maximum of x and y.

    If x and y are both NaN, return NaN. If exactly one of x and y is NaN,
    return the non-NaN value. If x and y are zeros of different signs, return
    +0.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_max,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


def is_negative(x):
    """ Return True if x has its sign bit set, else False.

    Note that this function returns True for negative zeros.

    """
    x = BigFloat._implicit_convert(x)
    return mpfr.mpfr_signbit(x)


def copysign(x, y, context=None):
    """
    Return a new BigFloat object with the magnitude of x but the sign of y.

    """
    return _apply_function_in_current_context(
        BigFloat,
        mpfr.mpfr_copysign,
        (
            BigFloat._implicit_convert(x),
            BigFloat._implicit_convert(y),
        ),
        context,
    )


# unary arithmetic operations
BigFloat.__pos__ = pos
BigFloat.__neg__ = neg
BigFloat.__abs__ = abs

# binary arithmetic operations
BigFloat.__add__ = _binop(add)
BigFloat.__sub__ = _binop(sub)
BigFloat.__mul__ = _binop(mul)
BigFloat.__truediv__ = _binop(div)
if _sys.version_info < (3,):
    BigFloat.__div__ = _binop(div)
BigFloat.__pow__ = _binop(pow)

# and their reverse operations
BigFloat.__radd__ = _rbinop(add)
BigFloat.__rsub__ = _rbinop(sub)
BigFloat.__rmul__ = _rbinop(mul)
BigFloat.__rtruediv__ = _rbinop(div)
if _sys.version_info < (3,):
    BigFloat.__rdiv__ = _rbinop(div)
BigFloat.__rpow__ = _rbinop(pow)

if (mpfr.MPFR_VERSION_MAJOR, mpfr.MPFR_VERSION_MINOR) >= (2, 4):
    BigFloat.__mod__ = _binop(mod)
    BigFloat.__rmod__ = _rbinop(mod)

# comparisons
BigFloat.__eq__ = _binop(equal)
BigFloat.__le__ = _binop(lessequal)
BigFloat.__lt__ = _binop(less)
BigFloat.__ge__ = _binop(greaterequal)
BigFloat.__gt__ = _binop(greater)

MPFR_VERSION_MAJOR = mpfr.MPFR_VERSION_MAJOR
MPFR_VERSION_MINOR = mpfr.MPFR_VERSION_MINOR

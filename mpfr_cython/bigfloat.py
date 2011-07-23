# Copyright 2009, 2010 Mark Dickinson.
#
# This file is part of the bigfloat module.
#
# The bigfloat module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat module is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat module.  If not, see <http://www.gnu.org/licenses/>.

# Python wrapper for MPFR library

from __future__ import with_statement  # for Python 2.5

# Names to export when someone does 'from bigfloat import *'.  The
# __all__ variable is extended to include standard functions later on.
# Note that this module defines functions 'abs' and 'pow', 'max' and
# 'min' which shadow the builtin functions of those names.  Don't do
# 'from bigfloat import *' if you don't want to clobber these
# functions.

__all__ = [
    # main class
    'BigFloat',

    # contexts
    'Context',

    # limits on emin, emax and precision
    'EMIN_MIN', 'EMIN_MAX',
    'EMAX_MIN', 'EMAX_MAX',
    'PRECISION_MIN', 'PRECISION_MAX',

    # context constants...
    'DefaultContext', 'EmptyContext',
    'half_precision', 'single_precision',
    'double_precision', 'quadruple_precision',
    'RoundTiesToEven', 'RoundTowardZero',
    'RoundTowardPositive', 'RoundTowardNegative',
    'RoundAwayFromZero',

    # ... and functions
    'IEEEContext', 'precision', 'extra_precision',

    # get and set current context
    'getcontext', 'setcontext',

    # flags
    'Inexact', 'Overflow', 'Underflow', 'NanFlag',

    # functions to test, set and clear individual flags
    'test_flag', 'set_flag', 'clear_flag',

    # and to get and set the entire flag state
    'set_flagstate', 'get_flagstate',

    # numeric functions
    'next_up', 'next_down',

    # constants
    'const_log2',
    'const_pi',
    'const_euler',
    'const_catalan',

    # single argument standard functions
    'pos',
    'neg',
    'abs',
    'sqrt',
    'exp',
    'log',
    'log2',

    # predicates
    'is_nan',
    'is_inf',
    'is_zero',
    'is_finite',
    'is_integer',
    'is_regular',
    'is_negative',
]

import sys as _sys
import contextlib as _contextlib

import mpfr

def mpfr_set_str2(rop, s, base, rnd):
    """Set value of rop from the string s, using given base and rounding mode.

    If s is a valid string for the given base, set the Mpfr variable
    rop from s, rounding in the direction given by 'rnd', and return
    the usual ternary value.

    If s is not a valid string for the given base, raise ValueError.

    """
    if s == s.strip():
        ternary, endindex = mpfr.mpfr_strtofr(rop, s, base, rnd)
        if not s[endindex:]:
            return ternary
    raise ValueError("not a valid numeric string")


def mpfr_get_str2(rop, base, ndigits, rounding_mode):
    digits, exp = mpfr.mpfr_get_str(base, ndigits, rop, rounding_mode)
    negative = digits.startswith('-')
    if negative:
        digits = digits[1:]
    return negative, digits, exp


################################################################################
# Rounding modes

ROUND_TIES_TO_EVEN = mpfr.MPFR_RNDN
ROUND_TOWARD_POSITIVE = mpfr.MPFR_RNDU
ROUND_TOWARD_NEGATIVE = mpfr.MPFR_RNDD
ROUND_TOWARD_ZERO = mpfr.MPFR_RNDZ
ROUND_AWAY_FROM_ZERO = mpfr.MPFR_RNDA

_available_rounding_modes = [
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_TOWARD_ZERO,
    ROUND_AWAY_FROM_ZERO,
]

################################################################################
# Context manager to give an easy way to change emin and emax temporarily.

@_contextlib.contextmanager
def eminmax(emin, emax):
    old_emin = mpfr.mpfr_get_emin()
    mpfr.mpfr_set_emin(emin)
    try:
        old_emax = mpfr.mpfr_get_emax()
        mpfr.mpfr_set_emax(emax)
        try:
            yield
        finally:
            mpfr.mpfr_set_emax(old_emax)
    finally:
        mpfr.mpfr_set_emin(old_emin)

# builtin abs, max, min and pow functions are shadowed by BigFloat
# max, min and pow functions later on; keep a copy of the builtin
# functions for later use
_builtin_abs = abs
_builtin_max = max
_builtin_min = min
_builtin_pow = pow

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
# bigfloat module to operate: a standard operation on BigFloats
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

_bit_length_correction = {
    '0': 4, '1': 3, '2': 2, '3': 2, '4': 1, '5': 1, '6': 1, '7': 1,
    '8': 0, '9': 0, 'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0,
    }
def _bit_length(n):
    """Bit length of an integer"""
    hex_n = '%x' % _builtin_abs(n)
    return 4 * len(hex_n) - _bit_length_correction[hex_n[0]]

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
        exp = dot_pos-1 if digits else dot_pos
        dot_pos -= exp

    # left pad with zeros, insert decimal point, and add exponent
    if dot_pos <= 0:
        digits = '0'*(1-dot_pos) + digits
        dot_pos += 1-dot_pos
    assert 1 <= dot_pos <= len(digits)
    if dot_pos < len(digits):
        digits = digits[:dot_pos] + '.' + digits[dot_pos:]
    if use_exponent:
        digits += "e%+d" % exp
    return '-' + digits if negative else digits

_Context_attributes = [
    'precision',
    'emin',
    'emax',
    'subnormalize',
    'rounding',
]

class Context(object):
    # Contexts are supposed to be immutable.  We make the attributes
    # of a Context private, and provide properties to access them in
    # order to discourage users from trying to set the attributes
    # directly.

    def __new__(cls, precision=None, emin=None, emax=None, subnormalize=None,
                rounding=None):
        if precision is not None and \
                not (PRECISION_MIN <= precision <= PRECISION_MAX):
            raise ValueError("Precision p should satisfy %d <= p <= %d." %
                             (PRECISION_MIN, PRECISION_MAX))
        if emin is not None and not EMIN_MIN <= emin <= EMIN_MAX:
            raise ValueError("exponent bound emin should satisfy "
                             "%d <= emin <= %d" % (EMIN_MIN, EMIN_MAX))
        if emax is not None and not EMAX_MIN <= emax <= EMAX_MAX:
            raise ValueError("exponent bound emax should satisfy "
                             "%d <= emax <= %d" % (EMAX_MIN, EMAX_MAX))
        if rounding is not None and not rounding in _available_rounding_modes:
            raise ValueError("unrecognised rounding mode")
        if subnormalize is not None and not subnormalize in [False, True]:
            raise ValueError("subnormalize should be either False or True")
        self = object.__new__(cls)
        self._precision = precision
        self._emin = emin
        self._emax = emax
        self._subnormalize = subnormalize
        self._rounding = rounding
        return self

    def __add__(self, other):
        """For contexts self and other, self + other is a new Context
        combining self and other: for attributes that are defined in
        both self and other, the attribute from other takes
        precedence."""

        return Context(
            precision = (other.precision
                         if other.precision is not None
                         else self.precision),
            emin = other.emin if other.emin is not None else self.emin,
            emax = other.emax if other.emax is not None else self.emax,
            subnormalize = (other.subnormalize
                            if other.subnormalize is not None
                            else self.subnormalize),
            rounding = (other.rounding
                        if other.rounding is not None
                        else self.rounding),
            )

    def __eq__(self, other):
        return (
            self.precision == other.precision and
            self.emin == other.emin and
            self.emax == other.emax and
            self.subnormalize == other.subnormalize and
            self.rounding == other.rounding
            )

    def __hash__(self):
        return hash((self.precision, self.emin, self.emax,
                     self.subnormalize, self.rounding))


    @property
    def precision(self):
        return self._precision
    @property
    def rounding(self):
        return self._rounding
    @property
    def emin(self):
        return self._emin
    @property
    def emax(self):
        return self._emax
    @property
    def subnormalize(self):
        return self._subnormalize

    def __repr__(self):
        args = []
        if self.precision is not None:
            args.append('precision=%r' % self.precision)
        if self.emax is not None:
            args.append('emax=%r' % self.emax)
        if self.emin is not None:
            args.append('emin=%r' % self.emin)
        if self.subnormalize is not None:
            args.append('subnormalize=%r' % self.subnormalize)
        if self.rounding is not None:
            args.append('rounding=%r' % self.rounding)
        return 'Context(%s)' % ', '.join(args)

    __str__ = __repr__

    def __enter__(self):
        _pushcontext(self)

    def __exit__(self, *args):
        _popcontext()

# some useful contexts

# DefaultContext is the context that the module always starts with.
DefaultContext = Context(precision=53,
                         rounding=ROUND_TIES_TO_EVEN,
                         emax=EMAX_MAX,
                         emin=EMIN_MIN,
                         subnormalize=False)

# EmptyContext is useful for situations where a context is
# required, but no change to the current context is desirable
EmptyContext = Context()

# provided rounding modes are implemented as contexts, so that
# they can be used directly in with statements
RoundTiesToEven = Context(rounding=ROUND_TIES_TO_EVEN)
RoundTowardPositive = Context(rounding=ROUND_TOWARD_POSITIVE)
RoundTowardNegative = Context(rounding=ROUND_TOWARD_NEGATIVE)
RoundTowardZero = Context(rounding=ROUND_TOWARD_ZERO)
RoundAwayFromZero = Context(rounding=ROUND_AWAY_FROM_ZERO)

# Contexts corresponding to IEEE 754-2008 binary interchange formats
# (see section 3.6 of the standard for details).

def IEEEContext(bitwidth):
    try:
        precision = {16: 11, 32: 24, 64: 53, 128: 113}[bitwidth]
    except KeyError:
        if bitwidth >= 128 and bitwidth % 32 == 0:
            with DefaultContext + Context(emin=-1, subnormalize=True):
                # log2(bitwidth), rounded to the nearest quarter
                l = log2(bitwidth)
            precision = 13 + bitwidth - int(4*l)
        else:
            raise ValueError("nonstandard bitwidth: bitwidth should be "
                             "16, 32, 64, 128, or k*32 for some k >= 4")

    emax = 1 << bitwidth - precision - 1
    return Context(precision=precision,
                   emin=4-emax-precision,
                   emax=emax,
                   subnormalize=True)

half_precision = IEEEContext(16)
single_precision = IEEEContext(32)
double_precision = IEEEContext(64)
quadruple_precision = IEEEContext(128)

# thread local variables:
#   __bigfloat_context__: current context
#   __context_stack__: context stack, used by with statement

import threading

local = threading.local()
local.__bigfloat_context__ = DefaultContext
local.__context_stack__ = []

def getcontext(_local = local):
    return _local.__bigfloat_context__

def setcontext(context, _local = local):
    # attributes provided by 'context' override those in the current
    # context; if 'context' doesn't specify a particular attribute,
    # the attribute from the current context shows through
    oldcontext = getcontext()
    _local.__bigfloat_context__ = oldcontext + context

def _pushcontext(context, _local = local):
    _local.__context_stack__.append(getcontext())
    setcontext(context)

def _popcontext(_local = local):
    setcontext(_local.__context_stack__.pop())

del threading, local

def precision(prec):
    """Return context specifying the given precision.

    precision(prec) is exactly equivalent to Context(precision=prec).

    """
    return Context(precision=prec)

def extra_precision(prec):
    """Return new context equal to the current context, but with
    precision increased by prec."""
    c = getcontext()
    return Context(precision=c.precision+prec)

def next_up(x, context=None):
    """next_up(x): return the least representable float that's
    strictly greater than x.

    This operation is quiet:  flags are not affected.
    """

    # make sure we don't alter any flags
    with _saved_flags():
        if context is None:
            context = EmptyContext
        x = BigFloat._implicit_convert(x)

        with context + RoundTowardPositive:
            # nan maps to itself
            if is_nan(x):
                return +x

            # round to current context; if value changes, we're done
            y = +x
            if y != x:
                return y

            # otherwise apply mpfr_nextabove
            bf = mpfr.Mpfr(y.precision)
            ternary = mpfr.mpfr_set(bf, y._value, ROUND_TIES_TO_EVEN)
            assert ternary == 0
            mpfr.mpfr_nextabove(bf)
            y = BigFloat._from_Mpfr(bf)

            # apply + one more time to deal with subnormals
            return +y

def next_down(x, context=None):
    """next_down(x): return the greatest representable float that's
    strictly less than x.

    This operation is quiet:  flags are not affected.
    """

    # make sure we don't alter any flags
    with _saved_flags():
        if context is None:
            context = EmptyContext
        x = BigFloat._implicit_convert(x)

        with context + RoundTowardNegative:
            # nan maps to itself
            if is_nan(x):
                return +x

            # round to current context; if value changes, we're done
            y = +x
            if y != x:
                return y

            # otherwise apply mpfr_nextabove
            bf = mpfr.Mpfr(y.precision)
            ternary = mpfr.mpfr_set(bf, y._value, ROUND_TIES_TO_EVEN)
            assert ternary == 0
            mpfr.mpfr_nextbelow(bf)
            y = BigFloat._from_Mpfr(bf)

            # apply + one more time to deal with subnormals
            return +y

def _apply_function_in_context(f, args, context):
    """ Apply an MPFR function 'f' to the given arguments 'args', rounding to
    the given context.  Returns a new Mpfr object with precision taken from
    the current context.

    """
    rounding = context.rounding
    bf = mpfr.Mpfr(context.precision)
    args = (bf,) + args + (rounding,)
    ternary = f(*args)
    with eminmax(context.emin, context.emax):
        ternary = mpfr.mpfr_check_range(bf, ternary, rounding)
        if context.subnormalize:
            # mpfr_subnormalize doesn't set underflow and
            # subnormal flags, so we do that ourselves.  We choose
            # to set the underflow flag for *all* cases where the
            # 'after rounding' result is smaller than the smallest
            # normal number, even if that result is exact.

            # if bf is zero but ternary is nonzero, the underflow
            # flag will already have been set by mpfr_check_range;
            if (mpfr.mpfr_number_p(bf) and
                not mpfr.mpfr_zero_p(bf) and
                mpfr.mpfr_get_exp(bf) < context.precision-1+context.emin):
                mpfr.mpfr_set_underflow()
            ternary = mpfr.mpfr_subnormalize(bf, ternary, rounding)
            if ternary:
                mpfr.mpfr_set_inexflag()
    return bf


def _wrap_constant(f, name=None):
    def wrapped_f(context=None):
        current_context = getcontext()
        if context is not None:
            context = current_context + context
        else:
            context = current_context

        bf = _apply_function_in_context(f, (), context)
        return BigFloat._from_Mpfr(bf)

    if name is None:
        assert f.__name__.startswith('mpfr_')
        name = f.__name__[len('mpfr_'):]
    wrapped_f.__name__ = name
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f

def _wrap_unary_function(f, name=None):
    def wrapped_f(op, context=None):
        current_context = getcontext()
        if context is not None:
            context = current_context + context
        else:
            context = current_context

        args = (BigFloat._implicit_convert(op)._value,)
        bf = _apply_function_in_context(f, args, context)
        return BigFloat._from_Mpfr(bf)

    if name is None:
        assert f.__name__.startswith('mpfr_')
        name = f.__name__[len('mpfr_'):]
    wrapped_f.__name__ = name
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f

def _wrap_binary_function(f, name=None):
    def wrapped_f(op1, op2, context=None):
        current_context = getcontext()
        if context is not None:
            context = current_context + context
        else:
            context = current_context

        args = (
            BigFloat._implicit_convert(op1)._value,
            BigFloat._implicit_convert(op2)._value,
        )
        bf = _apply_function_in_context(f, args, context)
        return BigFloat._from_Mpfr(bf)

    if name is None:
        assert f.__name__.startswith('mpfr_')
        name = f.__name__[len('mpfr_'):]
    wrapped_f.__name__ = name
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f

def _wrap_binary_predicate(f):
    def wrapped_f(op1, op2):
        return f(
            BigFloat._implicit_convert(op1)._value,
            BigFloat._implicit_convert(op2)._value,
        )
    return wrapped_f

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

class BigFloat(object):
    @classmethod
    def _from_Mpfr(cls, value):
        # this is the true initialization function;  any creation
        # of a BigFloat instance goes through this function.
        #
        # value should be an Mpfr instance; recall that Mpfr instances
        # are mutable, but there should be no possibility of
        # accidental future modifications to value.  It's up to the
        # caller of _from_Mpfr to ensure this, by making a copy if
        # necessary.
        if not isinstance(value, mpfr.Mpfr):
            raise TypeError("value should be a Mpfr instance")
        self = object.__new__(cls)
        self._value = value
        return self

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
        elif isinstance(value, str):
            return set_str2(value.strip(), 10)
        elif isinstance(value, unicode):
            value = value.strip().encode('ascii')
            return set_str2(value, 10)
        elif isinstance(value, (int, long)):
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

    @staticmethod
    def _fromhex_exact(value):
        """Private function used in testing"""
        # private low-level version of fromhex that always does an exact
        # conversion.  Avoids using any heavy machinery (contexts, function
        # wrapping), since its main use is in the testing of that machinery.

        # XXX Maybe we should move this function into test_bigfloat
        bf = mpfr.Mpfr(len(value)*4) # should be sufficient precision
        ternary = mpfr_set_str2(bf, value, 16, ROUND_TIES_TO_EVEN)
        if ternary:
            # conversion should have been exact, except possibly if
            # value overflows or underflows
            raise ValueError("_fromhex_exact failed to do an exact "
                             "conversion.  This shouldn't happen. "
                             "Please report.")
        return BigFloat._from_Mpfr(bf)

    # alternative constructor, that does exact conversions
    @classmethod
    def exact(cls, value, precision=None):
        """Convert an integer, float or BigFloat with no loss of precision.
        Also convert a string with given precision.

        This constructor makes no use of the current context.
        """

        # figure out precision to use
        if isinstance(value, basestring):
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
            elif isinstance(value, (int, long)):
                precision = _builtin_max(_bit_length(value), PRECISION_MIN)
            elif isinstance(value, BigFloat):
                precision = value.precision
            else:
                raise TypeError("Can't convert argument %s of type %s "
                                "to BigFloat" % (value, type(value)))

        # use Default context, with given precision
        with _saved_flags():
            set_flagstate(set())  # clear all flags
            with DefaultContext + Context(precision = precision):
                result = BigFloat(value)
            if test_flag(Overflow):
                raise ValueError("value too large to represent as a BigFloat")
            if test_flag(Underflow):
                raise ValueError("value too small to represent as a BigFloat")
            if test_flag(Inexact) and not isinstance(value, basestring):
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
        negative, digits, e = mpfr_get_str2(self._value, 16, 0, ROUND_TIES_TO_EVEN)
        n = int(digits, 16)
        e = 4*(e-len(digits))
        if e >= 0:
            n <<= e
        else:
            n >>= -e
        return int(-n) if negative else int(n)

    def __long__(self):
        return long(int(self))

    def __float__(self):
        """BigFloat -> float.

        Rounds using RoundTiesToEven, regardless of current rounding mode.

        """
        return mpfr.mpfr_get_d(self._value, ROUND_TIES_TO_EVEN)

    def _sign(self):
        return mpfr.mpfr_signbit(self._value)

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

        m = mpfr.Mpfr(self.precision)
        mpfr.mpfr_set(m, self._value, ROUND_TIES_TO_EVEN)
        if self and is_finite(self):
            mpfr.mpfr_set_exp(m, 0)
        mpfr.mpfr_setsign(m, m, False, ROUND_TIES_TO_EVEN)
        return BigFloat._from_Mpfr(m)

    def _exponent(self):
        """Return the exponent of self, as an integer.

        The exponent is defined as the unique integer k such that
        2**(k-1) <= abs(self) < 2**k.

        If self is not finite and nonzero, return a string:  one
        of '0', 'Infinity' or 'NaN'.

        """

        if self and is_finite(self):
            return mpfr.mpfr_get_exp(self._value)

        if not self:
            return '0'
        elif is_inf(self):
            return 'Infinity'
        elif is_nan(self):
            return 'NaN'
        else:
            assert False, "shouldn't ever get here"

    def copy_neg(self):
        """ Return a copy of self with the opposite sign bit.

        Unlike -self, this does not make use of the context:  the result
        has the same precision as the original.

        """
        result = mpfr.Mpfr(self.precision)
        new_sign = not self._sign()
        mpfr.mpfr_setsign(result, self._value, new_sign, ROUND_TIES_TO_EVEN)
        return BigFloat._from_Mpfr(result)

    def copy_abs(self):
        """ Return a copy of self with the sign bit unset.

        Unlike abs(self), this does not make use of the context: the result
        has the same precision as the original.

        """
        result = mpfr.Mpfr(self.precision)
        mpfr.mpfr_setsign(result, self._value, False, ROUND_TIES_TO_EVEN)
        return BigFloat._from_Mpfr(result)

    def hex(self):
        """Return a hexadecimal representation of a BigFloat."""

        sign = '-' if self._sign() else ''
        e = self._exponent()
        if isinstance(e, basestring):
            return sign + e

        m = self._significand()
        _, digits, _ = mpfr_get_str2(m._value, 16, 0, ROUND_TIES_TO_EVEN)
        # only print the number of digits that are actually necessary
        n = 1+(self.precision-1)//4
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
        negative, digits, e = mpfr_get_str2(self._value, 16, 0, ROUND_TIES_TO_EVEN)
        digits = digits.rstrip('0')

        # find number of trailing 0 bits in last hex digit
        v = int(digits[-1], 16)
        v &= -v
        n, d = int(digits, 16)//v, 1
        e = (e-len(digits) << 2) + {1: 0, 2: 1, 4: 2, 8: 3}[v]

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
            negative, digits, e = mpfr_get_str2(self._value, 10, 0, ROUND_TIES_TO_EVEN)
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
        sign, digits, exp = mpfr_get_str2(
            self._value, 10, 2, ROUND_TOWARD_NEGATIVE
        )

        # If the last digit is 5, we can't tell which way to round; instead,
        # recompute with the opposite rounding direction, and round based on
        # the result of that.
        if digits[-1] == '5':
            sign, digits, exp = mpfr_get_str2(
                self._value, 10, 2, ROUND_TOWARD_POSITIVE
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

        sign, digits, exp = mpfr_get_str2(
            self._value, 10, precision, ROUND_TIES_TO_EVEN
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
        _, _, exp = mpfr_get_str2(self._value, 10, 2, ROUND_TOWARD_ZERO)

        sig_figs = exp + precision

        if sig_figs < 0:
            sign = self._sign()
            return sign, '0', -precision

        elif sig_figs == 0:
            # Ex: 0.1 <= x < 1.0, rounding x to nearest multiple of 1.0.
            # Or: 100.0 <= x < 1000.0, rounding x to nearest multiple of 1000.0
            sign, digits, new_exp = mpfr_get_str2(
                self._value, 10, 2, ROUND_TOWARD_NEGATIVE
            )
            if int(digits) == 50:
                # Halfway case
                sign, digits, new_exp = mpfr_get_str2(
                    self._value, 10, 2, ROUND_TOWARD_POSITIVE
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
        negative, digits, e = mpfr_get_str2(self._value, 16, 0,
                                            ROUND_TIES_TO_EVEN)
        e -= len(digits)
        # The value of self is (-1)**negative * int(digits, 16) *
        # 16**e.  Compute a strictly positive integer n such that n is
        # congruent to abs(self) modulo 2**64-1 (e.g., in the sense
        # that the numerator of n - abs(self) is divisible by
        # 2**64-1).

        if e >= 0:
            n = int(digits, 16)*_builtin_pow(16, e, 2**64-1)
        else:
            n = int(digits, 16)*_builtin_pow(2**60, -e, 2**64-1)
        return hash(-n if negative else n)

    def __ne__(self, other):
        return not (self == other)

    def __nonzero__(self):
        return not is_zero(self)

    @property
    def precision(self):
        return mpfr.mpfr_get_prec(self._value)

    @classmethod
    def _implicit_convert(cls, arg):
        """Implicit conversion used for binary operations, comparisons,
        functions, etc.  Return value should be an instance of
        BigFloat."""

        # ints, long and floats mix freely with BigFloats, and are
        # converted exactly.
        if isinstance(arg, (int, long, float)):
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
NanFlag ='NanFlag'

_all_flags = set([Inexact, Overflow, Underflow, NanFlag])

_flag_translate = {
    'underflow' : Underflow,
    'overflow' : Overflow,
    'nanflag' : NanFlag,
    'inexflag' : Inexact,
}

_clear_flag_fns = dict((v, getattr(mpfr, 'mpfr_clear_' + k))
                      for k, v in _flag_translate.items())
_set_flag_fns = dict((v, getattr(mpfr, 'mpfr_set_' + k))
                    for k, v in _flag_translate.items())
_test_flag_fns = dict((v, getattr(mpfr, 'mpfr_' + k + '_p'))
                     for k, v in _flag_translate.items())

def test_flag(f):
    return _test_flag_fns[f]()

def set_flag(f):
    return _set_flag_fns[f]()

def clear_flag(f):
    return _clear_flag_fns[f]()


def get_flagstate():
    return set(f for f in _all_flags if test_flag(f))

def set_flagstate(flagset):
    # set all flags in the given flag set;  clear all flags not
    # in the given flag set.
    if not flagset <= _all_flags:
        raise ValueError("unrecognized flags in flagset")

    for f in flagset:
        set_flag(f)
    for f in _all_flags-flagset:
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
    current_context = getcontext()
    if context is not None:
        context = current_context + context
    else:
        context = current_context
    
    bf = _apply_function_in_context(mpfr.mpfr_set_d, (x,), context)
    return BigFloat._from_Mpfr(bf)

def set_str2(s, base, context=None):
    current_context = getcontext()
    if context is not None:
        context = current_context + context
    else:
        context = current_context
    
    bf = _apply_function_in_context(mpfr_set_str2, (s, base), context)
    return BigFloat._from_Mpfr(bf)
    

const_log2 = _wrap_constant(mpfr.mpfr_const_log2)
const_pi = _wrap_constant(mpfr.mpfr_const_pi)
const_euler = _wrap_constant(mpfr.mpfr_const_euler)
const_catalan = _wrap_constant(mpfr.mpfr_const_catalan)

pos = _wrap_unary_function(mpfr.mpfr_set, name='pos')
neg = _wrap_unary_function(mpfr.mpfr_neg)
abs = _wrap_unary_function(mpfr.mpfr_abs)
sqrt = _wrap_unary_function(mpfr.mpfr_sqrt)
exp = _wrap_unary_function(mpfr.mpfr_exp)
log = _wrap_unary_function(mpfr.mpfr_log)
log2 = _wrap_unary_function(mpfr.mpfr_log2)

add = _wrap_binary_function(mpfr.mpfr_add)
sub = _wrap_binary_function(mpfr.mpfr_sub)
mul = _wrap_binary_function(mpfr.mpfr_mul)
div = _wrap_binary_function(mpfr.mpfr_div)
pow = _wrap_binary_function(mpfr.mpfr_pow)
mod = _wrap_binary_function(mpfr.mpfr_fmod, name='mod')


# Predicates
def is_nan(x):
    """ Return True if x is a NaN, else False. """

    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_nan_p(x)

def is_inf(x):
    """ Return True if x is an infinity, else False. """

    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_inf_p(x)

def is_zero(x):
    """ Return True if x is a zero, else False. """

    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_zero_p(x)

def is_finite(x):
    """ Return True if x is finite, else False.

    A BigFloat instance is considered to be finite if it is neither an
    infinity or a NaN.

    """
    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_number_p(x)

def is_integer(x):
    """ Return True if x is an exact integer, else False. """

    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_integer_p(x)

def is_regular(x):
    """ Return True if x is finite and nonzero, else False. """

    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_regular_p(x)

def is_negative(x):
    """ Return True if x has its sign bit set, else False.

    Note that this function returns True for negative zeros.

    """
    x = BigFloat._implicit_convert(x)._value
    return mpfr.mpfr_signbit(x)

_is_equal = _wrap_binary_predicate(mpfr.mpfr_equal_p)
_is_greater = _wrap_binary_predicate(mpfr.mpfr_greater_p)
_is_greaterequal = _wrap_binary_predicate(mpfr.mpfr_greaterequal_p)
_is_less = _wrap_binary_predicate(mpfr.mpfr_less_p)
_is_lessequal = _wrap_binary_predicate(mpfr.mpfr_lessequal_p)
lessgreater = _wrap_binary_predicate(mpfr.mpfr_lessgreater_p)
unordered = _wrap_binary_predicate(mpfr.mpfr_unordered_p)

# unary arithmetic operations
BigFloat.__pos__ = pos
BigFloat.__neg__ = neg
BigFloat.__abs__ = abs

# binary arithmetic operations
BigFloat.__add__ = _binop(add)
BigFloat.__sub__ = _binop(sub)
BigFloat.__mul__ = _binop(mul)
BigFloat.__div__ = BigFloat.__truediv__ = _binop(div)
BigFloat.__pow__ = _binop(pow)

# and their reverse operations
BigFloat.__radd__ = _rbinop(add)
BigFloat.__rsub__ = _rbinop(sub)
BigFloat.__rmul__ = _rbinop(mul)
BigFloat.__rdiv__ = BigFloat.__rtruediv__ = _rbinop(div)
BigFloat.__rpow__ = _rbinop(pow)

if (mpfr.MPFR_VERSION_MAJOR, mpfr.MPFR_VERSION_MINOR) >= (2, 4):
    BigFloat.__mod__ = _binop(mod)
    BigFloat.__rmod__ = _rbinop(mod)

# comparisons
BigFloat.__eq__ = _binop(_is_equal)
BigFloat.__le__ = _binop(_is_lessequal)
BigFloat.__lt__ = _binop(_is_less)
BigFloat.__ge__ = _binop(_is_greaterequal)
BigFloat.__gt__ = _binop(_is_greater)

MPFR_VERSION_MAJOR = mpfr.MPFR_VERSION_MAJOR
MPFR_VERSION_MINOR = mpfr.MPFR_VERSION_MINOR

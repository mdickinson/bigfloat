# Pythonic wrapper for MPFR library

# BigFloats are treated as immutable.

# XXX: this module defines functions 'abs', 'pow' and 'set', which
# shadow the builtin functions of those names.  Don't do 'from
# bigfloat import *' if you don't want to clobber these functions.

import sys

from pympfr import pympfr
from pympfr import mpfr
from pympfr import GMP_RNDN, GMP_RNDZ, GMP_RNDU, GMP_RNDD
from pympfr import MPFR_PREC_MIN
from pympfr import standard_functions, predicates

try:
    DBL_PRECISION = sys.float_info.mant_dig
except AttributeError:
    # Python 2.5 and earlier don't have sys.float_info; assume IEEE
    # 754 doubles
    DBL_PRECISION = 53

bit_length_correction = {
    '0': 4, '1': 3, '2': 2, '3': 2, '4': 1, '5': 1, '6': 1, '7': 1,
    '8': 0, '9': 0, 'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0,
    }
    
# the abs builtin is shadowed by the MPFR abs function later on
def bit_length(n, _abs=abs):
    """Bit length of an integer"""
    hex_n = '%x' % _abs(n)
    return 4 * len(hex_n) - bit_length_correction[hex_n[0]]

def format_finite(digits, dot_pos):
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
        digits += "e{0:+}".format(exp)
    return digits

# Note that context objects are immutable

class Context(object):
    # Contexts are supposed to be immutable.  We make the attributes
    # of a Context private, to discourage users from trying to set the
    # attributes directly.

    def __new__(cls, precision, rounding_mode,
                emax, emin, subnormalize):
        self = object.__new__(cls)
        self._precision = precision
        self._rounding_mode = rounding_mode
        self._emax = emax
        self._emin = emin
        self._subnormalize = subnormalize
        return self

    @property
    def precision(self):
        return self._precision

    @property
    def rounding_mode(self):
        return self._rounding_mode

    @property
    def emax(self):
        return self._emax

    @property
    def emin(self):
        return self._emin

    @property
    def subnormalize(self):
        return self._subnormalize

    def as_dict(self):
        return {
            'precision' : self.precision,
            'rounding_mode' : self.rounding_mode,
            'emax' : self.emax,
            'emin' : self.emin,
            'subnormalize' : self.subnormalize
            }

    def __call__(self, **kw):
        """Return copy of this context, updated with the given
        keyword parameters."""

        self_dict = self.as_dict()
        self_dict.update(kw)
        return Context(**self_dict)

    def __repr__(self):
        return ("Context(precision=%s, rounding_mode=%s, " +
                "emax=%s, emin=%s, subnormalize=%s)") % (
            self.precision, self.rounding_mode,
            self.emax, self.emin, self.subnormalize)

    __str__ = __repr__

    def __enter__(self):
        pushcontext(self)

    def __exit__(self, *args):
        popcontext()

# some useful contexts

def StandardContext(precision):
    return Context(precision=precision,
                   rounding_mode=GMP_RNDN,
                   emax = mpfr.mpfr_get_emax_max(),
                   emin = mpfr.mpfr_get_emin_min(),
                   subnormalize = False)

double_precision = Context(precision=53,
                           rounding_mode = GMP_RNDN,
                           emax = 1024,
                           emin = -1073,
                           subnormalize = True)

# thread local variables:
#   __bigfloat_context__: current context
#   __context_stack__: context stack, used by with statement

import threading

local = threading.local()
local.__bigfloat_context__ = StandardContext(53)
local.__context_stack__ = []

def getcontext(_local = local):
    return _local.__bigfloat_context__

def setcontext(context, _local = local):
    _local.__bigfloat_context__ = context
    mpfr.mpfr_set_emin(context.emin)
    mpfr.mpfr_set_emax(context.emax)

def pushcontext(context, _local = local):
    _local.__context_stack__.append(getcontext())
    setcontext(context)

def popcontext(_local = local):
    setcontext(_local.__context_stack__.pop())

del threading, local

def wrap_standard_function(f):
    def wrapped_f(*args):
        context = getcontext()
        argtypes = f.argtypes[1:-1]
        if len(args) != len(argtypes):
            raise TypeError("Wrong number of arguments")
        converted_args = []
        for arg, arg_t in zip(args, argtypes):
            if arg_t is pympfr:
                arg = BigFloat.implicit_convert(arg)._value
            converted_args.append(arg)
        converted_args.append(context.rounding_mode)
        bf = pympfr(precision=context.precision)
        ternary = f(bf, *converted_args)
        if context.subnormalize:
            ternary = mpfr.mpfr_subnormalize(bf, ternary, context.rounding_mode)
        return BigFloat._from_pympfr(bf)
    return wrapped_f

def wrap_predicate(f):
    def wrapped_f(*args):
        context = getcontext()
        argtypes = f.argtypes
        if len(args) != len(argtypes):
            raise TypeError("Wrong number of arguments")
        converted_args = []
        for arg, arg_t in zip(args, argtypes):
            if arg_t is pympfr:
                arg = BigFloat.implicit_convert(arg)._value
            converted_args.append(arg)
        return f(*converted_args)
    return wrapped_f

def reverse_args(f):
    def reversed_f(self, other):
        return f(other, self)
    return reversed_f

class BigFloat(object):
    @classmethod
    def _from_pympfr(cls, value):
        # this is the true initialization function;  any creation
        # of a BigFloat instance goes through this function.
        #
        # value should be a pympfr instance; recall that pympfr
        # instances are mutable, but there should be no possibility of
        # accidental future modifications to value.  It's up to the
        # caller of _from_pympfr to ensure this, by making a copy if
        # necessary.
        if not isinstance(value, pympfr):
            raise TypeError("value should be a pympfr instance")
        self = object.__new__(cls)
        self._value = value
        return self

    def __new__(cls, value):
        """Create BigFloat from integer, float, string or another BigFloat.

        Uses the current precision and rounding mode.

        """
        if isinstance(value, float):
            return set_d(value)
        elif isinstance(value, basestring):
            return set_str2(value.strip(), 10)
        elif isinstance(value, (int, long)):
            return set_str2('%x' % value, 16)
        elif isinstance(value, BigFloat):
            return set(value)
        else:
            raise TypeError("Can't convert argument %s of type %s to BigFloat" % (value, type(value)))

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
                raise TypeError("precision must be supplied when converting from a string")
        else:
            if precision is not None:
                raise TypeError("precision argument should not be specified except when converting from a string")
            if isinstance(value, float):
                precision = max(DBL_PRECISION, MPFR_PREC_MIN)
            elif isinstance(value, (int, long)):
                precision = max(bit_length(value), MPFR_PREC_MIN)
            elif isinstance(value, BigFloat):
                precision = value.precision
            else:
                raise TypeError("Can't convert argument %s of type %s to BigFloat" % (value, type(value)))

        # use Default context, with given precision
        with StandardContext(precision):
            return BigFloat(value)

    def __int__(self):
        """BigFloat -> int.

        Rounds using round-towards-zero, regardless of current
        rounding mode.

        """
        # convert via hex string; rounding mode doesn't matter here,
        # since conversion should be exact
        if not self.is_finite:
            raise ValueError("Can't convert infinity or nan to integer")

        e, digits = self._value.get_str(16, 0, GMP_RNDN)
        digits = digits.lstrip('-').rstrip('0')
        n = int(digits, 16)
        e = e-len(digits) << 2
        if e >= 0:
            n <<= e
        else:
            n >>= -e
        return int(-n) if self.is_negative else int(n)

    def __long__(self):
        return long(int(self))

    def __float__(self):
        """BigFloat -> float.

        Rounds using round-half-to-even, regardless of current
        rounding mode.

        """
        return mpfr.mpfr_get_d(self._value, GMP_RNDN)

    def __repr__(self):
        if self.is_zero:
            num = '0'
        elif self.is_finite:
            expt, digits = self._value.get_str(10, 0, GMP_RNDN)
            num = format_finite(digits.lstrip('-'), expt)
        elif self.is_inf:
            num = 'Infinity'
        else:
            assert self.is_nan
            num = 'NaN'

        if self.is_negative:
            num = '-' + num
        return "BigFloat.exact('{0}', precision={1})".format(
            num, self.precision)

    __str__ = __repr__

    # binary arithmetic operations
    __add__ = wrap_standard_function(mpfr.mpfr_add)
    __sub__ = wrap_standard_function(mpfr.mpfr_sub)
    __mul__ = wrap_standard_function(mpfr.mpfr_mul)
    __div__ = __truediv__ = wrap_standard_function(mpfr.mpfr_div)
    __pow__ = wrap_standard_function(mpfr.mpfr_pow)
    __mod__ = wrap_standard_function(mpfr.mpfr_fmod)

    # and their reverse
    __radd__ = reverse_args(__add__)
    __rsub__ = reverse_args(__sub__)
    __rmul__ = reverse_args(__mul__)
    __rdiv__ = __rtruediv__ = reverse_args(__truediv__)
    __rpow__ = reverse_args(__pow__)
    __rmod__ = reverse_args(__mod__)

    # unary arithmetic operations
    __abs__ = wrap_standard_function(mpfr.mpfr_abs)
    __pos__ = wrap_standard_function(mpfr.mpfr_set)
    __neg__ = wrap_standard_function(mpfr.mpfr_neg)

    # rich comparisons
    __eq__ = wrap_predicate(mpfr.mpfr_equal_p)
    __le__ = wrap_predicate(mpfr.mpfr_lessequal_p)
    __lt__ = wrap_predicate(mpfr.mpfr_less_p)
    __ge__ = wrap_predicate(mpfr.mpfr_greaterequal_p)
    __gt__ = wrap_predicate(mpfr.mpfr_greater_p)
    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return not is_zero_p(self)

    @property
    def precision(self):
        return self._value.precision

    @property
    def is_zero(self):
        return mpfr.mpfr_zero_p(self._value)

    @property
    def is_finite(self):
        return mpfr.mpfr_number_p(self._value)

    @property
    def is_inf(self):
        return mpfr.mpfr_inf_p(self._value)

    @property
    def is_nan(self):
        return mpfr.mpfr_nan_p(self._value)

    @property
    def is_negative(self):
        return mpfr.mpfr_signbit(self._value)

    @classmethod
    def implicit_convert(cls, arg):
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


for fn, argtypes in standard_functions:
    mpfr_fn = getattr(mpfr, 'mpfr_' + fn)
    globals()[fn] = wrap_standard_function(mpfr_fn)

for fn, argtypes in predicates:
    mpfr_fn = getattr(mpfr, 'mpfr_' + fn)
    globals()[fn] = wrap_predicate(mpfr_fn)

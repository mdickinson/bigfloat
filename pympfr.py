__all__ = [
    # mpfr library
    'mpfr',

    # pympfr class: thin wrapper around mpfr_t type
    'pympfr',

    # global functions for getting and setting default precision
    'get_default_precision', 'set_default_precision',

    # constants giving limits on the precision
    'MPFR_PREC_MIN', 'MPFR_PREC_MAX',

    # rounding modes;  two sets of names are exported, for convenience
    'tonearest', 'tozero', 'toinf', 'toneginf',
    'RoundTiesToEven', 'RoundTowardZero',
    'RoundTowardPositive', 'RoundTowardNegative',

    # lists of standard functions and predicates
    'standard_functions', 'predicates',

    ]


import ctypes
import ctypes.util

################################################################################
# Some utility functions, that have little to do with mpfr.

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

################################################################################
# Locate and load the library

mpfr = ctypes.cdll.LoadLibrary(ctypes.util.find_library('mpfr'))

################################################################################
# Platform dependent values

# To do: get these values directly by parsing or processing gmp.h
# It might be possible to use cpp directly to do this, or to
# compile and run a test program that outputs the values.

# set to value of __GMP_MP_SIZE_T_INT in gmp.h (should be 0 or 1)
__GMP_MP_SIZE_T_INT = 0

# set to True if __GMP_SHORT_LIMB is defined in gmp.h
__GMP_SHORT_LIMB_DEFINED = False

# set to True if _LONG_LONG_LIMB is defined in gmp.h
_LONG_LONG_LIMB_DEFINED = False

# set to True if your system uses a type smaller than int for an enum
# that includes negative values.  gcc usually uses int unless the
# -fshort-enums is specified.  On some platforms, -fshort-enums is the
# default.
_SHORT_ENUMS = False

################################################################################
# Types

# These 4 types are used directly by the public MPFR functions:
#
#   mpfr_prec_t: type used for representing a precision
#   mpfr_exp_t: type used for representing exponents of mpfr_t instances
#   mpfr_rnd_t: type used for rounding modes
#   mpfr_t: type used for mpfr floating-point variables
#
# In addition, we define:
#
#   mpfr_limb_t: internal type used for the digits

if __GMP_MP_SIZE_T_INT == 1:
    mpfr_prec_t = ctypes.c_uint
    mpfr_exp_t = ctypes.c_int
else:
    mpfr_prec_t = ctypes.c_ulong
    mpfr_exp_t = ctypes.c_long

if __GMP_SHORT_LIMB_DEFINED:
    mpfr_limb_t = ctypes.c_uint
elif _LONG_LONG_LIMB_DEFINED:
    mpfr_limb_t = ctypes.c_ulonglong
else:
    mpfr_limb_t = ctypes.c_ulong

if _SHORT_ENUMS:
    mpfr_rnd_t = ctypes.c_byte
else:
    mpfr_rnd_t = ctypes.c_int

mpfr_sign_t = ctypes.c_int

class __mpfr_struct(ctypes.Structure):
    _fields_ = [
        ("_mpfr_prec", mpfr_prec_t),
        ("_mpfr_sign", mpfr_sign_t),
        ("_mpfr_exp", mpfr_exp_t),
        ("_mpfr_d", ctypes.POINTER(mpfr_limb_t))
        ]

mpfr_t = __mpfr_struct * 1

# Precision class used for automatic range checking of precisions.
# Arguments of type mpfr_prec_t should use the Precision class.
# Return values of type mpfr_prec_t should just be declared as
# mpfr_prec_t.

class Precision(object):
    @classmethod
    def from_param(cls, value):
        if not isinstance(value, (int, long)):
            raise TypeError("precision should be an integer")
        if not MPFR_PREC_MIN <= value <= MPFR_PREC_MAX:
            raise TypeError("precision should be in the range "
                "[{0}, {1}]".format(MPFR_PREC_MIN, MPFR_PREC_MAX))
        return mpfr_prec_t(value)


# Rounding modes
tonearest = RoundTiesToEven = 'RoundTiesToEven'
tozero = RoundTowardZero = 'RoundTowardZero'
toinf = RoundTowardPositive = 'RoundTowardPositive'
toneginf = RoundTowardNegative = 'RoundTowardNegative'
rounding_mode_dict = {tonearest: 0, tozero: 1, toinf: 2, toneginf: 3}

# Rounding mode class is used for automatically validating the
# rounding mode before passing it to the MPFR library.

class RoundingMode(object):
    @classmethod
    def from_param(cls, value):
        try:
            return mpfr_rnd_t(rounding_mode_dict[value])
        except KeyError:
            raise ValueError("Invalid rounding mode")

# Base (i.e., radix) class, used for conversions to and from string

class Base(object):
    @classmethod
    def from_param(cls, value):
        if not 2 <= value <= 36:
            raise ValueError("base b should satisfy 2 <= b <= 36")
        return ctypes.c_int(value)

# UnsignedLong behaves like c_ulong, but raises an exception on
# overflow instead of wrapping

ULONG_MAX = ctypes.c_ulong(-1).value

class UnsignedLong(object):
    @classmethod
    def from_param(cls, value):
        if not 0 <= value <= ULONG_MAX:
            raise ValueError("value too large to fit in a C unsigned long")
        return ctypes.c_ulong(value)

# and Long is similar

LONG_MAX = ULONG_MAX >> 1
LONG_MIN = -1-LONG_MAX

class Long(object):
    @classmethod
    def from_param(cls, value):
        if not LONG_MIN <= value <= LONG_MAX:
            raise ValueError("value too large to fit in a C long")
        return ctypes.c_long(value)

# Bool represents a boolean parameter, passed as a c_int.
# True values map to 1, False values to 0.

class Bool(object):
    @classmethod
    def from_param(cls, value):
        return ctypes.c_int(bool(value))

# normalize a value intended to be an MPFR sign, as used
# for example by the mpfr_set_inf function.  All nonnegative
# values are mapped to 1;  negative values are mapped to -1.

class Sign(object):
    @classmethod
    def from_param(cls, value):
        return ctypes.c_int(1 if value >= 0 else -1)

# This is the main class, implemented as a wrapper around mpfr_t.

class pympfr(object):
    @classmethod
    def from_param(cls, value):
        if not isinstance(value, cls):
            raise TypeError
        if not hasattr(value, '_as_parameter_'):
            raise ValueError("value is not initialized")
        return value._as_parameter_

    def __init__(self, precision=None):
        # if reinitializing, clear first
        if hasattr(self, '_as_parameter_'):
            raise TypeError("can't reinitialize a previously "
                            "initialized pympfr instance")

        value = mpfr_t()
        if precision is None:
            mpfr.mpfr_init(value)
        else:
            mpfr.mpfr_init2(value, precision)
        self._as_parameter_ = value

    # keep a reference to mpfr_clear.  Previously, the clear method
    # included the line 'mpfr.mpfr_clear(self)', but this can give a
    # (harmless, but ugly) NameError on interpreter shutdown if the
    # global variable 'mpfr' is removed before __del__ is called on
    # pympfr instances.
    clear_method = mpfr.mpfr_clear
    def clear(self):
        self.clear_method(self)
        del self._as_parameter_

    def as_float(self, rounding_mode):
        """Convert to a Python float, using the given rounding mode"""
        return mpfr.mpfr_get_d(self, rounding_mode)

    def as_integer_ratio(self):
        """Return pair n, d of integers such that the value of self is exactly
        equal to n/d, n and d are relatively prime, and d >= 1."""

        if not self.is_finite:
            raise ValueError("Can't express infinity or nan as "
                             "an integer ratio")
        elif self.is_zero:
            return 0, 1

        # convert to a hex string, and from there to a fraction
        e, digits = self.get_str(16, 0, tonearest)
        digits = digits.lstrip('-').rstrip('0')

        # find number of trailing 0 bits in last hex digit
        v = int(digits[-1], 16)
        v &= -v
        n, d = int(digits, 16)//v, 1
        e = (e-len(digits) << 2) + {1: 0, 2: 1, 4: 2, 8: 3}[v]

        # number now has value n * 2**e, and n is odd
        if e >= 0:
            n <<= e
        else:
            d <<= -e

        return (-n if self.is_negative else n), d

    def __del__(self):
        if hasattr(self, '_as_parameter_'):
            self.clear()

    def __repr__(self):
        if self.is_zero:
            num = '0'
        elif self.is_finite:
            expt, digits = self.get_str(10, 0, tonearest)
            num = format_finite(digits.lstrip('-'), expt)
        elif self.is_inf:
            num = 'Infinity'
        else:
            assert self.is_nan
            num = 'NaN'

        if self.is_negative:
            num = '-' + num
        return "pympfr('{0}', precision={1})".format(num, self.precision)

    __str__ = __repr__

    def get_str(self, base, ndigits, rounding_mode):
        """Convert self to a string in the given base, 2 <= base <= 36.

        The input parameter ndigits gives the number of significant
        digits required.  If ndigits is 0, this function produces a
        number of digits that depends on the precision.

        """
        if not 2 <= base <= 36:
            raise ValueError("base must be an integer between 2 and 36 inclusive")
        if ndigits < 0:
            raise ValueError("n should be a nonnegative integer")

        exp = mpfr_exp_t()
        p = mpfr.mpfr_get_str(None, ctypes.pointer(exp),
                              base, ndigits, self, rounding_mode)
        result = ctypes.cast(p, ctypes.c_char_p).value
        mpfr.mpfr_free_str(p)
        return exp.value, result

    @property
    def precision(self):
        return mpfr.mpfr_get_prec(self)

    @precision.setter
    def precision(self, precision):
        mpfr.mpfr_set_prec(self, precision)

    @property
    def is_zero(self):
        return mpfr.mpfr_zero_p(self)

    @property
    def is_finite(self):
        return mpfr.mpfr_number_p(self)

    @property
    def is_inf(self):
        return mpfr.mpfr_inf_p(self)

    @property
    def is_nan(self):
        return mpfr.mpfr_nan_p(self)

    @property
    def is_negative(self):
        return mpfr.mpfr_signbit(self)

    # comparisons
    def __eq__(self, other):
        return mpfr.mpfr_equal_p(self, other)

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return mpfr.mpfr_lessequal_p(self, other)

    def __ge__(self, other):
        return mpfr.mpfr_greaterequal_p(self, other)

    def __lt__(self, other):
        return mpfr.mpfr_less_p(self, other)

    def __gt__(self, other):
        return mpfr.mpfr_greater_p(self, other)

################################################################################
# Limits, and other constants

# limits on precision
MPFR_PREC_MIN = 2
MPFR_PREC_MAX = mpfr_prec_t(-1).value >> 1

################################################################################
# Wrap functions from the library

# 5.1 Initialization Functions

# Only the functions mpfr_init and mpfr_init2 take arguments of type
# mpfr_t.  All other functions use type pympfr instead.  The reason is
# that the pympfr type implements a check that the underlying mpfr_t
# instance is already initialized; for mpfr_init and mpfr_init2 that
# check isn't valid, of course.

mpfr.mpfr_init2.argtypes = [mpfr_t, Precision]
mpfr.mpfr_init2.restype = None

mpfr.mpfr_clear.argtypes = [pympfr]
mpfr.mpfr_clear.restype = None

mpfr.mpfr_init.argtypes = [mpfr_t]
mpfr.mpfr_init.restype = None

mpfr.mpfr_set_default_prec.argtypes = [Precision]
mpfr.mpfr_set_default_prec.restype = None

mpfr.mpfr_get_default_prec.argtypes = []
mpfr.mpfr_get_default_prec.restype = int

mpfr.mpfr_set_prec.argtypes = [pympfr, Precision]
mpfr.mpfr_set_prec.restype = None

mpfr.mpfr_get_prec.argtypes = [pympfr]
mpfr.mpfr_get_prec.restype = int

# 5.2 Assignment Functions

# need to wrap mpfr_strtofr specially: the Python version returns a
# pair consisting of the ternary value and the number of characters
# consumed.

mpfr.mpfr_strtofr.argtypes = [pympfr, ctypes.c_char_p,
                              ctypes.POINTER(ctypes.c_char_p),
                              Base, RoundingMode]

def strtofr(x, s, base, rounding_mode):
    """Set value of x from string s.

    Returns a pair (t, n) giving the ternary value t and
    the number n of characters consumed.  If n == 0
    the the input string was invalid;  in this case x is
    set to 0.

    """
    if not 2 <= base <= 36:
        raise ValueError("base should satsify 2 <= base <= 36")
    startptr = ctypes.c_char_p(s)
    endptr = ctypes.c_char_p()
    ternary = mpfr.mpfr_strtofr(x, startptr, ctypes.byref(endptr), base, rounding_mode)
    return ternary, endptr.value

# mpfr_set_str2 has the form of a standard function.  It's like
# mpfr_set_str, but raises a Python exception for failure, and
# otherwise returns a ternary value.
def mpfr_set_str2(x, s, base, rounding_mode):
    if s != s.strip():
        raise ValueError("not a valid numeric string")
    ternary, remainder = strtofr(x, s, base, rounding_mode)
    if remainder:
        raise ValueError("not a valid numeric string")
    return ternary

mpfr.mpfr_set_str2 = mpfr_set_str2

mpfr.mpfr_set_inf.argtypes = [pympfr, Sign]
mpfr.mpfr_set_inf.restype = None

mpfr.mpfr_set_nan.argtypes = [pympfr]
mpfr.mpfr_set_nan.restype = None

# mpfr_set_zero is an extension to MPFR, with similar semantics to
# mpfr_set_inf.

def mpfr_set_zero(x, sign):
    mpfr.mpfr_set_ui(x, 0)
    mpfr.mpfr_setsign(x, x, sign < 0, RoundTiesToEven)
mpfr_set_zero.argtypes = [pympfr, Sign]
mpfr_set_zero.restype = None

mpfr.mpfr_set_zero = mpfr_set_zero

# We don't implement the MPFR assignments from C integer types, C long
# double, C decimal64, GMP rationals, or GMP floats.

# To do:  implement assignment from a Python int, using mpfr_set_z.

# for mpfr_set, mpfr_set_d see standard functions below

# 5.4 Conversion Functions

mpfr.mpfr_get_d.argtypes = [pympfr, RoundingMode]
mpfr.mpfr_get_d.restype = ctypes.c_double

# declare mpfr_get_str.restype as POINTER(c_char) to avoid the
# automatic c_char_p -> string unboxing.
mpfr.mpfr_get_str.argtypes = [ctypes.c_char_p, ctypes.POINTER(mpfr_exp_t),
                              Base, ctypes.c_size_t,
                              pympfr, RoundingMode]
mpfr.mpfr_get_str.restype = ctypes.POINTER(ctypes.c_char)

mpfr.mpfr_free_str.argtypes = [ctypes.POINTER(ctypes.c_char)]
mpfr.mpfr_free_str.restype = None

# 5.12 Miscellaneous Functions

mpfr.mpfr_nexttoward.argtypes = [pympfr, pympfr]
mpfr.mpfr_nexttoward.restype = None

# for mpfr_signbit:  see section 5.6

# 5.13 Exception Related Functions

mpfr.mpfr_get_emin.argtypes = []
mpfr.mpfr_get_emin.restype = mpfr_exp_t

mpfr.mpfr_get_emax.argtypes = []
mpfr.mpfr_get_emax.restype = mpfr_exp_t

mpfr.mpfr_set_emin.argtypes = [mpfr_exp_t]
mpfr.mpfr_set_emax.argtypes = [mpfr_exp_t]

mpfr.mpfr_get_emin_min.argtypes = []
mpfr.mpfr_get_emin_min.restype = mpfr_exp_t

mpfr.mpfr_get_emin_max.argtypes = []
mpfr.mpfr_get_emin_max.restype = mpfr_exp_t

mpfr.mpfr_get_emax_min.argtypes = []
mpfr.mpfr_get_emax_min.restype = mpfr_exp_t

mpfr.mpfr_get_emax_max.argtypes = []
mpfr.mpfr_get_emax_max.restype = mpfr_exp_t

mpfr.mpfr_check_range.argtypes = [pympfr, ctypes.c_int, RoundingMode]

mpfr.mpfr_subnormalize.argtypes = [pympfr, ctypes.c_int, RoundingMode]

################################################################################
# Functions to be exported at the module level

set_default_precision = mpfr.mpfr_set_default_prec
get_default_precision = mpfr.mpfr_get_default_prec

def rewrap(f):
    def wrapped_f(*args):
        return f(*args)
    return wrapped_f

pympfr.set_d = rewrap(mpfr.mpfr_set_d)
pympfr.set = rewrap(mpfr.mpfr_set)

################################################################################
# Standard arithmetic and mathematical functions
#
# A large number of MPFR's functions take a standard form: a
# *standard* function is one that takes some number of arguments,
# including a rounding mode, and returns the result in an existing
# variable of type mpfr_t, along with a ternary value.  For all such
# functions:
#
#   - the first argument has type mpfr_t, and receives the result
#   - the last argument is the rounding mode
#   - the return value has type int, and gives the ternary value
#
# In this section we provide details about these functions.

standard_constants = [
    'const_log2', 'const_pi', 'const_euler', 'const_catalan',
    ]

# standard functions taking a single mpfr_t as input

standard_unary_functions = [
    'set', 'neg', 'abs',
    'sqr', 'sqrt', 'rec_sqrt', 'cbrt',
    'log', 'log2', 'log10',
    'exp', 'exp2', 'exp10',
    'cos', 'sin', 'tan',
    'sec', 'csc', 'cot',
    'acos', 'asin', 'atan',
    'cosh', 'sinh', 'tanh',
    'sech', 'csch', 'coth',
    'acosh', 'asinh', 'atanh',
    'log1p', 'expm1',
    'eint', 'li2',
    'gamma', 'lngamma', 'lgamma',
    'zeta',
    'erf', 'erfc',
    'j0', 'j1', 'y0', 'y1',
    'rint_ceil', 'rint_floor', 'rint_round', 'rint_trunc',
    'frac',
    ]

# standard functions taking two mpfr_t objects as input

standard_binary_functions = [
    'add', 'sub', 'mul', 'div', 'pow',
    'dim', 'atan2', 'agm', 'hypot',
    'fmod', 'remainder',
    'max', 'min',
    'copysign',
    ]

standard_ternary_functions = [
    'fma', 'fms',
    ]

# more standard functions, with argument types
additional_standard_functions = [
    ('set_d', [ctypes.c_double]),
    ('set_str2', [ctypes.c_char_p, Base]),
    ('mul_2ui', [pympfr, UnsignedLong]),
    ('mul_2si', [pympfr, Long]),
    ('div_2ui', [pympfr, UnsignedLong]),
    ('div_2si', [pympfr, Long]),
    ('setsign', [pympfr, Bool]),
]

standard_functions = \
    [(name, []) for name in standard_constants] + \
    [(name, [pympfr]) for name in standard_unary_functions] + \
    [(name, [pympfr]*2) for name in standard_binary_functions] + \
    [(name, [pympfr]*3) for name in standard_ternary_functions] + \
    additional_standard_functions

for fn, args in standard_functions:
    mpfr_fn = getattr(mpfr, 'mpfr_' + fn)
    mpfr_fn.argtypes = [pympfr] + args + [RoundingMode]

unary_predicates = [
    'nan_p', 'inf_p', 'number_p', 'zero_p',
    'signbit', 'integer_p'
    ]

binary_predicates = [
    'greater_p', 'greaterequal_p',
    'less_p', 'lessequal_p',
    'lessgreater_p', 'equal_p', 'unordered_p'
    ]

predicates = \
    [(name, [pympfr]) for name in unary_predicates] + \
    [(name, [pympfr]*2) for name in binary_predicates]
    
for pred, args in predicates:
    mpfr_pred = getattr(mpfr, 'mpfr_' + pred)
    mpfr_pred.argtypes = args
    mpfr_pred.restype = bool

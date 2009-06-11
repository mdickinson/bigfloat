__all__ = [
    # pympfr class: thin wrapper around mpfr_t type
    'pympfr',

    # global functions for getting and setting default precision
    'get_default_precision', 'set_default_precision',

    # setters
    'set_d',

    # getters
    'get_d',

    # constants giving limits on the precision
    'MPFR_PREC_MIN', 'MPFR_PREC_MAX',

    # rounding modes
    'GMP_RNDN', 'GMP_RNDZ', 'GMP_RNDU', 'GMP_RNDD',
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
        digits += "e{:+}".format(exp)
    return digits

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
#   mpfr_sign_t: type used for representing the sign
#   mpfr_limb_t: internal type used for the digits

if __GMP_MP_SIZE_T_INT == 1:
    mpfr_exp_t = mpfr_prec_t = ctypes.c_uint
else:
    mpfr_exp_t = mpfr_prec_t = ctypes.c_ulong

mpfr_sign_t = ctypes.c_int

if __GMP_SHORT_LIMB_DEFINED:
    mpfr_limb_t = ctypes.c_uint
elif _LONG_LONG_LIMB_DEFINED:
    mpfr_limb_t = ctypes.c_ulonglong
else:
    mpfr_limb_t = ctypes.c_long

if _SHORT_ENUMS:
    mpfr_rnd_t = ctypes.c_byte
else:
    mpfr_rnd_t = ctypes.c_int

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
            raise TypeError("precision should be in the range [%s, %s]" % (MPFR_PREC_MIN, MPFR_PREC_MAX))
        return mpfr_prec_t(value)

# Rounding mode class is used for automatically validating the
# rounding mode before passing it to the MPFR library.

class RoundingMode(object):
    @classmethod
    def from_param(cls, value):
        if not value in [GMP_RNDN, GMP_RNDZ, GMP_RNDU, GMP_RNDD]:
            raise ValueError("Invalid rounding mode")
        return mpfr_rnd_t(value)

# This is the main class, implemented as a wrapper around mpfr_t.

class pympfr(object):
    @classmethod
    def from_param(cls, value):
        if not isinstance(value, pympfr):
            raise TypeError
        if not hasattr(value, '_as_parameter_'):
            raise ValueError("value is not initialized")
        return value._as_parameter_

    def __init__(self, precision=None):
        # if reinitializing, clear first
        if hasattr(self, '_as_parameter_'):
            self._clear()

        value = mpfr_t()
        if precision is None:
            mpfr.mpfr_init(value)
        else:
            mpfr.mpfr_init2(value, precision)
        self._as_parameter_ = value

    def _clear(self):
        mpfr.mpfr_clear(self)
        del self._as_parameter_

    def __del__(self):
        if hasattr(self, '_as_parameter_'):
            self._clear()

    def __repr__(self):
        if self.is_zero:
            num = '0'
        elif self.is_finite:
            expt, digits = self.get_str(10, 0, GMP_RNDN)
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

################################################################################
# Limits, and other constants

# limits on precision
MPFR_PREC_MIN = 2
MPFR_PREC_MAX = mpfr_prec_t(-1).value >> 1

# rounding modes
GMP_RNDN, GMP_RNDZ, GMP_RNDU, GMP_RNDD = range(4)

################################################################################
# Wrap functions from the library

mpfr = ctypes.cdll.LoadLibrary(ctypes.util.find_library('mpfr'))

# 5.1 Initialization Functions

# Only the functions mpfr_init and mpfr_init2 take arguments of type
# mpfr_t.  All other functions use type pympfr instead.  The reason is
# that the pympfr type implements a check that the underlying mpfr_t
# instance is already initialized; for mpfr_init and mpfr_init2 that
# check isn't valid, of course.

mpfr.mpfr_init2.argtypes = [mpfr_t, Precision]
mpfr.mpfr_init2.restype = None

mpfr.mpfr_init.argtypes = [mpfr_t]
mpfr.mpfr_init.restype = None

mpfr.mpfr_clear.argtypes = [pympfr]
mpfr.mpfr_clear.restype = None

mpfr.mpfr_set_prec.argtypes = [pympfr, Precision]
mpfr.mpfr_set_prec.restype = None

mpfr.mpfr_set_default_prec.argtypes = [Precision]
mpfr.mpfr_set_default_prec.restype = None

mpfr.mpfr_get_default_prec.argtypes = []
mpfr.mpfr_get_default_prec.restype = mpfr_prec_t

mpfr.mpfr_get_prec.argtypes = [pympfr]
mpfr.mpfr_get_prec.restype = mpfr_prec_t

set_default_precision = mpfr.mpfr_set_default_prec
get_default_precision = mpfr.mpfr_get_default_prec

# 5.2 Assignment Functions

mpfr.mpfr_set.argtypes = [pympfr, pympfr, RoundingMode]
mpfr.mpfr_set_d.argtypes = [pympfr, ctypes.c_double, RoundingMode]

set_d = mpfr.mpfr_set_d

# 5.4 Conversion Functions

mpfr.mpfr_get_d.argtypes = [pympfr, RoundingMode]
mpfr.mpfr_get_d.restype = ctypes.c_double

# declare mpfr_get_str.restype as POINTER(c_char) to avoid the
# automatic c_char_p -> string unboxing.
mpfr.mpfr_get_str.argtypes = [ctypes.c_char_p, ctypes.POINTER(mpfr_exp_t),
                              ctypes.c_int, ctypes.c_size_t,
                              pympfr, RoundingMode]
mpfr.mpfr_get_str.restype = ctypes.POINTER(ctypes.c_char)

mpfr.mpfr_free_str.argtypes = [ctypes.POINTER(ctypes.c_char)]
mpfr.mpfr_free_str.restype = None

get_d = mpfr.mpfr_get_d

# 5.6 Comparison Functions

# also includes signbit from section 5.12
for unary_predicate in ['nan_p', 'inf_p', 'number_p', 'zero_p', 'signbit']:
    mpfr_predicate = getattr(mpfr, 'mpfr_' + unary_predicate)
    mpfr_predicate.argtypes = [pympfr]
    mpfr_predicate.restype = bool

# 5.12 Miscellaneous Functions

# for mpfr_signbit:  see section 5.6

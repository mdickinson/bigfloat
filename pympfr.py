import ctypes
import ctypes.util

__all__ = [
    # mpfr library, giving access to the various Python-wrapped MPFR functions
    'mpfr',

    # class implementing the floats themselves (corresponds to mpfr_t)
    'Mpfr',

    # constants giving limits on the precision
    'MPFR_PREC_MIN', 'MPFR_PREC_MAX',

    # rounding modes
    'RoundTiesToEven', 'RoundTowardZero',
    'RoundTowardPositive', 'RoundTowardNegative',

    # lists of standard functions and predicates
    'standard_functions', 'predicates',

    # extra functions that aren't part of the mpfr library proper
    'set_str2', 'get_str2', 'strtofr2',

    ]

################################################################################
# Locate and load the library

mpfr_library_name = ctypes.util.find_library('mpfr')
# temporary hack to make this work with mpfr from macports
if mpfr_library_name is None:
    mpfr_library_name = '/opt/local/lib/libmpfr.dylib'
mpfr = ctypes.cdll.LoadLibrary(mpfr_library_name)

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
# Substitutes for ctypes integer types that do overflow checking instead
# of simply wrapping.

UINT_MAX = ctypes.c_uint(-1).value
ULONG_MAX = ctypes.c_ulong(-1).value
SIZE_T_MAX = ctypes.c_size_t(-1).value
INT_MAX = UINT_MAX >> 1
INT_MIN = -1-INT_MAX
LONG_MAX = ULONG_MAX >> 1
LONG_MIN = -1-LONG_MAX

class Int(object):
    @classmethod
    def from_param(cls, value):
        if not INT_MIN <= value <= INT_MAX:
            raise ValueError("value too large to fit in a C int")
        return ctypes.c_int(value)

class UnsignedLong(object):
    @classmethod
    def from_param(cls, value):
        if not 0 <= value <= ULONG_MAX:
            raise ValueError("value too large to fit in a C unsigned long")
        return ctypes.c_ulong(value)

class Long(object):
    @classmethod
    def from_param(cls, value):
        if not LONG_MIN <= value <= LONG_MAX:
            raise ValueError("value too large to fit in a C long")
        return ctypes.c_long(value)

class Size_t(object):
    @classmethod
    def from_param(cls, value):
        if not 0 <= value <= SIZE_T_MAX:
            raise ValueError("value too large to fit in a C size_t")
        return ctypes.c_size_t(value)

################################################################################
# Types

# These 4 types are used directly by the public MPFR functions:
#
#   mpfr_prec_t: type used for representing a precision
#   mpfr_exp_t: type used for representing exponents of Mpfr instances
#   mpfr_rnd_t: type used for rounding modes
#   Mpfr: type used for mpfr floating-point variables
#
# In addition, we define:
#
#   mpfr_limb_t: internal type used for the digits

if __GMP_MP_SIZE_T_INT == 1:
    mpfr_prec_t = ctypes.c_uint
    mpfr_exp_t = ctypes.c_int
    Exponent = Int  # use this in argtypes for arguments expecting an mpfr_exp_t
else:
    mpfr_prec_t = ctypes.c_ulong
    mpfr_exp_t = ctypes.c_long
    Exponent = Long

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

Mpfr = __mpfr_struct * 1

# Precision class used for automatic range checking of precisions.
# Arguments of type mpfr_prec_t should use the Precision class.
# Return values of type mpfr_prec_t should just be declared as
# mpfr_prec_t.

class Precision(object):
    @classmethod
    def from_param(cls, value):
        if not MPFR_PREC_MIN <= value <= MPFR_PREC_MAX:
            raise TypeError("precision should be in the range "
                "[{0}, {1}]".format(MPFR_PREC_MIN, MPFR_PREC_MAX))
        return mpfr_prec_t(value)


# Rounding mode constants
RoundTiesToEven = 'RoundTiesToEven'
RoundTowardZero = 'RoundTowardZero'
RoundTowardPositive = 'RoundTowardPositive'
RoundTowardNegative = 'RoundTowardNegative'

_rounding_mode_dict = {
    RoundTiesToEven: 0,
    RoundTowardZero: 1,
    RoundTowardPositive: 2,
    RoundTowardNegative: 3,
}

# Rounding mode class is used for automatically validating the
# rounding mode before passing it to the MPFR library.

class RoundingMode(object):
    @classmethod
    def from_param(cls, value):
        try:
            return mpfr_rnd_t(_rounding_mode_dict[value])
        except KeyError:
            raise ValueError("Invalid rounding mode")

# Base (i.e., radix) class, used for conversions to and from string

class Base(object):
    @classmethod
    def from_param(cls, value):
        if not 2 <= value <= 36:
            raise ValueError("base b should satisfy 2 <= b <= 36")
        return ctypes.c_int(value)

# Bool represents a boolean parameter, passed as a c_int.
# Values that are true (in the Python sense) are mapped to c_int(1);
# values that are false are mapped to c_int(0).

class Bool(object):
    @classmethod
    def from_param(cls, value):
        return ctypes.c_int(1 if value else 0)

# Sign is used for a c_int argument representing a sign

class Sign(object):
    @classmethod
    def from_param(cls, value):
        return ctypes.c_int(1 if value >= 0 else -1)

def Ternary(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

# Type UMpfr represents an uninitialized Mpfr instance

class UMpfr(object):
    @classmethod
    def from_param(cls, value):
        if not isinstance(value, Mpfr):
            raise TypeError("Expecting argument of type Mpfr")
        if hasattr(value, '_initialized'):
            raise ValueError("Mpfr instance is already initialized")
        return value

# Type Mpfr represents an initialized Mpfr instance

class Mpfr(object):
    @classmethod
    def from_param(cls, value):
        if not isinstance(value, Mpfr):
            raise TypeError("Expecting argument of type Mpfr")
        if not value._initialized:
            raise ValueError("Mpfr instance is not initialized")
        return value

################################################################################
# Various useful errcheck functions

def set_init(result, func, args):
    mpfr_instance = args[0]
    assert not hasattr(mpfr_instance, '_initialized')
    mpfr_instance._initialized=True

def clear_init(result, func, args):
    mpfr_instance = args[0]
    assert mpfr_instance._initialized
    del mpfr_instance._initialized

def set_init_on_success(result, func, args):
    if result:
        raise ValueError("Initialization call failed")
    set_init(result, func, args)

def error_on_failure(result, func, args):
    if result:
        raise ValueError("call failed")
    return result

################################################################################
# Limits, and other constants

# limits on precision
MPFR_PREC_MIN = 2
MPFR_PREC_MAX = mpfr_prec_t(-1).value >> 1

# standard exponent limits, copied from mpfr.h

MPFR_EMAX_DEFAULT = (1<<30)-1
MPFR_EMIN_DEFAULT = -MPFR_EMAX_DEFAULT

################################################################################
# Wrap functions from the library

# 5.1 Initialization Functions

# Only the initialization functions take arguments of type UMpfr.  All
# other functions use type Mpfr instead.  The reason is that the Mpfr
# type implements a check that the underlying Mpfr instance is
# already initialized, but mpfr_init and mpfr_init2 expect to receive
# uninitialized instances.

mpfr_functions = [

    # 5.1: Initialization Functions
    ('init2', [UMpfr, Precision], None, set_init),
    ('clear', [Mpfr], None, clear_init),
    ('init', [UMpfr], None, set_init),
    ('set_default_prec', [Precision], None),
    ('get_default_prec', [], mpfr_prec_t),
    ('set_prec', [Mpfr, Precision], None),
    ('get_prec', [Mpfr], mpfr_prec_t),

    # 5.2 Assignment Functions

    # mpfr_set, mpfr_set_ui, mpfr_set_si, mpfr_set_d,
    # mpfr_set_ui_2exp, mpfr_set_si_2exp, are standard functions,
    # dealt with below.

    # mpfr_set_uj, mpfr_set_sj, mpfr_set_ld, mpfr_set_decimal64,
    # mpfr_set_z, mpfr_set_q, mpfr_set_f, mpfr_set_uj_2exp,
    # mpfr_set_sj_2exp, are not made available.

    # use of mpfr_set_str is not recommended, since it doesn't return
    # the ternary value.  Use set_str2 (defined below) instead.
    ('set_str', [Mpfr, ctypes.c_char_p, Base, RoundingMode], ctypes.c_int,
     error_on_failure),
    ('strtofr', [Mpfr, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), 
                 Base, RoundingMode], Ternary),
    ('set_inf', [Mpfr, Sign], None),
    ('set_nan', [Mpfr], None),
    ('swap', [Mpfr, Mpfr], None),

    # 5.3 Combined Initialization and Assignment Functions
    # Apart from init_set_str, these are all macros
    ('init_set_str', [UMpfr, ctypes.c_char_p, Base, RoundingMode],
     ctypes.c_int, set_init_on_success),

    # 5.4 Conversion Functions
    ('get_d', [Mpfr, RoundingMode], ctypes.c_double),
    ('get_d_2exp', [ctypes.POINTER(ctypes.c_long), Mpfr, RoundingMode],
     ctypes.c_double),
    ('get_si', [Mpfr, RoundingMode], ctypes.c_long),
    ('get_ui', [Mpfr, RoundingMode], ctypes.c_ulong),
    ('get_str', [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(mpfr_exp_t),
                 Base, Size_t, Mpfr, RoundingMode],
     ctypes.POINTER(ctypes.c_char)),
    ('free_str', [ctypes.POINTER(ctypes.c_char)], None),
    ('fits_ulong_p', [Mpfr, RoundingMode], bool),
    ('fits_slong_p', [Mpfr, RoundingMode], bool),
    ('fits_uint_p', [Mpfr, RoundingMode], bool),
    ('fits_sint_p', [Mpfr, RoundingMode], bool),
    ('fits_ushort_p', [Mpfr, RoundingMode], bool),
    ('fits_sshort_p', [Mpfr, RoundingMode], bool),

    # 5.5 Basic Arithmetic Functions
    # Most of these are standard functions, declared below.
    # Functions involved GMP mpz_t and mpq_t types aren't wrapped.

    # 5.6 Comparison Functions
    ('cmp', [Mpfr, Mpfr], Ternary),
    ('cmp_ui', [Mpfr, UnsignedLong], Ternary),
    ('cmp_si', [Mpfr, Long], Ternary),
    ('cmp_d', [Mpfr, ctypes.c_double], Ternary),
    ('cmp_ui_2exp', [Mpfr, UnsignedLong, Exponent], Ternary),
    ('cmp_si_2exp', [Mpfr, Long, Exponent], Ternary),
    ('cmpabs', [Mpfr, Mpfr], Ternary),
    
    # nan_p, inf_p, number_p, zero_p are standard predicates, declared below
    ('sgn', [Mpfr], Ternary),

    # remaining functions are again standard predicates, declared below

    # 5.7 Special Functions

    # Most of these are standard functions, declared below.
    ('sin_cos', [Mpfr, Mpfr, Mpfr, RoundingMode], Ternary),
    ('sinh_cosh', [Mpfr, Mpfr, Mpfr, RoundingMode], Ternary),
    ('free_cache', [], None),
    # we don't wrap mpfr_sum at the moment

    # 5.8 Input and Output Functions
    # 5.9 Formatted Output Functions
    # we don't currently wrap any functions in these two sections

    # 5.10 +:  to do;  there's stuff missing from everything below...

    # 5.12 Miscellaneous Functions
    ('nexttoward', [Mpfr, Mpfr], None),
    ('nextabove', [Mpfr], None),
    ('nextbelow', [Mpfr], None),
    ('set_exp', [Mpfr, Exponent], ctypes.c_int, error_on_failure),
    ('get_exp', [Mpfr], mpfr_exp_t),

    # 5.13 Exception Related Functions
    ('get_emin', [], mpfr_exp_t),
    ('get_emax', [], mpfr_exp_t),
    ('set_emin', [Exponent], ctypes.c_int, error_on_failure),
    ('set_emax', [Exponent], ctypes.c_int, error_on_failure),
    ('get_emin_min', [], mpfr_exp_t),
    ('get_emin_max', [], mpfr_exp_t),
    ('get_emax_min', [], mpfr_exp_t),
    ('get_emax_max', [], mpfr_exp_t),
    ('check_range', [Mpfr, ctypes.c_int, RoundingMode], Ternary),
    ('subnormalize', [Mpfr, ctypes.c_int, RoundingMode], Ternary),

    ('clear_flags', [], None),
    ]

# additional functions for flags
flags = ['underflow', 'overflow', 'nanflag', 'inexflag', 'erangeflag']
for f in flags:
    mpfr_functions.append(('clear_' + f, [], None))
for f in flags:
    mpfr_functions.append(('set_' + f, [], None))
for f in flags:
    mpfr_functions.append((f+'_p', [], bool))

################################################################################
# Standard arithmetic and mathematical functions
#
# A large number of MPFR's functions take a standard form: a
# *standard* function is one that takes some number of arguments,
# including a rounding mode, and returns the result in an existing
# variable of type Mpfr, along with a ternary value.  For all such
# functions:
#
#   - the first argument has type Mpfr, and receives the result
#   - the last argument is the rounding mode
#   - all arguments except the first are unmodified by the call,
#     and the current value of the first argument is not used.
#   - the return value has type int, and gives the ternary value
#
# In this section we provide details about these functions.

standard_constants = [
    'const_log2', 'const_pi', 'const_euler', 'const_catalan',
    ]

# standard functions taking a single Mpfr instance as input

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

# standard functions taking two Mpfr instances as input

standard_binary_functions = [
    'add', 'sub', 'mul', 'div', 'pow',
    'dim', 'atan2', 'agm', 'hypot',
    'fmod', 'remainder',
    'max', 'min',
    'copysign',
    ]

# and three Mpfr instances...

standard_ternary_functions = [
    'fma', 'fms',
    ]

# more standard functions, with argument types
additional_standard_functions = [
    # 5.2 Assignment Functions
    ('set_ui', [UnsignedLong]),
    ('set_si', [Long]),
    ('set_d', [ctypes.c_double]),
    ('set_ui_2exp', [UnsignedLong, Exponent]),
    ('set_si_2exp', [Long, Exponent]),

    # 5.5 Basic Arithmetic Functions
    ('add_ui', [Mpfr, UnsignedLong]),
    ('add_si', [Mpfr, Long]),
    ('add_d', [Mpfr, ctypes.c_double]),
    ('ui_sub', [UnsignedLong, Mpfr]),
    ('sub_ui', [Mpfr, UnsignedLong]),
    ('si_sub', [Long, Mpfr]),
    ('sub_si', [Mpfr, Long]),
    ('d_sub', [ctypes.c_double, Mpfr]),
    ('sub_d', [Mpfr, ctypes.c_double]),
    ('mul_ui', [Mpfr, UnsignedLong]),
    ('mul_si', [Mpfr, Long]),
    ('mul_d', [Mpfr, ctypes.c_double]),
    ('ui_div', [UnsignedLong, Mpfr]),
    ('div_ui', [Mpfr, UnsignedLong]),
    ('si_div', [Long, Mpfr]),
    ('div_si', [Mpfr, Long]),
    ('d_div', [ctypes.c_double, Mpfr]),
    ('div_d', [Mpfr, ctypes.c_double]),
    ('sqrt_ui', [UnsignedLong]),
    ('root', [Mpfr, UnsignedLong]),
    ('pow_ui', [Mpfr, UnsignedLong]),
    ('pow_si', [Mpfr, Long]),
    ('ui_pow_ui', [UnsignedLong, UnsignedLong]),
    ('ui_pow', [UnsignedLong, Mpfr]),
    ('mul_2ui', [Mpfr, UnsignedLong]),
    ('mul_2si', [Mpfr, Long]),
    ('div_2ui', [Mpfr, UnsignedLong]),
    ('div_2si', [Mpfr, Long]),

    # 5.7 Special Functions
    ('fac_ui', [UnsignedLong]),
    ('zeta_ui', [UnsignedLong]),
    ('jn', [Long, Mpfr]),
    ('yn', [Long, Mpfr]),

    # 5.12 Miscellaneous Functions
    ('setsign', [Mpfr, Bool]),
]

standard_functions = \
    [(name, []) for name in standard_constants] + \
    [(name, [Mpfr]) for name in standard_unary_functions] + \
    [(name, [Mpfr]*2) for name in standard_binary_functions] + \
    [(name, [Mpfr]*3) for name in standard_ternary_functions] + \
    additional_standard_functions

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
    [(name, [Mpfr]) for name in unary_predicates] + \
    [(name, [Mpfr]*2) for name in binary_predicates]
    
for fn, args in standard_functions:
    mpfr_functions.append((fn, [Mpfr] + args + [RoundingMode], Ternary))

for pred, args in predicates:
    mpfr_functions.append((pred, args, bool))

# set argtypes, restype, errcheck for all functions
for t in mpfr_functions:
    mpfr_fn = getattr(mpfr, 'mpfr_' + t[0])
    if len(t) == 3:
        mpfr_fn.argtypes, mpfr_fn.restype = t[1:]
    else:
        assert len(t) == 4
        mpfr_fn.argtypes, mpfr_fn.restype, mpfr_fn.errcheck = t[1:]

################################################################################
# Some of the MPFR documented functions are implemented as macros, and hence
# aren't available from the libmpfr file.  Here are Python substitutes for
# those functions.

# mpfr_init_set_* are macros; here are corresponding Python functions

def init_set(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set(rop, op, rnd)

def init_set_ui(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_ui(rop, op, rnd)

def init_set_si(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_si(rop, op, rnd)

def init_set_d(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_d(rop, op, rnd)

for macro in ['init_set', 'init_set_ui', 'init_set_si', 'init_set_d']:
    name = 'mpfr_' + macro
    setattr(mpfr, name, globals()[macro])

################################################################################
# Python wrappers for some of the functions that are awkward to use directly

def set_str2(rop, s, base, rnd):
    """Set value of rop from the string s, using given base and rounding mode.

    If s is a valid string for the given base, set the Mpfr variable
    rop from s, rounding in the direction given by 'rnd', and return
    the usual ternary value.

    If s is not a valid string for the given base, raise ValueError.

    """
    if s == s.strip():
        ternary, remainder = strtofr2(rop, s, base, rounding_mode)
        if not remainder:
            return ternary
    raise ValueError("not a valid numeric string")

def get_str2(rop, base, ndigits, rounding_mode):
    """Convert rop to a string in the given base, 2 <= base <= 36.

    The input parameter ndigits gives the number of significant
    digits required.  If ndigits is 0, this function produces a
    number of digits that depends on the precision.

    """
    exp = mpfr_exp_t()
    p = mpfr.mpfr_get_str(None, ctypes.pointer(exp),
                          base, ndigits, rop, rounding_mode)
    result = ctypes.cast(p, ctypes.c_char_p).value
    mpfr.mpfr_free_str(p)

    negative = result.startswith('-')
    if negative:
        result = result[1:]
    return negative, result, exp.value

def strtofr2(rop, s, base, rounding_mode):
    """Set value of rop from string s.

    Returns a pair (t, n) giving the ternary value t and
    the characters that weren't parsed.
    """

    startptr = ctypes.c_char_p(s)
    endptr = ctypes.c_char_p()
    ternary = mpfr.mpfr_strtofr(rop, startptr, ctypes.byref(endptr),
                                base, rounding_mode)
    return ternary, endptr.value

################################################################################
# For ease of debugging, give the Mpfr class a usable __repr__.  This function
# shouldn't be exported.

def _mpfr_repr(self):
    negative, digits, exp = get_str2(self, 10, 0, RoundTiesToEven)
    return ('-' if negative else '') + '0.' + digits + 'E' + str(exp)

Mpfr.__repr__ = _mpfr_repr

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

from __future__ import with_statement  # for Python 2.5

from contextlib import contextmanager
import ctypes
import ctypes.util
import weakref
import os.path

try:
    import bigfloat_config
except ImportError:
    bigfloat_config = None


__all__ = [
    # mpfr library, giving access to the various Python-wrapped MPFR functions
    'mpfr',

    # MPFR major and minor version numbers
    'MPFR_VERSION_MAJOR', 'MPFR_VERSION_MINOR',

    # class implementing the floats themselves (corresponds to mpfr_t)
    'Mpfr',

    # constants giving limits on the precision
    'MPFR_PREC_MIN', 'MPFR_PREC_MAX',

    # constants giving emin and emax values
    'MPFR_EMIN_DEFAULT', 'MPFR_EMIN_MIN', 'MPFR_EMIN_MAX',
    'MPFR_EMAX_DEFAULT', 'MPFR_EMAX_MIN', 'MPFR_EMAX_MAX',

    # rounding modes
    'RoundTiesToEven', 'RoundTowardZero',
    'RoundTowardPositive', 'RoundTowardNegative',

    # lists of standard functions and predicates
    'standard_functions', 'predicates', 'extra_standard_functions',

    # extra functions that aren't part of the mpfr library proper
    'strtofr2', 'remquo2',

    # context manager for temporarily changing exponent bounds
    'eminmax',

    ]

################################################################################
# Locate and load the library

_locate_error_message = """\
Failed to find the MPFR library.  Please ensure that the MPFR library
is installed on your system and is in the library search path.  You
may need to set LD_LIBRARY_PATH (or DYLD_LIBRARY_PATH on OS X) for
this.

If necessary you can edit the 'mpfr_library_location' entry in the
bigfloat_config.py configuration file to give the location of the
library.  This configuration file can be found in the same place that
the bigfloat library was installed:

%s
""" % (os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'bigfloat_config.py'),)

# try the config file first
_mpfr_library_name = getattr(bigfloat_config, 'mpfr_library_location', None)
if not _mpfr_library_name:
    # then try ctypes.find_library
    _mpfr_library_name = ctypes.util.find_library('mpfr')
    if _mpfr_library_name is None:
        raise OSError(_locate_error_message)

mpfr = ctypes.cdll.LoadLibrary(_mpfr_library_name)

# get library version, and check that it's new enough
mpfr.mpfr_get_version.argtypes = []
mpfr.mpfr_get_version.restype = ctypes.c_char_p

_mpfr_version = mpfr.mpfr_get_version()
MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR, _ = _mpfr_version.split('.', 2)
MPFR_VERSION_MAJOR = int(MPFR_VERSION_MAJOR)
MPFR_VERSION_MINOR = int(MPFR_VERSION_MINOR)

if (MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR) < (2, 3):
    raise RuntimeError("This module requires MPFR version 2.3 or later; "
                       "found version %s" % _mpfr_version)

################################################################################
# Platform dependent values

# To do: get these values directly by parsing or processing gmp.h
# It might be possible to use cpp directly to do this, or to
# compile and run a test program that outputs the values.

# True if GMP uses C type 'int' for the mp_size_t and mp_exp_t types,
# and False otherwise (GMP uses C type 'long' in this case).
__GMP_MP_SIZE_T_INT = getattr(bigfloat_config, 'gmp_mp_size_t_int', False)

# True if GMP uses C type 'short' for limbs; otherwise False
__GMP_SHORT_LIMB_DEFINED = getattr(bigfloat_config, 'gmp_short_limb', False)

# True if GMP uses C type 'long long' for limbs; otherwise False
_LONG_LONG_LIMB_DEFINED = getattr(bigfloat_config, 'gmp_long_long_limb', False)

# True if the MPFR library uses type 'signed char' for the enum
# of rounding modes, and False if it uses type 'int'.  On most
# platforms, 'int' is right.
_SHORT_ENUMS = getattr(bigfloat_config, 'mpfr_short_enums', False)

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

PreMpfr = __mpfr_struct * 1

# Wrapper for the PreMpfr type that ensures initialization, and
# automatic calling of mpfr.mpfr_clear when an Mpfr instance goes out
# of scope.

# We ensure mpfr.mpfr_clear gets called by using a suitable weakref
# callback.

class Mpfr(object):
    # Dictionary from weakrefs to PreMpfr instances.
    _values = {}
    def __new__(cls, precision):
        self = object.__new__(cls)
        self._value = PreMpfr()
        wref = weakref.ref(self, self._clear_value)
        self._values[wref] = self._value
        self._initialized = False
        return self

    @classmethod
    def _clear_value(cls, wref):
        mpfr.mpfr_clear(cls._values[wref])
        del cls._values[wref]

    def __init__(self, precision):
        if self._initialized:
            mpfr.mpfr_set_prec(self._value, precision)
        else:
            mpfr.mpfr_init2(self._value, precision)
            self._initialized = True

    @classmethod
    def from_param(cls, self):
        return self._value

    def __repr__(self):
        # Crude but usable string representation for Mpfr type.
        negative, digits, exp = get_str2(self, 10, 0, RoundTiesToEven)
        if '@NaN@' not in digits and '@Inf@' not in digits:
            digits = '0.' + digits + 'E' + str(exp)
        return ('-' if negative else '') + digits

    __str__ = __repr__


# Precision class used for automatic range checking of precisions.
# Arguments of type mpfr_prec_t should use the Precision class.
# Return values of type mpfr_prec_t should just be declared as
# mpfr_prec_t.

class Precision(object):
    @classmethod
    def from_param(cls, value):
        if not MPFR_PREC_MIN <= value <= MPFR_PREC_MAX:
            raise ValueError("precision should be in the range "
                "[%s, %s]" % (MPFR_PREC_MIN, MPFR_PREC_MAX))
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

_inv_rounding_mode_dict = dict((v, k) for k, v in _rounding_mode_dict.items())

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

################################################################################
# Various useful errcheck functions

def error_on_failure(result, func, args):
    if result:
        raise ValueError("call failed")
    return result

def convert_to_rounding_mode(result, func, args):
    return _inv_rounding_mode_dict[result]

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

mpfr_functions = [

    # 5.1: Initialization Functions
    ('init2', [PreMpfr, Precision], None),
    ('clear', [PreMpfr], None),
    ('set_default_prec', [Precision], None),
    ('get_default_prec', [], mpfr_prec_t),
    ('set_prec', [PreMpfr, Precision], None),
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
    # All of these are standard functions, declared below.
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
    ('lgamma', [Mpfr, ctypes.POINTER(ctypes.c_int), Mpfr, RoundingMode],
     Ternary),
    ('free_cache', [], None),

    # we don't wrap mpfr_sum at the moment

    # 5.8 Input and Output Functions
    # 5.9 Formatted Output Functions
    # we don't currently wrap any functions in these two sections

    # 5.10 Integer and Remainder Related Functions
    # note that 'rint' is *not* a standard function: the rounding
    # mode determines the actual operation, not the method of
    # rounding the result.
    ('rint', [Mpfr, Mpfr, RoundingMode], Ternary),
    ('ceil', [Mpfr, Mpfr], Ternary),
    ('floor', [Mpfr, Mpfr], Ternary),
    ('round', [Mpfr, Mpfr], Ternary),
    ('trunc', [Mpfr, Mpfr], Ternary),

    # rint_ceil, rint_floor, rint_round, rint_trunc are standard
    # frac is standard
    # fmod, remainder are standard
    ('remquo', [Mpfr, ctypes.POINTER(ctypes.c_long), Mpfr, Mpfr, RoundingMode],
     Ternary),
    # integer_p is a standard predicate

    # 5.11 Rounding Related Functions
    ('set_default_rounding_mode', [RoundingMode], None),
    ('get_default_rounding_mode', [], mpfr_rnd_t, convert_to_rounding_mode),
    ('prec_round', [Mpfr, Precision, RoundingMode], Ternary),
    ('can_round', [Mpfr, Exponent, RoundingMode, RoundingMode, Precision],
     bool),
    ('print_rnd_mode', [RoundingMode], ctypes.c_char_p),

    # 5.12 Miscellaneous Functions
    ('nexttoward', [Mpfr, Mpfr], None),
    ('nextabove', [Mpfr], None),
    ('nextbelow', [Mpfr], None),
    # min and max are standard functions; see below
    # urandomb not supported
    ('get_exp', [Mpfr], mpfr_exp_t),
    ('set_exp', [Mpfr, Exponent], ctypes.c_int, error_on_failure),
    # signbit is a standard predicate
    # setsign and copysign are standard functions
    ('get_version', [], ctypes.c_char_p),
    ('get_patches', [], ctypes.c_char_p),

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
    # for flag set, clear and test functions see below
    ('clear_flags', [], None),

    # 5.14 Compatibility With MPF
    # 5.15 Custom Interface
    # Functions from 5.14 and 5.15 not wrapped.
    ]

# functions that are new in MPFR version 2.4
if (MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR) >= (2, 4):
    mpfr_functions.extend([
            ('modf', [Mpfr, Mpfr, Mpfr, RoundingMode], Ternary),
            ('sinh_cosh', [Mpfr, Mpfr, Mpfr, RoundingMode], Ternary),
            ])

# additional functions for flags in section 13
mpfr_flags = ['underflow', 'overflow', 'nanflag', 'inexflag', 'erangeflag']
for f in mpfr_flags:
    mpfr_functions.append(('clear_' + f, [], None))
for f in mpfr_flags:
    mpfr_functions.append(('set_' + f, [], None))
for f in mpfr_flags:
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
    'sqr', 'sqrt', 'cbrt',
    'log', 'log2', 'log10',
    'exp', 'exp2', 'exp10',
    'cos', 'sin', 'tan',
    'sec', 'csc', 'cot',
    'acos', 'asin', 'atan',
    'cosh', 'sinh', 'tanh',
    'sech', 'csch', 'coth',
    'acosh', 'asinh', 'atanh',
    'log1p', 'expm1',
    'eint',
    'gamma', 'lngamma',
    'zeta',
    'erf', 'erfc',
    'j0', 'j1', 'y0', 'y1',
    'rint_ceil', 'rint_floor', 'rint_round', 'rint_trunc',
    'frac',
    ]

# functions that are new in MPFR version 2.4
if (MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR) >= (2, 4):
    standard_unary_functions.extend([
            'li2', 'rec_sqrt',
            ])

# standard functions taking two Mpfr instances as input

standard_binary_functions = [
    'add', 'sub', 'mul', 'div', 'pow',
    'dim', 'atan2', 'agm', 'hypot',
    'remainder',
    'max', 'min',
    'copysign',
    ]

# functions that are new in MPFR version 2.4
if (MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR) >= (2, 4):
    standard_binary_functions.extend([
            'fmod',
            ])

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
    ('ui_sub', [UnsignedLong, Mpfr]),
    ('sub_ui', [Mpfr, UnsignedLong]),
    ('si_sub', [Long, Mpfr]),
    ('sub_si', [Mpfr, Long]),
    ('mul_ui', [Mpfr, UnsignedLong]),
    ('mul_si', [Mpfr, Long]),
    ('ui_div', [UnsignedLong, Mpfr]),
    ('div_ui', [Mpfr, UnsignedLong]),
    ('si_div', [Long, Mpfr]),
    ('div_si', [Mpfr, Long]),
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

# functions that are new in MPFR version 2.4
if (MPFR_VERSION_MAJOR, MPFR_VERSION_MINOR) >= (2, 4):
    additional_standard_functions.extend([
            ('add_d', [Mpfr, ctypes.c_double]),
            ('sub_d', [Mpfr, ctypes.c_double]),
            ('d_sub', [ctypes.c_double, Mpfr]),
            ('mul_d', [Mpfr, ctypes.c_double]),
            ('div_d', [Mpfr, ctypes.c_double]),
            ('d_div', [ctypes.c_double, Mpfr]),
            ])

standard_functions = \
    [(name, []) for name in standard_constants] + \
    [(name, [Mpfr]) for name in standard_unary_functions] + \
    [(name, [Mpfr]*2) for name in standard_binary_functions] + \
    [(name, [Mpfr]*3) for name in standard_ternary_functions] + \
    additional_standard_functions

# Additional standard functions that aren't in MPFR itself, but are
# defined by this module.

extra_standard_functions = [
    ('set_str2', [ctypes.c_char_p, Base]),
    ('lgamma_nosign', [Mpfr]),
    ]

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

def _init_set(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set(rop, op, rnd)

def _init_set_ui(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_ui(rop, op, rnd)

def _init_set_si(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_si(rop, op, rnd)

def _init_set_d(rop, op, rnd):
    mpfr.mpfr_init(rop)
    return mpfr.mpfr_set_d(rop, op, rnd)

for macro in ['_init_set', '_init_set_ui', '_init_set_si', '_init_set_d']:
    setattr(mpfr, 'mpfr' + macro, globals()[macro])

# more constants

MPFR_EMIN_MIN = mpfr.mpfr_get_emin_min()
MPFR_EMIN_MAX = mpfr.mpfr_get_emin_max()
MPFR_EMAX_MIN = mpfr.mpfr_get_emax_min()
MPFR_EMAX_MAX = mpfr.mpfr_get_emax_max()

################################################################################
# Python wrappers for some of the functions that are awkward to use directly

def lgamma_nosign(rop, x, rnd):
    """Like mpfr_lgamma, but doesn't return the sign."""

    sign = ctypes.c_int()
    return mpfr.mpfr_lgamma(rop, ctypes.pointer(sign), x, rnd)

mpfr.mpfr_lgamma_nosign = lgamma_nosign

def set_str2(rop, s, base, rnd):
    """Set value of rop from the string s, using given base and rounding mode.

    If s is a valid string for the given base, set the Mpfr variable
    rop from s, rounding in the direction given by 'rnd', and return
    the usual ternary value.

    If s is not a valid string for the given base, raise ValueError.

    """
    if s == s.strip():
        ternary, remainder = strtofr2(rop, s, base, rnd)
        if not remainder:
            return ternary
    raise ValueError("not a valid numeric string")

mpfr.mpfr_set_str2 = set_str2

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

mpfr.mpfr_get_str2 = get_str2

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

def remquo2(r, x, y, rnd):
    """Set r to the value of x-ny, and also return low bits of quotient n.

    Returns a pair (ternary, q)."""
    q = ctypes.c_long()
    ternary = mpfr.mpfr_remquo(r, ctypes.byref(q), x, y, rnd)
    return ternary, q


################################################################################
# Context manager to give an easy way to change emin and emax temporarily.

@contextmanager
def eminmax(emin, emax):
    old_emin = mpfr.mpfr_get_emin()
    old_emax = mpfr.mpfr_get_emax()
    mpfr.mpfr_set_emin(emin)
    mpfr.mpfr_set_emax(emax)
    try:
        yield
    finally:
        mpfr.mpfr_set_emin(old_emin)
        mpfr.mpfr_set_emax(old_emax)

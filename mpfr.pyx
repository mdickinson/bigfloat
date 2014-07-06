# -*- coding: utf-8 -*-
# cython: embedsignature = True

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

cimport cmpfr

import sys

cdef extern from "limits.h":
    cdef long LONG_MAX
    cdef long LONG_MIN


###############################################################################
# Various constants exported to Python
###############################################################################

# Make LONG_MAX and LONG_MIN available to Python.  These are the limits of
# values accepted by functions like e.g., mpfr_set_si.
_LONG_MAX = LONG_MAX
_LONG_MIN = LONG_MIN

# Make precision limits available to Python
MPFR_PREC_MIN = cmpfr.MPFR_PREC_MIN
MPFR_PREC_MAX = cmpfr.MPFR_PREC_MAX

# Make rounding mode values available to Python
MPFR_RNDN =  cmpfr.MPFR_RNDN
MPFR_RNDZ =  cmpfr.MPFR_RNDZ
MPFR_RNDU =  cmpfr.MPFR_RNDU
MPFR_RNDD =  cmpfr.MPFR_RNDD
MPFR_RNDA =  cmpfr.MPFR_RNDA

# Default values for Emax and Emin
MPFR_EMAX_DEFAULT = cmpfr.MPFR_EMAX_DEFAULT
MPFR_EMIN_DEFAULT = cmpfr.MPFR_EMIN_DEFAULT


###############################################################################
# Helper functions, not exposed to Python
###############################################################################

# Forward declaration
cdef class Mpfr_t

# Checks for valid parameter ranges
cdef int check_rounding_mode(cmpfr.mpfr_rnd_t rnd) except -1:
    """
    Check that the given rounding mode is valid.  Raise ValueError if not.

    """
    if MPFR_RNDN <= rnd <= MPFR_RNDA:
        return 0
    else:
        raise ValueError("invalid rounding mode {}".format(rnd))


cdef int check_base(int b, int allow_zero) except -1:
    """
    Check that the given base (for string conversion) is valid.

    Raise ValueError if not.

    """
    if allow_zero:
        if 2 <= b <= 62 or b == 0:
            return 0
        else:
            raise ValueError(
                "base should be zero or in the range 2 to 62 (inclusive)"
            )
    else:
        if 2 <= b <= 62:
            return 0
        else:
            raise ValueError("base should be in the range 2 to 62 (inclusive)")


cdef int check_get_str_n(size_t n) except -1:
    """
    Check that the given number of requested digits is valid.

    Raise ValueError if not.

    """
    if n == 0 or 2 <= n:
        return 0
    else:
        raise ValueError("n should be either 0 or at least 2")


cdef int check_precision(cmpfr.mpfr_prec_t precision) except -1:
    """
    Check that the given precision is valid.  Raise ValueError if not.

    """
    if MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
        return 0
    else:
        raise ValueError(
            "precision should be between {} and {}".format(
                MPFR_PREC_MIN, MPFR_PREC_MAX
            )
        )


cdef int check_initialized(Mpfr_t x) except -1:
    """
    Check that the given Mpfr_t x instance has been initialized.

    Raise ValueError if not.

    """
    if not cmpfr_initialized_p(&x._value):
        raise ValueError(
            "Mpfr_t instance {} should be initialized before use".format(x)
        )


cdef int check_not_initialized(Mpfr_t x) except -1:
    """
    Check that the given Mpfr_t x instance has *not* been initialized.

    Raise ValueError if it has.  This function is used by the mpfr_init
    and mpfr_init2 functions.

    """
    if cmpfr_initialized_p(&x._value):
        raise ValueError(
            "Mpfr_t instance {} is already initialized.".format(x)
        )


cdef decode_ternary_pair(int ternary_pair):
    """
    Decode an encoded pair of ternary values.

    Some MPFR functions with two outputs (mpfr_sin_cos, mpfr_sinh_cosh,
    mpfr_modf) also return a pair of ternary values encoded into a single int.
    This function decodes that ternary pair, returning a Python pair of
    the corresponding ternary values.

    """
    cdef int first_ternary, second_ternary

    first_ternary = ternary_pair & 3
    if first_ternary == 2:
        first_ternary = -1
    second_ternary = ternary_pair >> 2
    if second_ternary == 2:
        second_ternary = -1
    return first_ternary, second_ternary


cdef int cmpfr_initialized_p(cmpfr.mpfr_ptr op):
    """
    Return non-zero if op is initialized.  Return zero otherwise.

    """
    return op._mpfr_d != NULL


###############################################################################
# The main Python extension type, based on mpfr_t.
###############################################################################

cdef class Mpfr_t:
    """
    Mutable arbitrary-precision binary floating-point numbers.

    Mpfr_t() -> new, uninitialized Mpfr object

    Mpfr_t() creates a new, uninitialized Mpfr_t object.  This object must be
    initialized before use, for example by using the mpfr_init2 function.
    However, unlike the underlying MPFR library, it's not necessary to clear
    the object when it's no longer used.

    """
    cdef cmpfr.__mpfr_struct _value

    def __dealloc__(self):
        if cmpfr_initialized_p(&self._value):
            cmpfr.mpfr_clear(&self._value)


##############################################################################
# Additional functions provided by this extension module
###############################################################################

def mpfr_initialized_p(Mpfr_t op not None):
    """
    Return True if op has been initialized.  Return False otherwise.

    """
    return bool(cmpfr_initialized_p(&op._value))


##############################################################################
# 5.1 Initialization Functions
###############################################################################

def mpfr_init2(Mpfr_t x not None, cmpfr.mpfr_prec_t prec):
    """
    Initialize x, set its precision to be prec bits and its value to NaN.

    Normally, a variable should be initialized once only or at least be
    cleared, using mpfr_clear, between initializations. To change the precision
    of a variable which has already been initialized, use mpfr_set_prec. The
    precision prec must be an integer between MPFR_PREC_MIN and MPFR_PREC_MAX
    (otherwise the behavior is undefined).

    """
    check_not_initialized(x)
    check_precision(prec)
    cmpfr.mpfr_init2(&x._value, prec)

def mpfr_inits2(cmpfr.mpfr_prec_t prec, *args):
    """
    Initialize each of the variables in args: set its precision to prec bits
    and its value to NaN.

    """
    check_precision(prec)
    for arg in args:
        mpfr_init2(arg, prec)

def mpfr_clear(Mpfr_t x not None):
    """
    Free the space occupied by the significand of x.

    It's not usually necessary to call this function directly: it will be
    called automatically when x is garbage-collected.

    """
    check_initialized(x)
    cmpfr.mpfr_clear(&x._value)

def mpfr_clears(*args):
    """
    Free the space occupied by each of the variables in args.  See mpfr_clear
    for more details.

    """
    for arg in args:
        mpfr_clear(arg)

def mpfr_init(Mpfr_t x not None):
    """
    Initialize x, set its precision to the default precision, and set its value
    to NaN. The default precision can be changed by a call to
    mpfr_set_default_prec.

    Warning! In a given program, some other libraries might change the default
    precision and not restore it. Thus it is safer to use mpfr_init2.

    """
    check_not_initialized(x)
    cmpfr.mpfr_init(&x._value)

def mpfr_inits(*args):
    """
    Initialize each of the variables in args: set its precision to the default
    precision, and set its value to NaN. The default precision can be changed
    by a call to mpfr_set_default_prec.

    Warning! In a given program, some other libraries might change the default
    precision and not restore it. Thus it is safer to use mpfr_inits2.

    """
    for arg in args:
        mpfr_init(arg)

def mpfr_set_default_prec(cmpfr.mpfr_prec_t prec):
    """
    Set the default precision to be exactly prec bits.

    prec can be any integer between MPFR_PREC_MIN and MPFR_PREC_MAX. The
    precision of a variable means the number of bits used to store its
    significand. All subsequent calls to mpfr_init or mpfr_inits will use this
    precision, but previously initialized variables are unaffected. The default
    precision is set to 53 bits initially.

    """
    check_precision(prec)
    cmpfr.mpfr_set_default_prec(prec)

def mpfr_get_default_prec():
    """
    Return the current default MPFR precision in bits.

    """
    return cmpfr.mpfr_get_default_prec()

def mpfr_set_prec(Mpfr_t x not None, cmpfr.mpfr_prec_t prec):
    """
    Reset precision of x.

    Reset the precision of x to be exactly prec bits, and set its value to
    NaN. The previous value stored in x is lost. It is equivalent to a call to
    mpfr_clear(x) followed by a call to mpfr_init2(x, prec), but more efficient
    as no allocation is done in case the current allocated space for the
    significand of x is enough. The precision prec can be any integer between
    MPFR_PREC_MIN and MPFR_PREC_MAX. In case you want to keep the previous
    value stored in x, use mpfr_prec_round instead.

    """
    check_initialized(x)
    check_precision(prec)
    cmpfr.mpfr_set_prec(&x._value, prec)

def mpfr_get_prec(Mpfr_t x not None):
    """
    Return the precision of x

    Returns the number of bits used to store the significand of x.

    """
    check_initialized(x)
    return cmpfr.mpfr_get_prec(&x._value)


###############################################################################
# 5.2 Assignment Functions
###############################################################################

def mpfr_set(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop from op, rounded in the direction rnd.

    Set the value of rop from the value of the Mpfr_t object op, rounded toward
    the given direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set(&rop._value, &op._value, rnd)

def mpfr_set_si(Mpfr_t rop not None, long int op, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from a Python int, rounded in the direction rnd.

    Set the value of rop from op, rounded toward the given direction rnd. Note
    that the input 0 is converted to +0, regardless of the rounding mode.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_si(&rop._value, op, rnd)

def mpfr_set_d(Mpfr_t rop not None, double op, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from a Python float op, rounded in the direction rnd.

    Set the value of rop from op, rounded toward the given direction rnd.  If
    the system does not support the IEEE 754 standard, mpfr_set_d might not
    preserve the signed zeros.

    Note: If you want to store a floating-point constant to an Mpfr_t object, you
    should use mpfr_set_str (or one of the MPFR constant functions, such as
    mpfr_const_pi for Pi) instead of mpfr_set_d.  Otherwise the floating-point
    constant will be first converted into a reduced-precision (e.g., 53-bit)
    binary number before MPFR can work with it.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_d(&rop._value, op, rnd)

def mpfr_set_si_2exp(Mpfr_t rop not None, long int op,
                     cmpfr.mpfr_exp_t e, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op multiplied by a power of 2.

    Set the value of rop from op multiplied by two to the power e, rounded
    toward the given direction rnd. Note that the input 0 is converted to +0.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_si_2exp(&rop._value, op, e, rnd)

def mpfr_set_str(Mpfr_t rop not None, object s, int base, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop from a string s.

    Set rop to the value of the string s in base base, rounded in the direction
    rnd. See the documentation of mpfr_strtofr for a detailed description of
    the valid string formats. Contrary to mpfr_strtofr, mpfr_set_str requires
    the whole string to represent a valid floating-point number. This function
    returns 0 if the entire string up to the final null character is a valid
    number in base base; otherwise it returns −1, and rop may have
    changed. Note: it is preferable to use mpfr_strtofr if one wants to
    distinguish between an infinite rop value coming from an infinite s or from
    an overflow.

    """
    cdef bytes bytes_s
    bytes_s = s.encode('ascii')
    check_initialized(rop)
    check_base(base, False)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_str(&rop._value, bytes_s, base, rnd)

def mpfr_strtofr(Mpfr_t rop not None, object s, int base, cmpfr.mpfr_rnd_t rnd):
    """
    Read a floating-point number from a string.

    Read a floating-point number from a string s in base base, rounded in
    the direction rnd; base must be either 0 (to detect the base, as described
    below) or a number from 2 to 62 (otherwise the behavior is undefined).

    If s starts with valid data, the result is stored in rop and the function
    returns a pair (ternary, endindex) where ternary is the usual ternary
    return value and endindex gives the index of the character just after the
    valid data.  Otherwise rop is set to zero (for consistency with strtod) and
    endindex is 0.

    Parsing follows the standard C strtod function with some extensions. After
    optional leading whitespace, one has a subject sequence consisting of an
    optional sign (+ or -), and either numeric data or special data. The
    subject sequence is defined as the longest initial subsequence of the input
    string, starting with the first non-whitespace character, that is of the
    expected form.

    The form of numeric data is a non-empty sequence of significand digits with
    an optional decimal point, and an optional exponent consisting of an
    exponent prefix followed by an optional sign and a non-empty sequence of
    decimal digits. A significand digit is either a decimal digit or a Latin
    letter (62 possible characters), with A = 10, B = 11, ..., Z = 35; case is
    ignored in bases less or equal to 36, in bases larger than 36, a = 36, b =
    37, ..., z = 61. The value of a significand digit must be strictly less
    than the base. The decimal point can be either the one defined by the
    current locale or the period (the first one is accepted for consistency
    with the C standard and the practice, the second one is accepted to allow
    the programmer to provide MPFR numbers from strings in a way that does not
    depend on the current locale). The exponent prefix can be e or E for bases
    up to 10, or @ in any base; it indicates a multiplication by a power of the
    base. In bases 2 and 16, the exponent prefix can also be p or P, in which
    case the exponent, called binary exponent, indicates a multiplication by a
    power of 2 instead of the base (there is a difference only for base 16); in
    base 16 for example 1p2 represents 4 whereas 1@2 represents 256. The value
    of an exponent is always written in base 10.

    If the argument base is 0, then the base is automatically detected as
    follows. If the significand starts with 0b or 0B, base 2 is assumed. If the
    significand starts with 0x or 0X, base 16 is assumed. Otherwise base 10 is
    assumed.

    Note: The exponent (if present) must contain at least a digit. Otherwise
    the possible exponent prefix and sign are not part of the number (which
    ends with the significand). Similarly, if 0b, 0B, 0x or 0X is not followed
    by a binary/hexadecimal digit, then the subject sequence stops at the
    character 0, thus 0 is read.

    Special data (for infinities and NaN) can be @inf@ or
    @nan@(n-char-sequence-opt), and if base <= 16, it can also be infinity,
    inf, nan or nan(n-char-sequence-opt), all case insensitive. A
    n-char-sequence-opt is a possibly empty string containing only digits,
    Latin letters and the underscore (0, 1, 2, ..., 9, a, b, ..., z, A, B, ...,
    Z, _). Note: one has an optional sign for all data, even NaN. For example,
    -@nAn@(This_Is_Not_17) is a valid representation for NaN in base 17.

    """
    cdef char* endptr
    cdef char* startptr
    cdef bytes bytes_s
    bytes_s = s.encode('ascii')

    startptr = bytes_s

    check_initialized(rop)
    check_base(base, True)
    check_rounding_mode(rnd)
    ternary = cmpfr.mpfr_strtofr(
        &rop._value,
        bytes_s,
        &endptr,
        base,
        rnd,
    )
    endindex = endptr - startptr
    return ternary, endindex

def mpfr_set_nan(Mpfr_t op not None):
    """ Set x to a NaN.

    Set the variable x to NaN (Not-a-Number).  The sign bit of the result is
    unspecified.

    """
    check_initialized(op)
    cmpfr.mpfr_set_nan(&op._value)

def mpfr_set_inf(Mpfr_t op not None, int sign):
    """ Set x to an infinity.

    Set the variable x to infinity.  x is set to positive infinity if the sign
    is nonnegative, and negative infinity otherwise.

    Note the unusual sign convention here: most MPFR function that deal with
    signs use a nonzero value (or True) to indicate a negative number, and zero
    to indiciate a positive number.

    """
    check_initialized(op)
    cmpfr.mpfr_set_inf(&op._value, sign)

def mpfr_set_zero(Mpfr_t op not None, int sign):
    """ Set x to a zero.

    Set the variable x to zero.  x is set to positive zero if the sign is
    nonnegative, and negative zero otherwise.

    Note the unusual sign convention here: most MPFR function that deal with
    signs use a nonzero value (or True) to indicate a negative number, and zero
    to indiciate a positive number.

    """
    check_initialized(op)
    cmpfr.mpfr_set_zero(&op._value, sign)

def mpfr_swap(Mpfr_t x not None, Mpfr_t y not None):
    """
    Swap the values of x and y efficiently.

    Warning: the precisions are exchanged too; in case the precisions are
    different, mpfr_swap is thus not equivalent to three mpfr_set calls using a
    third auxiliary variable.

    """
    check_initialized(x)
    check_initialized(y)
    cmpfr.mpfr_swap(&x._value, &y._value)


###############################################################################
# 5.4 Conversion Functions
###############################################################################

def mpfr_get_d(Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Convert op to a Python float.

    Convert op to a Python float using the rounding mode rnd. If op is NaN,
    some fixed NaN (either quiet or signaling) or the result of 0.0/0.0 is
    returned. If op is ±Inf, an infinity of the same sign or the result of
    ±1.0/0.0 is returned. If op is zero, this function returns a zero, trying
    to preserve its sign, if possible.

    """
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_get_d(&op._value, rnd)

def mpfr_get_si(Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Convert op to a Python int.

    Convert op to a Python int after rounding it with respect to rnd. If op is
    NaN, 0 is returned and the erange flag is set. If op is too big for a
    Python int, the function returns the maximum or the minimum representable
    int, depending on the direction of the overflow; the erange flag is set
    too.

    """
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_get_si(&op._value, rnd)

def mpfr_get_d_2exp(Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Convert op to a Python float and an exponent.

    Return a pair (d, exp) consisting of a Python float d and an exponent exp
    such that 0.5<=abs(d)<1 and d times 2 raised to exp equals op rounded to
    double (resp. long double) precision, using the given rounding mode. If op
    is zero, then a zero of the same sign (or an unsigned zero, if the
    implementation does not have signed zeros) is returned, and exp is set to
    0. If op is NaN or an infinity, then the corresponding double precision
    (resp. long-double precision) value is returned, and exp is undefined.

    """
    cdef long int exp
    cdef double d

    check_initialized(op)
    check_rounding_mode(rnd)
    d =  cmpfr.mpfr_get_d_2exp(&exp, &op._value, rnd)
    return d, exp

def mpfr_get_str(int b, size_t n, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Compute a base 'b' string representation for 'op'.

    Convert op to a string of digits in base b, with rounding in the direction
    rnd, where n is either zero (see below) or the number of significant digits
    output in the string; in the latter case, n must be greater or equal to
    2. The base may vary from 2 to 62.  Returns a pair (digits, exp) where
    digits gives the base-b digits of op, and for an ordinary number, exp is
    the exponent (for input 0, the current minimal exponent is written).

    The generated string is a fraction, with an implicit radix point
    immediately to the left of the first digit. For example, the number −3.1416
    would be returned as ("−31416", 1). If rnd is to nearest, and op is exactly
    in the middle of two consecutive possible outputs, the one with an even
    significand is chosen, where both significands are considered with the
    exponent of op. Note that for an odd base, this may not correspond to an
    even last digit: for example with 2 digits in base 7, (14) and a half is
    rounded to (15) which is 12 in decimal, (16) and a half is rounded to (20)
    which is 14 in decimal, and (26) and a half is rounded to (26) which is 20
    in decimal.

    If n is zero, the number of digits of the significand is chosen large
    enough so that re-reading the printed value with the same precision,
    assuming both output and input use rounding to nearest, will recover the
    original value of op. More precisely, in most cases, the chosen precision
    of str is the minimal precision m depending only on p = PREC(op) and b that
    satisfies the above property, i.e., m = 1 + ceil(p*log(2)/log(b)), with p
    replaced by p−1 if b is a power of 2, but in some very rare cases, it might
    be m+1 (the smallest case for bases up to 62 is when p equals 186564318007
    for bases 7 and 49).

    Space for the digit string is automatically allocated, and freed by Python
    when no longer needed.  There's no requirement to free this space manually.

    RuntimeError is raised on error.

    """
    cdef cmpfr.mpfr_exp_t exp
    cdef bytes digits
    cdef char *c_digits

    check_base(b, False)
    check_get_str_n(n)
    check_initialized(op)
    check_rounding_mode(rnd)
    c_digits = cmpfr.mpfr_get_str(NULL, &exp, b, n, &op._value, rnd)
    if c_digits == NULL:
        raise RuntimeError("Error during string conversion.")

    # It's possible for the conversion from c_digits to digits to raise, so use
    # a try-finally block to ensure that c_digits always gets freed.
    try:
        digits = bytes(c_digits)
    finally:
        cmpfr.mpfr_free_str(c_digits)

    if sys.version_info < (3,):
        return digits, exp
    else:
        return digits.decode('ascii'), exp

def mpfr_fits_slong_p(Mpfr_t x not None, cmpfr.mpfr_rnd_t rnd):
    """
    Return True if op would fit into a Python int.

    Return True if op would fit into a Python int when rounded to an integer
    in the direction rnd.

    """
    check_initialized(x)
    check_rounding_mode(rnd)
    return bool(cmpfr.mpfr_fits_slong_p(&x._value, rnd))


###############################################################################
# 5.5 Basic Arithmetic Functions
###############################################################################

def mpfr_add(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 + op2 rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_add(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_sub(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 - op2, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sub(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_mul(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 times op2, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_mul(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_sqr(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the square of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sqr(&rop._value, &op._value, rnd)

def mpfr_div(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 divided by op2, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_div(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_sqrt(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the square root of op, rounded in the direction rnd.

    Set rop to −0 if op is −0, to be consistent with the IEEE 754 standard. Set
    rop to NaN if op is negative.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sqrt(&rop._value, &op._value, rnd)

def mpfr_rec_sqrt(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the reciprocal square root of op, rounded in the direction rnd.

    Set rop to +Inf if op is ±0, +0 if op is +Inf, and NaN if op is negative.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rec_sqrt(&rop._value, &op._value, rnd)

def mpfr_cbrt(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the cube root of op rounded in the direction rnd.

    For op negative, set rop to a negative number.  The cube root of -0 is
    defined to be -0.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_cbrt(&rop._value, &op._value, rnd)

def mpfr_root(Mpfr_t rop not None, Mpfr_t op not None,
              unsigned long int k, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the kth root of op, rounding in the direction rnd.

    For k odd (resp. even) and op negative (including −Inf), set rop to a
    negative number (resp. NaN). The kth root of −0 is defined to be −0,
    whatever the parity of k.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_root(&rop._value, &op._value, k, rnd)

def mpfr_pow(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 raised to the power op2, rounded in the direction rnd.

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
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_pow(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_neg(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to -op, rounded in the direction rnd.

    This function just changes or adjusts the sign if rop and op are the same
    variable, otherwise a rounding might occur if the precision of rop is less
    than that of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_neg(&rop._value, &op._value, rnd)

def mpfr_abs(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the absolute value of op, rounded in the direction rnd.

    This function just changes or adjusts the sign if rop and op are the same
    variable, otherwise a rounding might occur if the precision of rop is less
    than that of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_abs(&rop._value, &op._value, rnd)

def mpfr_dim(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to max(op1 - op2, 0), rounded in the direction rnd.

    Set rop to op1 - op2 rounded in the direction rnd if op1 > op2, +0 if op1
    <= op2, and NaN if op1 or op2 is NaN.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_dim(&rop._value, &op1._value, &op2._value, rnd)


###############################################################################
# 5.6 Comparison Functions
###############################################################################

def mpfr_cmp(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Perform a three-way comparison of op1 and op2.

    Return a positive value if op1 > op2, zero if op1 = op2, and a negative
    value if op1 < op2. Both op1 and op2 are considered to their full own
    precision, which may differ. If one of the operands is NaN, set the erange
    flag and return zero.

    Note: This function may be useful to distinguish the three possible
    cases. If you need to distinguish two cases only, it is recommended to use
    the predicate functions (e.g., mpfr_equal_p for the equality) described
    below; they behave like the IEEE 754 comparisons, in particular when one or
    both arguments are NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return cmpfr.mpfr_cmp(&op1._value, &op2._value)

def mpfr_cmpabs(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Compare the absolute values of op1 and op2.

    Compare |op1| and |op2|. Return a positive value if |op1| > |op2|, zero if
    |op1| == |op2|, and a negative value if |op1| < |op2|. If one of the
    operands is NaN, set the erange flag and return zero.

    """
    check_initialized(op1)
    check_initialized(op2)
    return cmpfr.mpfr_cmpabs(&op1._value, &op2._value)

def mpfr_nan_p(Mpfr_t op not None):
    """
    Return True if op is a NaN.  Return False otherwise.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_nan_p(&op._value))

def mpfr_inf_p(Mpfr_t op not None):
    """
    Return True if op is an infinity.  Return False otherwise.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_inf_p(&op._value))

def mpfr_number_p(Mpfr_t op not None):
    """
    Return True if op is an ordinary number.  Return False otherwise.

    An ordinary number is a number which is neither a NaN nor an infinity.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_number_p(&op._value))

def mpfr_zero_p(Mpfr_t op not None):
    """
    Return True if op is zero.  Return False otherwise.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_zero_p(&op._value))

def mpfr_regular_p(Mpfr_t op not None):
    """
    Return True if op is a regular number.  Return False otherwise.

    A regular number is a number which is neither a NaN, nor an infinity, nor a
    zero.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_regular_p(&op._value))

def mpfr_sgn(Mpfr_t op not None):
    """
    Return the sign of op.

    Return a positive value if op > 0, zero if op = 0, and a negative value if
    op < 0. If the operand is NaN, set the erange flag and return zero. This is
    equivalent to mpfr_cmp_ui (op, 0), but more efficient.

    """
    check_initialized(op)
    return cmpfr.mpfr_sgn(&op._value)

def mpfr_greater_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 > op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_greater_p(&op1._value, &op2._value))

def mpfr_greaterequal_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 >= op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_greaterequal_p(&op1._value, &op2._value))

def mpfr_less_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 < op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_less_p(&op1._value, &op2._value))

def mpfr_lessequal_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 <= op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_lessequal_p(&op1._value, &op2._value))

def mpfr_equal_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 == op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_equal_p(&op1._value, &op2._value))

def mpfr_lessgreater_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 < op2 or op1 > op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_lessgreater_p(&op1._value, &op2._value))

def mpfr_unordered_p(Mpfr_t op1 not None, Mpfr_t op2 not None):
    """
    Return True if op1 or op2 is a NaN and False otherwise.

    """
    check_initialized(op1)
    check_initialized(op2)
    return bool(cmpfr.mpfr_unordered_p(&op1._value, &op2._value))


###############################################################################
# 5.7 Special Functions
###############################################################################

def mpfr_log(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the natural logarithm of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log(&rop._value, &op._value, rnd)

def mpfr_log2(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the base-two logarithm of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log2(&rop._value, &op._value, rnd)

def mpfr_log10(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the base-ten logarithm of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log10(&rop._value, &op._value, rnd)

def mpfr_exp(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the exponential of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_exp(&rop._value, &op._value, rnd)

def mpfr_exp2(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to two raised to the power op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_exp2(&rop._value, &op._value, rnd)

def mpfr_exp10(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to ten raised to the power op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_exp10(&rop._value, &op._value, rnd)

def mpfr_cos(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the cosine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_cos(&rop._value, &op._value, rnd)

def mpfr_sin(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the sine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sin(&rop._value, &op._value, rnd)

def mpfr_tan(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the tangent of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_tan(&rop._value, &op._value, rnd)

def mpfr_sin_cos(Mpfr_t sop not None, Mpfr_t cop not None,
                 Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Compute sin(op) and cos(op), rounded in the direction rnd.

    Set simultaneously sop to the sine of op and cop to the cosine of op,
    rounded in the direction rnd with the corresponding precisions of sop and
    cop, which must be different variables.

    Returns a pair (sin_ternary, cos_ternary) of the corresponding ternary
    values.  Note that this differs from the original mpfr_sin_cos function
    from MPFR, which combines the ternary values into a single int return.

    """
    cdef int ternary_pair

    check_initialized(sop)
    check_initialized(cop)
    check_initialized(op)
    check_rounding_mode(rnd)
    ternary_pair = cmpfr.mpfr_sin_cos(
        &sop._value, &cop._value, &op._value, rnd
    )
    return decode_ternary_pair(ternary_pair)

def mpfr_sec(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the secant of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sec(&rop._value, &op._value, rnd)

def mpfr_csc(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the cosecant of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_csc(&rop._value, &op._value, rnd)

def mpfr_cot(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the cotangent of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_cot(&rop._value, &op._value, rnd)

def mpfr_acos(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the arc-cosine of op, rounded in the direction rnd.

    The result will usually be in the range [0, Pi].  However, note that since
    acos(-1) returns the floating-point number closest to Pi according to the
    given rounding mode, this number might not be in the output range [0, Pi];
    still, the result lies in the image of this output range by the rounding
    function.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_acos(&rop._value, &op._value, rnd)

def mpfr_asin(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the arc-sine of op, rounded in the direction rnd.

    The result will usually be in the range [-Pi/2, Pi/2].  However, note that
    since asin(-1) and asin(1) return the floating-point numbers closest to
    -Pi/2 and Pi/2 (respectively) according to the given rounding mode, these
    numbers might not be in the output range [-Pi/2, Pi/2]; still, the result
    lies in the image of this output range by the rounding function.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_asin(&rop._value, &op._value, rnd)

def mpfr_atan(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the arc-tangent of op, rounded in the direction rnd.

    The result will usually be in the range [-Pi/2, Pi/2].  However, note that
    since atan(-inf) and atan(inf) return the floating-point numbers closest to
    -Pi/2 and Pi/2 (respectively) according to the given rounding mode, these
    numbers might not be in the output range [-Pi/2, Pi/2]; still, the result
    lies in the image of this output range by the rounding function.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_atan(&rop._value, &op._value, rnd)

def mpfr_atan2(Mpfr_t rop not None, Mpfr_t y not None,
               Mpfr_t x not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to atan(y / x) with the appropriate choice of function branch.

    Set rop to the arc-tangent2 of y and x, rounded in the direction rnd: if x
    > 0, atan2(y, x) = atan (y/x); if x < 0, atan2(y, x) = sign(y)*(Pi - atan
    (abs(y/x))), thus a number from -Pi to Pi. As for atan, in case the exact
    mathematical result is +Pi or -Pi, its rounded result might be outside the
    function output range.

    atan2(y, 0) does not raise any floating-point exception. Special values are
    handled as described in the ISO C99 and IEEE 754-2008 standards for the
    atan2 function:

    atan2(+0, -0) returns +Pi.
    atan2(-0, -0) returns -Pi.
    atan2(+0, +0) returns +0.
    atan2(-0, +0) returns −0.
    atan2(+0, x) returns +Pi for x < 0.
    atan2(-0, x) returns -Pi for x < 0.
    atan2(+0, x) returns +0 for x > 0.
    atan2(-0, x) returns −0 for x > 0.
    atan2(y, 0) returns -Pi/2 for y < 0.
    atan2(y, 0) returns +Pi/2 for y > 0.
    atan2(+Inf, -Inf) returns +3*Pi/4.
    atan2(-Inf, -Inf) returns -3*Pi/4.
    atan2(+Inf, +Inf) returns +Pi/4.
    atan2(-Inf, +Inf) returns -Pi/4.
    atan2(+Inf, x) returns +Pi/2 for finite x.
    atan2(-Inf, x) returns -Pi/2 for finite x.
    atan2(y, -Inf) returns +Pi for finite y > 0.
    atan2(y, -Inf) returns -Pi for finite y < 0.
    atan2(y, +Inf) returns +0 for finite y > 0.
    atan2(y, +Inf) returns −0 for finite y < 0.

    """
    check_initialized(rop)
    check_initialized(y)
    check_initialized(x)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_atan2(&rop._value, &y._value, &x._value, rnd)

def mpfr_cosh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic cosine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_cosh(&rop._value, &op._value, rnd)

def mpfr_sinh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic sine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sinh(&rop._value, &op._value, rnd)

def mpfr_tanh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic tangent of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_tanh(&rop._value, &op._value, rnd)

def mpfr_sinh_cosh(Mpfr_t sop not None, Mpfr_t cop not None,
                   Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Compute sinh(op) and cosh(op), rounded in the direction rnd.

    Set simultaneously sop to the hyperbolic sine of op and cop to the
    hyperbolic cosine of op, rounded in the direction rnd with the
    corresponding precisions of sop and cop, which must be different variables.

    Returns a pair (sinh_ternary, cosh_ternary) of the corresponding ternary
    values.  Note that this differs from the original mpfr_sinh_cosh function
    from MPFR, which combines the ternary values into a single int return.

    """
    cdef int ternary_pair

    check_initialized(sop)
    check_initialized(cop)
    check_initialized(op)
    check_rounding_mode(rnd)
    ternary_pair = cmpfr.mpfr_sinh_cosh(
        &sop._value, &cop._value, &op._value, rnd
    )
    return decode_ternary_pair(ternary_pair)

def mpfr_sech(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic secant of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sech(&rop._value, &op._value, rnd)

def mpfr_csch(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic cosecant of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_csch(&rop._value, &op._value, rnd)

def mpfr_coth(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the hyperbolic cotangent of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_coth(&rop._value, &op._value, rnd)

def mpfr_acosh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the inverse hyperbolic cosine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_acosh(&rop._value, &op._value, rnd)

def mpfr_asinh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the inverse hyperbolic sine of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_asinh(&rop._value, &op._value, rnd)

def mpfr_atanh(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the inverse hyperbolic tangent of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_atanh(&rop._value, &op._value, rnd)

def mpfr_fac_ui(Mpfr_t rop not None, unsigned long int op, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the factorial of op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fac_ui(&rop._value, op, rnd)

def mpfr_log1p(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the logarithm of one plus op, rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log1p(&rop._value, &op._value, rnd)

def mpfr_expm1(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the exponential of op followed by a subtraction by one, rounded
    in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_expm1(&rop._value, &op._value, rnd)

def mpfr_eint(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the exponential integral of op, rounded in the direction
    rnd.

    For positive op, the exponential integral is the sum of Euler's constant,
    of the logarithm of op, and of the sum for k from 1 to infinity of op to
    the power k, divided by k and factorial(k). For negative op, rop is set to
    NaN.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_eint(&rop._value, &op._value, rnd)

def mpfr_li2(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to real part of the dilogarithm of op, rounded in the direction
    rnd.

    MPFR defines the dilogarithm function as the integral of -log(1-t)/t from 0
    to op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_li2(&rop._value, &op._value, rnd)

def mpfr_gamma(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the Gamma function on op, rounded in the direction
    rnd.

    When op is a negative integer, rop is set to NaN.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_gamma(&rop._value, &op._value, rnd)

def mpfr_lngamma(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the logarithm of the Gamma function on op, rounded
    in the direction rnd.

    When −2k−1 <= op <= −2k, k being a non-negative integer, rop is set to
    NaN. See also mpfr_lgamma.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_lngamma(&rop._value, &op._value, rnd)

def mpfr_lgamma(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the logarithm of the absolute value of the Gamma
    function on op, rounded in the direction rnd.

    Return a pair (ternary, sign) where ternary is the usual ternary value and
    sign is the sign (1 or -1) of Gamma(rop).

    When op is an infinity or a non-positive integer, set rop to +Inf. When op
    is NaN, −Inf or a negative integer, signp is undefined, and when op is ±0,
    signp is the sign of the zero.

    """
    cdef int signp

    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    ternary = cmpfr.mpfr_lgamma(
        &rop._value, &signp, &op._value, rnd
    )
    return ternary, signp

def mpfr_digamma(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the Digamma (sometimes also called Psi) function on
    op, rounded in the direction rnd.

    When op is a negative integer, set rop to NaN.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_digamma(&rop._value, &op._value, rnd)

def mpfr_zeta(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the Riemann Zeta function on op, rounded in the
    direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_zeta(&rop._value, &op._value, rnd)

def mpfr_zeta_ui(Mpfr_t rop not None, unsigned long int op, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the Riemann Zeta function on op, rounded in the
    direction rnd.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_zeta_ui(&rop._value, op, rnd)

def mpfr_erf(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the error function on op, rounded in the direction
    rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_erf(&rop._value, &op._value, rnd)

def mpfr_erfc(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the the complementary error function on op, rounded
    in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_erfc(&rop._value, &op._value, rnd)

def mpfr_j0(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the first kind Bessel function of order 0 on op,
    rounded in the direction rnd. When op is NaN, rop is always set to
    NaN. When op is plus or minus infinity, rop is set to +0.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_j0(&rop._value, &op._value, rnd)

def mpfr_j1(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the first kind Bessel function of order 1, on op,
    rounded in the direction rnd. When op is NaN, rop is always set to
    NaN. When op is plus or minus infinity, rop is set to +0. When op is zero,
    rop is set to +0 or −0 depending on the sign of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_j1(&rop._value, &op._value, rnd)

def mpfr_jn(Mpfr_t rop not None, long int n, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the first kind Bessel function of order n on op,
    rounded in the direction rnd. When op is NaN, rop is always set to
    NaN. When op is plus or minus Infinity, rop is set to +0. When op is zero,
    and n is not zero, rop is set to +0 or −0 depending on the parity and sign
    of n, and the sign of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_jn(&rop._value, n, &op._value, rnd)

def mpfr_y0(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the second kind Bessel function of order 0 on op,
    rounded in the direction rnd.

    When op is NaN or negative, rop is always set to NaN. When op is plus
    infinity, rop is set to +0.  When op is zero, rop is set to +0 or -0
    depending on the sign of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_y0(&rop._value, &op._value, rnd)

def mpfr_y1(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the second kind Bessel function of order 1 on op,
    rounded in the direction rnd.

    When op is NaN or negative, rop is always set to NaN. When op is plus
    infinity, rop is set to +0.  When op is zero, rop is set to +0 or -0
    depending on the sign of op.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_y1(&rop._value, &op._value, rnd)

def mpfr_yn(Mpfr_t rop not None, long int n, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the second kind Bessel function of order n on op,
    rounded in the direction rnd. When op is NaN or negative, rop is always set
    to NaN. When op is +Inf, rop is set to +0. When op is zero, rop is set to
    +Inf or −Inf depending on the parity and sign of n.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_yn(&rop._value, n, &op._value, rnd)

def mpfr_fma(Mpfr_t rop not None,
             Mpfr_t op1 not None,
             Mpfr_t op2 not None,
             Mpfr_t op3 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to (op1 times op2) + op3 rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_initialized(op3)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fma(
        &rop._value, &op1._value, &op2._value, &op3._value, rnd
    )

def mpfr_fms(Mpfr_t rop not None,
             Mpfr_t op1 not None,
             Mpfr_t op2 not None,
             Mpfr_t op3 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to (op1 times op2) - op3 rounded in the direction rnd.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_initialized(op3)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fms(
        &rop._value, &op1._value, &op2._value, &op3._value, rnd
    )

def mpfr_agm(Mpfr_t rop not None,
             Mpfr_t op1 not None,
             Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the arithmetic-geometric mean of op1 and op2, rounded in the
    direction rnd. The arithmetic-geometric mean is the common limit of the
    sequences u_n and v_n, where u_0=op1, v_0=op2, u_(n+1) is the arithmetic
    mean of u_n and v_n, and v_(n+1) is the geometric mean of u_n and v_n. If
    any operand is negative, set rop to NaN.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_agm(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_hypot(Mpfr_t rop not None,
             Mpfr_t x not None,
             Mpfr_t y not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the Euclidean norm of x and y, i.e., the square root of the sum
    of the squares of x and y, rounded in the direction rnd. Special values are
    handled as described in Section F.9.4.3 of the ISO C99 and IEEE 754-2008
    standards: If x or y is an infinity, then +Inf is returned in rop, even if
    the other number is NaN.

    """
    check_initialized(rop)
    check_initialized(x)
    check_initialized(y)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_hypot(&rop._value, &x._value, &y._value, rnd)

def mpfr_ai(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the value of the Airy function Ai on x, rounded in the direction
    rnd.

    When x is NaN, rop is always set to NaN. When x is +Inf or −Inf, rop
    is +0. The current implementation is not intended to be used with large
    arguments. It works with abs(x) typically smaller than 500. For larger
    arguments, other methods should be used and will be implemented in a future
    version.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_ai(&rop._value, &op._value, rnd)

def mpfr_const_log2(Mpfr_t rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to log(2), rounded in the direction rnd.

    Set rop to the natural logarithm of 2, rounded in the direction rnd.  This
    function caches the computed values to avoid other calculations if a lower
    or equal precision is requested.  To free this cache, use mpfr_free_cache.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_log2(&rop._value, rnd)

def mpfr_const_pi(Mpfr_t rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Pi, rounded in the direction rnd.

    Set rop to the value of Pi, rounded in the direction rnd.  This function
    caches the computed value to avoid other calculations if a lower or equal
    precision is requested.  To free this cache, use mpfr_free_cache.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_pi(&rop._value, rnd)

def mpfr_const_euler(Mpfr_t rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Euler's constant, rounded in the direction rnd.

    Set rop to the value of Euler's constant 0.577..., rounded in the direction
    rnd.  This function caches the computed value to avoid other calculations
    if a lower or equal precision is requested.  To free this cache, use
    mpfr_free_cache.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_euler(&rop._value, rnd)

def mpfr_const_catalan(Mpfr_t rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Catalan's constant, rounded in the direction rnd.

    Set rop to the value of Catalan's constant 0.915..., rounded in the
    direction rnd.  This function caches the computed value to avoid other
    calculations if a lower or equal precision is requested.  To free this
    cache, use mpfr_free_cache.

    """
    check_initialized(rop)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_catalan(&rop._value, rnd)

def mpfr_free_cache():
    """
    Free internal MPFR caches.

    Free various caches used by MPFR internally, in particular the caches
    used by the functions computing constants (mpfr_const_log2, mpfr_const_pi,
    mpfr_const_euler and mpfr_const_catalan). You should call this function
    before terminating a thread, even if you did not call these functions
    directly (they could have been called internally).

    """
    cmpfr.mpfr_free_cache()


###############################################################################
# 5.10 Integer and Remainder Related Functions
###############################################################################

def mpfr_rint(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op rounded to an integer in the direction given by rnd.

    The returned value is zero when the result is exact, positive when it is
    greater than the original value of op, and negative when it is
    smaller. More precisely, the returned value is 0 when op is an integer
    representable in rop, 1 or −1 when op is an integer that is not
    representable in rop, 2 or −2 when op is not an integer.

    Note that no double rounding is performed; for instance, 10.5 (1010.1 in
    binary) is rounded by mpfr_rint with rounding to nearest to 12 (1100 in
    binary) in 2-bit precision, because the two enclosing numbers representable
    on two bits are 8 and 12, and the closest is 12. (If one first rounded to
    an integer, one would round 10.5 to 10 with even rounding, and then 10
    would be rounded to 8 again with even rounding.)

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rint(&rop._value, &op._value, rnd)

def mpfr_ceil(Mpfr_t rop not None, Mpfr_t op not None):
    """
    Set rop to op rounded to the next higher or equal representable integer.

    The returned value is zero when the result is exact, positive when it is
    greater than the original value of op, and negative when it is
    smaller. More precisely, the returned value is 0 when op is an integer
    representable in rop, 1 or −1 when op is an integer that is not
    representable in rop, 2 or −2 when op is not an integer.

    """
    check_initialized(rop)
    check_initialized(op)
    return cmpfr.mpfr_ceil(&rop._value, &op._value)

def mpfr_floor(Mpfr_t rop not None, Mpfr_t op not None):
    """
    Set rop to op rounded to the next lower or equal representable integer.

    The returned value is zero when the result is exact, positive when it is
    greater than the original value of op, and negative when it is
    smaller. More precisely, the returned value is 0 when op is an integer
    representable in rop, 1 or −1 when op is an integer that is not
    representable in rop, 2 or −2 when op is not an integer.

    """
    check_initialized(rop)
    check_initialized(op)
    return cmpfr.mpfr_floor(&rop._value, &op._value)

def mpfr_round(Mpfr_t rop not None, Mpfr_t op not None):
    """
    Set rop to op rounded to the nearest representable integer, rounding
    halfway cases away from zero (as in the roundTiesToAway mode of IEEE
    754-2008).

    The returned value is zero when the result is exact, positive when it is
    greater than the original value of op, and negative when it is
    smaller. More precisely, the returned value is 0 when op is an integer
    representable in rop, 1 or −1 when op is an integer that is not
    representable in rop, 2 or −2 when op is not an integer.

    Note that mpfr_round is different from mpfr_rint called with the rounding
    to nearest mode (where halfway cases are rounded to an even integer or
    significand). Note also that no double rounding is performed; for instance,
    10.5 (1010.1 in binary) is rounded by mpfr_rint with rounding to nearest to
    12 (1100 in binary) in 2-bit precision, because the two enclosing numbers
    representable on two bits are 8 and 12, and the closest is 12. (If one
    first rounded to an integer, one would round 10.5 to 10 with even rounding,
    and then 10 would be rounded to 8 again with even rounding.)
    """
    check_initialized(rop)
    check_initialized(op)
    return cmpfr.mpfr_round(&rop._value, &op._value)

def mpfr_trunc(Mpfr_t rop not None, Mpfr_t op not None):
    """
    Set rop to op rounded to the next representable integer toward zero.

    The returned value is zero when the result is exact, positive when it is
    greater than the original value of op, and negative when it is
    smaller. More precisely, the returned value is 0 when op is an integer
    representable in rop, 1 or −1 when op is an integer that is not
    representable in rop, 2 or −2 when op is not an integer.

    """
    check_initialized(rop)
    check_initialized(op)
    return cmpfr.mpfr_trunc(&rop._value, &op._value)

def mpfr_rint_ceil(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op rounded to the next higher or equal integer.

    If the result is not representable, it is rounded in the direction rnd. The
    returned value is the ternary value associated with the considered
    round-to-integer function (regarded in the same way as any other
    mathematical function).

    Unlike mpfr_ceil, this function does perform a double rounding: first op is
    rounded to the next higher or equal integer, then this integer (if not
    representable) is rounded in the given direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rint_ceil(&rop._value, &op._value, rnd)

def mpfr_rint_floor(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op rounded to the next lower or equal integer.

    If the result is not representable, it is rounded in the direction rnd. The
    returned value is the ternary value associated with the considered
    round-to-integer function (regarded in the same way as any other
    mathematical function).

    Unlike mpfr_floor, this function does perform a double rounding: first op
    is rounded to the next lower or equal integer, then this integer (if not
    representable) is rounded in the given direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rint_floor(&rop._value, &op._value, rnd)

def mpfr_rint_round(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op rounded to the nearest integer, rounding halfway cases
    away from zero.

    If the result is not representable, it is rounded in the direction rnd. The
    returned value is the ternary value associated with the considered
    round-to-integer function (regarded in the same way as any other
    mathematical function).

    Unlike mpfr_round, this function does perform a double rounding: first op
    is rounded to the nearest integer, then this nearest integer (if not
    representable) is rounded in the given direction rnd.

    For example, mpfr_rint_round with rounding to nearest and a precision of
    two bits rounds 6.5 to 7 (halfway cases away from zero), then 7 is rounded
    to 8 by the round-even rule, despite the fact that 6 is also representable
    on two bits, and is closer to 6.5 than 8.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rint_round(&rop._value, &op._value, rnd)

def mpfr_rint_trunc(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op rounded to the next integer toward zero.

    If the result is not representable, it is rounded in the direction rnd. The
    returned value is the ternary value associated with the considered
    round-to-integer function (regarded in the same way as any other
    mathematical function).

    Unlike mpfr_trunc, this function does perform a double rounding: first op
    is rounded to the next integer toward zero, then this integer (if not
    representable) is rounded in the given direction rnd.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_rint_trunc(&rop._value, &op._value, rnd)

def mpfr_frac(Mpfr_t rop not None, Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the fractional part of op, having the same sign as op, rounded
    in the direction rnd (unlike in mpfr_rint, rnd affects only how the exact
    fractional part is rounded, not how the fractional part is generated).

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_frac(&rop._value, &op._value, rnd)

def mpfr_modf(Mpfr_t iop not None, Mpfr_t fop not None,
              Mpfr_t op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set simultaneously iop to the integral part of op and fop to the fractional
    part of op, rounded in the direction rnd with the corresponding precision
    of iop and fop.

    Equivalent to mpfr_trunc(iop, op, rnd) and mpfr_frac(fop, op, rnd). The
    variables iop and fop must be different.

    Return a pair (int_ternary, frac_ternary) of the corresponding ternary
    values.  Note that this differs from the original mpfr_modf function from
    MPFR, which combines the ternary values into a single int return.

    """
    cdef int ternary_pair

    check_initialized(iop)
    check_initialized(fop)
    check_initialized(op)
    check_rounding_mode(rnd)
    ternary_pair = cmpfr.mpfr_modf(
        &iop._value, &fop._value, &op._value, rnd
    )
    return decode_ternary_pair(ternary_pair)

def mpfr_fmod(Mpfr_t r not None, Mpfr_t x not None,
              Mpfr_t y not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set r to x reduced modulo y, rounded in direction rnd.

    Set r to the value of x - n * y, rounded according to the direction
    rnd, where n is the integer quotient of x divided by y, rounded toward
    zero.

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If x is infinite or y is zero, r is NaN. If y is infinite
    and x is finite, r is x rounded to the precision of r. If r is
    zero, it has the sign of x. The return value is the ternary value
    corresponding to r.

    """
    check_initialized(r)
    check_initialized(x)
    check_initialized(y)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fmod(&r._value, &x._value, &y._value, rnd)

def mpfr_remainder(Mpfr_t r not None, Mpfr_t x not None,
                   Mpfr_t y not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set r to x reduced modulo y, rounded in direction rnd.

    Set r to the value of x - n * y, rounded according to the direction rnd,
    where n is the integer quotient of x divided by y, rounded to the nearest
    integer (ties rounded to even).

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If x is infinite or y is zero, r is NaN. If y is infinite
    and x is finite, r is x rounded to the precision of r. If r is
    zero, it has the sign of x. The return value is the ternary value
    corresponding to r.

    """
    check_initialized(r)
    check_initialized(x)
    check_initialized(y)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_remainder(&r._value, &x._value, &y._value, rnd)

def mpfr_remquo(Mpfr_t r not None, Mpfr_t x not None,
                Mpfr_t y not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set r to x reduced modulo y, rounded in the direction rnd.  Also return
    low bits of quotient.

    Set r to the value of x - n * y, rounded according to the direction rnd,
    where n is the integer quotient of x divided by y, rounded to the nearest
    integer (ties rounded to even).

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If x is infinite or y is zero, r is NaN. If y is infinite and x
    is finite, r is x rounded to the precision of r. If r is zero, it has the
    sign of x. The return value is the ternary value corresponding to r.

    Returns a pair (ternary, quotient) where ternary is the ternary value
    corresponding to r, and q gives the low significant bits from the quotient
    n (more precisely the number of bits in a long minus one), with the
    sign of x divided by y (except if those low bits are all zero, in which
    case zero is returned). Note that x may be so large in magnitude relative
    to y that an exact representation of the quotient is not practical.

    """
    cdef long int quotient

    check_initialized(r)
    check_initialized(x)
    check_initialized(y)
    check_rounding_mode(rnd)
    ternary = cmpfr.mpfr_remquo(
        &r._value, &quotient, &x._value, &y._value, rnd
    )
    return ternary, quotient

def mpfr_integer_p(Mpfr_t op not None):
    """
    Return True if op is an integer.  Return False otherwise.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_integer_p(&op._value))


###############################################################################
# 5.11 Rounding Related Functions
###############################################################################

def mpfr_set_default_rounding_mode(cmpfr.mpfr_rnd_t rnd):
    """
    Set the default rounding mode to rnd.

    The default rounding mode is to nearest initially.

    """
    check_rounding_mode(rnd)
    cmpfr.mpfr_set_default_rounding_mode(rnd)

def mpfr_get_default_rounding_mode():
    """
    Get the default rounding mode.

    """
    return cmpfr.mpfr_get_default_rounding_mode()

def mpfr_prec_round(
    Mpfr_t x not None, cmpfr.mpfr_prec_t prec, cmpfr.mpfr_rnd_t rnd
    ):
    """
    Round x according to the given rounding mode and precision.

    Round x according to rnd with precision prec, which must be an integer
    between MPFR_PREC_MIN and MPFR_PREC_MAX (otherwise the behavior is
    undefined). If prec is greater or equal to the precision of x, then new
    space is allocated for the significand, and it is filled with
    zeros. Otherwise, the significand is rounded to precision prec with the
    given direction. In both cases, the precision of x is changed to prec.

    Here is an example of how to use mpfr_prec_round to implement Newton's
    algorithm to compute the inverse of a, assuming x is already an
    approximation to n bits:

            mpfr_set_prec (t, 2 * n);
            mpfr_set (t, a, MPFR_RNDN);         /* round a to 2n bits */
            mpfr_mul (t, t, x, MPFR_RNDN);      /* t is correct to 2n bits */
            mpfr_ui_sub (t, 1, t, MPFR_RNDN);   /* high n bits cancel with 1 */
            mpfr_prec_round (t, n, MPFR_RNDN);  /* t is correct to n bits */
            mpfr_mul (t, t, x, MPFR_RNDN);      /* t is correct to n bits */
            mpfr_prec_round (x, 2 * n, MPFR_RNDN); /* exact */
            mpfr_add (x, x, t, MPFR_RNDN);      /* x is correct to 2n bits */

    """
    check_initialized(x)
    check_precision(prec)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_prec_round(&x._value, prec, rnd)

def mpfr_can_round(Mpfr_t b not None, cmpfr.mpfr_exp_t err,
                   cmpfr.mpfr_rnd_t rnd1, cmpfr.mpfr_rnd_t rnd2,
                   cmpfr.mpfr_prec_t prec):
    """
    Assuming b is an approximation of an unknown number x in the direction rnd1
    with error at most two to the power E(b)-err where E(b) is the exponent of
    b, return a non-zero value if one is able to round correctly x to precision
    prec with the direction rnd2, and 0 otherwise (including for NaN and
    Inf). This function does not modify its arguments.

    If rnd1 is MPFR_RNDN, then the sign of the error is unknown, but its
    absolute value is the same, so that the possible range is twice as large as
    with a directed rounding for rnd1.

    Note: if one wants to also determine the correct ternary value when
    rounding b to precision prec with rounding mode rnd, a useful trick is the
    following:

     if mpfr_can_round(b, err, MPFR_RNDN, MPFR_RNDZ, prec + (rnd == MPFR_RNDN)):
         ...

    Indeed, if rnd is MPFR_RNDN, this will check if one can round to prec+1
    bits with a directed rounding: if so, one can surely round to nearest to
    prec bits, and in addition one can determine the correct ternary value,
    which would not be the case when b is near from a value exactly
    representable on prec bits.

    """
    check_initialized(b)
    check_rounding_mode(rnd1)
    check_rounding_mode(rnd2)
    check_precision(prec)
    return bool(cmpfr.mpfr_can_round(&b._value, err, rnd1, rnd2, prec))

def mpfr_min_prec(Mpfr_t x not None):
    """
    Return the minimal number of bits required to store the significand of x,
    and 0 for special values, including 0. (Warning: the returned value can be
    less than MPFR_PREC_MIN.)

    The function name is subject to change.

    """
    check_initialized(x)
    return cmpfr.mpfr_min_prec(&x._value)

def mpfr_print_rnd_mode(cmpfr.mpfr_rnd_t rnd):
    """
    Return a string ("MPFR_RNDD", "MPFR_RNDU", "MPFR_RNDN", "MPFR_RNDZ",
    "MPFR_RNDA") corresponding to the rounding mode rnd.

    Raise a ValueError if rnd is an invalid rounding mode.

    """
    cdef bytes rounding_mode
    check_rounding_mode(rnd)
    rounding_mode = cmpfr.mpfr_print_rnd_mode(rnd)
    if sys.version_info < (3,):
        return rounding_mode
    else:
        return rounding_mode.decode('ascii')

###############################################################################
# 5.12 Miscellaneous Functions
###############################################################################

def mpfr_nexttoward(Mpfr_t x not None, Mpfr_t y not None):
    """
    Replace x by the next floating-point number in the direction of y.

    If x or y is NaN, set x to NaN. If x and y are equal, x is
    unchanged. Otherwise, if x is different from y, replace x by the next
    floating-point number (with the precision of x and the current exponent
    range) in the direction of y (the infinite values are seen as the smallest
    and largest floating-point numbers). If the result is zero, it keeps the
    same sign. No underflow or overflow is generated.

    """
    check_initialized(x)
    check_initialized(y)
    cmpfr.mpfr_nexttoward(&x._value, &y._value)

def mpfr_nextabove(Mpfr_t op not None):
    """
    Equivalent to mpfr_nexttoward(op, y) where y is plus infinity.

    """
    check_initialized(op)
    cmpfr.mpfr_nextabove(&op._value)

def mpfr_nextbelow(Mpfr_t op not None):
    """
    Equivalent to mpfr_nexttoward(op, y) where y is minus infinity.

    """
    check_initialized(op)
    cmpfr.mpfr_nextbelow(&op._value)

def mpfr_min(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the minimum of op1 and op2.

    If op1 and op2 are both NaN, then rop is set to NaN. If op1 or op2 is NaN,
    then rop is set to the numeric value. If op1 and op2 are zeros of different
    signs, then rop is set to −0.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_min(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_max(Mpfr_t rop not None, Mpfr_t op1 not None, Mpfr_t op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the maximum of op1 and op2.

    If op1 and op2 are both NaN, then rop is set to NaN. If op1 or op2 is NaN,
    then rop is set to the numeric value. If op1 and op2 are zeros of different
    signs, then rop is set to +0.

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_max(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_get_exp(Mpfr_t op not None):
    """
    Return the exponent of op.

    Return the exponent of op, assuming that op is a non-zero ordinary number
    and the significand is considered in [1/2, 1). The behavior for NaN,
    infinity or zero is undefined.

    """
    check_initialized(op)
    return cmpfr.mpfr_get_exp(&op._value)

def mpfr_set_exp(Mpfr_t op not None, cmpfr.mpfr_exp_t exp):
    """
    Set the exponent of op.

    Set the exponent of op to exp if exp is in the current exponent range (even
    if x is not a non-zero ordinary number).  If exp is not in the current
    exponent range, raise ValueError.  The significand is assumed to be in
    [1/2, 1).

    """
    check_initialized(op)
    error_code = cmpfr.mpfr_set_exp(&op._value, exp)
    if error_code:
        raise ValueError("exponent not in current exponent range")

def mpfr_signbit(Mpfr_t op not None):
    """
    Return True if op has its sign bit set.  Return False otherwise.

    This function returns True for negative numbers, negative infinity, -0,
    or a NaN whose representation has its sign bit set.

    """
    check_initialized(op)
    return bool(cmpfr.mpfr_signbit(&op._value))

def mpfr_setsign(Mpfr_t rop not None, Mpfr_t op not None, s, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from op and the sign of rop from s.

    Set the value of rop from op, rounded toward the given direction rnd, then
    set (resp. clear) its sign bit if s is non-zero (resp. zero), even when op
    is a NaN.

    """
    check_initialized(rop)
    check_initialized(op)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_setsign(&rop._value, &op._value, s, rnd)

def mpfr_copysign(Mpfr_t rop not None, Mpfr_t op1 not None,
                  Mpfr_t op2 not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 with the sign of op2.

    Set the value of rop from op1, rounded toward the given direction rnd, then
    set its sign bit to that of op2 (even when op1 or op2 is a NaN). This
    function is equivalent to mpfr_setsign (rop, op1, mpfr_signbit (op2), rnd).

    """
    check_initialized(rop)
    check_initialized(op1)
    check_initialized(op2)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_copysign(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_get_version():
    """
    Return the MPFR version, as a string.

    """
    cdef bytes version = cmpfr.mpfr_get_version()
    if sys.version_info < (3,):
        return version
    else:
        return version.decode('ascii')


MPFR_VERSION = cmpfr.MPFR_VERSION
MPFR_VERSION_MAJOR = cmpfr.MPFR_VERSION_MAJOR
MPFR_VERSION_MINOR = cmpfr.MPFR_VERSION_MINOR
MPFR_VERSION_PATCHLEVEL = cmpfr.MPFR_VERSION_PATCHLEVEL
if sys.version_info < (3,):
    MPFR_VERSION_STRING = cmpfr.MPFR_VERSION_STRING
else:
    MPFR_VERSION_STRING = cmpfr.MPFR_VERSION_STRING.decode('ascii')

def MPFR_VERSION_NUM(int major, int minor, int patchlevel):
    """
    Create an integer in the same format as used by MPFR_VERSION from the given
    major, minor and patchlevel.

    """
    return cmpfr.MPFR_VERSION_NUM(major, minor, patchlevel)

def mpfr_get_patches():
    """
    Return information about patches applied to the MPFR library.

    Return a list containing the ids of patches applied to the MPFR
    library (contents of the PATCHES file), separated by spaces.

    Note: If the program has been compiled with an older MPFR version and is
    dynamically linked with a new MPFR library version, the identifiers of the
    patches applied to the old (compile-time) MPFR version are not available
    (however this information should not have much interest in general).

    """
    cdef bytes patches = cmpfr.mpfr_get_patches()
    if sys.version_info < (3,):
        return patches.split()
    else:
        return patches.decode('ascii').split()

def mpfr_buildopt_tls_p():
    """
    Return True if MPFR was compiled as thread safe using compiler-level Thread
    Local Storage (that is, MPFR was built with the --enable-thread-safe
    configure option, see INSTALL file), return False otherwise.

    """
    return bool(cmpfr.mpfr_buildopt_tls_p())

def mpfr_buildopt_decimal_p():
    """
    Return True if MPFR was compiled with decimal float support (that is, MPFR
    was built with the --enable-decimal-float configure option), return False
    otherwise.

    """
    return bool(cmpfr.mpfr_buildopt_decimal_p())


###############################################################################
# 5.13 Exception Related Functions
###############################################################################


def mpfr_get_emin():
    """
    Return smallest exponent allowed.

    Return the (current) smallest and exponent allowed for a floating-point
    variable. The smallest positive value of a floating-point variable is one
    half times 2 raised to the smallest exponent.

    """
    return cmpfr.mpfr_get_emin()

def mpfr_get_emax():
    """
    Return largest exponent allowed.

    Return the (current) largest exponent allowed for a floating-point
    variable. The largest positive value of a floating-point variable has the
    form (1 - epsilon) times 2 raised to the largest exponent, where epsilon
    depends on the precision of the considered variable.

    """
    return cmpfr.mpfr_get_emax()

def mpfr_set_emin(cmpfr.mpfr_exp_t exp):
    """
    Set the smallest exponent allowed for a floating-point variable.

    Raises ValueError when exp is not in the range accepted by the
    implementation (in that case the smallest exponent is not changed).

    If the user changes the exponent range, it is her/his responsibility to
    check that all current floating-point variables are in the new allowed
    range (for example using mpfr_check_range), otherwise the subsequent
    behavior will be undefined, in the sense of the ISO C standard.

    """
    error_code = cmpfr.mpfr_set_emin(exp)
    if error_code:
        raise ValueError("new exponent for emin is outside allowable range")

def mpfr_set_emax(cmpfr.mpfr_exp_t exp):
    """
    Set the largest exponent allowed for a floating-point variable.

    Raises ValueError when exp is not in the range accepted by the
    implementation (in that case the largest exponent is not changed).

    If the user changes the exponent range, it is her/his responsibility to
    check that all current floating-point variables are in the new allowed
    range (for example using mpfr_check_range), otherwise the subsequent
    behavior will be undefined, in the sense of the ISO C standard.

    """
    error_code = cmpfr.mpfr_set_emax(exp)
    if error_code:
        raise ValueError("new exponent for emin is outside allowable range")

def mpfr_get_emin_min():
    """
    Return the minimum exponent allowed for mpfr_set_emin.

    This value is implementation dependent, thus a program using
    mpfr_set_emin(mpfr_get_emin_min()) may not be portable.

    """
    return cmpfr.mpfr_get_emin_min()

def mpfr_get_emin_max():
    """
    Return the maximum exponent allowed for mpfr_set_emin.

    This value is implementation dependent, thus a program using
    mpfr_set_emin(mpfr_get_emin_max()) may not be portable.

    """
    return cmpfr.mpfr_get_emin_max()

def mpfr_get_emax_min():
    """
    Return the minimum exponent allowed for mpfr_set_emax.

    This value is implementation dependent, thus a program using
    mpfr_set_emax(mpfr_get_emax_min()) may not be portable.

    """
    return cmpfr.mpfr_get_emax_min()

def mpfr_get_emax_max():
    """
    Return the maximum exponent allowed for mpfr_set_emax.

    This value is implementation dependent, thus a program using
    mpfr_set_emax(mpfr_get_emax_max()) may not be portable.

    """
    return cmpfr.mpfr_get_emax_max()

def mpfr_check_range(Mpfr_t x not None, int t, cmpfr.mpfr_rnd_t rnd):
    """
    Modify x if necessary to fit into the current exponent range.

    This function assumes that x is the correctly-rounded value of some real
    value y in the direction rnd and some extended exponent range, and that t
    is the corresponding ternary value. For example, one performed t = mpfr_log
    (x, u, rnd), and y is the exact logarithm of u. Thus t is negative if x is
    smaller than y, positive if x is larger than y, and zero if x equals
    y. This function modifies x if needed to be in the current range of
    acceptable values: It generates an underflow or an overflow if the exponent
    of x is outside the current allowed range; the value of t may be used to
    avoid a double rounding. This function returns zero if the new value of x
    equals the exact one y, a positive value if that new value is larger than
    y, and a negative value if it is smaller than y. Note that unlike most
    functions, the new result x is compared to the (unknown) exact one y, not
    the input value x, i.e., the ternary value is propagated.

    Note: If x is an infinity and t is different from zero (i.e., if the
    rounded result is an inexact infinity), then the overflow flag is set. This
    is useful because mpfr_check_range is typically called (at least in MPFR
    functions) after restoring the flags that could have been set due to
    internal computations.

    """
    check_initialized(x)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_check_range(&x._value, t, rnd)

def mpfr_subnormalize(Mpfr_t x not None, int t, cmpfr.mpfr_rnd_t rnd):
    """
    Modify x if necessary to account for subnormalization.

    This function rounds x emulating subnormal number arithmetic: if x is
    outside the subnormal exponent range, it just propagates the ternary value
    t; otherwise, it rounds x to precision EXP(x)-emin+1 according to rounding
    mode rnd and previous ternary value t, avoiding double rounding
    problems. More precisely in the subnormal domain, denoting by e the value
    of emin, x is rounded in fixed-point arithmetic to an integer multiple of
    two to the power e−1; as a consequence, 1.5 multiplied by two to the power
    e−1 when t is zero is rounded to two to the power e with rounding to
    nearest.

    PREC(x) is not modified by this function. rnd and t must be the rounding
    mode and the returned ternary value used when computing x (as in
    mpfr_check_range). The subnormal exponent range is from emin to
    emin+PREC(x)-1. If the result cannot be represented in the current exponent
    range (due to a too small emax), the behavior is undefined. Note that
    unlike most functions, the result is compared to the exact one, not the
    input value x, i.e., the ternary value is propagated.

    As usual, if the returned ternary value is non zero, the inexact flag is
    set. Moreover, if a second rounding occurred (because the input x was in
    the subnormal range), the underflow flag is set.

    """
    check_initialized(x)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_subnormalize(&x._value, t, rnd)

def mpfr_clear_underflow():
    """
    Clear the underflow flag.

    """
    cmpfr.mpfr_clear_underflow()

def mpfr_clear_overflow():
    """
    Clear the overflow flag.

    """
    cmpfr.mpfr_clear_overflow()

def mpfr_clear_divby0():
    """
    Clear the divide-by-zero flag.

    """
    cmpfr.mpfr_clear_divby0()

def mpfr_clear_nanflag():
    """
    Clear the invalid flag.

    """
    cmpfr.mpfr_clear_nanflag()

def mpfr_clear_inexflag():
    """
    Clear the inexact flag.

    """
    cmpfr.mpfr_clear_inexflag()

def mpfr_clear_erangeflag():
    """
    Clear the erange flag.

    """
    cmpfr.mpfr_clear_erangeflag()

def mpfr_set_underflow():
    """
    Set the underflow flag.

    """
    cmpfr.mpfr_set_underflow()

def mpfr_set_overflow():
    """
    Set the overflow flag.

    """
    cmpfr.mpfr_set_overflow()

def mpfr_set_divby0():
    """
    Set the divide-by-zero flag.

    """
    cmpfr.mpfr_set_divby0()

def mpfr_set_nanflag():
    """
    Set the invalid flag.

    """
    cmpfr.mpfr_set_nanflag()

def mpfr_set_inexflag():
    """
    Set the inexact flag.

    """
    cmpfr.mpfr_set_inexflag()

def mpfr_set_erangeflag():
    """
    Set the erange flag.

    """
    cmpfr.mpfr_set_erangeflag()

def mpfr_clear_flags():
    """
    Clear all global flags.

    """
    cmpfr.mpfr_clear_flags()

def mpfr_underflow_p():
    """
    Return True if the underflow flag is set, else False.

    """
    return bool(cmpfr.mpfr_underflow_p())

def mpfr_overflow_p():
    """
    Return True if the overflow flag is set, else False.

    """
    return bool(cmpfr.mpfr_overflow_p())

def mpfr_divby0_p():
    """
    Return True if the divide-by-zero flag is set, else False.

    """
    return bool(cmpfr.mpfr_divby0_p())

def mpfr_nanflag_p():
    """
    Return True if the invalid flag is set, else False.

    """
    return bool(cmpfr.mpfr_nanflag_p())

def mpfr_inexflag_p():
    """
    Return True if the inexact flag is set, else False.

    """
    return bool(cmpfr.mpfr_inexflag_p())

def mpfr_erangeflag_p():
    """
    Return True if the erange flag is set, else False.

    """
    return bool(cmpfr.mpfr_erangeflag_p())



# Functions that are documented in the MPFR 3.0.1 documentation, but aren't
# (currently) wrapped:
#
#
# 5.2 Assignment functions
# ------------------------
#
#   mpfr_set_ui
#   mpfr_set_uj
#   mpfr_set_sj
#   mpfr_set_flt
#   mpfr_set_ld
#   mpfr_set_decimal64
#   mpfr_set_z
#   mpfr_set_q
#   mpfr_set_f
#     -- these types not (currently) readily available in Python.  Only
#        mpfr_set, mpfr_set_si and mpfr_set_d are wrapped.
#
#   mpfr_set_ui_2exp
#   mpfr_set_uj_2exp
#   mpfr_set_sj_2exp
#   mpfr_set_z_2exp
#     -- these functions again concern types not readily available in Python.
#        Only mpfr_set_si_2exp is wrapped.
#
#
# 5.3 Combined initialization and assignment functions
# ----------------------------------------------------
#
# None of these functions are currently wrapped.
#
#
# 5.4 Conversion functions
# ------------------------
#
#  mpfr_get_flt
#  mpfr_get_ld
#  mpfr_get_decimal64
#  mpfr_get_ui
#  mpfr_get_sj
#  mpfr_get_uj
#  mpfr_get_ld_2exp
#  mpfr_get_z_2exp
#  mpfr_get_z
#  mpfr_get_f
#    -- these concern types not readily available in Python.  Only mpfr_get_d
#       and mpfr_get_si are wrapped.
#
#  mpfr_get_str and mpfr_free_str are used by the mpfr_get_str function here
#  (which has a slightly different signature to MPFRs mpfr_get_str).  There's
#  no need to wrap mpfr_free_str separately.
#
#  mpfr_fits_ulong_p
#  mpfr_fits_uint_p
#  mpfr_fits_sint_p
#  mpfr_fits_ushort_p
#  mpfr_fits_sshort_p
#  mpfr_fits_uintmax_p
#  mpfr_fits_intmax_p
#    -- only mpfr_fits_slong_p is wrapped from this section.
#
#
# 5.5 Basic Arithmetic Functions
# ------------------------------
#
# None of the functions involving types ui, si, d, z or q are implemented.
# This may change for the d, ui and si functions.
#
#
# 5.6 Comparison Functions
# ------------------------
#
# None of the functions involving types ui, si, d, ld, z, q or f are
# implemented.  This may change for the d, ui and si functions.
#
#
# 5.7 Special Functions
# ---------------------
#
# The following are not yet implemented.
#
#  mpfr_sum
#
#
#  5.8 Input and Output Functions
#  ------------------------------
#
#  mpfr_out_str
#  mpfr_inp_str
#
#
#  5.9 Formatted Output Functions
#  ------------------------------
#
#  mpfr_fprintf
#  mpfr_vfprintf
#
#  mpfr_printf
#  mpfr_vprintf
#
#  mpfr_sprintf
#  mpfr_vsprintf
#
#  mpfr_snprintf
#  mpfr_vsnprintf
#
#  mpfr_asprintf
#  mpfr_vasprintf
#
#
#  5.10 Integer and Remainder Related Functions
#  --------------------------------------------
#
#  All functions in this section wrapped.
#
#
#  5.11 Rounding Related Functions
#  --------------------------------------------
#
#  All functions in this section wrapped.
#
#
#  5.12 Miscellaneous Functions
#  ----------------------------
#
#  mpfr_urandomb
#  mpfr_urandom
#
#
#  5.13 Exception Related Functions
#  --------------------------------
#
#  All functions in this section wrapped.
#
#
#  5.14 Compatibility with MPFR
#  ----------------------------
#
#  No functions in this section wrapped.
#
#
#  5.15 Custom Interface
#  ---------------------
#
#  No functions in this section wrapped.

#  Sections 5.14 and later: details to come.

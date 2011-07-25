# -*- coding: utf-8 -*-
# cython: embedsignature = True

# Copyright 2009--2011 Mark Dickinson.
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

cimport cmpfr

# Version information
MPFR_VERSION_MAJOR = cmpfr.MPFR_VERSION_MAJOR
MPFR_VERSION_MINOR = cmpfr.MPFR_VERSION_MINOR
MPFR_VERSION_PATCHLEVEL = cmpfr.MPFR_VERSION_PATCHLEVEL
MPFR_VERSION_STRING = cmpfr.MPFR_VERSION_STRING

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


# Checks for valid parameter ranges
cdef int check_rounding_mode(cmpfr.mpfr_rnd_t rnd) except -1:
    if MPFR_RNDN <= rnd <= MPFR_RNDA:
        return 0
    else:
        raise ValueError("invalid rounding mode {}".format(rnd))


cdef int check_base(int b, int allow_zero) except -1:
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
    if n == 0 or 2 <= n:
        return 0
    else:
        raise ValueError("n should be either 0 or at least 2")


cdef int check_precision(cmpfr.mpfr_prec_t precision) except -1:
    if MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
        return 0
    else:
        raise ValueError(
            "precision should be between {} and {}".format(
                MPFR_PREC_MIN, MPFR_PREC_MAX
            )
        )


cdef class Mpfr:
    """
    Class representing a mutable arbitrary-precision floating-point number.

    Mpfr(prec) -> new Mpfr object

    Creates a new Mpfr object and sets its precision to be exactly 'prec' bits
    and its value to NaN.  The precision must be an integer between
    MPFR_PREC_MIN and MPFR_PREC_MAX; otherwise a ValueError is raised.

    """
    cdef cmpfr.__mpfr_struct _value

    def __cinit__(self, precision):
        check_precision(precision)
        cmpfr.mpfr_init2(&self._value, precision)

    def __dealloc__(self):
        if self._value._mpfr_d != NULL:
            cmpfr.mpfr_clear(&self._value)

# Functions that are documented in the MPFR 3.0.1 documentation, but aren't
# (currently) wrapped:
#
#
# 5.1 Initialization Functions
# ----------------------------
#
# These functions are used by the Mpfr class, but not exported
# independently by the mpfr module:
#
#   mpfr_init2
#   mpfr_clear
#
# These functions aren't wrapped at all:
#
#   mpfr_inits2
#   mpfr_clears
#   mpfr_init
#   mpfr_inits
#     -- there's no direct use for these 4 functions, since initialization and
#        finalization are already handled by the Mpfr class.
#
#   mpfr_set_default_prec
#   mpfr_get_default_prec
#     -- we don't wrap any functions that make use of the default precision,
#        so these aren't useful
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
#    -- these concern types not readily available in Python.  Only mpfr_get_d
#       and mpfr_get_si are wrapped.
#
#  

def mpfr_get_str(int b, size_t n, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Compute a base 'b' string representation for 'op'.

    'b' should be an integer between 2 and 62 (inclusive).

    'rnd' gives the rounding mode to use.

    Returns a pair (digits, exp) where:

        'digits' gives the string of digits
        exp is the exponent

    The exponent is normalized so that 0.<digits>E<exp> approximates 'op'.

    Note that the signature of this function does not match that of the
    underlying MPFR function call.

    """
    cdef cmpfr.mpfr_exp_t exp
    cdef bytes digits
    cdef char *c_digits

    check_base(b, False)
    check_get_str_n(n)
    check_rounding_mode(rnd)
    c_digits = cmpfr.mpfr_get_str(NULL, &exp, b, n, &op._value, rnd)
    if c_digits == NULL:
        raise RuntimeError("Error during string conversion.")

    # It's possible for the conversion from c_digits to digits to raise, so use
    # a try-finally block to ensure that c_digits always gets freed.
    try:
        digits = str(c_digits)
    finally:
        cmpfr.mpfr_free_str(c_digits)

    return digits, exp

def mpfr_strtofr(Mpfr rop not None, bytes s, int base, cmpfr.mpfr_rnd_t rnd):
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

    startptr = s

    check_base(base, True)
    check_rounding_mode(rnd)
    ternary = cmpfr.mpfr_strtofr(
        &rop._value,
        s,
        &endptr,
        base,
        rnd,
    )
    endindex = endptr - startptr
    return ternary, endindex

def mpfr_swap(Mpfr x not None, Mpfr y not None):
    """
    Swap the values of x and y efficiently.

    Warning: the precisions are exchanged too; in case the precisions are
    different, mpfr_swap is thus not equivalent to three mpfr_set calls using a
    third auxiliary variable.

    """
    cmpfr.mpfr_swap(&x._value, &y._value)

def mpfr_fits_slong_p(Mpfr x not None, cmpfr.mpfr_rnd_t rnd):
    """
    Return True if op would fit into a Python int.

    Return True if op would fit into a Python int when rounded to an integer
    in the direction rnd.

    """
    check_rounding_mode(rnd)
    return bool(cmpfr.mpfr_fits_slong_p(&x._value, rnd))

def mpfr_get_exp(Mpfr op not None):
    """
    Return the exponent of op.

    Return the exponent of op, assuming that op is a non-zero ordinary number
    and the significand is considered in [1/2, 1). The behavior for NaN,
    infinity or zero is undefined.

    """
    return cmpfr.mpfr_get_exp(&op._value)

def mpfr_set_exp(Mpfr op not None, cmpfr.mpfr_exp_t exp):
    """
    Set the exponent of op.

    Set the exponent of op to exp if exp is in the current exponent range (even
    if x is not a non-zero ordinary number).  If exp is not in the current
    exponent range, raise ValueError.  The significand is assumed to be in
    [1/2, 1).

    """
    error_code = cmpfr.mpfr_set_exp(&op._value, exp)
    if error_code:
        raise ValueError("exponent not in current exponent range")

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


# MPFR functions for computing constants, returning a ternary value.

def mpfr_const_log2(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to log(2), rounded in the direction rnd.

    Set rop to the natural logarithm of 2, rounded in the direction rnd.  This
    function caches the computed values to avoid other calculations if a lower
    or equal precision is requested.  To free this cache, use mpfr_free_cache.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_log2(&rop._value, rnd)

def mpfr_const_pi(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Pi, rounded in the direction rnd.

    Set rop to the value of Pi, rounded in the direction rnd.  This function
    caches the computed value to avoid other calculations if a lower or equal
    precision is requested.  To free this cache, use mpfr_free_cache.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_pi(&rop._value, rnd)

def mpfr_const_euler(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Euler's constant, rounded in the direction rnd.

    Set rop to the value of Euler's constant 0.577..., rounded in the direction
    rnd.  This function caches the computed value to avoid other calculations
    if a lower or equal precision is requested.  To free this cache, use
    mpfr_free_cache.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_euler(&rop._value, rnd)

def mpfr_const_catalan(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to Catalan's constant, rounded in the direction rnd.

    Set rop to the value of Catalan's constant 0.915..., rounded in the
    direction rnd.  This function caches the computed value to avoid other
    calculations if a lower or equal precision is requested.  To free this
    cache, use mpfr_free_cache.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_catalan(&rop._value, rnd)

# MPFR functions taking a single argument, returning a ternary value.

def mpfr_set(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop from op, rounded in the direction rnd.

    Set the value of rop from the value of the Mpfr object op, rounded toward
    the given direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set(&rop._value, &op._value, rnd)

def mpfr_neg(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to -op, rounded in the direction rnd.

    This function just changes or adjusts the sign if rop and op are the same
    variable, otherwise a rounding might occur if the precision of rop is less
    than that of op.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_neg(&rop._value, &op._value, rnd)

def mpfr_abs(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the absolute value of op, rounded in the direction rnd.

    This function just changes or adjusts the sign if rop and op are the same
    variable, otherwise a rounding might occur if the precision of rop is less
    than that of op.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_abs(&rop._value, &op._value, rnd)

def mpfr_sqrt(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the square root of op, rounded in the direction rnd.

    Set rop to −0 if op is −0, to be consistent with the IEEE 754 standard. Set
    rop to NaN if op is negative.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sqrt(&rop._value, &op._value, rnd)

def mpfr_exp(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the exponential of op, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_exp(&rop._value, &op._value, rnd)

def mpfr_log(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the natural logarithm of op, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log(&rop._value, &op._value, rnd)

def mpfr_log2(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to the base-2 logarithm of op, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log2(&rop._value, &op._value, rnd)

# MPFR functions taking two arguments, returning a ternary value.

def mpfr_add(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 + op2 rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_add(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_sub(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 - op2, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sub(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_mul(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 times op2, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_mul(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_div(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
             cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 divided by op2, rounded in the direction rnd.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_div(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_fmod(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
              cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op1 reduced modulo op2, rounded in direction rnd.

    Set rop to the value of op1 - n * op2, rounded according to the direction
    rnd, where n is the integer quotient of op1 divided by op2, rounded toward
    zero.

    Special values are handled as described in Section F.9.7.1 of the ISO C99
    standard: If op1 is infinite or op2 is zero, rop is NaN. If op2 is infinite
    and op1 is finite, rop is op1 rounded to the precision of rop. If rop is
    zero, it has the sign of op1. The return value is the ternary value
    corresponding to rop.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fmod(&rop._value, &op1._value, &op2._value, rnd)

def mpfr_pow(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None,
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
    check_rounding_mode(rnd)
    return cmpfr.mpfr_pow(&rop._value, &op1._value, &op2._value, rnd)


def mpfr_set_si(Mpfr rop not None, long int op, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from a Python int, rounded in the direction rnd.

    Set the value of rop from op, rounded toward the given direction rnd. Note
    that the input 0 is converted to +0, regardless of the rounding mode.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_si(&rop._value, op, rnd)

def mpfr_set_si_2exp(Mpfr rop not None, long int op,
                     cmpfr.mpfr_exp_t e, cmpfr.mpfr_rnd_t rnd):
    """
    Set rop to op multiplied by a power of 2.

    Set the value of rop from op multiplied by two to the power e, rounded
    toward the given direction rnd. Note that the input 0 is converted to +0.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_si_2exp(&rop._value, op, e, rnd)

def mpfr_set_d(Mpfr rop not None, double op, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from a Python float op, rounded in the direction rnd.

    Set the value of rop from op, rounded toward the given direction rnd.  If
    the system does not support the IEEE 754 standard, mpfr_set_d might not
    preserve the signed zeros.

    Note: If you want to store a floating-point constant to an Mpfr object, you
    should use mpfr_set_str (or one of the MPFR constant functions, such as
    mpfr_const_pi for Pi) instead of mpfr_set_d.  Otherwise the floating-point
    constant will be first converted into a reduced-precision (e.g., 53-bit)
    binary number before MPFR can work with it.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_d(&rop._value, op, rnd)

def mpfr_set_str(Mpfr rop not None, bytes s, int base, cmpfr.mpfr_rnd_t rnd):
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
    check_base(base, False)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_str(&rop._value, s, base, rnd)

# Functions for getting exponent bounds.
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

def mpfr_set_prec(Mpfr x not None, cmpfr.mpfr_prec_t prec):
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
    check_precision(prec)
    cmpfr.mpfr_set_prec(&x._value, prec)

def mpfr_get_prec(Mpfr x not None):
    """
    Return the precision of x

    Returns the number of bits used to store the significand of x.

    """
    return cmpfr.mpfr_get_prec(&x._value)

def mpfr_setsign(Mpfr rop not None, Mpfr op not None, s, cmpfr.mpfr_rnd_t rnd):
    """
    Set the value of rop from op and the sign of rop from s.

    Set the value of rop from op, rounded toward the given direction rnd, then
    set (resp. clear) its sign bit if s is non-zero (resp. zero), even when op
    is a NaN.

    """
    s = bool(s)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_setsign(&rop._value, &op._value, s, rnd)

def mpfr_get_si(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    """
    Convert op to a Python int.

    Convert op to a Python int after rounding it with respect to rnd. If op is
    NaN, 0 is returned and the erange flag is set. If op is too big for a
    Python int, the function returns the maximum or the minimum representable
    int, depending on the direction of the overflow; the erange flag is set
    too.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_get_si(&rop._value, rnd)

def mpfr_get_d(Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """
    Convert op to a Python float.

    Convert op to a Python float using the rounding mode rnd. If op is NaN,
    some fixed NaN (either quiet or signaling) or the result of 0.0/0.0 is
    returned. If op is ±Inf, an infinity of the same sign or the result of
    ±1.0/0.0 is returned. If op is zero, this function returns a zero, trying
    to preserve its sign, if possible.

    """
    check_rounding_mode(rnd)
    return cmpfr.mpfr_get_d(&op._value, rnd)

def mpfr_get_d_2exp(Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
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

    check_rounding_mode(rnd)
    d =  cmpfr.mpfr_get_d_2exp(&exp, &op._value, rnd)
    return d, exp

def mpfr_set_nan(Mpfr op not None):
    """ Set x to a NaN.

    Set the variable x to NaN (Not-a-Number).  The sign bit of the result is
    unspecified.

    """
    cmpfr.mpfr_set_nan(&op._value)

def mpfr_set_inf(Mpfr op not None, int sign):
    """ Set x to an infinity.

    Set the variable x to infinity.  x is set to positive infinity if the sign
    is nonnegative, and negative infinity otherwise.

    """
    cmpfr.mpfr_set_inf(&op._value, sign)

def mpfr_set_zero(Mpfr op not None, int sign):
    """ Set x to a zero.

    Set the variable x to zero.  x is set to positive zero if the sign is
    nonnegative, and negative zero otherwise.

    """
    cmpfr.mpfr_set_zero(&op._value, sign)

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

def mpfr_clear_flags():
    """
    Clear all global flags.

    """
    cmpfr.mpfr_clear_flags()

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

def mpfr_check_range(Mpfr x not None, int t, cmpfr.mpfr_rnd_t rnd):
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
    check_rounding_mode(rnd)
    return cmpfr.mpfr_check_range(&x._value, t, rnd)

def mpfr_subnormalize(Mpfr x not None, int t, cmpfr.mpfr_rnd_t rnd):
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
    check_rounding_mode(rnd)
    return cmpfr.mpfr_subnormalize(&x._value, t, rnd)

def mpfr_nan_p(Mpfr op not None):
    """
    Return True if op is a NaN.  Return False otherwise.

    """
    return bool(cmpfr.mpfr_nan_p(&op._value))

def mpfr_inf_p(Mpfr op not None):
    """
    Return True if op is an infinity.  Return False otherwise.

    """
    return bool(cmpfr.mpfr_inf_p(&op._value))

def mpfr_number_p(Mpfr op not None):
    """
    Return True if op is an ordinary number.  Return False otherwise.

    An ordinary number is a number which is neither a NaN nor an infinity.

    """
    return bool(cmpfr.mpfr_number_p(&op._value))

def mpfr_zero_p(Mpfr op not None):
    """
    Return True if op is zero.  Return False otherwise.

    """
    return bool(cmpfr.mpfr_zero_p(&op._value))

def mpfr_regular_p(Mpfr op not None):
    """
    Return True if op is a regular number.  Return False otherwise.

    A regular number is a number which is neither a NaN, nor an infinity, nor a
    zero.

    """
    return bool(cmpfr.mpfr_regular_p(&op._value))

def mpfr_integer_p(Mpfr op not None):
    """
    Return True if op is an integer.  Return False otherwise.

    """
    return bool(cmpfr.mpfr_integer_p(&op._value))

def mpfr_signbit(Mpfr op not None):
    """
    Return True if op has its sign bit set.  Return False otherwise.

    This function returns True for negative numbers, negative infinity, -0,
    or a NaN whose representation has its sign bit set.

    """
    return bool(cmpfr.mpfr_signbit(&op._value))

def mpfr_greater_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 > op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_greater_p(&op1._value, &op2._value))

def mpfr_greaterequal_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 >= op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_greaterequal_p(&op1._value, &op2._value))

def mpfr_less_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 < op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_less_p(&op1._value, &op2._value))

def mpfr_lessequal_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 <= op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_lessequal_p(&op1._value, &op2._value))

def mpfr_equal_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 == op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_equal_p(&op1._value, &op2._value))

def mpfr_lessgreater_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 < op2 or op1 > op2 and False otherwise.

    This function returns False whenever op1 and/or op2 is a NaN.

    """
    return bool(cmpfr.mpfr_lessgreater_p(&op1._value, &op2._value))

def mpfr_unordered_p(Mpfr op1 not None, Mpfr op2 not None):
    """
    Return True if op1 or op2 is a NaN and False otherwise.

    """
    return bool(cmpfr.mpfr_unordered_p(&op1._value, &op2._value))

def mpfr_nexttoward(Mpfr x not None, Mpfr y not None):
    """
    Replace x by the next floating-point number in the direction of y.

    If x or y is NaN, set x to NaN. If x and y are equal, x is
    unchanged. Otherwise, if x is different from y, replace x by the next
    floating-point number (with the precision of x and the current exponent
    range) in the direction of y (the infinite values are seen as the smallest
    and largest floating-point numbers). If the result is zero, it keeps the
    same sign. No underflow or overflow is generated.

    """
    cmpfr.mpfr_nexttoward(&x._value, &y._value)

def mpfr_nextabove(Mpfr op not None):
    """
    Equivalent to mpfr_nexttoward(op, y) where y is plus infinity.

    """
    cmpfr.mpfr_nextabove(&op._value)

def mpfr_nextbelow(Mpfr op not None):
    """
    Equivalent to mpfr_nexttoward(op, y) where y is minus infinity.

    """
    cmpfr.mpfr_nextbelow(&op._value)

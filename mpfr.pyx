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
MPFR_RNDF =  cmpfr.MPFR_RNDF
MPFR_RNDNA =  cmpfr.MPFR_RNDNA

# Default values for Emax and Emin
MPFR_EMAX_DEFAULT = cmpfr.MPFR_EMAX_DEFAULT
MPFR_EMIN_DEFAULT = cmpfr.MPFR_EMIN_DEFAULT


# Checks for valid parameter ranges
cdef check_rounding_mode(cmpfr.mpfr_rnd_t rnd):
    # MPFR_RNDF not implemented yet; MPFR_RNDNA should not be used.
    if not MPFR_RNDN <= rnd <= MPFR_RNDA:
        raise ValueError("invalid rounding mode {}".format(rnd))


cdef check_ternary_value(int t):
    if not -1 <= t <= 1:
        raise ValueError("ternary value should be -1, 0 or 1")


cdef check_base(int b, int allow_zero):
    if allow_zero:
        if not ((2 <= b <= 62) or (b == 0)):
            raise ValueError(
                "base should be zero or in the range 2 to 62 (inclusive)"
            )
    else:
        if not (2 <= b <= 62):
            raise ValueError("base should be in the range 2 to 62 (inclusive)")


cdef check_get_str_n(size_t n):
    if not (n == 0 or 2 <= n):
        raise ValueError("n should be either 0 or at least 2")


cdef check_precision(cmpfr.mpfr_prec_t precision):
    if not MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
        raise ValueError(
            "precision should be between {} and {}".format(
                MPFR_PREC_MIN, MPFR_PREC_MAX
            )
        )


cdef class Mpfr:
    """ Mutable arbitrary-precision floating-point type. """
    cdef cmpfr.mpfr_t _value

    def __cinit__(self, precision):
        check_precision(precision)
        cmpfr.mpfr_init2(self._value, precision)

    def __dealloc__(self):
        if self._value._mpfr_d != NULL:
            cmpfr.mpfr_clear(self._value)


def mpfr_get_str(int b, size_t n, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    """ Compute a base 'b' string representation for 'op'.

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

    check_base(b, False)
    check_get_str_n(n)
    check_rounding_mode(rnd)
    c_digits = cmpfr.mpfr_get_str(NULL, &exp, b, n, op._value, rnd)
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
    """ Read a floating-point number from a string s.

    Returns a pair (ternary, endindex), where:

      - ternary is the usual ternary return value
      - endindex gives the index that points to the character of s
        just after the valid data.

    """
    cdef char* endptr
    cdef char* startptr

    startptr = s

    check_base(base, True)
    check_rounding_mode(rnd)
    ternary = cmpfr.mpfr_strtofr(
        rop._value,
        s,
        &endptr,
        base,
        rnd,
    )
    endindex = endptr - startptr
    return ternary, endindex

def mpfr_const_pi(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_pi(rop._value, rnd)

def mpfr_const_catalan(Mpfr rop not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_const_catalan(rop._value, rnd)

def mpfr_set(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set(rop._value, op._value, rnd)

def mpfr_neg(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_neg(rop._value, op._value, rnd)

def mpfr_add(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_add(rop._value, op1._value, op2._value, rnd)

def mpfr_sub(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sub(rop._value, op1._value, op2._value, rnd)

def mpfr_mul(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_mul(rop._value, op1._value, op2._value, rnd)

def mpfr_div(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_div(rop._value, op1._value, op2._value, rnd)

def mpfr_fmod(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_fmod(rop._value, op1._value, op2._value, rnd)

def mpfr_pow(Mpfr rop not None, Mpfr op1 not None, Mpfr op2 not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_pow(rop._value, op1._value, op2._value, rnd)

def mpfr_sqrt(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_sqrt(rop._value, op._value, rnd)

def mpfr_exp(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_exp(rop._value, op._value, rnd)

def mpfr_log(Mpfr rop not None, Mpfr op not None, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_log(rop._value, op._value, rnd)

def mpfr_set_d(Mpfr rop not None, double op, cmpfr.mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_d(rop._value, op, rnd)

def mpfr_set_str(Mpfr rop not None, bytes s, int base, cmpfr.mpfr_rnd_t rnd):
    check_base(base, False)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_set_str(rop._value, s, base, rnd)

# Functions for getting exponent bounds.
def mpfr_get_emin():
    return cmpfr.mpfr_get_emin()

def mpfr_get_emin_min():
    return cmpfr.mpfr_get_emin_min()

def mpfr_get_emin_max():
    return cmpfr.mpfr_get_emin_max()

def mpfr_get_emax():
    return cmpfr.mpfr_get_emax()

def mpfr_get_emax_min():
    return cmpfr.mpfr_get_emax_min()

def mpfr_get_emax_max():
    return cmpfr.mpfr_get_emax_max()

def mpfr_set_emin(cmpfr.mpfr_exp_t exp):
    error_code = cmpfr.mpfr_set_emin(exp)
    if error_code:
        raise ValueError("new exponent for emin is outside allowable range")

def mpfr_set_emax(cmpfr.mpfr_exp_t exp):
    error_code = cmpfr.mpfr_set_emax(exp)
    if error_code:
        raise ValueError("new exponent for emin is outside allowable range")

def mpfr_get_prec(Mpfr x not None):
    return cmpfr.mpfr_get_prec(x._value)

def mpfr_clear_underflow():
    cmpfr.mpfr_clear_underflow()

def mpfr_clear_overflow():
    cmpfr.mpfr_clear_overflow()

def mpfr_clear_nanflag():
    cmpfr.mpfr_clear_nanflag()

def mpfr_clear_inexflag():
    cmpfr.mpfr_clear_inexflag()

def mpfr_clear_erangeflag():
    cmpfr.mpfr_clear_erangeflag()

def mpfr_set_underflow():
    cmpfr.mpfr_set_underflow()

def mpfr_set_overflow():
    cmpfr.mpfr_set_overflow()

def mpfr_set_nanflag():
    cmpfr.mpfr_set_nanflag()

def mpfr_set_inexflag():
    cmpfr.mpfr_set_inexflag()

def mpfr_set_erangeflag():
    cmpfr.mpfr_set_erangeflag()

def mpfr_underflow_p():
    return bool(cmpfr.mpfr_underflow_p())

def mpfr_overflow_p():
    return bool(cmpfr.mpfr_overflow_p())

def mpfr_nanflag_p():
    return bool(cmpfr.mpfr_nanflag_p())

def mpfr_inexflag_p():
    return bool(cmpfr.mpfr_inexflag_p())

def mpfr_erangeflag_p():
    return bool(cmpfr.mpfr_erangeflag_p())

def mpfr_check_range(Mpfr x not None, int t, cmpfr.mpfr_rnd_t rnd):
    check_ternary_value(t)
    check_rounding_mode(rnd)
    return cmpfr.mpfr_check_range(x._value, t, rnd)

def mpfr_nan_p(Mpfr op not None):
    return bool(cmpfr.mpfr_nan_p(op._value))

def mpfr_inf_p(Mpfr op not None):
    return bool(cmpfr.mpfr_inf_p(op._value))

def mpfr_number_p(Mpfr op not None):
    return bool(cmpfr.mpfr_number_p(op._value))

def mpfr_integer_p(Mpfr op not None):
    return bool(cmpfr.mpfr_integer_p(op._value))

def mpfr_zero_p(Mpfr op not None):
    return bool(cmpfr.mpfr_zero_p(op._value))

def mpfr_regular_p(Mpfr op not None):
    return bool(cmpfr.mpfr_regular_p(op._value))

def mpfr_signbit(Mpfr op not None):
    return bool(cmpfr.mpfr_signbit(op._value))

def mpfr_greater_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_greater_p(op1._value, op2._value))

def mpfr_greaterequal_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_greaterequal_p(op1._value, op2._value))

def mpfr_less_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_less_p(op1._value, op2._value))

def mpfr_lessequal_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_lessequal_p(op1._value, op2._value))

def mpfr_equal_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_equal_p(op1._value, op2._value))

def mpfr_lessgreater_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_lessgreater_p(op1._value, op2._value))

def mpfr_unordered_p(Mpfr op1 not None, Mpfr op2 not None):
    return bool(cmpfr.mpfr_unordered_p(op1._value, op2._value))

cdef extern from "gmp.h":
    # GMP type declarations
    ctypedef int mp_exp_t
    ctypedef unsigned int mp_limb_t

cdef extern from "mpfr.h":
    # MPFR type declarations
    ctypedef int mpfr_prec_t
    ctypedef int mpfr_sign_t
    ctypedef mp_exp_t mpfr_exp_t

    ctypedef struct __mpfr_struct:
        mpfr_prec_t _mpfr_prec
        mpfr_sign_t _mpfr_sign
        mpfr_exp_t  _mpfr_exp
        mp_limb_t   *_mpfr_d

    ctypedef __mpfr_struct mpfr_t[1]

    # MPFR rounding modes
    ctypedef enum mpfr_rnd_t:
        C_MPFR_RNDN "MPFR_RNDN" = 0
        C_MPFR_RNDZ "MPFR_RNDZ"
        C_MPFR_RNDU "MPFR_RNDU"
        C_MPFR_RNDD "MPFR_RNDD"
        C_MPFR_RNDA "MPFR_RNDA"
        C_MPFR_RNDF "MPFR_RNDF"
        C_MPFR_RNDNA "MPFR_RNDNA" = -1

    # Limits
    int C_MPFR_PREC_MIN "MPFR_PREC_MIN"
    int C_MPFR_PREC_MAX "MPFR_PREC_MAX"

    # MPFR function definitions
    void c_mpfr_init2 "mpfr_init2" (mpfr_t x, mpfr_prec_t prec)
    void c_mpfr_clear "mpfr_clear" (mpfr_t x)
    int c_mpfr_set "mpfr_set" (mpfr_t rop, mpfr_t op, mpfr_rnd_t rnd)
    int c_mpfr_set_d "mpfr_set_d" (mpfr_t rop, double op, mpfr_rnd_t rnd)

    int c_mpfr_set_str "mpfr_set_str" (
        mpfr_t rop, char *s, int base, mpfr_rnd_t rnd
    )

    char * c_mpfr_get_str "mpfr_get_str" (
        char *str, mpfr_exp_t *expptr, int b,
        size_t n, mpfr_t op, mpfr_rnd_t rnd
    )

    void c_mpfr_free_str "mpfr_free_str" (char *str)

    int c_mpfr_const_pi "mpfr_const_pi" (mpfr_t rop, mpfr_rnd_t rnd)


# Make precision limits available to Python
MPFR_PREC_MIN = C_MPFR_PREC_MIN
MPFR_PREC_MAX = C_MPFR_PREC_MAX

# Make rounding mode values available to Python
MPFR_RNDN =  C_MPFR_RNDN
MPFR_RNDZ =  C_MPFR_RNDZ
MPFR_RNDU =  C_MPFR_RNDU
MPFR_RNDD =  C_MPFR_RNDD
MPFR_RNDA =  C_MPFR_RNDA
MPFR_RNDF =  C_MPFR_RNDF
MPFR_RNDNA =  C_MPFR_RNDNA


# Checks for valid parameter ranges
cdef check_rounding_mode(mpfr_rnd_t rnd):
    if not MPFR_RNDN <= rnd <= MPFR_RNDA:
        raise ValueError("invalid rounding mode {}".format(rnd))


cdef check_base(int b):
    if not 2 <= b <= 62:
        raise ValueError("base should be in the range 2 to 62 (inclusive)")


cdef check_precision(int precision):
    if not MPFR_PREC_MIN <= precision <= MPFR_PREC_MAX:
        raise ValueError(
            "precision should be between {} and {}".format(
                MPFR_PREC_MIN, MPFR_PREC_MAX
            )
        )


cdef class Mpfr:
    """ Mutable arbitrary-precision floating-point type. """
    cdef mpfr_t _value

    def __cinit__(self, precision):
        check_precision(precision)
        c_mpfr_init2(self._value, precision)

    def __dealloc__(self):
        if self._value._mpfr_d != NULL:
            c_mpfr_clear(self._value)


def mpfr_get_str(Mpfr op not None, int b, mpfr_rnd_t rnd):
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
    cdef mpfr_exp_t exp
    cdef bytes digits

    check_base(b)
    check_rounding_mode(rnd)
    c_digits = c_mpfr_get_str(NULL, &exp, b, 0, op._value, rnd)
    if c_digits == NULL:
        raise RuntimeError("Error during string conversion.")

    try:
        digits = str(c_digits)
    finally:
        c_mpfr_free_str(c_digits)

    return digits, exp


def mpfr_const_pi(Mpfr rop not None, mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return c_mpfr_const_pi(rop._value, rnd)

def mpfr_set(Mpfr rop not None, Mpfr op not None, mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return c_mpfr_set(rop._value, op._value, rnd)

def mpfr_set_d(Mpfr rop not None, double op, mpfr_rnd_t rnd):
    check_rounding_mode(rnd)
    return c_mpfr_set_d(rop._value, op, rnd)

def mpfr_set_str(Mpfr rop not None, bytes s, int base, mpfr_rnd_t rnd):
    check_base(base)
    check_rounding_mode(rnd)
    return c_mpfr_set_str(rop._value, s, base, rnd)

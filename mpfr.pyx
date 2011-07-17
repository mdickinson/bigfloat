# GMP type declarations
cdef extern from "gmp.h":
    ctypedef int mp_exp_t
    ctypedef unsigned int mp_limb_t

# MPFR type declarations
cdef extern from "mpfr.h":
    ctypedef int mpfr_prec_t
    ctypedef int mpfr_sign_t
    ctypedef mp_exp_t mpfr_exp_t

    ctypedef struct __mpfr_struct:
        mpfr_prec_t _mpfr_prec
        mpfr_sign_t _mpfr_sign
        mpfr_exp_t  _mpfr_exp
        mp_limb_t   *_mpfr_d

    ctypedef __mpfr_struct mpfr_t[1]

    ctypedef enum mpfr_rnd_t:
        MPFR_RNDN = 0
        MPFR_RNDZ
        MPFR_RNDU
        MPFR_RNDD
        MPFR_RNDA
        MPFR_RNDF
        MPFR_RNDNA = -1

    int mpfr_const_pi(mpfr_t rop, mpfr_rnd_t rnd)
    void mpfr_init2(mpfr_t x, mpfr_prec_t prec)
    void mpfr_clear(mpfr_t x)

    char * mpfr_get_str (
        char *str, mpfr_exp_t *expptr, int b,
        size_t n, mpfr_t op, mpfr_rnd_t rnd
    )

    void mpfr_free_str(char *str)

def compute_pi(n):
    """ Return pi, computed to n bits. """

    cdef mpfr_t pi
    cdef mpfr_exp_t exp
    cdef char* pistr
    cdef bytes return_str

    mpfr_init2(pi, n)
    mpfr_const_pi(pi, MPFR_RNDN)

    pistr = mpfr_get_str(NULL, &exp, 10, 0, pi, MPFR_RNDN)
    if pistr is NULL:
        raise RuntimeError("Error during string conversion.")

    try:
        return_str = str(pistr)
    finally:
        mpfr_free_str(pistr)

    mpfr_clear(pi)

    return return_str

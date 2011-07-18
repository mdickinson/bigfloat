cimport cgmp

cdef extern from "mpfr.h":
    # Define MPFR version number
    int MPFR_VERSION_MAJOR
    int MPFR_VERSION_MINOR
    int MPFR_VERSION_PATCHLEVEL
    char *MPFR_VERSION_STRING

    # MPFR type declarations
    ctypedef int mpfr_prec_t
    ctypedef int mpfr_sign_t
    ctypedef cgmp.mp_exp_t mpfr_exp_t

    ctypedef struct __mpfr_struct:
        mpfr_prec_t _mpfr_prec
        mpfr_sign_t _mpfr_sign
        mpfr_exp_t  _mpfr_exp
        cgmp.mp_limb_t   *_mpfr_d

    ctypedef __mpfr_struct mpfr_t[1]

    # MPFR rounding modes
    ctypedef enum mpfr_rnd_t:
        MPFR_RNDN = 0
        MPFR_RNDZ
        MPFR_RNDU
        MPFR_RNDD
        MPFR_RNDA
        MPFR_RNDF
        MPFR_RNDNA = -1

    # Limits
    mpfr_prec_t MPFR_PREC_MIN
    mpfr_prec_t MPFR_PREC_MAX

    mpfr_exp_t MPFR_EMIN_DEFAULT
    mpfr_exp_t MPFR_EMAX_DEFAULT

    # Functions to get and set exponent min and max values.
    mpfr_exp_t mpfr_get_emin()
    mpfr_exp_t mpfr_get_emin_min()
    mpfr_exp_t mpfr_get_emin_max()
    mpfr_exp_t mpfr_get_emax()
    mpfr_exp_t mpfr_get_emax_min()
    mpfr_exp_t mpfr_get_emax_max()
    int mpfr_set_emin(mpfr_exp_t exp)
    int mpfr_set_emax(mpfr_exp_t exp)

    # MPFR function definitions
    void mpfr_init2(mpfr_t x, mpfr_prec_t prec)
    void mpfr_clear(mpfr_t x)
    int mpfr_set(mpfr_t rop, mpfr_t op, mpfr_rnd_t rnd)
    int mpfr_set_d(mpfr_t rop, double op, mpfr_rnd_t rnd)

    int mpfr_set_str(
        mpfr_t rop, char *s, int base, mpfr_rnd_t rnd
    )

    int mpfr_strtofr(
        mpfr_t rop, char *nptr, char **endptr, int base, mpfr_rnd_t rnd
    )

    char * mpfr_get_str(
        char *str, mpfr_exp_t *expptr, int b,
        size_t n, mpfr_t op, mpfr_rnd_t rnd
    )

    void mpfr_free_str(char *str)

    int mpfr_const_pi(mpfr_t rop, mpfr_rnd_t rnd)

    void mpfr_clear_flags()
    void mpfr_clear_underflow()
    void mpfr_clear_overflow()
    void mpfr_clear_nanflag()
    void mpfr_clear_inexflag()
    void mpfr_clear_erangeflag()

    void mpfr_set_underflow()
    void mpfr_set_overflow()
    void mpfr_set_nanflag()
    void mpfr_set_inexflag()
    void mpfr_set_erangeflag()

    int mpfr_underflow_p()
    int mpfr_overflow_p()
    int mpfr_nanflag_p()
    int mpfr_inexflag_p()
    int mpfr_erangeflag_p()

    int mpfr_check_range(mpfr_t x, int t, mpfr_rnd_t rnd)

    int mpfr_neg(mpfr_t rop, mpfr_t op, mpfr_rnd_t rnd)
    int mpfr_add(mpfr_t rop, mpfr_t op1, mpfr_t op2, mpfr_rnd_t rnd)
    int mpfr_sub(mpfr_t rop, mpfr_t op1, mpfr_t op2, mpfr_rnd_t rnd)
    int mpfr_mul(mpfr_t rop, mpfr_t op1, mpfr_t op2, mpfr_rnd_t rnd)
    int mpfr_div(mpfr_t rop, mpfr_t op1, mpfr_t op2, mpfr_rnd_t rnd)
    int mpfr_fmod(mpfr_t rop, mpfr_t op1, mpfr_t op2, mpfr_rnd_t rnd)

    int mpfr_zero_p(mpfr_t op)

    int mpfr_greater_p(mpfr_t op1, mpfr_t op2)
    int mpfr_greaterequal_p(mpfr_t op1, mpfr_t op2)
    int mpfr_less_p(mpfr_t op1, mpfr_t op2)
    int mpfr_lessequal_p(mpfr_t op1, mpfr_t op2)
    int mpfr_equal_p(mpfr_t op1, mpfr_t op2)

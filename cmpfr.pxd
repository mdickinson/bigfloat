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

cimport cgmp

cdef extern from "mpfr.h":
    # MPFR type declarations
    ctypedef int mpfr_prec_t
    ctypedef int mpfr_sign_t
    ctypedef cgmp.mp_exp_t mpfr_exp_t

    ctypedef struct __mpfr_struct:
        mpfr_prec_t _mpfr_prec
        mpfr_sign_t _mpfr_sign
        mpfr_exp_t  _mpfr_exp
        cgmp.mp_limb_t   *_mpfr_d

    # We don't export the mpfr_t type; it's not useful for Cython code, since
    # Cython (as of version 0.14.1) doesn't seem to understand it properly: the
    # generated C code includes temporary variables of type mpfr_t and
    # assignments from one object of type mpfr_t to another, which isn't valid
    # C.  So we comment out the definition here in order to catch any
    # accidental declarations using mpfr_t below.

    # ctypedef __mpfr_struct mpfr_t[1]
    ctypedef __mpfr_struct *mpfr_ptr

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


    ###########################################################################
    # 5.1 Initialization Functions
    ###########################################################################

    void mpfr_init2(mpfr_ptr x, mpfr_prec_t prec)
    void mpfr_clear(mpfr_ptr x)
    void mpfr_init(mpfr_ptr x)
    void mpfr_set_default_prec(mpfr_prec_t prec)
    mpfr_prec_t mpfr_get_default_prec()
    void mpfr_set_prec(mpfr_ptr x, mpfr_prec_t prec)
    mpfr_prec_t mpfr_get_prec(mpfr_ptr x)


    ###########################################################################
    # 5.2 Assignment Functions
    ###########################################################################

    int mpfr_set(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_set_si(mpfr_ptr rop, long int op, mpfr_rnd_t rnd)
    int mpfr_set_d(mpfr_ptr rop, double op, mpfr_rnd_t rnd)
    int mpfr_set_si_2exp(
        mpfr_ptr rop, long int op, mpfr_exp_t e, mpfr_rnd_t rnd
    )
    int mpfr_set_str(
        mpfr_ptr rop, const char *s, int base, mpfr_rnd_t rnd
    )
    int mpfr_strtofr(
        mpfr_ptr rop, const char *nptr, char **endptr, int base, mpfr_rnd_t rnd
    )
    void mpfr_set_nan(mpfr_ptr x)
    void mpfr_set_inf(mpfr_ptr x, int sign)
    void mpfr_set_zero(mpfr_ptr x, int sign)
    void mpfr_swap(mpfr_ptr x, mpfr_ptr y)


    ###########################################################################
    # 5.4 Conversion Functions
    ###########################################################################

    double mpfr_get_d(mpfr_ptr op, mpfr_rnd_t rnd)
    long int mpfr_get_si(mpfr_ptr op, mpfr_rnd_t rnd)
    double mpfr_get_d_2exp(long int *exp, mpfr_ptr op, mpfr_rnd_t rnd)
    char * mpfr_get_str(
        char *str, mpfr_exp_t *expptr, int b,
        size_t n, mpfr_ptr op, mpfr_rnd_t rnd
    )
    void mpfr_free_str(char *str)
    int mpfr_fits_slong_p(mpfr_ptr x, mpfr_rnd_t rnd)


    ###########################################################################
    # 5.5 Basic Arithmetic Functions
    ###########################################################################

    int mpfr_add(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_sub(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_mul(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_sqr(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_div(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_sqrt(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_rec_sqrt(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_cbrt(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_root(
        mpfr_ptr top, mpfr_ptr op, unsigned long int k, mpfr_rnd_t rnd
    )
    int mpfr_pow(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_neg(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_abs(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_dim(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)


    ###########################################################################
    # 5.6 Comparison Functions
    ###########################################################################

    int mpfr_cmp(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_cmpabs(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_nan_p(mpfr_ptr op)
    int mpfr_inf_p(mpfr_ptr op)
    int mpfr_number_p(mpfr_ptr op)
    int mpfr_zero_p(mpfr_ptr op)
    int mpfr_regular_p(mpfr_ptr op)
    int mpfr_sgn(mpfr_ptr op)
    int mpfr_greater_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_greaterequal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_less_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_lessequal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_equal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_lessgreater_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_unordered_p(mpfr_ptr op1, mpfr_ptr op2)


    ###########################################################################
    # 5.7 Special Functions
    ###########################################################################

    int mpfr_log(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_log2(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_log10(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_exp(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_exp2(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_exp10(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_cos(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_sin(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_tan(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_sin_cos(mpfr_ptr sop, mpfr_ptr cop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_sec(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_csc(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_cot(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_acos(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_asin(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_atan(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_atan2(mpfr_ptr rop, mpfr_ptr y, mpfr_ptr x, mpfr_rnd_t rnd)

    int mpfr_cosh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_sinh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_tanh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_sinh_cosh(mpfr_ptr sop, mpfr_ptr cop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_sech(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_csch(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_coth(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_acosh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_asinh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_atanh(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_fac_ui(mpfr_ptr rop, unsigned long int op, mpfr_rnd_t rnd)

    int mpfr_log1p(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_expm1(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_eint(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_li2(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_gamma(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_lngamma(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_lgamma(mpfr_ptr rop, int *signp, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_digamma(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_zeta(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_zeta_ui(mpfr_ptr rop, unsigned long int op, mpfr_rnd_t rnd)
    int mpfr_erf(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_erfc(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_j0(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_j1(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_jn(mpfr_ptr rop, long int n, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_y0(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_y1(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_yn(mpfr_ptr rop, long int n, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_fma(
        mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_ptr op3, mpfr_rnd_t rnd
    )
    int mpfr_fms(
        mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_ptr op3, mpfr_rnd_t rnd
    )
    int mpfr_agm(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_hypot(mpfr_ptr rop, mpfr_ptr x, mpfr_ptr y, mpfr_rnd_t rnd)

    int mpfr_ai(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_const_log2(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_pi(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_euler(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_catalan(mpfr_ptr rop, mpfr_rnd_t rnd)
    void mpfr_free_cache()


    ###########################################################################
    # 5.10 Integer and Remainder Related Functions
    ###########################################################################

    int mpfr_rint(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_ceil(mpfr_ptr rop, mpfr_ptr op)
    int mpfr_floor(mpfr_ptr rop, mpfr_ptr op)
    int mpfr_round(mpfr_ptr rop, mpfr_ptr op)
    int mpfr_trunc(mpfr_ptr rop, mpfr_ptr op)

    int mpfr_rint_ceil(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_rint_floor(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_rint_round(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_rint_trunc(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_frac(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_modf(mpfr_ptr iop, mpfr_ptr fop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_fmod(mpfr_ptr r, mpfr_ptr x, mpfr_ptr y, mpfr_rnd_t rnd)
    int mpfr_remainder(mpfr_ptr r, mpfr_ptr x, mpfr_ptr y, mpfr_rnd_t rnd)
    int mpfr_remquo(
        mpfr_ptr r, long int *q, mpfr_ptr x, mpfr_ptr y, mpfr_rnd_t rnd
    )
    int mpfr_integer_p(mpfr_ptr op)


    ###########################################################################
    # 5.11 Rounding Related Functions
    ###########################################################################

    void mpfr_set_default_rounding_mode(mpfr_rnd_t rnd)
    mpfr_rnd_t mpfr_get_default_rounding_mode()
    int mpfr_prec_round(mpfr_ptr x, mpfr_prec_t prec, mpfr_rnd_t rnd)
    int mpfr_can_round(
        mpfr_ptr b, mpfr_exp_t err,
        mpfr_rnd_t rnd1, mpfr_rnd_t rnd2,
        mpfr_prec_t prec
    )
    mpfr_prec_t mpfr_min_prec(mpfr_ptr x)
    const char *mpfr_print_rnd_mode(mpfr_rnd_t rnd)


    ###########################################################################
    # 5.12 Miscellaneous Functions
    ###########################################################################

    void mpfr_nexttoward(mpfr_ptr rop, mpfr_ptr op)
    void mpfr_nextabove(mpfr_ptr op)
    void mpfr_nextbelow(mpfr_ptr op)
    int mpfr_min(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_max(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    mpfr_exp_t mpfr_get_exp(mpfr_ptr x)
    int mpfr_set_exp(mpfr_ptr x, mpfr_exp_t exp)
    int mpfr_signbit(mpfr_ptr op)
    int mpfr_setsign(mpfr_ptr rop, mpfr_ptr op, int s, mpfr_rnd_t rnd)
    int mpfr_copysign(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    const char *mpfr_get_version()
    int MPFR_VERSION
    int MPFR_VERSION_MAJOR
    int MPFR_VERSION_MINOR
    int MPFR_VERSION_PATCHLEVEL
    const char *MPFR_VERSION_STRING
    int MPFR_VERSION_NUM(int major, int minor, int patchlevel)
    const char *mpfr_get_patches()
    int mpfr_buildopt_tls_p()
    int mpfr_buildopt_decimal_p()


    ###########################################################################
    # 5.13 Exception Related Functions
    ###########################################################################

    mpfr_exp_t mpfr_get_emin()
    mpfr_exp_t mpfr_get_emax()
    int mpfr_set_emin(mpfr_exp_t exp)
    int mpfr_set_emax(mpfr_exp_t exp)
    mpfr_exp_t mpfr_get_emin_min()
    mpfr_exp_t mpfr_get_emin_max()
    mpfr_exp_t mpfr_get_emax_min()
    mpfr_exp_t mpfr_get_emax_max()
    int mpfr_check_range(mpfr_ptr x, int t, mpfr_rnd_t rnd)
    int mpfr_subnormalize(mpfr_ptr x, int t, mpfr_rnd_t rnd)

    void mpfr_clear_underflow()
    void mpfr_clear_overflow()
    void mpfr_clear_divby0()
    void mpfr_clear_nanflag()
    void mpfr_clear_inexflag()
    void mpfr_clear_erangeflag()

    void mpfr_set_underflow()
    void mpfr_set_overflow()
    void mpfr_set_divby0()
    void mpfr_set_nanflag()
    void mpfr_set_inexflag()
    void mpfr_set_erangeflag()

    void mpfr_clear_flags()

    int mpfr_underflow_p()
    int mpfr_overflow_p()
    int mpfr_divby0_p()
    int mpfr_nanflag_p()
    int mpfr_inexflag_p()
    int mpfr_erangeflag_p()

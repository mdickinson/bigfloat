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

    # Functions to get and set exponent min and max values.
    mpfr_exp_t mpfr_get_emin()
    mpfr_exp_t mpfr_get_emin_min()
    mpfr_exp_t mpfr_get_emin_max()
    mpfr_exp_t mpfr_get_emax()
    mpfr_exp_t mpfr_get_emax_min()
    mpfr_exp_t mpfr_get_emax_max()
    int mpfr_set_emin(mpfr_exp_t exp)
    int mpfr_set_emax(mpfr_exp_t exp)

    void mpfr_set_prec(mpfr_ptr x, mpfr_prec_t prec)
    mpfr_prec_t mpfr_get_prec(mpfr_ptr x)
    int mpfr_setsign(mpfr_ptr rop, mpfr_ptr op, int s, mpfr_rnd_t rnd)

    double mpfr_get_d(mpfr_ptr op, mpfr_rnd_t rnd)
    long mpfr_get_si(mpfr_ptr op, mpfr_rnd_t rnd)

    # MPFR function definitions
    void mpfr_init2(mpfr_ptr x, mpfr_prec_t prec)
    void mpfr_clear(mpfr_ptr x)
    int mpfr_set(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_set_si(mpfr_ptr rop, long int op, mpfr_rnd_t rnd)
    int mpfr_set_d(mpfr_ptr rop, double op, mpfr_rnd_t rnd)

    int mpfr_set_si_2exp(
        mpfr_ptr rop, long int op, mpfr_exp_t e, mpfr_rnd_t rnd
    )

    int mpfr_set_str(
        mpfr_ptr rop, char *s, int base, mpfr_rnd_t rnd
    )

    int mpfr_strtofr(
        mpfr_ptr rop, char *nptr, char **endptr, int base, mpfr_rnd_t rnd
    )

    char * mpfr_get_str(
        char *str, mpfr_exp_t *expptr, int b,
        size_t n, mpfr_ptr op, mpfr_rnd_t rnd
    )

    void mpfr_free_str(char *str)

    void mpfr_set_nan(mpfr_ptr x)
    void mpfr_set_inf(mpfr_ptr x, int sign)
    void mpfr_set_zero(mpfr_ptr x, int sign)

    void mpfr_swap(mpfr_ptr x, mpfr_ptr y)

    mpfr_exp_t mpfr_get_exp(mpfr_ptr x)
    int mpfr_set_exp(mpfr_ptr x, mpfr_exp_t exp)

    int mpfr_const_log2(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_pi(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_euler(mpfr_ptr rop, mpfr_rnd_t rnd)
    int mpfr_const_catalan(mpfr_ptr rop, mpfr_rnd_t rnd)

    void mpfr_free_cache()

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

    int mpfr_check_range(mpfr_ptr x, int t, mpfr_rnd_t rnd)
    int mpfr_subnormalize(mpfr_ptr x, int t, mpfr_rnd_t rnd)

    int mpfr_neg(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_abs(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_add(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_sub(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_mul(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_div(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_fmod(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)
    int mpfr_pow(mpfr_ptr rop, mpfr_ptr op1, mpfr_ptr op2, mpfr_rnd_t rnd)

    int mpfr_sqrt(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_exp(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_log(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)
    int mpfr_log2(mpfr_ptr rop, mpfr_ptr op, mpfr_rnd_t rnd)

    int mpfr_nan_p(mpfr_ptr op)
    int mpfr_inf_p(mpfr_ptr op)
    int mpfr_number_p(mpfr_ptr op)
    int mpfr_integer_p(mpfr_ptr op)
    int mpfr_zero_p(mpfr_ptr op)
    int mpfr_regular_p(mpfr_ptr op)
    int mpfr_signbit(mpfr_ptr op)

    int mpfr_greater_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_greaterequal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_less_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_lessequal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_equal_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_lessgreater_p(mpfr_ptr op1, mpfr_ptr op2)
    int mpfr_unordered_p(mpfr_ptr op1, mpfr_ptr op2)

    void mpfr_nexttoward(mpfr_ptr rop, mpfr_ptr op)
    void mpfr_nextabove(mpfr_ptr op)
    void mpfr_nextbelow(mpfr_ptr op)

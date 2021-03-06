Coverage of MPFR functions by bigfloat
--------------------------------------

The following tables show the coverage of the MPFR library by ``bigfloat``.
They're organised according to the subsections of the "MPFR Interface"
section of the MPFR documentation
(https://www.mpfr.org/mpfr-current/mpfr.html#MPFR-Interface).

5.1 Initialization Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------------------+-----------------+
| mpfr_init2            | wrapped         |
+-----------------------+-----------------+
| mpfr_inits2           | emulated        |
+-----------------------+-----------------+
| mpfr_clear            | wrapped         |
+-----------------------+-----------------+
| mpfr_clears           | emulated        |
+-----------------------+-----------------+
| mpfr_init             | wrapped         |
+-----------------------+-----------------+
| mpfr_inits            | emulated        |
+-----------------------+-----------------+
| MPFR_DECL_INIT        | not implemented |
+-----------------------+-----------------+
| mpfr_set_default_prec | wrapped         |
+-----------------------+-----------------+
| mpfr_get_default_prec | wrapped         |
+-----------------------+-----------------+
| mpfr_set_prec         | wrapped         |
+-----------------------+-----------------+
| mpfr_get_prec         | wrapped         |
+-----------------------+-----------------+

5.2 Assignment functions
~~~~~~~~~~~~~~~~~~~~~~~~

+--------------------+-----------------+
| mpfr_set           | wrapped         |
+--------------------+-----------------+
| mpfr_set_ui        | wrapped         |
+--------------------+-----------------+
| mpfr_set_si        | wrapped         |
+--------------------+-----------------+
| mpfr_set_uj        | not implemented |
+--------------------+-----------------+
| mpfr_set_sj        | not implemented |
+--------------------+-----------------+
| mpfr_set_flt       | not implemented |
+--------------------+-----------------+
| mpfr_set_d         | wrapped         |
+--------------------+-----------------+
| mpfr_set_ld        | not implemented |
+--------------------+-----------------+
| mpfr_set_float128  | not implemented |
+--------------------+-----------------+
| mpfr_set_decimal64 | not implemented |
+--------------------+-----------------+
| mpfr_set_z         | wrapped         |
+--------------------+-----------------+
| mpfr_set_q         | not implemented |
+--------------------+-----------------+
| mpfr_set_f         | not implemented |
+--------------------+-----------------+
| mpfr_set_ui_2exp   | wrapped         |
+--------------------+-----------------+
| mpfr_set_si_2exp   | wrapped         |
+--------------------+-----------------+
| mpfr_set_uj_2exp   | not implemented |
+--------------------+-----------------+
| mpfr_set_sj_2exp   | not implemented |
+--------------------+-----------------+
| mpfr_set_z_2exp    | wrapped         |
+--------------------+-----------------+
| mpfr_set_str       | wrapped         |
+--------------------+-----------------+
| mpfr_strtofr       | wrapped         |
+--------------------+-----------------+
| mpfr_set_nan       | wrapped         |
+--------------------+-----------------+
| mpfr_set_inf       | wrapped         |
+--------------------+-----------------+
| mpfr_set_zero      | wrapped         |
+--------------------+-----------------+
| mpfr_swap          | wrapped         |
+--------------------+-----------------+

5.3 Combined Initialization and Assignment Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-------------------+-----------------+
| mpfr_init_set     | not implemented |
+-------------------+-----------------+
| mpfr_init_set_ui  | not implemented |
+-------------------+-----------------+
| mpfr_init_set_si  | not implemented |
+-------------------+-----------------+
| mpfr_init_set_d   | not implemented |
+-------------------+-----------------+
| mpfr_init_set_ld  | not implemented |
+-------------------+-----------------+
| mpfr_init_set_z   | not implemented |
+-------------------+-----------------+
| mpfr_init_set_q   | not implemented |
+-------------------+-----------------+
| mpfr_init_set_f   | not implemented |
+-------------------+-----------------+
| mpfr_init_set_str | not implemented |
+-------------------+-----------------+

5.4 Conversion Functions
~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+------------------------+
| mpfr_get_flt        | not implemented        |
+---------------------+------------------------+
| mpfr_get_d          | wrapped                |
+---------------------+------------------------+
| mpfr_get_ld         | not implemented        |
+---------------------+------------------------+
| mpfr_get_float128   | not implemented        |
+---------------------+------------------------+
| mpfr_get_decimal64  | not implemented        |
+---------------------+------------------------+
| mpfr_get_si         | wrapped                |
+---------------------+------------------------+
| mpfr_get_ui         | wrapped                |
+---------------------+------------------------+
| mpfr_get_sj         | not implemented        |
+---------------------+------------------------+
| mpfr_get_uj         | not implemented        |
+---------------------+------------------------+
| mpfr_get_d_2exp     | wrapped                |
+---------------------+------------------------+
| mpfr_get_ld_2exp    | not implemented        |
+---------------------+------------------------+
| mpfr_frexp          | wrapped                |
+---------------------+------------------------+
| mpfr_get_z_2exp     | wrapped                |
+---------------------+------------------------+
| mpfr_get_z          | wrapped                |
+---------------------+------------------------+
| mpfr_get_q          | not implemented        |
+---------------------+------------------------+
| mpfr_get_f          | not implemented        |
+---------------------+------------------------+
| mpfr_get_str        | wrapped (see note)     |
+---------------------+------------------------+
| mpfr_free_str       | not exposed (see note) |
+---------------------+------------------------+
| mpfr_fits_ulong_p   | wrapped                |
+---------------------+------------------------+
| mpfr_fits_slong_p   | wrapped                |
+---------------------+------------------------+
| mpfr_fits_uint_p    | not implemented        |
+---------------------+------------------------+
| mpfr_fits_sint_p    | not implemented        |
+---------------------+------------------------+
| mpfr_fits_ushort_p  | not implemented        |
+---------------------+------------------------+
| mpfr_fits_sshort_p  | not implemented        |
+---------------------+------------------------+
| mpfr_fits_uintmax_p | not implemented        |
+---------------------+------------------------+
| mpfr_fits_intmax_p  | not implemented        |
+---------------------+------------------------+

Note: the wrapper :func:`mpfr.mpfr_get_str` for ``mpfr_get_str`` does not
support writing to an existing buffer; it always returns a new Python string,
whose lifetime is handled by Python's usual garbage collection facilities.
There's no need to free the string explicitly.  The ``mpfr_free_str`` function
is used by :func:`mpfr.mpfr_get_str`, but is not exposed to Python.

5.5 Basic Arithmetic Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+------------------------+
| mpfr_add            | wrapped                |
+---------------------+------------------------+
| mpfr_add_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_add_si         | not implemented        |
+---------------------+------------------------+
| mpfr_add_d          | not implemented        |
+---------------------+------------------------+
| mpfr_add_z          | not implemented        |
+---------------------+------------------------+
| mpfr_add_q          | not implemented        |
+---------------------+------------------------+
| mpfr_sub            | wrapped                |
+---------------------+------------------------+
| mpfr_ui_sub         | not implemented        |
+---------------------+------------------------+
| mpfr_sub_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_si_sub         | not implemented        |
+---------------------+------------------------+
| mpfr_sub_si         | not implemented        |
+---------------------+------------------------+
| mpfr_d_sub          | not implemented        |
+---------------------+------------------------+
| mpfr_sub_d          | not implemented        |
+---------------------+------------------------+
| mpfr_z_sub          | not implemented        |
+---------------------+------------------------+
| mpfr_sub_z          | not implemented        |
+---------------------+------------------------+
| mpfr_sub_q          | not implemented        |
+---------------------+------------------------+
| mpfr_mul            | wrapped                |
+---------------------+------------------------+
| mpfr_mul_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_mul_si         | not implemented        |
+---------------------+------------------------+
| mpfr_mul_d          | not implemented        |
+---------------------+------------------------+
| mpfr_mul_z          | not implemented        |
+---------------------+------------------------+
| mpfr_mul_q          | not implemented        |
+---------------------+------------------------+
| mpfr_sqr            | wrapped                |
+---------------------+------------------------+
| mpfr_div            | wrapped                |
+---------------------+------------------------+
| mpfr_ui_div         | not implemented        |
+---------------------+------------------------+
| mpfr_div_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_si_div         | not implemented        |
+---------------------+------------------------+
| mpfr_div_si         | not implemented        |
+---------------------+------------------------+
| mpfr_d_div          | not implemented        |
+---------------------+------------------------+
| mpfr_div_d          | not implemented        |
+---------------------+------------------------+
| mpfr_div_z          | not implemented        |
+---------------------+------------------------+
| mpfr_div_q          | not implemented        |
+---------------------+------------------------+
| mpfr_sqrt           | wrapped                |
+---------------------+------------------------+
| mpfr_sqrt_ui        | not implemented        |
+---------------------+------------------------+
| mpfr_rec_sqrt       | wrapped                |
+---------------------+------------------------+
| mpfr_cbrt           | wrapped                |
+---------------------+------------------------+
| mpfr_rootn_ui       | wrapped                |
+---------------------+------------------------+
| mpfr_root           | wrapped (deprecated)   |
+---------------------+------------------------+
| mpfr_pow            | wrapped                |
+---------------------+------------------------+
| mpfr_pow_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_pow_si         | not implemented        |
+---------------------+------------------------+
| mpfr_pow_z          | not implemented        |
+---------------------+------------------------+
| mpfr_ui_pow_ui      | not implemented        |
+---------------------+------------------------+
| mpfr_ui_pow         | not implemented        |
+---------------------+------------------------+
| mpfr_neg            | wrapped                |
+---------------------+------------------------+
| mpfr_abs            | wrapped                |
+---------------------+------------------------+
| mpfr_dim            | wrapped                |
+---------------------+------------------------+
| mpfr_mul_2ui        | not implemented        |
+---------------------+------------------------+
| mpfr_mul_2si        | not implemented        |
+---------------------+------------------------+
| mpfr_div_2ui        | not implemented        |
+---------------------+------------------------+
| mpfr_div_2si        | not implemented        |
+---------------------+------------------------+

5.6 Comparison Functions
~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+------------------------+
| mpfr_cmp            | wrapped                |
+---------------------+------------------------+
| mpfr_cmp_ui         | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_si         | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_d          | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_ld         | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_z          | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_q          | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_f          | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_ui_2exp    | not implemented        |
+---------------------+------------------------+
| mpfr_cmp_si_2exp    | not implemented        |
+---------------------+------------------------+
| mpfr_cmpabs         | wrapped                |
+---------------------+------------------------+
| mpfr_nan_p          | wrapped                |
+---------------------+------------------------+
| mpfr_inf_p          | wrapped                |
+---------------------+------------------------+
| mpfr_number_p       | wrapped                |
+---------------------+------------------------+
| mpfr_zero_p         | wrapped                |
+---------------------+------------------------+
| mpfr_regular_p      | wrapped                |
+---------------------+------------------------+
| mpfr_sgn            | wrapped                |
+---------------------+------------------------+
| mpfr_greater_p      | wrapped                |
+---------------------+------------------------+
| mpfr_greaterequal_p | wrapped                |
+---------------------+------------------------+
| mpfr_less_p         | wrapped                |
+---------------------+------------------------+
| mpfr_lessequal_p    | wrapped                |
+---------------------+------------------------+
| mpfr_equal_p        | wrapped                |
+---------------------+------------------------+
| mpfr_lessgreater_p  | wrapped                |
+---------------------+------------------------+
| mpfr_unordered_p    | wrapped                |
+---------------------+------------------------+

5.7 Special Functions
~~~~~~~~~~~~~~~~~~~~~

+------------------------+------------------------+
| mpfr_log               | wrapped                |
+------------------------+------------------------+
| mpfr_log_ui            | wrapped                |
+------------------------+------------------------+
| mpfr_log2              | wrapped                |
+------------------------+------------------------+
| mpfr_log10             | wrapped                |
+------------------------+------------------------+
| mpfr_log1p             | wrapped                |
+------------------------+------------------------+
| mpfr_exp               | wrapped                |
+------------------------+------------------------+
| mpfr_exp2              | wrapped                |
+------------------------+------------------------+
| mpfr_exp10             | wrapped                |
+------------------------+------------------------+
| mpfr_expm1             | wrapped                |
+------------------------+------------------------+
| mpfr_cos               | wrapped                |
+------------------------+------------------------+
| mpfr_sin               | wrapped                |
+------------------------+------------------------+
| mpfr_tan               | wrapped                |
+------------------------+------------------------+
| mpfr_sin_cos           | wrapped                |
+------------------------+------------------------+
| mpfr_sec               | wrapped                |
+------------------------+------------------------+
| mpfr_csc               | wrapped                |
+------------------------+------------------------+
| mpfr_cot               | wrapped                |
+------------------------+------------------------+
| mpfr_acos              | wrapped                |
+------------------------+------------------------+
| mpfr_asin              | wrapped                |
+------------------------+------------------------+
| mpfr_atan              | wrapped                |
+------------------------+------------------------+
| mpfr_atan2             | wrapped                |
+------------------------+------------------------+
| mpfr_cosh              | wrapped                |
+------------------------+------------------------+
| mpfr_sinh              | wrapped                |
+------------------------+------------------------+
| mpfr_tanh              | wrapped                |
+------------------------+------------------------+
| mpfr_sinh_cosh         | wrapped                |
+------------------------+------------------------+
| mpfr_sech              | wrapped                |
+------------------------+------------------------+
| mpfr_csch              | wrapped                |
+------------------------+------------------------+
| mpfr_coth              | wrapped                |
+------------------------+------------------------+
| mpfr_acosh             | wrapped                |
+------------------------+------------------------+
| mpfr_asinh             | wrapped                |
+------------------------+------------------------+
| mpfr_atanh             | wrapped                |
+------------------------+------------------------+
| mpfr_fac_ui            | wrapped                |
+------------------------+------------------------+
| mpfr_eint              | wrapped                |
+------------------------+------------------------+
| mpfr_li2               | wrapped                |
+------------------------+------------------------+
| mpfr_gamma             | wrapped                |
+------------------------+------------------------+
| mpfr_gamma_inc         | wrapped                |
+------------------------+------------------------+
| mpfr_lngamma           | wrapped                |
+------------------------+------------------------+
| mpfr_lgamma            | wrapped                |
+------------------------+------------------------+
| mpfr_digamma           | wrapped                |
+------------------------+------------------------+
| mpfr_beta              | wrapped                |
+------------------------+------------------------+
| mpfr_zeta              | wrapped                |
+------------------------+------------------------+
| mpfr_zeta_ui           | wrapped                |
+------------------------+------------------------+
| mpfr_erf               | wrapped                |
+------------------------+------------------------+
| mpfr_erfc              | wrapped                |
+------------------------+------------------------+
| mpfr_j0                | wrapped                |
+------------------------+------------------------+
| mpfr_j1                | wrapped                |
+------------------------+------------------------+
| mpfr_jn                | wrapped                |
+------------------------+------------------------+
| mpfr_y0                | wrapped                |
+------------------------+------------------------+
| mpfr_y1                | wrapped                |
+------------------------+------------------------+
| mpfr_yn                | wrapped                |
+------------------------+------------------------+
| mpfr_fma               | wrapped                |
+------------------------+------------------------+
| mpfr_fms               | wrapped                |
+------------------------+------------------------+
| mpfr_fmma              | wrapped                |
+------------------------+------------------------+
| mpfr_fmms              | wrapped                |
+------------------------+------------------------+
| mpfr_agm               | wrapped                |
+------------------------+------------------------+
| mpfr_hypot             | wrapped                |
+------------------------+------------------------+
| mpfr_ai                | wrapped                |
+------------------------+------------------------+
| mpfr_const_log2        | wrapped                |
+------------------------+------------------------+
| mpfr_const_pi          | wrapped                |
+------------------------+------------------------+
| mpfr_const_euler       | wrapped                |
+------------------------+------------------------+
| mpfr_const_catalan     | wrapped                |
+------------------------+------------------------+
| mpfr_free_cache        | wrapped                |
+------------------------+------------------------+
| mpfr_free_cache2       | wrapped                |
+------------------------+------------------------+
| mpfr_free_pool         | wrapped                |
+------------------------+------------------------+
| mpfr_mp_memory_cleanup | wrapped                |
+------------------------+------------------------+
| mpfr_sum               | wrapped                |
+------------------------+------------------------+

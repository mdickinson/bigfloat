# Configuration file for the bigfloat module.

# Set 'mpfr_library_location' to a string giving the location of the
# MPFR library on your system.  This is particularly useful if you
# have multiple versions of MPFR installed and you'd like to specify
# which one should be used.  If this variable isn't set then the
# bigfloat module will make an attempt to find the library itself.
mpfr_library_location = '/opt/local/lib/libmpfr.dylib'

# Set 'gmp_mp_size_t_int' to True if GMP uses the C 'int' type for
# mp_size_t and mp_exp_t, and to False if is uses the C 'long' type
# (which it currently does on almost all platforms). The default is
# False.  This variable corresponds to the __GMP_MP_SIZE_T_INT in the
# GMP include file gmp.h.
# gmp_mp_size_t_int = False

# Set 'gmp_short_limb' to True if GMP uses the C 'short' type for mpn
# limbs, and False otherwise.  The default is False.  This variable
# corresponds to the __GMP_SHORT_LIMB macro in gmp.h.
# gmp_short_limb = False

# Set 'gmp_long_long_limb' to True if GMP uses the C 'long long' type
# for mpn limbs, and False otherwise.  The default is False.  This variable
# corresponds to the _LONG_LONG_LIMB macro in gmp.h.
# gmp_long_long_limb = False

# Set 'mpfr_short_enums' if, for the C compiler and options used to
# compile MPFR, an enum with only a few values uses type 'signed char'
# instead of type 'int'.  On most platforms, GCC uses type 'int' for
# enums unless the flag -fshort-enums is passed; however, on some
# platforms -fshort-enums is enabled by default.
# The default is False.
# mpfr_short_enums = False

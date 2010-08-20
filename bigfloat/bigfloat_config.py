# Copyright 2009, 2010 Mark Dickinson.
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


# Configuration file for the bigfloat module.

## Set 'mpfr_library_location' to a string giving the location of the
## MPFR library on your system.  This is particularly useful if you
## have multiple versions of MPFR installed and you'd like to specify
## which one should be used, or if your MPFR library is in an unusual
## location that's outside the usual library search paths.
##
## For example: to make bigfloat use the MacPorts version of mpfr on
## OS X you might use:
##
## mpfr_library_location = "/opt/local/lib/libmpfr.dylib"
##
#mpfr_library_location = None

## Set 'gmp_mp_size_t_int' to True if GMP uses the C 'int' type for
## mp_size_t and mp_exp_t, and to False if is uses the C 'long' type
## (which it currently does on almost all platforms). The default is
## False.  This variable corresponds to the __GMP_MP_SIZE_T_INT in the
## GMP include file gmp.h.
##
# gmp_mp_size_t_int = False

## Set 'gmp_short_limb' to True if GMP uses the C 'short' type for mpn
## limbs, and False otherwise.  The default is False.  This variable
## corresponds to the __GMP_SHORT_LIMB macro in gmp.h.
##
# gmp_short_limb = False

## Set 'gmp_long_long_limb' to True if GMP uses the C 'long long' type
## for mpn limbs, and False otherwise.  The default is False.  This variable
## corresponds to the _LONG_LONG_LIMB macro in gmp.h.
##
# gmp_long_long_limb = False

## Set 'mpfr_short_enums' to True if, for the C compiler and options
## used to compile MPFR, an enum with only a few values uses type
## 'signed char' instead of type 'int'.  On most platforms, GCC uses
## type 'int' for enums unless the flag -fshort-enums is passed;
## however, on some platforms -fshort-enums is enabled by default.  The
## default is False.
##
# mpfr_short_enums = False

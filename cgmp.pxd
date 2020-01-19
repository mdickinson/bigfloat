# Copyright 2009--2019 Mark Dickinson.
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

cdef extern from "gmp.h":
    # GMP type declarations
    ctypedef int mp_exp_t
    ctypedef unsigned int mp_limb_t

    ctypedef struct __mpz_struct:
        int _mp_alloc
        int _mp_size
        mp_limb_t *_mp_d

    # ctypedef __mpz_struct mpz_t[1]
    ctypedef __mpz_struct *mpz_ptr

    # Initialization Functions

    void mpz_init(mpz_ptr x)
    void mpz_clear(mpz_ptr x)

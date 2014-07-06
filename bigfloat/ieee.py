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

from bigfloat.core import log2
from bigfloat.context import Context, DefaultContext


def IEEEContext(bitwidth):
    """
    Return IEEE 754-2008 context for a given bit width.

    The IEEE 754 standard specifies binary interchange formats with bitwidths
    16, 32, 64, 128, and all multiples of 32 greater than 128.  This function
    returns the context corresponding to the interchange format for the given
    bitwidth.

    See section 3.6 of IEEE 754-2008 or the bigfloat source for more details.

    """
    try:
        precision = {16: 11, 32: 24, 64: 53, 128: 113}[bitwidth]
    except KeyError:
        if not (bitwidth >= 128 and bitwidth % 32 == 0):
            raise ValueError("nonstandard bitwidth: bitwidth should be "
                             "16, 32, 64, 128, or k*32 for some k >= 4")

        with DefaultContext + Context(emin=-1, subnormalize=True):
            # log2(bitwidth), rounded to the nearest quarter
            l = log2(bitwidth)
        precision = 13 + bitwidth - int(4 * l)

    emax = 1 << bitwidth - precision - 1
    return Context(
        precision=precision,
        emin=4 - emax - precision,
        emax=emax,
        subnormalize=True,
    )

half_precision = IEEEContext(16)
single_precision = IEEEContext(32)
double_precision = IEEEContext(64)
quadruple_precision = IEEEContext(128)

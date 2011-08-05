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

__all__ = [
    # main class
    'BigFloat',

    # contexts
    'Context',

    # limits on emin, emax and precision
    'EMIN_MIN', 'EMIN_MAX',
    'EMAX_MIN', 'EMAX_MAX',
    'PRECISION_MIN', 'PRECISION_MAX',

    # rounding mode constants
    'ROUND_TIES_TO_EVEN',
    'ROUND_TOWARD_ZERO',
    'ROUND_TOWARD_POSITIVE',
    'ROUND_TOWARD_NEGATIVE',
    'ROUND_AWAY_FROM_ZERO',

    # context constants...
    'DefaultContext', 'EmptyContext',
    'half_precision', 'single_precision',
    'double_precision', 'quadruple_precision',

    'RoundTiesToEven', 'RoundTowardZero',
    'RoundTowardPositive', 'RoundTowardNegative',
    'RoundAwayFromZero',

    # ... and functions
    'IEEEContext', 'precision', 'extra_precision', 'rounding',

    # get and set current context
    'getcontext', 'setcontext',

    # flags
    'Inexact', 'Overflow', 'Underflow', 'NanFlag',

    # functions to test, set and clear individual flags
    'test_flag', 'set_flag', 'clear_flag',

    # and to get and set the entire flag state
    'set_flagstate', 'get_flagstate',

    # numeric functions
    'next_up', 'next_down',
]

from bigfloat.core import (
    BigFloat,

    EMIN_MIN,
    EMIN_MAX,
    EMAX_MIN,
    EMAX_MAX,

    PRECISION_MIN,
    PRECISION_MAX,

    Inexact,
    Overflow,
    NanFlag,
    Underflow,
    set_flagstate,
    get_flagstate,
    _all_flags,

    test_flag,
    set_flag,
    clear_flag,

    # Predicates: 1-ary
    is_nan,
    is_zero,
    is_inf,
    is_negative,
    is_finite,
    is_regular,
    is_integer,

    # Predicates: 2-ary
    lessgreater,
    unordered,

    # Standard functions: 0-ary
    const_log2,
    const_catalan,
    const_pi,
    const_euler,

    # Standard functions: 1-ary
    abs,
    neg,
    pos,

    sqrt,
    log2,
    log,
    exp,

    # Standard functions: 2-ary
    add,
    mul,
    sub,
    div,
    pow,
    mod,

    # Miscellaneous functions
    next_down,
    next_up,
)

from bigfloat.mpfr import (
    # MPFR Version information
    MPFR_VERSION_MAJOR,
    MPFR_VERSION_MINOR,
)

from bigfloat.context import (
    Context,
    setcontext,
    getcontext,

    DefaultContext,
    EmptyContext,

    precision,
    rounding,
    extra_precision,

    RoundTiesToEven,
    RoundTowardZero,
    RoundTowardPositive,
    RoundTowardNegative,
    RoundAwayFromZero,
)

from bigfloat.ieee import (
    IEEEContext,
    half_precision,
    single_precision,
    double_precision,
    quadruple_precision,
)

from bigfloat.rounding_mode import (
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_AWAY_FROM_ZERO,
)

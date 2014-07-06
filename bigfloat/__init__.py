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
    'Inexact', 'Overflow', 'Underflow', 'NanFlag', 'ZeroDivision',

    # functions to test, set and clear individual flags
    'test_flag', 'set_flag', 'clear_flag',

    # and to get and set the entire flag state
    'set_flagstate', 'get_flagstate',

    # numeric functions
    'next_up', 'next_down',

    # 5.2 Assignment Functions
    'pos',

    # 5.5 Basic arithmetic functions
    'add', 'sub', 'mul', 'sqr', 'div', 'sqrt', 'rec_sqrt', 'cbrt', 'root',
    'pow', 'neg', 'abs', 'dim',

    # 5.6 Comparison functions
    'cmp', 'cmpabs', 'is_nan', 'is_inf', 'is_finite', 'is_zero', 'is_regular',
    'sgn', 'greater', 'greaterequal', 'less', 'lessequal', 'equal',
    'lessgreater', 'unordered',

    # 5.7 Special Functions
    'log', 'log2', 'log10', 'exp', 'exp2', 'exp10',
    'cos', 'sin', 'tan', 'sec', 'csc', 'cot', 'acos', 'asin', 'atan',
    'atan2',
    'cosh', 'sinh', 'tanh', 'sech', 'csch', 'coth', 'acosh', 'asinh', 'atanh',
    'factorial',
    'log1p', 'expm1',
    'eint', 'li2', 'gamma', 'lngamma', 'lgamma', 'digamma', 'zeta', 'zeta_ui',
    'erf', 'erfc',
    'j0', 'j1', 'jn', 'y0', 'y1', 'yn',
    'fma', 'fms', 'agm',
    'hypot',
    'ai',
    'const_log2', 'const_pi', 'const_euler', 'const_catalan',

    # 5.10 Integer and Remainder Related Functions
    'ceil', 'floor', 'round', 'trunc',
    'frac', 'mod', 'remainder', 'is_integer',

    # 5.12 Miscellaneous Functions
    'min', 'max',
    'is_negative',
    'copysign',

    'MPFR_VERSION',
    'MPFR_VERSION_MAJOR',
    'MPFR_VERSION_MINOR',
    'MPFR_VERSION_PATCHLEVEL',
    'MPFR_VERSION_STRING',
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
    ZeroDivision,
    NanFlag,
    Underflow,
    set_flagstate,
    get_flagstate,

    test_flag,
    set_flag,
    clear_flag,

    # Miscellaneous functions
    next_down,
    next_up,

    # 5.2 Assignment Functions
    pos,

    # 5.5 Basic Arithmetic Functions
    add, sub, mul, sqr, div, sqrt, rec_sqrt, cbrt, root, pow, neg, abs, dim,

    # 5.6 Comparison Functions
    cmp, cmpabs, is_nan, is_inf, is_finite, is_zero, is_regular, sgn,
    greater, greaterequal, less, lessequal, equal, lessgreater, unordered,

    # 5.7 Special Functions
    log, log2, log10, exp, exp2, exp10,
    cos, sin, tan, sec, csc, cot, acos, asin, atan,
    atan2,
    cosh, sinh, tanh, sech, csch, coth, acosh, asinh, atanh,
    factorial,
    log1p, expm1,
    eint, li2, gamma, lngamma, lgamma, digamma, zeta, zeta_ui,
    erf, erfc,
    j0, j1, jn, y0, y1, yn,
    fma, fms, agm,
    hypot,
    ai,
    const_log2, const_pi, const_euler, const_catalan,

    # 5.10 Integer and Remainder Related Functions
    ceil, floor, round, trunc,
    frac, mod, remainder, is_integer,

    # 5.12 Miscellaneous Functions
    min, max,
    is_negative,
    copysign,

)

from mpfr import (
    # MPFR Version information
    MPFR_VERSION,
    MPFR_VERSION_MAJOR,
    MPFR_VERSION_MINOR,
    MPFR_VERSION_PATCHLEVEL,
    MPFR_VERSION_STRING,
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

import contextlib as _contextlib

import bigfloat.mpfr as mpfr

from bigfloat.rounding_mode import (
    RoundingMode,
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_TOWARD_ZERO,
    ROUND_AWAY_FROM_ZERO,
)

EMAX_MAX = mpfr.MPFR_EMAX_DEFAULT
EMIN_MIN = mpfr.MPFR_EMIN_DEFAULT

PRECISION_MIN = mpfr.MPFR_PREC_MIN
PRECISION_MAX = mpfr.MPFR_PREC_MAX

EMAX_MIN = max(mpfr.MPFR_EMIN_DEFAULT, mpfr.mpfr_get_emax_min())
EMIN_MAX = min(mpfr.MPFR_EMAX_DEFAULT, mpfr.mpfr_get_emin_max())


_Context_attributes = [
    'precision',
    'emin',
    'emax',
    'subnormalize',
    'rounding',
]


class Context(object):
    # Contexts are supposed to be immutable.  We make the attributes
    # of a Context private, and provide properties to access them in
    # order to discourage users from trying to set the attributes
    # directly.

    def __new__(cls, precision=None, emin=None, emax=None, subnormalize=None,
                rounding=None):
        if precision is not None and \
                not (PRECISION_MIN <= precision <= PRECISION_MAX):
            raise ValueError("Precision p should satisfy %d <= p <= %d." %
                             (PRECISION_MIN, PRECISION_MAX))
        if emin is not None and not EMIN_MIN <= emin <= EMIN_MAX:
            raise ValueError("exponent bound emin should satisfy "
                             "%d <= emin <= %d" % (EMIN_MIN, EMIN_MAX))
        if emax is not None and not EMAX_MIN <= emax <= EMAX_MAX:
            raise ValueError("exponent bound emax should satisfy "
                             "%d <= emax <= %d" % (EMAX_MIN, EMAX_MAX))
        if rounding is not None:
            rounding = RoundingMode(rounding)
        if subnormalize is not None and not subnormalize in [False, True]:
            raise ValueError("subnormalize should be either False or True")
        self = object.__new__(cls)
        self._precision = precision
        self._emin = emin
        self._emax = emax
        self._subnormalize = subnormalize
        self._rounding = rounding
        return self

    def __add__(self, other):
        """For contexts self and other, self + other is a new Context
        combining self and other: for attributes that are defined in
        both self and other, the attribute from other takes
        precedence."""

        return Context(
            precision=(other.precision
                         if other.precision is not None
                         else self.precision),
            emin=other.emin if other.emin is not None else self.emin,
            emax=other.emax if other.emax is not None else self.emax,
            subnormalize=(other.subnormalize
                            if other.subnormalize is not None
                            else self.subnormalize),
            rounding=(other.rounding
                        if other.rounding is not None
                        else self.rounding),
            )

    def __eq__(self, other):
        return (
            self.precision == other.precision and
            self.emin == other.emin and
            self.emax == other.emax and
            self.subnormalize == other.subnormalize and
            self.rounding == other.rounding
            )

    def __hash__(self):
        return hash((self.precision, self.emin, self.emax,
                     self.subnormalize, self.rounding))

    @property
    def precision(self):
        return self._precision

    @property
    def rounding(self):
        return self._rounding

    @property
    def emin(self):
        return self._emin

    @property
    def emax(self):
        return self._emax

    @property
    def subnormalize(self):
        return self._subnormalize

    def __repr__(self):
        args = []
        if self.precision is not None:
            args.append('precision=%r' % self.precision)
        if self.emax is not None:
            args.append('emax=%r' % self.emax)
        if self.emin is not None:
            args.append('emin=%r' % self.emin)
        if self.subnormalize is not None:
            args.append('subnormalize=%r' % self.subnormalize)
        if self.rounding is not None:
            args.append('rounding=%r' % self.rounding)
        return 'Context(%s)' % ', '.join(args)

    __str__ = __repr__

    def __enter__(self):
        _pushcontext(self)

    def __exit__(self, *args):
        _popcontext()

# some useful contexts

# DefaultContext is the context that the module always starts with.
DefaultContext = Context(precision=53,
                         rounding=ROUND_TIES_TO_EVEN,
                         emax=EMAX_MAX,
                         emin=EMIN_MIN,
                         subnormalize=False)

# EmptyContext is useful for situations where a context is
# required, but no change to the current context is desirable
EmptyContext = Context()

# provided rounding modes are implemented as contexts, so that
# they can be used directly in with statements
RoundTiesToEven = Context(rounding=ROUND_TIES_TO_EVEN)
RoundTowardPositive = Context(rounding=ROUND_TOWARD_POSITIVE)
RoundTowardNegative = Context(rounding=ROUND_TOWARD_NEGATIVE)
RoundTowardZero = Context(rounding=ROUND_TOWARD_ZERO)
RoundAwayFromZero = Context(rounding=ROUND_AWAY_FROM_ZERO)

# thread local variables:
#   __bigfloat_context__: current context
#   __context_stack__: context stack, used by with statement

import threading

local = threading.local()
local.__bigfloat_context__ = DefaultContext
local.__context_stack__ = []


def getcontext(_local=local):
    return _local.__bigfloat_context__


def setcontext(context, _local=local):
    # attributes provided by 'context' override those in the current
    # context; if 'context' doesn't specify a particular attribute,
    # the attribute from the current context shows through
    oldcontext = getcontext()
    _local.__bigfloat_context__ = oldcontext + context


def _pushcontext(context, _local=local):
    _local.__context_stack__.append(getcontext())
    setcontext(context)


def _popcontext(_local=local):
    setcontext(_local.__context_stack__.pop())

del threading, local


def precision(prec):
    """Return context specifying the given precision.

    precision(prec) is exactly equivalent to Context(precision=prec).

    """
    return Context(precision=prec)


def extra_precision(prec):
    """Return new context equal to the current context, but with
    precision increased by prec."""
    c = getcontext()
    return Context(precision=c.precision + prec)


@_contextlib.contextmanager
def _temporary_exponent_bounds(emin, emax):
    old_emin = mpfr.mpfr_get_emin()
    mpfr.mpfr_set_emin(emin)
    try:
        old_emax = mpfr.mpfr_get_emax()
        mpfr.mpfr_set_emax(emax)
        try:
            yield
        finally:
            mpfr.mpfr_set_emax(old_emax)
    finally:
        mpfr.mpfr_set_emin(old_emin)


def _apply_function_in_context(f, args, context):
    """ Apply an MPFR function 'f' to the given arguments 'args', rounding to
    the given context.  Returns a new Mpfr object with precision taken from
    the current context.

    """
    rounding = context.rounding
    bf = mpfr.Mpfr(context.precision)
    args = (bf,) + args + (rounding,)
    ternary = f(*args)
    with _temporary_exponent_bounds(context.emin, context.emax):
        ternary = mpfr.mpfr_check_range(bf, ternary, rounding)
        if context.subnormalize:
            # mpfr_subnormalize doesn't set underflow and
            # subnormal flags, so we do that ourselves.  We choose
            # to set the underflow flag for *all* cases where the
            # 'after rounding' result is smaller than the smallest
            # normal number, even if that result is exact.

            # if bf is zero but ternary is nonzero, the underflow
            # flag will already have been set by mpfr_check_range;
            if (mpfr.mpfr_number_p(bf) and
                not mpfr.mpfr_zero_p(bf) and
                mpfr.mpfr_get_exp(bf) < context.precision - 1 + context.emin):
                mpfr.mpfr_set_underflow()
            ternary = mpfr.mpfr_subnormalize(bf, ternary, rounding)
            if ternary:
                mpfr.mpfr_set_inexflag()
    return bf

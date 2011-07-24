from mpfr import (
    MPFR_RNDN,
    MPFR_RNDZ,
    MPFR_RNDU,
    MPFR_RNDD,
    MPFR_RNDA,
)


__all__ = [
    'RoundingMode',
    'ROUND_TIES_TO_EVEN',
    'ROUND_TOWARD_ZERO',
    'ROUND_TOWARD_POSITIVE',
    'ROUND_TOWARD_NEGATIVE',
    'ROUND_AWAY_FROM_ZERO',
]


_rounding_mode_names = {
    MPFR_RNDN: 'ROUND_TIES_TO_EVEN',
    MPFR_RNDZ: 'ROUND_TOWARD_ZERO',
    MPFR_RNDU: 'ROUND_TOWARD_POSITIVE',
    MPFR_RNDD: 'ROUND_TOWARD_NEGATIVE',
    MPFR_RNDA: 'ROUND_AWAY_FROM_ZERO',
}


class RoundingMode(int):
    """ Subclass of int representing a rounding mode. """

    def __new__(cls, value):
        self = int.__new__(cls, value)
        if value not in _rounding_mode_names:
            raise ValueError("Invalid rounding mode {}".format(value))
        self._name = _rounding_mode_names[value]
        return self

    def __repr__(self):
        return self._name

    __str__ = __repr__


ROUND_TIES_TO_EVEN = RoundingMode(MPFR_RNDN)
ROUND_TOWARD_ZERO = RoundingMode(MPFR_RNDZ)
ROUND_TOWARD_POSITIVE = RoundingMode(MPFR_RNDU)
ROUND_TOWARD_NEGATIVE = RoundingMode(MPFR_RNDD)
ROUND_AWAY_FROM_ZERO = RoundingMode(MPFR_RNDA)

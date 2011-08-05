from bigfloat.core import log2
from bigfloat.context import Context, DefaultContext

# Contexts corresponding to IEEE 754-2008 binary interchange formats
# (see section 3.6 of the standard for details).

def IEEEContext(bitwidth):
    """ Return IEEE 754-2008 context for a given bit width.

    IEEE 754 specifies standard binary interchange formats with bitwidths
    16, 32, 64, 128, and all multiples of 32 greater than 128.  This function
    returns the context corresponding to the interchange format for the given
    bitwidth.

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

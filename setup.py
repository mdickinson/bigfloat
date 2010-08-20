# -*- coding: UTF-8
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install import install
from distutils.command.install_lib import install_lib
from distutils.cmd import Command
from distutils import log
import distutils.sysconfig
import distutils.ccompiler
import os.path
import sys
import platform

DESCRIPTION="""\
Arbitrary precision correctly-rounded floating point arithmetic, via MPFR.\
"""

LONG_DESCRIPTION="""\
The bigfloat package is a Python package providing arbitrary-precision
correctly-rounded binary floating-point arithmetic.  It is currently
implemented as a ctypes wrapper around the MPFR library (http://www.mpfr.org).

Features
--------

- correct rounding on all operations;  precisely defined semantics
  compatible with the IEEE 754-2008 standard.

- support for mixed-type operations with Python integers and floats

- support for emulating IEEE 754 arithmetic in any of the IEEE binary
  interchange formats described in IEEE 754-2008.  Infinities, NaNs,
  signed zeros, and subnormals are all supported.

- easy control of rounding modes and precisions, via Python's 'with'
  statement.

A quick tour
------------

The ``bigfloat`` module is small and simple to use.  Here's a quick
tour of some of its features.  See the `full tutorial and reference
documentation <http://packages.python.org/bigfloat/>`_ for more
details.

For demonstration purposes, start with::

    >>> from bigfloat import *

Note that this import clobbers some builtin Python functions, namely
``abs``, ``max``, ``min`` and ``pow``.  In normal usage you'll
probably only want to import the classes and functions that you
actually need.

The main class is the ``BigFloat`` class::

    >>> BigFloat(1)     # construction from an integer
    BigFloat.exact('1.0000000000000000', precision=53)
    >>> BigFloat(-1.23) # construction from a float
    BigFloat.exact('-1.2300000000000000', precision=53)
    >>> BigFloat('1.23456')
    BigFloat.exact('1.2345600000000001', precision=53)
    >>> BigFloat('1.23456') # and from a string
    BigFloat.exact('1.2345600000000001', precision=53)

Each new ``BigFloat`` instance is created in the current *context*.
The current context is represented by a ``Context`` instance.  Each
``Context`` instance determines, amongst other things, a precision
and a rounding mode used for the results of operations.  The current
context is given by the ``getcontext`` function::

    >>> getcontext()
    Context(precision=53, emax=1073741823, emin=-1073741823,
            subnormalize=False, rounding='RoundTiesToEven')

The context used for a calculation can be set using the ``setcontext``
function, but a better way to change the context (temporarily) is to
use Python's ``with`` statement::

    >>> with precision(1000):
    ...     print sqrt(2)
    ... 
    1.41421356237309504880168872420969807856967187537694807317667973
    7990732478462107038850387534327641572735013846230912297024924836
    0558507372126441214970999358314132226659275055927557999505011527
    8206057147010955997160597027453459686201472851741864088919860955
    232923048430871432145083976260362799525140798964

Here ``precision(1000)`` is a ``Context`` instance with a precision of
1000 bits, and ``sqrt`` is one of a number of mathematical functions
that bigfloat exports.  As you can see, these functions operate on
integers and floats as well as BigFloat instances.

Rounding modes can be controlled similarly.  Here are upper and lower
bounds for π, accurate to 53 significant bits.

    >>> with RoundTowardPositive:
    ...     const_pi()
    ... 
    BigFloat.exact('3.1415926535897936', precision=53)
    >>> with RoundTowardNegative:
    ...     const_pi()
    ... 
    BigFloat.exact('3.1415926535897931', precision=53)

And as you'd expect, ``with`` statements like those above can be
nested.  Contexts can also be combined using addition::

    >>> with RoundTowardPositive + precision(24):
    ...     BigFloat(1) / 3
    ... 
    BigFloat.exact('0.333333343', precision=24)

Various ``Context`` objects corresponding to IEEE 754 interchange
formats are predefined::

    >>> quadruple_precision
    Context(precision=113, emax=16384, emin=-16493, subnormalize=True)
    >>> half_precision
    Context(precision=11, emax=16, emin=-23, subnormalize=True)
    >>> with half_precision:
            log(2)
    ... 
    BigFloat.exact('0.69336', precision=11)


Links
-----

* `Package documentation <http://packages.python.org/bigfloat/>`_
* `Project homepage at bitbucket <http://bitbucket.org/dickinsm/bigfloat/>`_


"""

def main():

    setup(
        name='bigfloat',
        version='0.2',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Mark Dickinson',
        author_email='dickinsm@gmail.com',
        url='http://bitbucket.org/dickinsm/bigfloat',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: '
            'GNU Library or Lesser General Public License (LGPL)',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Mathematics',
            ],
        platforms = [
            'Linux',
            'OS X',
            ],
        license = 'GNU Library or Lesser General Public License (LGPL)',
        packages=[
            'bigfloat',
            'bigfloat.test',
            'bigfloat.examples',
            ],
        package_data={'bigfloat': [
                'docs/*.html',
                'docs/*.inv',
                'docs/*.js',
                'docs/_sources/*',
                'docs/_static/*',
                ]},
        )

if __name__ == "__main__":
    main()

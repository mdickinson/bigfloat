# -*- coding: UTF-8

# Copyright 2009--2011 Mark Dickinson.
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

from distutils.core import setup
from distutils.extension import Extension

DESCRIPTION = """\
Arbitrary precision correctly-rounded floating point arithmetic, via MPFR.\
"""

LONG_DESCRIPTION = """\
The ``bigfloat`` package is a Python package providing arbitrary-precision
correctly-rounded binary floating-point arithmetic.  It is currently
implemented as a Python extension module (generated using Cython) around the
MPFR library (http://www.mpfr.org).

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

    >>> BigFloat(1)  # can be constructed from an integer, float or string
    BigFloat.exact('1.0000000000000000', precision=53)
    >>> BigFloat('3.14159') ** 2 / 6.0  # can combine with ints and floats
    BigFloat.exact('1.6449312880166664', precision=53)
    >>> BigFloat('0.1', precision(200)) # high-precision value from string
    BigFloat.exact('0.1000000000000000000000000000000000000000000000000000
    0000000002', precision=200)


Newly-created ``BigFloat`` instances refer to the current *context* to
determine what precision and rounding modes to use.  This current
context is represented by a ``Context`` instance, and can be retrieved
by calling ``getcontext``::

    >>> getcontext()
    Context(precision=53, emax=1073741823, emin=-1073741823,
            subnormalize=False, rounding='RoundTiesToEven')

The ``precision(200)`` argument passed to the ``BigFloat`` constructor
above is also an example of a ``Context``::

    >>> precision(200)
    Context(precision=200)

The context used for a calculation can be set using the ``setcontext``
function, but a better way to make a temporary change to the context
is to use Python's ``with`` statement::

    >>> with precision(1000):
    ...     print sqrt(2)
    ...
    1.41421356237309504880168872420969807856967187537694807317667973
    7990732478462107038850387534327641572735013846230912297024924836
    0558507372126441214970999358314132226659275055927557999505011527
    8206057147010955997160597027453459686201472851741864088919860955
    232923048430871432145083976260362799525140798964

Here, ``sqrt`` is one of a number of mathematical functions that the
``bigfloat`` module exports.  As you can see, these functions operate on
integers and floats as well as ``BigFloat`` instances, but always
return a ``BigFloat`` instance.

Rounding modes can be controlled similarly.  Here are upper and lower
bounds for π, accurate to 53 significant bits::

    >>> with RoundTowardPositive:
    ...     const_pi()
    ...
    BigFloat.exact('3.1415926535897936', precision=53)
    >>> with RoundTowardNegative:
    ...     const_pi()
    ...
    BigFloat.exact('3.1415926535897931', precision=53)

And as you'd expect, ``with`` statements like those above can be
nested.  ``Context`` objects can also be combined using addition::

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

setup(
    # Name should really be capitalized as 'BigFloat'.  We keep 'bigfloat' to avoid
    # upload problems on PyPI.  (Previous versions of the package were also
    # called bigfloat.)
    name='bigfloat',
    version='0.3.0a2',
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
    platforms=[
        'Linux',
        'OS X',
    ],
    license='GNU Library or Lesser General Public License (LGPL)',
    ext_modules=[
        Extension(
            "bigfloat.mpfr",
            ["src/mpfr.c"],
            libraries=[
                'mpfr', 'gmp',
            ],
        ),
    ],
    packages=[
        'bigfloat',
        'bigfloat.test',
    ],
    package_data={
        'bigfloat': [
            'docs/html/*.html',
            'docs/html/*.inv',
            'docs/html/*.js',
            'docs/html/_sources/*',
            'docs/html/_static/*',
            'docs/pdf/*.pdf',
        ],
    },
)

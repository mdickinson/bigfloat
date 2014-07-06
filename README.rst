.. image:: https://travis-ci.org/mdickinson/bigfloat.svg?branch=master
   :alt: Status of most recent Travis CI run
   :target: https://travis-ci.org/mdickinson/bigfloat


The bigfloat package
====================

The ``bigfloat`` package is a Python package providing arbitrary-precision
correctly-rounded binary floating-point arithmetic.  It is implemented as a
`Cython <http://cython.org>`_ wrapper around the `GNU MPFR library
<http://www.mpfr.org>`_.  A couple of lines of Python code should give the
idea::

    >>> from bigfloat import *
    >>> with precision(200) + RoundTowardZero:
    ...     print(sqrt(2))
    ...
    1.4142135623730950488016887242096980785696718753769480731766796
    >>> with quadruple_precision:
    ...     const_pi()
    ...
    BigFloat.exact('3.14159265358979323846264338327950280', precision=113)

Features
--------

- Supports Python 2 (version 2.6 or later) and Python 3 (version 3.2 or later).

- Exactly reproducible correctly-rounded results across platforms;
  precisely-defined semantics compatible with the IEEE 754-2008 standard.

- Support for mixed-type operations with Python integers and floats.

- Support for emulating IEEE 754 arithmetic in any of the IEEE binary
  interchange formats described in IEEE 754-2008.  Infinities, NaNs,
  signed zeros, and subnormals are all supported.

- Easy control of rounding modes and precisions via ``Context`` objects
  and Python's ``with`` statement.

Documentation
-------------

Full `package documentation <http://bigfloat.readthedocs.org>`_ is hosted at
Read the Docs.  Read on for a quick tour.

A quick tour
------------

The ``bigfloat`` package is small and simple to use.  Here's a quick
tour of some of its features.

For demonstration purposes, start with::

    >>> from bigfloat import *

Note that this import shadows four builtin Python functions, namely
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
            subnormalize=False, rounding=ROUND_TIES_TO_EVEN)

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
``bigfloat`` package exports.  As you can see, these functions operate on
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

Installation
------------

The ``bigfloat`` package is `available on the Python package index
<https://pypi.python.org/pypi/bigfloat>`_, and can be installed in the usual
way using ``easy_install`` or ``pip``.  Alternatively, the development sources
may be downloaded from the project's `homepage
<https:/github.com/mdickinson/bigfloat>`_ on GitHub.

For more comprehensive installation instructions, please see the `full
documentation <http://bigfloat.readthedocs.org/en/latest/#installation>`_.

Feedback
--------

Feedback is welcome!  Please use the `GitHub issue tracker
<https://github.com/mdickinson/bigfloat/issues>`_ to report issues.
Alternatively, you can contact Mark Dickinson directly at dickinsm@gmail.com
with suggestions, complaints, bug reports, etc.

License
-------

The bigfloat package is copyright (C) 2009–2014 Mark Dickinson

The bigfloat package is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

The bigfloat package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
for more details.

You should have received a copy of the GNU Lesser General Public License
along with the bigfloat package.  If not, see <http://www.gnu.org/licenses/>.

Links
-----
- `Documentation at Read the Docs <http://bigfloat.readthedocs.org>`_
- `Python package index <https://pypi.python.org/pypi/bigfloat>`_
- `Project homepage at GitHub <https://github.com/mdickinson/bigfloat>`_
- `Issue tracker <https://github.com/mdickinson/bigfloat/issues>`_

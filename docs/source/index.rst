The bigfloat package --- high precision floating-point arithmetic
=================================================================

Release v\ |release|.

.. module:: bigfloat
   :synopsis: Python wrapper for MPFR floating-point library.

.. moduleauthor:: Mark Dickinson <dickinsm@gmail.com>

The :mod:`bigfloat` package is a Python wrapper for the `GNU MPFR library
<http://www.mpfr.org>`_ for arbitrary-precision floating-point reliable
arithmetic.  The MPFR library is a well-known portable C library for
arbitrary-precision arithmetic on floating-point numbers.  It provides precise
control over precisions and rounding modes and gives correctly-rounded
reproducible platform-independent results.

The :mod:`bigfloat` package aims to provide a convenient and friendly
Python interface to the operations and functions provided by the MPFR
library.  The main class, :class:`BigFloat`, gives an immutable
multiple-precision floating-point type that can be freely mixed with
Python integers and floats.  The :class:`Context` class, when used in
conjunction with Python's ``with`` statement, gives a simple way of
controlling precisions and rounding modes.  Additional module-level
functions provide various standard mathematical operations.  There is
full support for IEEE 754 signed zeros, nans, infinities and
subnormals.


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


Introduction
------------

Here's a quick tour::

   >>> from bigfloat import *
   >>> sqrt(2, precision(100))  # compute sqrt(2) with 100 bits of precision
   BigFloat.exact('1.4142135623730950488016887242092', precision=100)
   >>> with precision(100):     # another way to get the same result
   ...     sqrt(2)
   ... 
   BigFloat.exact('1.4142135623730950488016887242092', precision=100)
   >>> my_context = precision(100) + RoundTowardPositive
   >>> my_context
   Context(precision=100, rounding='RoundTowardPositive')
   >>> sqrt(2, my_context)      # and another, this time rounding up
   BigFloat.exact('1.4142135623730950488016887242108', precision=100)
   >>> with RoundTowardNegative: # a lower bound for zeta(2)
   ...     sum(1/sqr(n) for n in range(1, 10000))
   ... 
   BigFloat.exact('1.6448340618469506', precision=53)
   >>> zeta(2) # actual value, for comparison
   BigFloat.exact('1.6449340668482264', precision=53)
   >>> const_pi()**2/6.0  # double check value
   BigFloat.exact('1.6449340668482264', precision=53)
   >>> quadruple_precision  # context implementing IEEE 754 binary128 format
   Context(precision=113, emax=16384, emin=-16493, subnormalize=True)
   >>> next_up(0, quadruple_precision)  # smallest subnormal for binary128
   BigFloat.exact('6.47517511943802511092443895822764655e-4966', precision=113)
   >>> log2(_)
   BigFloat.exact('-16494.000000000000', precision=53)


Installation
------------

Where to get it
^^^^^^^^^^^^^^^

The latest released version of the :mod:`bigfloat` package can be
downloaded from its place at the `Python Package Index
<http://pypi.python.org/pypi/bigfloat/>`_.  Development sources can be
checked out from the project's `GitHub page
<http://github.com/mdickinson/bigfloat>`_.

Prerequisites
^^^^^^^^^^^^^

In order to use the :mod:`bigfloat` package you will need to have both the GMP
and MPFR libraries already installed on your system, along with the include
files for those libraries.  See the `MPFR homepage <http://www.mpfr.org>`_ and
the `GMP homepage <http://gmplib.org>`_ for more information about these
libraries.  Currently, MPFR version 2.3.0 or later is required.

The :mod:`bigfloat` package works with Python 2 (version 2.6 or later) or
Python 3 (version 3.2 or later), using a single codebase for both Python
dialects.

Installation
^^^^^^^^^^^^

Like most third party Python libraries, the :mod:`bigfloat` package is
installed by means of the ``setup.py`` script included in the
distribution.  On many systems, installation should be as simple as
doing::

   python setup.py install

in the top-level directory of the unpacked distribution.  You may need
superuser privileges to install the library, for example with::

   sudo python setup.py install

The MPFR and GMP libraries will need to be installed on your system prior to
installation of :mod:`bigfloat`, along with any necessary development header
files.  On Linux, look for a package called something like ``libmpfr-dev`` or
``mpfr-devel``, along with correspondingly named packages for GMP.  If the
libraries and/or include files are installed in an unusual place, it may be
necessary to specify their location using environment variables on the command
line.  As an example, on my OS X 10.9 system, with MPFR and GMP installed in
/opt/local/, I need to do::

    LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py install

Similarly, if installing from the Python package index using ``easy_install``
or ``pip``, you may also need to add the necessary environment variables first.


Detailed Documentation
======================

.. toctree::
   :maxdepth: 2

   tutorial/index
   reference/index


Indices and tables
==================

* :ref:`genindex`


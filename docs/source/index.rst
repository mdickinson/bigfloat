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

- Supports Python 2 (version 2.7) and Python 3 (version 3.5 or later).

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

The latest released version of the :mod:`bigfloat` package can be obtained from
the `Python Package Index <http://pypi.python.org/pypi/bigfloat/>`_.
Development sources can be checked out from the project's `GitHub page
<http://github.com/mdickinson/bigfloat>`_.


Prerequisites
^^^^^^^^^^^^^

The :mod:`bigfloat` package works with Python 2 (version 2.7) or
Python 3 (version 3.5 or later).  It uses a single codebase for both Python
dialects, so the same source works on both dialects of Python.

Whether installing ``bigfloat`` from source or from the Python Package Index,
you will need to have both the GMP and MPFR libraries already installed on your
system, along with the include files for those libraries.  See the `MPFR
homepage <http://www.mpfr.org>`_ and the `GMP homepage <http://gmplib.org>`_
for more information about these libraries.  Currently, MPFR version 3.0.0 or
later is required.

On Ubuntu, prerequisites can be installed with::

   sudo apt-get install libmpfr-dev

On Fedora Linux, use (for example)::

   su -c "yum install mpfr-devel"

On other flavours of Linux, some variant of one of the above should work.


Installation from the Python Package Index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have the prerequisites described above installed, the recommended
method for installation is to use `pip`_::

   pip install bigfloat

If you prefer, you can use the ``easy_install`` command from `setuptools`_::

   easy-install bigfloat

Depending on your system, you may need superuser privileges for the install.
For example::

   sudo pip install bigfloat

If the MPFR and GMP libraries are installed in an unusual location, you may
need to set appropriate environment variables when installing.  For example, on
an OS X 10.9 system with MPFR and GMP installed in /opt/local, I need to do::

   sudo LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include pip install bigfloat

Platform-specific installation instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On a newly-installed version of Ubuntu 14.04LTS (trusty), the commands below
are enough to install bigfloat for Python 3, from scratch.  You may not need
the first line if you already have ``pip`` and the Python development headers
installed.

::

   sudo apt-get install python3-dev python3-pip
   sudo apt-get install libmpfr-dev
   sudo pip3 install bigfloat

For Python 2, the procedure is similar::

   sudo apt-get install python-dev python-pip
   sudo apt-get install libmpfr-dev
   sudo pip install bigfloat

On Fedora 20, the following sequence of commands worked for me (for Python 3;
again, remove all occurrences of ``3`` to get the commands for Python 2)::

   su -c "yum install gcc python3-devel python3-pip"
   su -c "yum install mpfr-devel"
   su -c "pip-python3 install bigfloat"


Installation from source
^^^^^^^^^^^^^^^^^^^^^^^^

Installation from source (for example, from a GitHub checkout, or from an
unpacked source distribution), is similar to installation from the Python
Package Index: the only difference is that you should use the ``setup.py ``
script instead of using ``pip`` or ``easy_install``.  On many systems,
installation should be as simple as typing::

   python setup.py install

in the top-level directory of the unpacked distribution.  As above, you may
need superuser privileges to install the library, for example with::

   sudo python setup.py install

Again as above, if the libraries and include files are installed in an
unusual place, it may be necessary to specify their location using environment
variables on the command line.  For example::

   LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py install


Detailed Documentation
======================

.. toctree::
   :maxdepth: 2

   tutorial/index
   reference/index


Indices and tables
==================

* :ref:`genindex`

.. _pip: https://pypi.python.org/pypi/pip
.. _setuptools: https://pypi.python.org/pypi/setuptools

Reference
=========

.. module:: bigfloat
.. moduleauthor:: Mark Dickinson <dickinsm@gmail.com>

The :mod:`bigfloat` module is a Python wrapper for the MPFR library
for multiple-precision floating-point reliable arithmetic.

Introduction
------------

MPFR is a portable library written in C for arbitrary-precision
arithmetic on floating-point numbers. It provides precise control over
precisions and rounding modes and gives correctly-rounded
platform-independent results.

The :mod:`bigfloat` module provides a convenient and friendly Python
interface to the operations and functions provided by MPFR.  The main
class, :class:`BigFloat`, gives a multiple-precision floating-point
type that can be freely mixed with Python integers and floats.  The
:class:`Context` class, used in conjunction with Python's ``with``
statement, gives a simple way of controlling precisions and rounding
modes.  Additional module-level functions provide various standard
mathematical operations.

A quick tour
------------

Here's a quick tour to show off some of the features of the
:mod:`bigfloat` module, and give some idea of how it can be used.
Start off with::

   >>> from bigfloat import *

Note that this import brings a fairly large number of functions into
the current namespace, and clobbers some builtin Python functions:
``abs``, ``max``, ``min`` and ``pow``.  In normal usage you'll
probably only want to import the classes and functions that you
actually need.

The most important type is the :class:`BigFloat` class; a
:class:`BigFloat` instance can be created from an integer, a float or
a string::

   >>> BigFloat(123)
   BigFloat.exact('123.00000000000000', precision=53)
   >>> BigFloat(4.56)
   BigFloat.exact('4.5599999999999996', precision=53)
   >>> BigFloat('1e1000')
   BigFloat.exact('1.0000000000000001e+1000', precision=53)

As you see above, each BigFloat instance has a value and a precision,
with the latter giving the number of bits used to store the
significand of the BigFloat.  By default, newly-created BigFloats have
a precision of 53 bits; we'll see how to change this below.  The
slightly strange form of the output above is chosen to ensure that for
a BigFloat x, eval(repr(x)) recovers x exactly.  If you just want to
see the digits, use ``print`` instead::

   >>> print BigFloat('1e1000')
   1.0000000000000001e+1000

All the usual arithmetic operations apply to BigFloats, and BigFloat
instances can be freely mixed with integers and floats in those
operations::

   >>> BigFloat(1234)/3
   BigFloat.exact('411.33333333333331', precision=53)
   >>> BigFloat('1e1233')**0.5
   BigFloat.exact('3.1622776601683794e+616', precision=53)

(Exception: floor division and the divmod function are not yet
implemented for BigFloats.)  Comparisons between BigFloats and
integers or floats also behave as you'd expect them to.  The
:mod:`bigfloat` module provides a number of standard mathematical
functions.  For example::

   >>> sqrt(1729)
   BigFloat.exact('41.581245772583578', precision=53)
   >>> atanh(0.5)
   BigFloat.exact('0.54930614433405489', precision=53)
   >>> const_pi()
   BigFloat.exact('3.1415926535897931', precision=53)
   >>> const_catalan() # catalan's constant
   BigFloat.exact('0.91596559417721901', precision=53)
   >>> 4*exp(-const_pi()/2/agm(1, 1e-100))
   BigFloat.exact('9.9999999999998517e-101', precision=53)

Note that the arguments to all of these functions can be integers,
floats, or BigFloats.  The results are always BigFloats.

So far, a BigFloat instance looks and behaves very much like a Python
float, except that the exponent range for BigFloats is much larger
than that of floats.  But the MPFR library provides
arbitrary-precision arithmetic: how do we get at this from Python?
Python's with statement provides a good mechanism for making temporary
changes to the precision::

   >>> with precision(200):
   ...     x = 1/BigFloat(98)
   ... 
   >>> x
   BigFloat.exact('0.010204081632653061224489795918367346938775510204081632653061220', precision=200)

Here we get a result with 200 bits of precision, or around 60 decimal
digits.  Note that BigFloat instances are immutable: a change to the
precision does not affect existing BigFloat instances; it only affects
the choice of precision for newly-created BigFloats.

A more permanent change can be effected by using the setcontext
function.  After::

   >>> setcontext(precision(113))

any operation or function call on BigFloats will return a result with
precision 113.

Rounding modes can be controlled in a similar fashion.  There are four
rounding modes: ``RoundTiesToEven``, ``RoundTowardPositive``,
``RoundTowardNegative`` and ``RoundTowardZero``.  Here's an example
that uses the ``RoundTowardPositive`` and ``RoundTowardNegative``
rounding modes to compute upper and lower bounds for log10(2)::

   >>> with rounding(RoundTowardPositive):
   ...     upper_bound = log10(2)
   ...     exp_upper_bound = 10**upper_bound
   ... 
   >>> with rounding(RoundTowardNegative):
   ...     lower_bound = log10(2)
   ...     exp_lower_bound = 10**lower_bound
   ... 
   >>> exp_lower_bound  # should be strictly less than 2
   BigFloat.exact('1.99999999999999999999999999999999981', precision=113)
   >>> exp_lower_bound < 2 < exp_upper_bound
   True

Since it's common to want to change the rounding mode just for a
single operation, each of the mathematical functions that the
:mod:`bigfloat` module provides also accepts an optional ``rounding``
keyword argument.  So we could have performed the above calculations
more directly as follows::

   >>> upper_bound = log10(2, rounding=RoundTowardPositive)
   >>> exp_upper_bound = pow(10, upper_bound, rounding=RoundTowardPositive)
   >>> lower_bound = log10(2, rounding=RoundTowardNegative)
   >>> exp_lower_bound = pow(10, lower_bound, rounding=RoundTowardNegative)
   >>> exp_lower_bound < 2 < exp_upper_bound
   True

Note the use of the ``pow`` function above in place of the ``**``
operator.  For each Python arithmetic operator the :mod:`bigfloat`
module provides a corresponding function: ``pow`` for ``**``, ``add``
for ``+``, ``neg`` for unary minus, and so on.  (Here, ``pow`` is one
of the :mod:`bigfloat` functions that we imported at the start of the
session; it's not the usual builtin ``pow`` function.)


Installation
------------

Prerequisites
^^^^^^^^^^^^^

In order to use the :mod:`bigfloat` module you will need to have both
the GMP and MPFR libraries already installed on your system.  See the
`MPFR homepage <http://www.mpfr.org>`_ and the `GMP homepage
<http://gmplib.org>`_ for more information about these libraries.
Currently, MPFR version 2.4.0 or higher is required.

This module requires Python version 2.5 or higher.  For use with
Python 2.5, you'll need to do a ``from __future__ import
with_statement`` if you want to take advantage of all of the features
of this module.

Locating the MPFR library
^^^^^^^^^^^^^^^^^^^^^^^^^

The :mod:`bigfloat` module attempts to locate the MPFR library on your
system.  If it fails, or if you have multiple MPFR libraries installed
on your system and want to specify which one to use, you should edit
the 'mpfr_library_location' line in the 'bigfloat_config.py' file to
specify the library location.

Other configuration
^^^^^^^^^^^^^^^^^^^

The 'bigfloat_config.py' file also allows you to specify some other
system-dependent values.  On a typical system, with default installs
of GMP and MPFR, it's unlikely that these values will need to be
changed.  But if you're getting segmentation faults or crashes with
the bigfloat library then you may need to edit the values in this
file.  In this case it will probably also be useful to have the gmp.h
and mpfr.h include files handy;  on Linux systems, these files may
be in a different package from the library files (e.g., 'mpfr-devel'
instead of 'mpfr').


The BigFloat class
------------------

The :class:`BigFloat` class implements multiple-precision binary
floating-point numbers.  Each :class:`BigFloat` instance has both a
value and a precision; the precision is an integer giving the number
of significant bits used to store the value.  A finite nonzero
:class:`BigFloat` instance with precision p can be thought of as a
(sign, significand, exponent) triple (s, m, e), representing the value
(-1)**s * m * 2**e, where m is a value in the range [0.5, 1.0) stored
with p bits of precision.  (Thus m is of the form n/2**p for some
integer n with 2**(p-1) <= n < 2**p.)

In addition to nonzero finite numbers, :class:`BigFloat` instances can
also represent positive and negative infinities, positive and negative
zeros, and NaNs.

:class:`BigFloat` instances should be considered immutable.

.. class:: BigFloat(value)

   Construct a new :class:`BigFloat` instance from an integer, string,
   float or another :class:`BigFloat` instance, using the rounding-mode
   and precision given by the current context.

   *value* can be an integer, string, float, or another
   :class:`BigFloat` instance.  In all cases the given value is
   rounded to the format (precision, exponent limits and
   subnormalization) given by the current context, using the rounding
   mode specified by the current context.  The integer 0 is always
   converted to positive zero.

   .. method:: exact(cls, value, precision=None)

      A class method to construct a new :class:`BigFloat` instance
      from an integer, string, float or another :class:`BigFloat`
      instance, doing an exact conversion where possible.  Unlike the
      usual :class:`BigFloat` constructor, this alternative
      constructor makes no use of the current context and will not
      affect the current flags.

      If value is an integer, float or :class:`BigFloat`, then the precision
      keyword must not be given, and the conversion is exact.  The
      resulting :class:`BigFloat` has a precision sufficiently large to hold the
      converted value exactly.  If value is a string, then the
      precision argument must be given.  The string is converted using
      the given precision and the RoundTiesToEven rounding mode.

   .. method:: as_integer_ratio(self)

      Return a pair (n, d) of integers such that n and d are
      relatively prime, d is positive, and the value of self is
      exactly n/d.

      If self is an infinity or nan then ValueError is raised.  Both
      negative and positive zeros are converted to (0, 1).




Context objects
---------------

A :class:`Context` object is a simple immutable object that packages together
attributes describing a floating-point format, together with a rounding mode.

.. class:: Context(precision, rounding, emax, emin, subnormalize)

   Create a new Context object with the given attributes.  The
   arguments correspond to the attributes of the :class:`Context`
   object, described below.  :class:`Context` instances should be
   treated as immutable, and all attributes are read-only.

   .. attribute:: precision

      Precision of the floating-point format, given in bits.

   .. attribute:: emax

      Maximum exponent allowed for this format.  The largest
      representable finite number representable in the context self is
      (1-2**-self.precision) * 2**self.emax.

   .. attribute:: emin

      Minimum exponent allowed for this format.  The smallest representable
      positive number in the format is 0.5 * 2**emin.

   .. attribute:: subnormalize

      A boolean value, True if the format has gradual underflow, and
      False otherwise.  With gradual underflow, all finite floating-point
      numbers have a value that's an integer multiple of 2**(emin-1).

   .. attribute:: rounding

      The rounding mode of this Context.

   :class:`Context` instances are callable, accepting a set of keyword
   arguments that are used to update the attributes of the Context.
   This gives a convenient way to obtain a modification of an existing
   context::

      >>> double_precision
      Context(precision=53, rounding=RoundTiesToEven, emax=1024, emin=-1073, subnormalize=True)
      >>> double_precision(precision=64)
      Context(precision=64, rounding=RoundTiesToEven, emax=1024, emin=-1073, subnormalize=True)



The bigfloat module defines a number of predefined :class:`Context`
instances.

.. data:: DefaultContext

   The context that's in use when the bigfloat module is first
   imported.  It has precision of 53, large exponent bounds, no
   subnormalization, and the RoundTiesToEven rounding mode.

.. data:: half_precision
.. data:: single_precision
.. data:: double_precision
.. data:: quadruple_precision

   These :class:`Context` instances correspond to the binary16,
   binary32, binary64 and binary128 interchange formats described in
   IEEE 754-2008 (section 3.6).

.. function:: IEEEContext(bitwidth)

   If bitwidth is one of 16, 32, 64, or a multiple of 32 that's not
   less than 128, return the IEEE binary interchange format with the
   given bit width.  See section 3.6 of IEEE 754-2008 for details.


Creating new contexts
---------------------



The current context
-------------------

There can be many Context objects in existence at one time, but
there's only ever one *current context*.  The current context is given
by a thread-local :class:`Context` instance.  Whenever any arithmetic
operation or function computation is performed, the current context is
consulted to determine:

* The format that the result of the operation or function should take, and

* The rounding mode to use when computing the result, except when this
  rounding mode has been directly overridden by giving the 'rounding'
  keyword argument to a function call.

There are two ways to change the current context.  The direct way to
get and set the current context is to use the :func:`getcontext` and
:func:`setcontext` functions.

.. function:: getcontext()

   Return a copy of the current context.

.. function:: setcontext(context)

   Set the current context to the given context.

A neater way to make a temporary change to the current context is to
use a with statement.  Every :class:`Context` instance can be used
directly in a with statement, and changes the current context for the
duration of the block following the with statement, restoring the
previous context when the block is exited.  For example::

   >>> with single_precision:
   ...     sqrt(2)
   ... 
   BigFloat.exact('1.41421354', precision=24)
   >>> with quadruple_precision:
   ...     sqrt(2)
   ... 
   BigFloat.exact('1.41421356237309504880168872420969798', precision=113)

Here, single_precision and quadruple_precision are predefined
:class:`Context` instances that describe the IEEE 754 binary32 and
binary128 floating-point formats.

A number of convenience functions are provided for changing only
one aspect of the current context.

.. function:: precision(p)

   Return a copy of the current context with the precision changed to p.
   Example usage::

      >>> with precision(100):
      ...     sqrt(2)
      ... 
      BigFloat.exact('1.4142135623730950488016887242092', precision=100)

      >>> with precision(20):
      ...     const_pi()
      ... 
      BigFloat.exact('3.1415939', precision=20)

.. function:: rounding(rnd)

   Return a copy of the current context with the rounding mode changed
   to rnd.  Example usage::

      >>> with rounding(RoundTowardNegative):
      ...     lower_bound = log2(10)
      ... 
      >>> with rounding(RoundTowardPositive):
      ...     upper_bound = log2(10)
      ... 
      >>> lower_bound
      BigFloat.exact('3.3219280948873622', precision=53)
      >>> upper_bound
      BigFloat.exact('3.3219280948873626', precision=53)

.. function:: extra_precision(p)

   Return a copy of the current context with the precision increased
   by p.

      >>> getcontext().precision
      53
      >>> extra_precision(10).precision
      63
      >>> with extra_precision(20):
      ...     gamma(1.5)
      ... 
      BigFloat.exact('0.88622692545275801364912', precision=73)

.. function:: exponent_limits(emin=None, emax=None, subnormalize=False)

   Return a copy of the current context with given exponent
   limits. emin and emax default to the smallest and largest possible
   values, respectively.  When called with no arguments, this function
   can be convenient for temporarily relaxing exponents to avoid
   underflow or overflow during intermediate calculations::

      >>> with double_precision:
      ...     log(pow(2, 1234))   # intermediate power overflows
      ... 
      BigFloat.exact('Infinity', precision=53)
      >>> with double_precision:
      ...     with exponent_limits():
      ...         log(pow(2, 1234))
      ... 
      BigFloat.exact('855.34362081097254', precision=53)




   
Arithmetic on BigFloats
-----------------------

All the usual unary and binary arithmetic operations can be applied to
BigFloats.  The result of any operation is rounded to the current
context, using the rounding mode from the current context.  The value
of the result is as if the operation had been performed to
infinite-precision, and then correctly rounded using the current
rounding mode.

Mixed-type operations are permitted between a :class:`BigFloat` and an integer,
or a :class:`BigFloat` and a float.  For these operations, the integer or float
is first implicitly converted to a :class:`BigFloat`.  The implicit conversion
is performed exactly, without reference to the current context, so
that an arithmetic operation between (for example) an integer and a
:class:`BigFloat` will only involve a single round, at the end of the
operation.

Here are some notes on particular arithmetic operations.

* The unary + and - operations round to the current context, just like
  the binary operations.  So +x is not a no-op.  This can be useful
  for rounding the result of an extended computation with extra
  precision or relaxed exponent bounds back to the current context.

* Similarly, the builtin abs function rounds to the current context,
  using the context rounding mode.

* The remainder x % y has the sign of x, not the sign of y.  In this
  it differs from Python floats and integers.

* The floor division operator x // y and the builtin divmod function
  are not currently implemented for :class:`BigFloat` instances.

For each arithmetic operation there's a corresponding module-level
function.  This function also accepts a keyword argument 'rounding',
which can be used to override the rounding mode of the current
context.  For example::

   >>> div(2, 3, rounding=RoundTowardPositive)
   BigFloat.exact('0.66666666666666674', precision=53)
   >>> div(2, 3, rounding=RoundTowardNegative)
   BigFloat.exact('0.66666666666666663', precision=53)

This can be handy for places where you only want to alter the rounding
mode for a single function call or operation.

These module-level functions are also useful when you don't
necessarily know whether the input arguments are integers, floats or
BigFloats and you want to ensure that the result is a :class:`BigFloat`, or
that there's no loss of precision during argument conversion.  Consider
the following::

   >>> x = 10.**16  # exactly representable as a Python float
   >>> y = 10**16-1 # Python integer
   >>> x - y
   0.0
   >>> BigFloat(x) - BigFloat(y)
   BigFloat.exact('0', precision=53)
   >>> sub(x, y)
   BigFloat.exact('1.0000000000000000', precision=53)

In the first subtraction, y is implicity converted from an integer to
a Python float before the operation;  this conversion loses precision,
so the result of the subtraction is inaccurate.

The second subtraction is similar: both x and y are explicitly
converted to :class:`BigFloat` instances, and while x can be converted exactly,
y cannot at the current context precision.  So again the conversion
loses precision and the result of the subtraction is innaccurate.

In the third case both arguments x and y are converted with no loss of
precision, and the subtraction gives the correct result.

The module-level functions are :func:`add`, :func:`sub', :func:`mul`,
:func:`div`, :func:`pow` and :func:`mod`.  Note that :func:`pow`
shadows the builtin :func:`pow` function, and that :func:`div`
corresponds to true division.

Comparisons
-----------

The comparison operators should work as expected.  Note that any
comparison involving a NaN always returns False, with the exception of
the != comparison, which always returns True.  As with the arithmetic
operations, comparisons between :class:`BigFloat`s and integers or :class:`BigFloat`s
and floats also work as expected, performing an implicit exact
conversion of the integer or float to a :class:`BigFloat` before comparing.

There are two additional comparison functions that don't correspond to
any of the Python comparison operators.

.. function:: lessgreater(x, y)

   Return True if either x < y or x > y, and False otherwise.
   lessgreater(x, y) differs from x != y in the case where either x or
   y is a NaN: in that case, lessgreater(x, y) will return False,
   while x != y will return True.

.. function:: unordered(x, y)

   Return True if either x or y is a NaN, and False otherwise.

Conversions
-----------

Conversion of a :class:`BigFloat` to an integer using the :func:`int` builtin
function always truncates (rounds towards zero), regardless of the
current context rounding mode.

Conversion of a :class:`BigFloat` to a float using the :func:`float` builtin
function always rounds to the nearest floating-point number,
regardless of the current context rounding mode.

Number classification functions
-------------------------------

The following functions all accept a single :class:`BigFloat` instance (or a
float, or an integer) and return a boolean value.  They make no
use of the current context, and do not affect the state of the flags.

.. function:: is_nan(x)

   Return True if x is a NaN and False otherwise.

.. function:: is_inf(x)

   Return True if x is an infinity (either positive or negative), and False
   otherwise.

.. function:: is_zero(x)

   Return True if x is a zero (either positive zero or negative zero),
   and False otherwise.

.. function:: is_finite(x)

   Return True if x is not an infinity or NaN, and False otherwise.

.. function:: is_negative(x)

   Return True if the sign bit of x is set, and False otherwise.  Note that
   this function is misnamed:  is_negative(-0.0) returns True, even though
   -0.0 is not, strictly speaking, negative.

.. function:: is_integer(x)

   Return True if x is an exact integer and False otherwise.




.. class:: BigFloat(value)

   Construct a new :class:`BigFloat` instance from an integer, string,
   float or another :class:`BigFloat` instance, using the rounding-mode
   and precision given by the current context.

   *value* can be an integer, string, float, or another
   :class:`BigFloat` instance.  In all cases the given value is
   rounded to the format (precision, exponent limits and
   subnormalization) given by the current context, using the rounding
   mode specified by the current context.  The integer 0 is always
   converted to positive zero.

   .. method:: exact(cls, value, precision=None)

      A classmethod to construct a new :class:`BigFloat` instance from
      an integer, string, float or another :class:`BigFloat` instance,
      doing an exact conversion where possible.  Unlike the usual
      :class:`BigFloat` constructor, this alternative constructor makes no use
      of the current context and will not affect the current flags.

      If value is an integer, float or :class:`BigFloat`, then the
      precision keyword must not be given, and the conversion is
      exact.  The resulting :class:`BigFloat` has a precision
      sufficiently large to hold the converted value exactly.  If
      value is a string, then the precision argument must be given.
      The string is converted using the given precision and the
      RoundTiesToEven rounding mode.

   .. method:: as_integer_ratio(self)

      Return a pair (n, d) of integers such that n and d are
      relatively prime, d is positive, and the value of self is
      exactly n/d.

      If self is an infinity or nan then ValueError is raised.  Both
      negative and positive zeros are converted to (0, 1).


Reference
=========

.. module:: bigfloat
.. moduleauthor:: Mark Dickinson <dickinsm@gmail.com>

The :mod:`bigfloat` module is a Python wrapper for the MPFR library
for multiple-precision floating-point reliable arithmetic.

Introduction
------------

MPFR is a portable C library for arbitrary-precision arithmetic on
floating-point numbers.  It provides precise control over precisions
and rounding modes and gives correctly-rounded platform-independent
results.

The :mod:`bigfloat` module provides a convenient and friendly Python
interface to the operations and functions provided by MPFR.  The main
class, :class:`BigFloat`, gives a multiple-precision floating-point
type that can be freely mixed with Python integers and floats, and can
be used to emulate IEEE 754 arithmetic exactly.  The :class:`Context`
class, used in conjunction with Python's ``with`` statement, gives a
simple way of controlling precisions and rounding modes.  Additional
module-level functions provide various standard mathematical
operations.


Installation
------------

Prerequisites
^^^^^^^^^^^^^

In order to use the :mod:`bigfloat` module you will need to have both
the GMP and MPFR libraries already installed on your system.  See the
`MPFR homepage <http://www.mpfr.org>`_ and the `GMP homepage
<http://gmplib.org>`_ for more information about these libraries.
Currently, MPFR version 2.4.0 or later is required.

This module requires Python version 2.5 or later.  For Python 2.5,
you'll need to do a ``from __future__ import with_statement`` if you
want to take advantage of all of the features of this module.

Locating the MPFR library
^^^^^^^^^^^^^^^^^^^^^^^^^

The :mod:`bigfloat` module attempts to locate the MPFR library on your
system.  If it fails, or if you have multiple MPFR libraries installed
on your system and want to specify which one to use, you should edit
the ``mpfr_library_location`` setting in the ``bigfloat_config.py``
file to specify the library location.

Other configuration
^^^^^^^^^^^^^^^^^^^

The ``bigfloat_config.py`` file also allows you to specify some other
system-dependent values.  On a typical system, with default installs
of GMP and MPFR, it's unlikely that these values will need to be
changed.  But if you're getting segmentation faults or crashes with
the bigfloat library then you may need to edit the values in this
file.  In this case it will probably also be useful to have the gmp.h
and mpfr.h include files handy;  on Linux systems, these files may
be in a different package from the library files (e.g., 'mpfr-devel'
instead of 'mpfr').


Tutorial
--------

Start by importing the module (assuming that you've already installed
it and its prerequisites) with:

   >>> from bigfloat import *

This import brings a fairly large number of functions into the current
namespace, and clobbers some builtin Python functions: ``abs``,
``max``, ``min`` and ``pow``.  In normal usage you'll probably only
want to import the classes and functions that you actually need.

BigFloat construction
^^^^^^^^^^^^^^^^^^^^^

The main type of interest is the :class:`BigFloat` class.  The
BigFloat type is an immutable binary floating-point type.  A
:class:`BigFloat` instance can be created from an integer, a float or
a string:

   >>> BigFloat(123)
   BigFloat.exact('123.00000000000000', precision=53)
   >>> BigFloat(-4.56)
   BigFloat.exact('-4.5599999999999996', precision=53)

Each BigFloat instance has both a *value* and a *precision*.  The
precision gives the number of bits used to store the significand of
the BigFloat.  The *value* of a (finite, nonzero) BigFloat with
precision ``p`` is a real number of the form ``(-1)**sign * m * 2**e``
where ``sign`` is either ``0`` or ``1``, ``m`` is the *significand*, a
number in the half-open interval [0.5, 1.0) that can be expressed in
the form ``n/2**p`` for some integer ``n``, and ``e`` is an integer
giving the *exponent*.  In addition, zeros (positive and negative),
infinities and NaNs are representable.  Note that printed form of a
BigFloat shows only a decimal approximation to the stored value, for
the sake of human readers.

The precision of newly-constructed BigFloat instances is dictated by
the *current precision*, which defaults to 53.  This setting can be
overridden by supplying a ``context`` keyword argument to the
constructor:

   >>> BigFloat(-4.56, context=precision(24))
   BigFloat.exact('-4.55999994', precision=24)

The input value is rounded to the correct precision using the *current
rounding mode*, which defaults to ``RoundTiesToEven``; again, this can
be overridden with the ``context`` keyword argument:

   >>> BigFloat('3.14')
   BigFloat.exact('3.1400000000000001', precision=53)
   >>> BigFloat('3.14', context=RoundTowardZero)
   BigFloat.exact('3.1399999999999997', precision=53)
   >>> BigFloat('3.14', context=RoundTowardPositive + precision(24))
   BigFloat.exact('3.14000010', precision=24)

More generally, the second argument to the BigFloat constructor should
be an instance of the :class:`Context` class.  The various rounding
modes are all Context instances, and ``precision`` is a function
returning a Context:

   >>> RoundTowardNegative
   Context(rounding='RoundTowardNegative')
   >>> precision(1000)
   Context(precision=1000)

Contexts can be combined by addition, as seen above.

   >>> precision(1000) + RoundTowardNegative
   Context(precision=1000, rounding='RoundTowardNegative')

The `bigfloat` module also defines various constant Contexts.  For
example, ``quadruple_precision`` is a Context that corresponds to the
IEEE 754 binary128 interchange format::

   >>> quadruple_precision
   Context(precision=113, emax=16384, emin=-16493, subnormalize=True)
   >>> BigFloat('1.1', quadruple_precision)
   BigFloat.exact('1.10000000000000000000000000000000008', precision=113)

The current settings for precision and rounding mode are also given by
a Context instance, the *current context*, accessible via the
:func:`getcontext` function:

   >>> getcontext()
   Context(precision=53, emax=1073741823, emin=-1073741823, subnormalize=False, rounding='RoundTiesToEven')

Note that (unlike Python's standard decimal module), :class:`Context`
instances are immutable.  We'll learn more about Contexts, and how to
use them, below.

There's also a second method for constructing BigFloat instances:
:meth:`BigFloat.exact`.  As with the usual constructor, this
constructor accepts integers, floats and strings.  However, for
integers and floats it performs an exact conversion, creating a
BigFloat with precision large enough to hold the integer or float
exactly (regardless of the current precision setting):

   >>> BigFloat.exact(-123)
   BigFloat.exact('-123.0', precision=7)
   >>> BigFloat.exact(7**30)
   BigFloat.exact('22539340290692258087863249.0', precision=85)
   >>> BigFloat.exact(-56.7)
   BigFloat.exact('-56.700000000000003', precision=53)

For strings, :meth:`BigFloat.exact` accepts a second ``precision``
argument, and always rounds using the ``RoundTiesToEven`` rounding
mode.

   >>> BigFloat.exact('1.1', precision=80)
   BigFloat.exact('1.1000000000000000000000003', precision=80)

Also unlike the usual constructor, BigFloat.exact makes no use of the
current context, and so evaluates the same way every time; this is why
the :func:`repr` of a BigFloat is expressed in terms of
:meth:`BigFloat.exact`.  The :func:`str` of a BigFloat looks prettier,
but doesn't supply enough information to recover that BigFloat
exactly:

   >>> print BigFloat('1e1000')
   1.0000000000000001e+1000

Arithmetic on BigFloats
^^^^^^^^^^^^^^^^^^^^^^^

All the usual arithmetic operations, with the exception of floor
division, apply to BigFloats, and BigFloat instances can be freely
mixed with integers and floats (but not strings!) in those operations:

   >>> BigFloat(1234)/3
   BigFloat.exact('411.33333333333331', precision=53)
   >>> BigFloat('1e1233')**0.5
   BigFloat.exact('3.1622776601683794e+616', precision=53)

As with the BigFloat constructor, the precision for the result is
taken from the current context, as is the rounding mode used to round
the exact mathematical result to the nearest BigFloat.

For mixed-type operations, the integer or float is converted *exactly*
to a BigFloat before the operation (as though the BigFloat.exact
constructor had been applied to it).  So there's only a single point
where precision might be lost: namely, when the result of the
operation is rounded to the nearest value representable as a BigFloat.

.. note::

   The current precision and rounding mode even apply to the unary
   plus and minus operations.  In particular, ``+x`` is not
   necessarily a no-op for a BigFloat instance x:

   >>> BigFloat.exact(7**100)
   BigFloat.exact('3234476509624757991344647769100216810857203198904625400933895331391691459636928060001.0', precision=281)
   >>> +BigFloat.exact(7**100)
   BigFloat.exact('3.2344765096247579e+84', precision=53)

   This is occasionally useful, for rounding a result produced in a
   different context to the current context.

For each arithmetic operation the :mod:`bigfloat` module exports a
corresponding function.  For example, the :func:`div` function
corresponds to usual (true) division:

   >>> 355/BigFloat(113)
   BigFloat.exact('3.1415929203539825', precision=53)
   >>> div(355, 113)
   BigFloat.exact('3.1415929203539825', precision=53)

This is useful for a couple of reasons: one reason is that it makes it
possible to use ``div(x, y)`` in contexts where a BigFloat result is
desired but where one or both of x and y might be an integer or float.
But a more important reason is that these functions, like the BigFloat
constructor, accept an extra ``context`` keyword argument giving a
context for the operation::

   >>> div(355, 113, context=single_precision)
   BigFloat.exact('3.14159298', precision=24)

Similarly, the ``sub`` function corresponds to Python's subtraction
operation.  To fully appreciate some of the subtleties of the ways
that binary arithmetic operations might be performed, note the
difference in the results of the following:

   >>> x = 10**16+1  # integer, not exactly representable as a float
   >>> y = 10**16.   # 10.**16 is exactly representable as a float
   >>> x - y
   0.0
   >>> BigFloat(x) - BigFloat(y)
   BigFloat.exact('0', precision=53)
   >>> sub(x, y)
   BigFloat.exact('1.0000000000000000', precision=53)

For the first subtraction, the integer is first converted to a float,
losing accuracy, and then the subtraction is performed, giving a
result of 0.0.  The second case is similar: ``x`` and ``y`` are both
explicitly converted to BigFloat instances, and the conversion of
``y`` again loses precision.  In the third case, ``x`` and ``y`` are
*implicitly* converted to BigFloat instances, and that conversion is
exact, so the subtraction produces exactly the right answer.

Comparisons between BigFloats and integers or floats also behave as
you'd expect them to; for these, there's no need for a corresponding
function.

The :mod:`bigfloat` module provides a number of standard mathematical
functions.  These functions follow the same rules as the arithmetic
operations above: the inputs can be integers, floats or BigFloat
instances; integers and floats are converted to BigFloats using an
exact conversion; the result is a BigFloat with precision and rounding
mode taken from the current context, and parameters from the current
context can be overridden by providing a ``context`` keyword argument.
Here are some examples:

   >>> sqrt(1729, context=RoundTowardZero)
   BigFloat.exact('41.581245772583578', precision=53)
   >>> sqrt(1729, context=RoundTowardPositive)
   BigFloat.exact('41.581245772583586', precision=53)
   >>> atanh(0.5, context=precision(20))
   BigFloat.exact('0.54930592', precision=20)
   >>> const_catalan(precision(1000))
   BigFloat.exact('0.915965594177219015054603514932384110774149374281672134266498119621763019776254769479356512926115106248574422619196199579035898803325859059431594737481158406995332028773319460519038727478164087865909024706484152163000228727640942388259957741508816397470252482011560707644883807873370489900864775113226027', precision=1000)
   >>> 4*exp(-const_pi()/2/agm(1, 1e-100))
   BigFloat.exact('9.9999999999998517e-101', precision=53)

For a full list of the supported functions, see the reference manual.

Controlling the precision and rounding mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've seen one way of controlling precision and rounding mode, via the
``context`` keyword argument.  There's another way that's often more
convenient, especially when a single context change is supposed to
apply to multiple operations: contexts can be used directly in Python
``with`` statements.  Note: if you're using Python 2.5, you'll need
to enable with statements with:

   >>> from __future__ import with_statement

For example, here we compute high-precision upper and lower-bounds for
the thousandth harmonic number:

   >>> with precision(100):
   ...     with RoundTowardNegative:  # lower bound
   ...         lower_bound = sum(div(1, n) for n in range(1, 1001))
   ...     with RoundTowardPositive:  # upper bound
   ...         upper_bound = sum(div(1, n) for n in range(1, 1001))
   ... 
   >>> lower_bound
   BigFloat.exact('7.4854708605503449126565182015873', precision=100)
   >>> upper_bound
   BigFloat.exact('7.4854708605503449126565182077593', precision=100)

The effect of the with statement is to change the current context for
the duration of the with block; when the block exits, the previous
context is restored.  With statements can be nested, as seen above.
Let's double-check the above results using the asymptotic formula for
the nth harmonic number [#harmonic]_:

   >>> n = 1000
   >>> with precision(100):
   ...     approx = log(n) + const_euler() + div(1, 2*n) - 1/(12*sqr(n))
   ... 
   >>> approx
   BigFloat.exact('7.4854708605503365793271531207983', precision=100)

The error in this approximation should be approximately -1/(120*n**4):

   >>> error = approx - lower_bound
   >>> error
   BigFloat.exact('-8.3333293650807890e-15', precision=53)
   >>> -1/(120*pow(n, 4))
   BigFloat.exact('-8.3333333333333336e-15', precision=53)

A more permanent change to the context can be effected using the
:func:`setcontext` function, which takes a single argument of type
:class:`Context`:

   >>> setcontext(precision(30))
   >>> sqrt(2)
   BigFloat.exact('1.4142135624', precision=30)
   >>> setcontext(RoundTowardZero)
   >>> sqrt(2)
   BigFloat.exact('1.4142135605', precision=30)

An important point here is that in all places that a context is used,
only the attributes specified by that context are changed.  For
example, the context ``precision(30)`` only has the ``precision``
attribute, so only that attribute is affected by the ``setcontext``
call; the other attributes are not changed.  Similarly, the
``setcontext(RoundTowardZero)`` line above doesn't affect the
precision.

There's a ``DefaultContext`` constant giving the default context, so
you can always restore the original default context as follows:

   >>> setcontext(DefaultContext)

.. note::

   If :func:`setcontext` is used within a with statement, its effects
   only last for the duration of the block following the with
   statement.


Flags
^^^^^

The :mod:`bigfloat` module also provides four global flags: 'Inexact',
'Overflow', 'Underflow', 'NanFlag', along with methods to set and test
these flags:

   >>> set_flagstate(set())  # clear all flags
   >>> get_flagstate()
   set([])
   >>> exp(10**100)
   BigFloat.exact('Infinity', precision=53)
   >>> get_flagstate()
   set(['Overflow', 'Inexact'])

These flags show that overflow occurred, and that the given result
(infinity) was inexact.  The flags are sticky: none of the standard
operations ever clears a flag:

   >>> sqrt(2)
   BigFloat.exact('1.4142135623730951', precision=53)
   >>> get_flagstate()  # overflow flag still set from the exp call
   set(['Overflow', 'Inexact'])
   >>> set_flagstate(set())  # clear all flags
   >>> sqrt(2)
   BigFloat.exact('1.4142135623730951', precision=53)
   >>> get_flagstate()   # sqrt only sets the inexact flag
   set(['Inexact'])

The functions :func:`clear_flag`, :func:`set_flag` and
:func:`test_flag` allow clearing, setting and testing of individual
flags.


Reference
---------

The BigFloat class
^^^^^^^^^^^^^^^^^^

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

      If self is an infinity or nan then ValueError is raised.
      Negative and positive zero are both converted to (0, 1).




The Context class
^^^^^^^^^^^^^^^^^

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
previous context when the block is exited.  For example:

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
   to rnd.  Example usage:

      >>> with RoundTowardNegative:
      ...     lower_bound = log2(10)
      ... 
      >>> with RoundTowardPositive:
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
function.  This function also accepts a keyword argument 'context',
which can be used to override the rounding mode of the current
context.  For example:

   >>> div(2, 3, context=RoundTowardPositive)
   BigFloat.exact('0.66666666666666674', precision=53)
   >>> div(2, 3, context=RoundTowardNegative)
   BigFloat.exact('0.66666666666666663', precision=53)

This can be handy for places where you only want to alter the rounding
mode for a single function call or operation.

These module-level functions are also useful when you don't
necessarily know whether the input arguments are integers, floats or
BigFloats and you want to ensure that the result is a :class:`BigFloat`, or
that there's no loss of precision during argument conversion.  Consider
the following:

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
operations, comparisons between :class:`BigFloat` objects and integers
or :class:`BigFloat` objects and floats also work as expected,
performing an implicit exact conversion of the integer or float to a
:class:`BigFloat` before comparing.

The module provides two additional comparison functions that don't
correspond to any of the Python comparison operators.

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

.. rubric:: Footnotes

.. [#harmonic] See http://mathworld.wolfram.com/HarmonicNumber.html
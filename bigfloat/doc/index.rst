The bigfloat package --- high precision floating-point arithmetic
=================================================================

.. module:: bigfloat
   :synopsis: Python wrapper for MPFR floating-point library.

.. moduleauthor:: Mark Dickinson <dickinsm@gmail.com>

Introduction
------------

The :mod:`bigfloat` module is a Python wrapper for the MPFR library
for arbitrary precision floating-point reliable arithmetic.

The `MPFR library <http://www.mpfr.org>`_ is a well-known portable C
library for arbitrary-precision arithmetic on floating-point numbers.
It provides precise control over precisions and rounding modes and
gives correctly-rounded reproducible platform-independent results.

The :mod:`bigfloat` module aims to provide a convenient and friendly
Python interface to the operations and functions provided by the MPFR
library.  The main class, :class:`BigFloat`, gives an immutable
multiple-precision floating-point type that can be freely mixed with
Python integers and floats.  The :class:`Context` class, when used in
conjunction with Python's ``with`` statement, gives a simple way of
controlling precisions and rounding modes.  Additional module-level
functions provide various standard mathematical operations.  There is
full support for IEEE 754 signed zeros, nans, infinities and
subnormals.

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

The latest released version of the :mod:`bigfloat` module can be
downloaded from its place at the `Python Package Index
<http://pypi.python.org/pypi/bigfloat/>`_.  Development sources can be
checked out from the project's `bitbucket page
<http://bitbucket.org/dickinsm/bigfloat>`_.

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

Installation
^^^^^^^^^^^^

Like most third party Python libraries, the :mod:`bigfloat` module is
installed by means of the ``setup.py`` script included in the
distribution.  On most systems, installation should be as simple as
doing::

   python setup.py install

in the top-level directory of the unpacked distribution.  You may need
superuser privileges to install the library, for example with::

   sudo python setup.py install


Locating the MPFR library
^^^^^^^^^^^^^^^^^^^^^^^^^

The `setup.py` installation script attempts to locate the MPFR library
on your system.  If it fails, or if you have multiple MPFR libraries
installed on your system and want to specify which one to use, you
should edit the ``mpfr_library_location`` setting in the
``bigfloat/bigfloat_config.py.in`` file to specify the library location.

Other configuration
^^^^^^^^^^^^^^^^^^^

The ``bigfloat/bigfloat_config.py.in`` file also allows you to specify
some other system-dependent values.  On a typical system, with default
installs of GMP and MPFR, it's unlikely that these values will need to
be changed.  But if you're getting segmentation faults or crashes with
the bigfloat library then you may need to edit the values in this
file.  In this case it will probably also be useful to have the gmp.h
and mpfr.h include files handy to refer to; on Linux systems, these
files may be in a different package from the library files (e.g.,
'mpfr-devel' instead of 'mpfr').


Tutorial
--------

Start by importing the contents of the module (assuming that you've
already installed it and its prerequisites) with:

   >>> from bigfloat import *

This import brings a fairly large number of functions into the current
namespace, and clobbers some builtin Python functions: ``abs``,
``max``, ``min`` and ``pow``.  In normal usage you'll probably only
want to import the classes and functions that you actually need.

If you're using Python 2.5 you'll also need to do:

   >>> from __future__ import with_statement

:class:`BigFloat` construction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The main type of interest is the :class:`BigFloat` class.  The
:class:`BigFloat` type is an immutable binary floating-point type.  A
:class:`BigFloat` instance can be created from an integer, a float or
a string:

   >>> BigFloat(123)
   BigFloat.exact('123.00000000000000', precision=53)
   >>> BigFloat(-4.56)
   BigFloat.exact('-4.5599999999999996', precision=53)

Each :class:`BigFloat` instance has both a *value* and a *precision*.
The precision gives the number of bits used to store the significand
of the :class:`BigFloat`.  The *value* of a finite nonzero
:class:`BigFloat` with precision ``p`` is a real number of the form
``(-1)**s * m * 2**e``, where the *sign* ``s`` is either ``0`` or
``1``, the *significand* ``m`` is a number in the half-open interval
[0.5, 1.0) that can be expressed in the form ``n/2**p`` for some
integer ``n``, and ``e`` is an integer giving the *exponent*.  In
addition, zeros (positive and negative), infinities and NaNs are
representable.  Just like Python floats, the printed form of a
:class:`BigFloat` shows only a decimal approximation to the exact
stored value, for the benefit of human readers.

The precision of a newly-constructed :class:`BigFloat` instance is
dictated by the *current precision*, which defaults to ``53``.  This
setting can be overridden by supplying the ``context`` keyword
argument to the constructor:

   >>> BigFloat(-4.56, context=precision(24))
   BigFloat.exact('-4.55999994', precision=24)

The first argument to the :class:`BigFloat` constructor is rounded to
the correct precision using the *current rounding mode*, which
defaults to ``RoundTiesToEven``; again, this can be overridden with
the ``context`` keyword argument:

   >>> BigFloat('3.14')
   BigFloat.exact('3.1400000000000001', precision=53)
   >>> BigFloat('3.14', context=RoundTowardZero)
   BigFloat.exact('3.1399999999999997', precision=53)
   >>> BigFloat('3.14', context=RoundTowardPositive + precision(24))
   BigFloat.exact('3.14000010', precision=24)

More generally, the second argument to the :class:`BigFloat`
constructor can be any instance of the :class:`Context` class.  The
various rounding modes are all Context instances, and ``precision`` is
a function returning a Context:

   >>> RoundTowardNegative
   Context(rounding='RoundTowardNegative')
   >>> precision(1000)
   Context(precision=1000)

Context instances can be combined by addition, as seen above.

   >>> precision(1000) + RoundTowardNegative
   Context(precision=1000, rounding='RoundTowardNegative')

When adding two contexts that both specify values for a particular
attribute, the value for the right-hand addend takes precedence::

   >>> c = Context(subnormalize=False, rounding='RoundTowardPositive')
   >>> double_precision
   Context(precision=53, emax=1024, emin=-1073, subnormalize=True)
   >>> double_precision + c
   Context(precision=53, emax=1024, emin=-1073, subnormalize=False,
   rounding='RoundTowardPositive')
   >>> c + double_precision
   Context(precision=53, emax=1024, emin=-1073, subnormalize=True,
   rounding='RoundTowardPositive')

The `bigfloat` module also defines various constant Context instances.
For example, ``quadruple_precision`` is a Context that corresponds to
the IEEE 754 binary128 interchange format::

   >>> quadruple_precision
   Context(precision=113, emax=16384, emin=-16493, subnormalize=True)
   >>> BigFloat('1.1', quadruple_precision)
   BigFloat.exact('1.10000000000000000000000000000000008', precision=113)

The current settings for precision and rounding mode given by the
*current context*, accessible via the :func:`getcontext` function:

   >>> getcontext()
   Context(precision=53, emax=1073741823, emin=-1073741823, subnormalize=False,
   rounding='RoundTiesToEven')

There's also a :func:`setcontext` function for changing the current
context; however, the preferred method for making temporary changes to
the current context is to use Python's with statement.  More on this below.

Note that (in contrast to Python's standard library decimal module),
:class:`Context` instances are immutable.

There's also a second method for constructing :class:`BigFloat`
instances: :meth:`BigFloat.exact`.  Just like the usual constructor,
:meth:`BigFloat.exact` accepts integers, floats and strings.  However,
for integers and floats it performs an exact conversion, creating a
:class:`BigFloat` instance with precision large enough to hold the
integer or float exactly (regardless of the current precision
setting):

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

The result of a call to :class:`BigFloat`.exact is independent of the current
context; this is why the :func:`repr` of a :class:`BigFloat` is expressed in
terms of :meth:`BigFloat.exact`.  The :func:`str` of a :class:`BigFloat` looks
prettier, but doesn't supply enough information to recover that
:class:`BigFloat` exactly if you don't know the precision:

   >>> print BigFloat('1e1000', precision(20))
   9.9999988e+999
   >>> print BigFloat('1e1000', precision(21))
   9.9999988e+999

Arithmetic on :class:`BigFloat` instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the usual arithmetic operations, with the exception of floor
division, apply to :class:`BigFloat` instances, and those instances can be
freely mixed with integers and floats (but not strings!) in those
operations:

   >>> BigFloat(1234)/3
   BigFloat.exact('411.33333333333331', precision=53)
   >>> BigFloat('1e1233')**0.5
   BigFloat.exact('3.1622776601683794e+616', precision=53)

As with the :class:`BigFloat` constructor, the precision for the result is
taken from the current context, as is the rounding mode used to round
the exact mathematical result to the nearest :class:`BigFloat`.

For mixed-type operations, the integer or float is converted *exactly*
to a :class:`BigFloat` before the operation (as though the
:class:`BigFloat`.exact constructor had been applied to it).  So
there's only a single point where precision might be lost: namely,
when the result of the operation is rounded to the nearest value
representable as a :class:`BigFloat`.

.. note::

   The current precision and rounding mode even apply to the unary
   plus and minus operations.  In particular, ``+x`` is not
   necessarily a no-op for a :class:`BigFloat` instance x:

   >>> BigFloat.exact(7**100)
   BigFloat.exact('323447650962475799134464776910021681085720319890462540093389
   5331391691459636928060001.0', precision=281)
   >>> +BigFloat.exact(7**100)
   BigFloat.exact('3.2344765096247579e+84', precision=53)

   This makes the unary plus operator useful as a way to round a
   result produced in a different context to the current context.

For each arithmetic operation the :mod:`bigfloat` module exports a
corresponding function.  For example, the :func:`div` function
corresponds to usual (true) division:

   >>> 355/BigFloat(113)
   BigFloat.exact('3.1415929203539825', precision=53)
   >>> div(355, 113)
   BigFloat.exact('3.1415929203539825', precision=53)

This is useful for a couple of reasons: one reason is that it makes it
possible to use ``div(x, y)`` in contexts where a :class:`BigFloat` result is
desired but where one or both of x and y might be an integer or float.
But a more important reason is that these functions, like the :class:`BigFloat`
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
explicitly converted to :class:`BigFloat` instances, and the conversion of
``x`` again loses precision.  In the third case, ``x`` and ``y`` are
*implicitly* converted to :class:`BigFloat` instances, and that conversion is
exact, so the subtraction produces exactly the right answer.

Comparisons between :class:`BigFloat` instances and integers or floats also
behave as you'd expect them to; for these, there's no need for a
corresponding function.

Mathematical functions
^^^^^^^^^^^^^^^^^^^^^^

The :mod:`bigfloat` module provides a number of standard mathematical
functions.  These functions follow the same rules as the arithmetic
operations above:

  - the arguments can be integers, floats or :class:`BigFloat` instances

  - integers and float arguments are converted exactly to :class:`BigFloat`
    instances before the function is applied

  - the result is a :class:`BigFloat` instance, with the precision of
    the result, and the rounding mode used to obtain the result, taken
    from the current context.

  - attributes of the current context can be overridden by providing
    an additional ``context`` keyword argument.  Here are some
    examples:

   >>> sqrt(1729, context=RoundTowardZero)
   BigFloat.exact('41.581245772583578', precision=53)
   >>> sqrt(1729, context=RoundTowardPositive)
   BigFloat.exact('41.581245772583586', precision=53)
   >>> atanh(0.5, context=precision(20))
   BigFloat.exact('0.54930592', precision=20)
   >>> const_catalan(precision(1000))
   BigFloat.exact('0.9159655941772190150546035149323841107741493742816721342664
   9811962176301977625476947935651292611510624857442261919619957903589880332585
   9059431594737481158406995332028773319460519038727478164087865909024706484152
   1630002287276409423882599577415088163974702524820115607076448838078733704899
   00864775113226027', precision=1000)
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

The error in this approximation should be approximately -1/(120*n**4).
Let's check it:

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

An important point here is that in any place that a context is used,
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

Support for these flags is preliminary, and the API may change in
future versions.


Reference
---------

The :class:`BigFloat` class
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`BigFloat` class implements multiple-precision binary
floating-point numbers.  Each :class:`BigFloat` instance has both a
value and a precision; the precision is an integer giving the number
of significant bits used to store the value.  A finite nonzero
:class:`BigFloat` instance with precision p can be thought of as a
(sign, significand, exponent) triple (s, m, e), representing the value
(-1)**s * m * 2**e, where m is a value in the range [0.5, 1.0) stored
with p bits of precision.  Thus m is of the form n/2**p for some
integer n with 2**(p-1) <= n < 2**p.

In addition to nonzero finite numbers, :class:`BigFloat` instances can
also represent positive and negative infinity, positive and negative
zero, and NaNs.

:class:`BigFloat` instances should be treated as immutable.

.. class:: BigFloat(value, context=None)

   Construct a new :class:`BigFloat` instance from an integer, string,
   float or another :class:`BigFloat` instance, using the
   rounding-mode and output format (precision, exponent bounds and
   subnormalization) given by the current context.  If the *context*
   keyword argument is given, its value should be a :class:`Context`
   instance and its attributes override those of the current context.

   *value* can be an integer, string, float, or another
   :class:`BigFloat` instance.  In all cases the given value is
   rounded to the format (determined by precision, exponent limits and
   subnormalization) given by the current context, using the rounding
   mode specified by the current context.  The integer 0 is always
   converted to positive zero.

   .. method:: as_integer_ratio(self)

      Return a pair (n, d) of integers such that n and d are
      relatively prime, d is positive, and the value of self is
      exactly n/d.

      If self is an infinity or nan then ValueError is raised.
      Negative and positive zero are both converted to (0, 1).

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

   .. method:: fromhex(cls, value, context=None)

      Class method that constructs a new :class:`BigFloat` instance
      from a hexadecimal string.  Rounds to the current context using
      the given precision.  If the *context* keyword argument is
      given, its value should be a :class:`Context` instance and its
      attributes override those of the current context.

   .. method:: hex(self)

      Return a hexadecimal representation of a :class:`BigFloat`.  The
      advantage of the hexadecimal representation is that it
      represents the value of the :class:`BigFloat` exactly.

   .. attribute:: precision

      Precision of a :class:`BigFloat` instance, in bits.


Special methods
""""""""""""""""

The :class:`BigFloat` type has a full complement of special methods.
Here are some brief notes on those methods, indicating some possible
deviations from expected behaviour.

* The repr of a :class:`BigFloat` instance ``x`` is independent of the
  current context, and has the property that ``eval(repr(x))``
  recovers ``x`` exactly.

* The '+' ,'-', '*', '/', '**' and '%' binary operators are supported,
  and mixed-type operations involving a :class:`BigFloat` and an integer or
  float are permitted.  Mixed-type operations behave as though the
  non :class:`BigFloat` operand is first converted to a :class:`BigFloat` with no loss
  of accuracy.  The '/' operator implements true division, regardless
  of whether 'from __future__ import division' is in effect or not.
  The result of '%' has the same sign as the first argument, not the
  second.  Floor division is not currently implemented.

* The '+' and '-' unary operators and built-in :func:`abs` function
  are supported.  Note that these all round to the current context; in
  particular, '+x' is not necessarily equal to 'x' for a
  :class:`BigFloat` instance ``x``.

* The six comparison operators '==', '<=', '<', '!=', '>', '>=' are
  supported.  Comparisons involving NaNs always return False, except
  in the case of '!=' where they always return True.  Again,
  comparisons with integers or floats are permitted, with the integer
  or float being converted exactly before the comparison; the context
  does not affect the result of a comparison.

* Conversions to int and long always round towards zero; conversions
  to float always use the ``RoundTiesToEven`` rounding mode.
  Conversion to bool returns False for a nonzero :class:`BigFloat` and True
  otherwise.  None of these conversions is affected by the current
  context.

* :class:`BigFloat` instances are hashable.  For Python 2.6 and later,
  the hash function obeys the rule that objects that compare equal
  should hash equal; in particular, if ``x == n`` for some
  :class:`BigFloat` instance ``x`` and some Python int or long ``n``
  then ``hash(x) == hash(n)``, and similarly for floats.  In Python
  2.5, there are some rare cases where ``x == n`` does not imply
  ``hash(x) == hash(n)``.  For that reason it's inadvisable to mix
  integers and BigFloat instances in a set, or to use both integers
  and BigFloat instances as keys in the same dictionary.


The Context class
^^^^^^^^^^^^^^^^^

A :class:`Context` object is a simple immutable object that packages
together attributes describing a floating-point format, together with
a rounding mode.

.. class:: Context(precision=None, emin=None, emax=None, subnormalize=None, rounding=None)

   Create a new Context object with the given attributes.  Not all
   attributes need to be specified.  Note that all attributes of the
   generated Context are read-only.  Attributes that are unset for
   this Context instance return ``None``.

   .. attribute:: precision

      Precision of the floating-point format, given in bits.  This
      should be an integer in the range [``PRECISION_MIN``,
      ``PRECISION_MAX``].  ``PRECISION_MIN`` is usually ``2``.

   .. attribute:: emax

      Maximum exponent allowed for this format.  The largest finite
      number representable in the context self is
      ``(1-2**-self.precision) * 2**self.emax``.

   .. attribute:: emin

      Minimum exponent allowed for this format.  The smallest positive
      number representable in the context self is ``0.5 * 2**self.emin``.

      .. note::

         There's nothing to stop you defining a context with emin >
         emax, but don't expect to get sensible results if you do
         this.

   .. attribute:: subnormalize

      A boolean value: True if the format has gradual underflow, and
      False otherwise.  With gradual underflow, all finite
      floating-point numbers have a value that's an integer multiple
      of 2**(emin-1).

   .. attribute:: rounding

      The rounding mode of this Context.  This should be a string.
      Valid values are 'RoundTiesToEven', 'RoundTowardZero',
      'RoundTowardPositive' and 'RoundTowardNegative'.  Note that the
      rounding modes ``RoundTiesToEven``, etc. exported by the
      :mod:`bigfloat` module are Context instances, not strings, so
      cannot be used directly here.


:class:`Context` instances can be added.  If ``x`` and ``y`` are
Context instances then ``x + y`` is the Context whose attributes
combine those of ``x`` and ``y``.  In the case that both ``x`` and
``y`` have a particular attribute set, the value for ``y`` takes
precedence:

   >>> x = Context(precision=200, rounding='RoundTiesToEven')
   >>> y = Context(precision=53, subnormalize=True)
   >>> x + y
   Context(precision=53, subnormalize=True, rounding='RoundTiesToEven')
   >>> y + x
   Context(precision=200, subnormalize=True, rounding='RoundTiesToEven')

:class:`Context` instances can be used in with statements to alter
the current context.  In effect, ::

   with c:
       <block>

behaves roughly like ::

   old_context = getcontext()
   setcontext(c)
   <block>
   setcontext(old_context)

except that nesting of with statements works as you'd expect, and the
old context is guaranteed to be restored even if an exception occurs
during execution of the block.

Note that for Context instances ``x`` and ``y``, ::

   with x + y:
       <block>

is exactly equivalent to ::

   with x:
       with y:
           <block>

The bigfloat module defines a number of predefined :class:`Context`
instances.

.. data:: DefaultContext

   The context that's in use when the bigfloat module is first
   imported.  It has precision of 53, large exponent bounds, no
   subnormalization, and the RoundTiesToEven rounding mode.

.. data:: EmptyContext

   Equal to Context().  Occasionally useful where a context is
   syntactically required for a with statement, but no change to the
   current context is desired.  For example::

      if <want_extra_precision>:
          c = extra_precision(10)
      else:
          c = EmptyContext

      with c:
          <do calculation>

.. data:: half_precision
.. data:: single_precision
.. data:: double_precision
.. data:: quadruple_precision

   These :class:`Context` instances correspond to the binary16,
   binary32, binary64 and binary128 interchange formats described in
   IEEE 754-2008 (section 3.6).  They're all special cases of the
   :func:`IEEEContext` function.

.. function:: IEEEContext(bitwidth)

   If bitwidth is one of widths permitted by IEEE 754 (that is, either
   16, 32, 64, or a multiple of 32 not less than 128), return the IEEE
   754 binary interchange format with the given bit width.  See
   section 3.6 of IEEE 754-2008 or the bigfloat source for details.

.. function:: precision(p)

   A convenience function.  ``precision(p)`` is exactly equivalent to
   ``Context(precision=p)``.

.. data:: RoundTiesToEven
.. data:: RoundTowardZero
.. data:: RoundTowardPositive
.. data:: RoundTowardNegative

   Contexts corresponding to the four available rounding modes.
   ``RoundTiesToEven`` rounds the result of an operation or function
   to the nearest representable :class:`BigFloat`, with ties rounded to the
   :class:`BigFloat` whose least significant bit is zero.  ``RoundTowardZero``
   rounds results towards zero.  ``RoundTowardPositive`` rounds
   results towards positive infinity, and ``RoundTowardsNegative``
   rounds results towards negative infinity.

Constants
""""""""""

.. data:: PRECISION_MIN
.. data:: PRECISION_MAX

   Minimum and maximum precision that's valid for Contexts and
   :class:`BigFloat` instances.  In the current implementation,
   ``PRECISION_MIN`` is ``2`` and ``PRECISION_MAX`` is ``2**31-1``.

.. data:: EMIN_MIN
.. data:: EMIN_MAX

   Minimum and maximum allowed values for the Context emin attribute.
   In the current implementation, ``EMIN_MIN == -EMIN_MAX == 1-2**30``.

.. data:: EMAX_MIN
.. data:: EMAX_MAX

   Minimum and maximum allowed values for the Context emax attribute.
   In the current implementation, ``-EMAX_MIN == EMAX_MAX == 2**30-1``.


The current context
""""""""""""""""""""

There can be many Context objects in existence at one time, but
there's only ever one *current context*.  The current context is given
by a thread-local :class:`Context` instance.  Whenever the :class:`BigFloat`
constructor is called, or any arithmetic operation or standard
function computation is performed, the current context is consulted to
determine:

* The format that the result of the operation or function should take
  (as specified by the ``precision``, ``emax``, ``emin`` and
  ``subnormalize`` attributes of the context), and

* The rounding mode to use when computing the result, as specified by
  the ``rounding`` attribute of the current context.

If an additional ``context`` keyword argument is given to the
operation, function or constructor, then attributes from the context
override the corresponding attributes in the current context.
For example, ::

   sqrt(x, context=my_context)

is equivalent to ::

   with my_context:
       sqrt(x)

The current context can be read and written directly using the
:func:`getcontext` and :func:`setcontext` functions.

.. function:: getcontext()

   Return a copy of the current context.

.. function:: setcontext(context)

   Set the current context to the given context.

It's usually neater to make a temporary change to the context using a
with statement, as described above.  There's also one convenience
function that's often useful in calculations:

.. function:: extra_precision(p)

   Return a copy of the current context with the precision increased
   by p.  Equivalent to
   ``Context(precision=getcontext().precision+p)``.

      >>> getcontext().precision
      53
      >>> extra_precision(10).precision
      63
      >>> with extra_precision(20):
      ...     gamma(1.5)
      ... 
      BigFloat.exact('0.88622692545275801364912', precision=73)


Standard functions
^^^^^^^^^^^^^^^^^^

All functions in this section follow the same rules:

* Arguments can be :class:`BigFloat` instances, integers or floats, unless
  otherwise specified.
* Integer or float arguments are converted exactly to :class:`BigFloat`
  instances.
* The format of the result and the rounding mode used to obtain that
  result are taken from the current context.
* Attributes of the current context can be overridden by supplying an
  explicit ``context`` keyword argument.
* Results are correctly rounded.

Conversion from string
""""""""""""""""""""""

.. function:: set_str2(s, base)

   Convert a string s, representing a number in base b, to a :class:`BigFloat`.
   The base should satisfy 2 <= base <= 36.

Arithmetic functions
""""""""""""""""""""

.. function:: add(x, y)
.. function:: sub(x, y)
.. function:: mul(x, y)
.. function:: div(x, y)
.. function:: pow(x, y)

   Return x+y, x-y, x*y, x/y and x**y respectively.

.. function:: mod(x, y)

   Return the reduction of x modulo y.  The result has the same sign as x.
   In other words, return x-q*y, where q is the integer part of x/y.

.. function:: remainder(x, y)

   Return x-q*y, where q is the closest integer to x/y, with ties rounded
   to the nearest even integer.

.. function:: dim(x, y)

   Return max(x-y, 0).

.. function:: pos(x)
.. function:: neg(x)
.. function:: abs(x)

   Return +x, -x and the absolute value of x respectively.  Note that
   these functions will round if x is not exactly representable in the
   current context.

.. function:: fma(x, y, z)

   Return x*y+z, but with no loss of intermediate accuracy.

.. function:: fms(x, y, z)

   Return x*y-z, with no loss of intermediate accuracy.

.. function:: sqr(x)

   Return x*x.

.. function:: sqrt(x)

   Return the square root of x, or a NaN if x is negative.  The square
   root of negative zero returns negative zero.

.. function:: rec_sqrt(x)

   Return the reciprocal of the square root of x.  rec_sqrt of zero
   returns positive infinity, regardless of the sign of the zero.
   Note that this means that 1/sqrt(x) differs from rec_sqrt(x) when
   x is negative zero.

.. function:: cbrt(x)

   Return the cube root of x.

.. function:: root(x, n)

   Return the nth root of x; n should be a nonnegative integer.  For
   even n, return NaN if x is negative.  For n = 0, always return NaN.

.. function:: hypot(x, y)

   Return the square root of x*x+y*y.

Exponential and logarithmic functions
""""""""""""""""""""""""""""""""""""""

.. function:: exp(x)

   Return ``e**x``, where ``e`` is Euler's constant. (2.71828...)

.. function:: expm1(x)

   Return ``e**x - 1``.  Useful for values of ``x`` close to 0, when
   the expression ``exp(x)-1`` would lose significant accuracy.

   >>> exp(1e-10)-1
   BigFloat.exact('1.0000000827403710e-10', precision=53)
   >>> exp(1e-10, precision(100))-1
   BigFloat.exact('1.0000000000500000e-10', precision=53)
   >>> expm1(1e-10)
   BigFloat.exact('1.0000000000500000e-10', precision=53)

.. function:: exp2(x)

   Return ``2**x``.

.. function:: exp10(x)

   Return ``10**x``.

.. function:: log(x)

   Return the natural (base ``e``) logarithm of *x*.

.. function:: log1p(x)

   Return ``log(1+x)``.  Useful for small values of x, where
   computing ``log(1+x)`` directly loses significant accuracy.

.. function:: log2(x)

   Return the log base 2 of *x*.

.. function:: log10(x)

   Return the log base 10 of *x*.

Trigonometric functions
""""""""""""""""""""""""

.. function:: cos(x)
.. function:: sin(x)
.. function:: tan(x)
.. function:: sec(x)
.. function:: csc(x)
.. function:: cot(x)

   Cosine, sine, tangent, secant, cosecant and cotangent of x,
   respectively.  Note that these functions are (necessarily) very
   slow for large arguments (for example, ``x`` larger than
   ``BigFloat('1e1000000')``), since reducing ``x`` correctly modulo
   ``pi`` requires computing ``pi`` to high precision.  Input
   arguments are in radians, not degrees.

.. function:: acos(x)
.. function:: asin(x)
.. function:: atan(x)

   Inverse cosine, sine and tangent functions, giving a result in
   radians.

.. function:: atan2(y, x)

   Return the arctangent2 of y and x.  This is the angle that the ray
   joining (0, 0) to (x, y) makes with the positive x-axis.

Hyperbolic trig functions
""""""""""""""""""""""""""

.. function:: cosh(x)
.. function:: sinh(x)
.. function:: tanh(x)
.. function:: sech(x)
.. function:: csch(x)
.. function:: coth(x)

   Hyperbolic cosine, sine, tangent, secant, cosecant and cotangent of x,
   respectively.

.. function:: acosh(x)
.. function:: asinh(x)
.. function:: atanh(x)

   Inverse hyperbolic cosine, sine and tangent functions.

Special functions
""""""""""""""""""

.. function:: eint(x)

   Return the exponential integral of x.

.. function:: li2(x)

   Return the real part of the dilogarithm of x.

.. function:: factorial(n)

   Return the factorial of n.  *n* should be a nonnegative integer.

.. function:: gamma(x)

   Return the gamma function applied to x.

.. function:: lgamma(x)

   Return the natural log of the absolute value of gamma(x).

.. function:: lngamma(x)

   Return log(gamma(x)).

.. function:: zeta(x)

   Return the Riemann zeta function of x.

.. function:: erf(x)

   Return the error function of x.

.. function:: erfc(x)

   Return the complementary error function of x.

.. function:: j0(x)
.. function:: j1(x)
.. function:: jn(n, x)

   Return Bessel function of the first kind of order 0, 1 and n,
   evaluated at x.  For ``jn``, *n* should be an integer.

.. function:: y0(x)
.. function:: y1(x)
.. function:: yn(n, x)

   Return Bessel function of the second kind of order 0, 1 and n,
   evaluated at x.  For ``yn``, *n* should be an integer.

.. function:: agm(x, y)

   Return the arithmetic-geometric mean of x and y.

Constants
""""""""""

.. function:: const_catalan()

   The Catalan constant 1 - 1/3**2 + 1/5**2 - 1/7**2 + 1/9**2 - ... = 0.9159655941...

.. function:: const_euler()

   The Euler-Mascheroni constant 0.5772156649..., equal to the limit
   of (1 + 1/2 + 1/3 + ... + 1/n) - log(n) as n approaches infinity.

.. function:: const_log2()

   The natural log of 2, 0.6931471805...

.. function:: const_pi()

   The constant pi = 3.1415926535...


Miscellaneous functions
""""""""""""""""""""""""

.. function:: max(x, y)

   Return the maximum of *x* and *y*.  If *x* and *y* are zeros with
   different signs, return positive zero.

.. function:: min(x, y)

   Return the minimum of *x* and *y*.  If *x* and *y* are zeros with
   different signs, return negative zero.

.. function:: copysign(x, y)

   Return a :class:`BigFloat` with absolute value taken from x and sign taken
   from y.

.. function:: frac(x)

   Return the fractional part of x.  The result has the same sign
   as x.

.. function:: floor(x)

   Return the floor of x.  Note that since the result is rounded to
   the current context, it's quite possible for the result to be
   larger than x:

   >>> with DefaultContext:
   ...     floor(2**100-1) <= 2**100-1
   ... 
   False

   If you want to be sure of getting a result that's no larger than
   *x*, use the ``RoundTowardNegative`` rounding mode.  Alternatively,
   if you want the exact floor you may want to clear the ``Inexact``
   flag before the call and test it afterwards.  Similar comments
   apply to the :func:`ceil`, :func:`round` and :func:`trunc`
   functions.

.. function:: ceil(x)

   Return the ceiling of x.

.. function:: round(x)

   Return x, rounded to the nearest integer.  Ties are rounded
   away from zero. ('Biased rounding')

.. function:: trunc(x)

   Return the integer part of x.

Other Functions
^^^^^^^^^^^^^^^

These are the functions exported by the :mod:`bigfloat` module that
don't fit into the above section, for one reason or another.

Additional Comparisons
""""""""""""""""""""""

There are two additional comparison functions that don't
correspond to any of the Python comparison operators.

.. function:: lessgreater(x, y)

   Return True if either x < y or x > y, and False otherwise.
   lessgreater(x, y) differs from x != y in the case where either x or
   y is a NaN: in that case, lessgreater(x, y) will return False,
   while x != y will return True.

.. function:: unordered(x, y)

   Return True if either x or y is a NaN, and False otherwise.

Number classification functions
""""""""""""""""""""""""""""""""

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

   Return True if the sign bit of x is set, and False otherwise.  Note
   that the name of this function is slightly misleading for zeros:
   is_negative(-0.0) returns True, even though -0.0 is not, strictly
   speaking, negative.

.. function:: is_integer(x)

   Return True if x is finite and an exact integer, and False
   otherwise.

Miscellaneous functions
"""""""""""""""""""""""

.. function:: next_up(x)

   Return the least representable BigFloat that's strictly greater than x.
   This operation is quiet:  it doesn't affect any of the flags.

.. function:: next_down(x)

   Return the greatest representable BigFloat that's strictly less than x.
   This operation is quiet:  it doesn't affect any of the flags.


Flags
^^^^^

.. data:: Underflow

   Underflow flag.  Set whenever the result of an operation
   underflows.  The meaning of this flag differs depending on whether
   the subnormalize attribute is true for the operation context.  In
   the language of IEEE 754, we use the `after rounding` semantics.
   The Underflow flag is set on underflow even when the result of an
   operation is exact.

   In detail: let ``c`` be the context that's in effect for an
   operation, function or :class:`BigFloat` construction.  Let ``x`` be the
   result of the operation, rounded to the context precision with the
   context rounding mode, but as though the exponent were unbounded.

   If c.subnormalize is False, the Underflow flag is set if and only
   if ``x`` is nonzero, finite, and strictly smaller than
   ``2**(c.emin-1)`` in absolute value.  If c.subnormalize is True,
   the Underflow flag is set if and only if ``x`` is nonzero, finite,
   and strictly smaller than ``2**(c.emin+c.precision-2)`` in absolute
   value.

.. data:: Overflow

   Set whenever the result of an operation overflows.  An operation
   performed in a context ``c`` overflows if the result computed as if
   with unbounded exponent range is finite and greater than or equal
   to ``2**c.emax`` in absolute value.

.. data:: Inexact

   Inexact flag.  Set whenever the result of an operation is not
   exactly equal to the true mathematical result.

.. data:: NanFlag

   NaN flag.  Set whever the result of an operation gives a NaN
   result.

.. function:: clear_flag(flag)

   Clear the given flag.

.. function:: set_flag(flag)

   Set the given flag.

.. function:: test_flag(flag)

   Return True if the given flag is set and False otherwise.

.. function:: get_flagstate()

   Return a set containing the flags that are currently set.

.. function:: set_flagstate(flag_set)

   Set all flags that are in *flag_set*, and clear all other flags.

.. rubric:: Footnotes

.. [#harmonic] See http://mathworld.wolfram.com/HarmonicNumber.html

Indices and tables
==================

* :ref:`genindex`


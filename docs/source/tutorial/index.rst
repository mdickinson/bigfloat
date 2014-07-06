Tutorial
--------

Start by importing the contents of the package (assuming that you've
already installed it and its prerequisites) with:

   >>> from bigfloat import *

You should be a little bit careful here: this import brings a fairly large
number of functions into the current namespace, four of which shadow existing
Python builtins, namely ``abs``, ``max``, ``min`` and ``pow``.  In normal usage
you'll probably only want to import the classes and functions that you actually
need.


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

The :mod:`bigfloat` package also defines various constant Context instances.
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

There's a second method for constructing :class:`BigFloat`
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

For each arithmetic operation the :mod:`bigfloat` package exports a
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

The :mod:`bigfloat` package provides a number of standard mathematical
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
``with`` statements.

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

The :mod:`bigfloat` package also provides five global flags: 'Inexact',
'Overflow', 'ZeroDivision', 'Underflow', and 'NanFlag', along with methods to
set and test these flags:

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


.. rubric:: Footnotes

.. [#harmonic] See http://mathworld.wolfram.com/HarmonicNumber.html

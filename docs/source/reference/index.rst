API Reference
-------------

.. module:: bigfloat
   :synopsis: Python wrapper for MPFR floating-point library.

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

   .. method:: copy_abs(self)

      Return a copy of *self* with the sign bit unset.

      In contrast to ``abs(self)``, ``self.copy_abs()`` makes no use of the
      context, and the result has the same precision as the original.
      
   .. method:: copy_neg(self)

      Return a copy of *self* with the opposite sign bit.

      In constract to ``neg(self)``, ``self.copy_neg()`` makes no use of the
      context, and the result has the same precision as the original.

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
"""""""""""""""

The :class:`BigFloat` type has a full complement of special methods.
Here are some brief notes on those methods, indicating some possible
deviations from expected behaviour.

* The repr of a :class:`BigFloat` instance ``x`` is independent of the
  current context, and has the property that ``eval(repr(x))``
  recovers ``x`` exactly.

* The '+' ,'-', '*', '/' and '**' binary operators are supported, and
  mixed-type operations involving a :class:`BigFloat` and an integer
  or float are permitted.  For MPFR version >= 2.4.0, the '%' is also
  supported.  Mixed-type operations behave as though the non
  :class:`BigFloat` operand is first converted to a :class:`BigFloat`
  with no loss of accuracy.  The '/' operator implements true
  division, regardless of whether 'from __future__ import division' is
  in effect or not.  The result of '%' has the same sign as the first
  argument, not the second.  Floor division is not currently
  implemented.

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

* :class:`BigFloat` instances are hashable.  The hash function obeys the rule
  that objects that compare equal should hash equal; in particular, if ``x ==
  n`` for some :class:`BigFloat` instance ``x`` and some Python int or long
  ``n`` then ``hash(x) == hash(n)``, and similarly for floats.


The :class:`Context` class
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
      :mod:`bigfloat` package are Context instances, not strings, so
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

The bigfloat package defines a number of predefined :class:`Context`
instances.

.. data:: DefaultContext

   The context that's in use when the bigfloat package is first
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

.. autofunction:: IEEEContext

.. autofunction:: precision
.. autofunction:: rounding

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
"""""""""

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
"""""""""""""""""""

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

.. autofunction:: getcontext()
.. autofunction:: setcontext(context)

It's usually neater to make a temporary change to the context using a
with statement, as described above.  There's also one convenience
function that's often useful in calculations:

.. autofunction:: extra_precision


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


Arithmetic functions
""""""""""""""""""""

.. autofunction:: add
.. autofunction:: sub
.. autofunction:: mul
.. autofunction:: div
.. autofunction:: pow
.. autofunction:: mod

.. autofunction:: remainder

.. autofunction:: dim

.. autofunction:: pos
.. autofunction:: neg
.. autofunction:: abs

.. autofunction:: fma
.. autofunction:: fms
.. autofunction:: sqr
.. autofunction:: sqrt
.. autofunction:: rec_sqrt
.. autofunction:: cbrt
.. autofunction:: root
.. autofunction:: hypot


Exponential and logarithmic functions
"""""""""""""""""""""""""""""""""""""

.. autofunction:: exp
.. autofunction:: exp2
.. autofunction:: exp10

.. autofunction:: log
.. autofunction:: log2
.. autofunction:: log10

.. autofunction:: expm1
.. autofunction:: log1p


Trigonometric functions
"""""""""""""""""""""""

.. autofunction:: cos
.. autofunction:: sin
.. autofunction:: tan
.. autofunction:: sec
.. autofunction:: csc
.. autofunction:: cot

The above six trigonometric functions are inefficient for large arguments (for
example, ``x`` larger than ``BigFloat('1e1000000')``), since reducing ``x``
correctly modulo π requires computing π to high precision.  Input
arguments are in radians, not degrees.

.. autofunction:: acos
.. autofunction:: asin
.. autofunction:: atan

These functions return a result in radians.

.. autofunction:: atan2


Hyperbolic trig functions
"""""""""""""""""""""""""

.. autofunction:: cosh
.. autofunction:: sinh
.. autofunction:: tanh
.. autofunction:: sech
.. autofunction:: csch
.. autofunction:: coth

.. autofunction:: acosh
.. autofunction:: asinh
.. autofunction:: atanh

Special functions
"""""""""""""""""

.. autofunction:: eint
.. autofunction:: li2
.. autofunction:: gamma
.. autofunction:: lngamma
.. autofunction:: lgamma
.. autofunction:: zeta
.. autofunction:: zeta_ui
.. autofunction:: erf
.. autofunction:: erfc
.. autofunction:: j0
.. autofunction:: j1
.. autofunction:: jn
.. autofunction:: y0
.. autofunction:: y1
.. autofunction:: yn
.. autofunction:: agm
.. autofunction:: factorial


Constants
"""""""""

.. autofunction:: const_catalan
.. autofunction:: const_euler
.. autofunction:: const_log2
.. autofunction:: const_pi


Miscellaneous functions
"""""""""""""""""""""""

.. autofunction:: max
.. autofunction:: min
.. autofunction:: copysign

.. autofunction:: frac

.. autofunction:: ceil
.. autofunction:: floor
.. autofunction:: round
.. autofunction:: trunc


Other Functions
^^^^^^^^^^^^^^^

These are the functions exported by the :mod:`bigfloat` package that
don't fit into the above section, for one reason or another.

Comparisons
"""""""""""

These functions provide three-way comparisons.

.. autofunction:: sgn
.. autofunction:: cmp
.. autofunction:: cmpabs

The following functions match the functionality of the builtin Python
comparison operators.

.. autofunction:: greater
.. autofunction:: greaterequal
.. autofunction:: less
.. autofunction:: lessequal
.. autofunction:: equal 

There are two additional comparison functions that don't
correspond to any of the Python comparison operators.

.. autofunction:: lessgreater
.. autofunction:: unordered


Number classification functions
"""""""""""""""""""""""""""""""

The following functions all accept a single :class:`BigFloat` instance (or a
float, or an integer) and return a boolean value.  They make no
use of the current context, and do not affect the state of the flags.

.. autofunction:: is_nan
.. autofunction:: is_inf
.. autofunction:: is_zero
.. autofunction:: is_finite
.. autofunction:: is_negative
.. autofunction:: is_integer


Miscellaneous functions
"""""""""""""""""""""""

.. autofunction:: next_up
.. autofunction:: next_down


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

.. data:: ZeroDivision

   Set whenever an exact infinite result is obtained from finite inputs.
   Despite the name, this flag is not just set for divisions by zero.  For
   example, ``log(0)`` will set the ZeroDivision flag.

.. data:: Inexact

   Inexact flag.  Set whenever the result of an operation is not
   exactly equal to the true mathematical result.

.. data:: NanFlag

   NaN flag.  Set whever the result of an operation gives a NaN
   result.

.. autofunction:: clear_flag
.. autofunction:: set_flag
.. autofunction:: test_flag
.. autofunction:: get_flagstate
.. autofunction:: set_flagstate


MPFR Version information
^^^^^^^^^^^^^^^^^^^^^^^^

.. data:: MPFR_VERSION_STRING

   The version of the MPFR library being used, as a string.

.. data:: MPFR_VERSION

   The version of the MPFR library being used, as an integer.

.. data:: MPFR_VERSION_MAJOR

   An integer giving the major level of the MPFR version.

.. data:: MPFR_VERSION_MINOR

   An integer giving the minor level of the MPFR version.

.. data:: MPFR_VERSION_PATCHLEVEL

   An integer giving the patch level of the MPFR version.

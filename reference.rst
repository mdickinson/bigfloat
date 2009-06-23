Reference
=========

BigFloat objects
----------------

The BigFloat class represents multiple-precision binary
floating-point numbers.  Each BigFloat instance has both a value
and a precision; the precision is an integer giving the number of
significant bits used to store the value.  A finite nonzero
BigFloat instance with precision p can be thought of as a (sign,
significand, exponent) triple (s, m, e), representing the value
(-1)**s * m * 2**e, where m is a value in the range [0.5, 1.0)
stored with p bits of precision.  (Thus m is of the form n/2**p for
some integer n with 2**(p-1) <= n < 2**p.)

In addition to nonzero finite numbers, BigFloats can also represent
positive and negative infinities, positive and negative zeros, and
NaNs.

BigFloat instances should be considered immutable.

Arithmetic on BigFloats
-----------------------

All the usual unary and binary arithmetic operations can be applied to
BigFloats.  The result of any operation is rounded to the current
context, using the rounding mode from the current context.  The value
of the result is as if the operation had been performed to
infinite-precision, and then correctly rounded using the current
rounding mode.

Mixed-type operations are permitted between a BigFloat and an integer,
or a BigFloat and a float.  For these operations, the integer or float
is first implicitly converted to a BigFloat.  The implicit conversion
is performed exactly, without reference to the current context, so
that an arithmetic operation between (for example) an integer and a
BigFloat will only involve a single round, at the end of the
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
  are not currently implemented for BigFloat instances.

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
BigFloats and you want to ensure that the result is a BigFloat, or
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
converted to BigFloat instances, and while x can be converted exactly,
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
operations, comparisons between BigFloats and integers or BigFloats
and floats also work as expected, performing an implicit exact
conversion of the integer or float to a BigFloat before comparing.

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

Conversion of a BigFloat to an integer using the :func:`int` builtin
function always truncates (rounds towards zero), regardless of the
current context rounding mode.

Conversion of a BigFloat to a float using the :func:`float` builtin
function always rounds to the nearest floating-point number,
regardless of the current context rounding mode.

Number classification functions
-------------------------------

The following functions all accept a single BigFloat instance (or a
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
      BigFloat constructor, this alternative constructor makes no use
      of the current context and will not affect the current flags.

      If value is an integer, float or BigFloat, then the precision
      keyword must not be given, and the conversion is exact.  The
      resulting BigFloat has a precision sufficiently large to hold the
      converted value exactly.  If value is a string, then the
      precision argument must be given.  The string is converted using
      the given precision and the RoundTiesToEven rounding mode.

   .. method:: as_integer_ratio(self)

      Return a pair (n, d) of integers such that n and d are
      relatively prime, d is positive, and the value of self is
      exactly n/d.

      If self is an infinity or nan then ValueError is raised.  Both
      negative and positive zeros are converted to (0, 1).


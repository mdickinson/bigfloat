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

Comparisons between BigFloats and integers or BigFloats and floats
also work as expected, performing an implicit exact conversion of the
integer or float to a BigFloat before comparing.


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

   .. method:: exact(value, precision=None)

     Construct a new :class:`BigFloat` instance from an integer,
     string, float or another :class:`BigFloat` instance, doing an
     exact conversion where possible.  Unlike the usual BigFloat
     constructor, this alternative constructor makes no use of the
     current context.

     If value is an integer, float or BigFloat, then the precision
     keyword must not be given, and the conversion is exact.  The
     resulting BigFloat has a precision sufficiently large to hold the
     converted value exactly.  If value is a string, then the
     precision argument must be given.  The string is converted using
     the given precision and the RoundTiesToEven rounding mode.



Tutorial
========

What is it?
-----------

The :mod:`bigfloat` module provides multiprecision binary
floating-point arithmetic, with correctly rounded operations and
functions.  It wraps the well-known open-source MPFR library for
multiprecision floating-point reliable arithmetic.


Getting started
---------------

In this section we give a brief tour of the :mod:`bigfloat` module,
touching on the most important features.  To begin, just type the
following at a Python prompt::

   >>> from bigfloat import *

This will import two classes and a number of auxiliary functions.  The
most important class is the :class:`BigFloat` class.  An instance of
this class represents a floating-point number, stored with a
particular precision.

BigFloat instances are immutable, and can be created from integers,
strings, floats, or other BigFloats::

   >>> x = BigFloat(123)
   >>> x
   BigFloat.exact('123.00000000000000', precision=53)
   >>> y = BigFloat('3.1415926535')
   >>> y
   BigFloat.exact('3.1415926535000001', precision=53)

As you'd expect, all the usual arithmetic operations can be applied to
BigFloats.  BigFloat instances can be freely mixed with integers and
floats in arithmetic operations, and those integers or floats undergo
an exact implict conversion to a BigFloat before the operation is
performed.

   >>> x + y
   BigFloat.exact('126.14159265350000', precision=53)
   >>> x ** 2
   BigFloat.exact('15129.000000000000', precision=53)
   >>> 1/x 
   BigFloat.exact('0.0081300813008130090', precision=53)

In addition, there are a number of functions that operate on BigFloat
instances.  As with the arithmetic operations, all these functions
also accept integers and floats::

   >>> sqrt(3)  # square root of 3, as a BigFloat
   BigFloat.exact('1.7320508075688772', precision=53)
   >>> agm(2, 3)
   BigFloat.exact('2.4746804362363046', precision=53)
   >>> const_pi()
   BigFloat.exact('3.1415926535897931', precision=53)
   

Contexts
--------

You'll notice that in the above examples, the displayed value for each
BigFloat ended with ``precision=53``, indicating that the
:class:`BigFloat` instance is stored with 53 bits of binary precision.

The precision of the result of an arithmetic operation or function is
controlled by the current *context*.  Almost all arithmetic operations
and functions that return a :class:`BigFloat` instance use the current
context to determine the precision of a result; this also applies to
creation of a BigFloat instance from an integer or float.

The current context also controls the method used to round an inexact
result, along with some other details that we'll meet later.

The current context is given by a global (more correctly thread-local)
instance of the :class:`Context` class.  To retrieve the current
context, use the :func:`getcontext` function::

   >>> getcontext()
   Context(precision=53, rounding=RoundTiesToEven, emax=1073741823, emin=-1073741823, subnormalize=False)

To set the current context, use the :func:`setcontext` function, which
needs to be supplied with the context to be used.

:class:`Context` instances are *immutable*, so if you want to change
the precision or rounding mode, you first need to generate a new
:class:`Context` instance with the desired settings.  The easiest way
to do this is to start with an existing Context object::

   >>> mycontext = DefaultContext(precision=200)

The current context can then be set using the :func:`setcontext` function::

   >>> setcontext(mycontext)

And now all operations will produce a result with 200 bits of precision::

   >>> sqrt(2)
   BigFloat.exact('1.4142135623730950488016887242096980785696718753769480731766796', precision=200)

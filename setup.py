from distutils.core import setup
setup(name='bigfloat',
      version='0.1',
      description='Arbitrary precision correctly-rounded floating point arithmetic, via MPFR',
      long_description=

"""The bigfloat module provides a Python wrapper for the MPFR library.
The MPFR library is a well-known, well-tested C library for
arbitrary-precision binary floating point reliable arithmetic; it's
already used by a wide variety of projects, including GCC and SAGE.
It gives precise control over rounding modes and precisions, and
guaranteed reproducible and portable results.  You'll need to have the
MPFR and GMP libraries already installed on your system to use this
module.

Features:

 - the main 'BigFloat' type interacts well with Python integers and
   floats.

 - support for emulating IEEE 754 arithmetic in any of the IEEE binary
   interchange formats described in IEEE 754-2008.


""",
      author='Mark Dickinson',
      author_email='dickinsm@gmail.com',
      url='http://www.mpfr.org',
      packages=['bigfloat'],
      )

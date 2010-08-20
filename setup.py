from distutils.core import setup
from distutils.command.build import build
from distutils.command.install import install
from distutils.command.install_lib import install_lib
from distutils.cmd import Command
from distutils import log
import distutils.sysconfig
import distutils.ccompiler
import os.path
import sys
import platform

DESCRIPTION="""\
Arbitrary precision correctly-rounded floating point arithmetic, via MPFR.\
"""

LONG_DESCRIPTION="""\
The bigfloat package is a Python package providing arbitrary-precision
correctly-rounded floating-point arithmetic.  It is implemented as a
wrapper around the MPFR library (http://www.mpfr.org).

Features:

 - correct rounding on all operations;  precisely defined semantics
   compatible with the IEEE 754-2008 standard.

 - the BigFloat type interacts well with Python integers and floats.

 - full support for emulating IEEE 754 arithmetic in any of the IEEE binary
   interchange formats described in IEEE 754-2008.  Infinities, NaNs,
   signed zeros, and subnormals are all supported.

 - easy control of rounding modes and precisions, via Python's 'with'
   statement.

For current documentation, see:

   http://packages.python.org/bigfloat/


"""

def main():

    setup(
        name='bigfloat',
        version='0.2',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Mark Dickinson',
        author_email='dickinsm@gmail.com',
        url='http://bitbucket.org/dickinsm/bigfloat',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Mathematics',
            ],
        platforms = [
            'Linux',
            'OS X',
            ],
        license = 'GNU Library or Lesser General Public License (LGPL)',
        packages=[
            'bigfloat',
            'bigfloat.test',
            'bigfloat.examples',
            ],
        package_data={'bigfloat': [
                'docs/*.html',
                'docs/*.inv',
                'docs/*.js',
                'docs/_sources/*',
                'docs/_static/*',
                ]},
        )

if __name__ == "__main__":
    main()


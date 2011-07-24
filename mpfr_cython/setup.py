# Use:  python setup.py build_ext --inplace

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension(
            "bigfloat.mpfr",
            ["bigfloat/mpfr.pyx"],
            include_dirs = [
                'bigfloat',
                # FIXME: replace with something more general.
                '/opt/local/include',
            ],
            libraries = [
                'mpfr', 'gmp',
            ],
        ),
    ],
)

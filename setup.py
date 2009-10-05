from distutils.core import setup
from distutils.command.build import build
import distutils.ccompiler
import os.path
import sys

DESCRIPTION="""\
Arbitrary precision correctly-rounded floating point arithmetic, via MPFR.\
"""

LONG_DESCRIPTION="""\
The bigfloat module provides a Python wrapper for the MPFR library.
The MPFR library is a well-known, well-tested C library for
arbitrary-precision binary floating point reliable arithmetic; it's
already used by a wide variety of projects, including GCC and SAGE.
It gives precise control over rounding modes and precisions, and
guaranteed reproducible and portable results.  You'll need to have the
MPFR and GMP libraries already installed on your system to use this
module.

Features:

 - correct rounding on all operations;  precisely defined semantics
   compatible with the IEEE 754-2008 standard.

 - the main 'BigFloat' type interacts well with Python integers and
   floats.

 - full support for emulating IEEE 754 arithmetic in any of the IEEE binary
   interchange formats described in IEEE 754-2008.  Infinities, NaNs,
   signed zeros, and subnormals are all supported.
"""


def find_library_file(dirs, libname):
    """Locate the library file for a particular library."""
    # make use of distutils' knowledge of library file extensions
    cc = distutils.ccompiler.new_compiler()
    lib = cc.find_library_file(dirs, libname)
    if lib is None:
        raise ValueError("Unable to locate %s library" % libname)
    return lib

def find_include_file(dirs, libname):
    """Locate the include file for a particular library."""
    includename = libname + '.h'
    for dir in dirs:
        include = os.path.join(dir, includename)
        if os.path.exists(include):
            return include
    # failed to find include file
    raise ValueError("Unable to locate include file for %s library" % libname)


# the main job of this class is to create the configuration file,
# including the locations of the libraries and include files.

class BigFloatBuild(build):
    def run(self):

        library_dirs = ['/usr/local/lib', '/usr/lib']
        include_dirs = ['/usr/local/include', '/usr/include']

        if sys.platform == "darwin":
            # fink directories
            library_dirs.append('/sw/lib')
            include_dirs.append('/sw/include')
            # macports directories
            library_dirs.append('/opt/local/lib')
            include_dirs.append('/opt/local/include')

        # directories from prefix
        #prefix = sysconfig.get_config_var('prefix')
        #if prefix:
        #    library_dirs.append(os.path.join(prefix, 'lib'))
        #    include_dirs.append(os.path.join(prefix, 'include'))

        # standard locations
        library_dirs.append('/usr/local/lib')
        include_dirs.append('/usr/local/include')
        library_dirs.append('/usr/lib')
        include_dirs.append('/usr/include')

        mpfr_lib = find_library_file(library_dirs, 'mpfr')

        # don't actually need the location of the gmp library,
        # though we may in the future
        #gmp_lib = find_library_file(library_dirs, 'gmp')

        # We don't actually need the include files right now
        #mpfr_include = find_include_file(include_dirs, 'mpfr')
        #gmp_include = find_include_file(include_dirs, 'gmp')

        print mpfr_lib

        # now need to put this info into the configuration file, somehow.
        # and include the configuration file in the files to copy...

        # we're effectively imitating the build_scripts command,
        # which also needs to copy and edit

        # first we need to get the build_dir;  let's use the build-temp
        # directory for this

        # name of config file
        config = 'bigfloat_config.py.in'
        self.mkpath(self.build_temp)
        outfile = os.path.join(self.build_temp, 'bigfloat_config.py')
        outf = open(outfile, 'w')

        f = open(config, 'r')
        for line in f:
            if '$(MPFR_LIB_LOC)' in line:
                line = line.replace('$(MPFR_LIB_LOC)', mpfr_lib)
            outf.write(line)
        outf.close()



def main():

    setup(name='bigfloat',
          version='0.1',
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author='Mark Dickinson',
          author_email='dickinsm@gmail.com',
          url='http://www.mpfr.org',
          packages=['bigfloat'],

          # Build info
          cmdclass = {'build':BigFloatBuild},
          )

if __name__ == "__main__":
    main()


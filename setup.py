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

def create_config(infile, outfile, replacement_dict):
    # make substitutions in config file
    outf = open(outfile, 'w')
    for line in open(infile, 'r'):
        if not line.startswith('#'):
            for k, v in replacement_dict.items():
                if k in line:
                    line = line.replace(k, repr(v))
        outf.write(line)
    outf.close()

class build_config(Command):
    description = "build config file (copy and make substitutions)"

    user_options = [
        ('build-dir=', 'd', 'directory to build in'),
        ]

    def initialize_options(self):
        self.build_dir = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_dir'))

    def run(self):
        # determine where to look for library files
        library_dirs = []
        if sys.platform == "darwin":
            # fink directory
            library_dirs.append('/sw/lib')
            # macports directory
            library_dirs.append('/opt/local/lib')

        # directory from prefix
        prefix = distutils.sysconfig.get_config_var('prefix')
        if prefix:
            library_dirs.append(os.path.join(prefix, 'lib'))

        # standard locations
        if platform.architecture()[0] == '64bit':
            library_dirs.extend(['/usr/local/lib64', '/usr/lib64'])
        else:
            library_dirs.extend(['/usr/local/lib32', '/usr/lib32'])

        library_dirs.append('/usr/local/lib')
        library_dirs.append('/usr/lib')

        # find mpfr library file
        mpfr_lib = find_library_file(library_dirs, 'mpfr')
        log.info("found MPFR library at '%s'", mpfr_lib)

        # write config file
        config_in = 'bigfloat/bigfloat_config.py.in'
        config_out = 'bigfloat/bigfloat_config.py'
        log.info("creating '%s' from '%s'", config_out, config_in)
        create_config(config_in, config_out, {'$(MPFR_LIB_LOC)': mpfr_lib})

class BigFloatBuild(build):
    sub_commands = build.sub_commands
    sub_commands.insert(0, ('build_config', lambda self:True))

class BigFloatInstallLib(install_lib):
    def build(self):
        install_lib.build(self)
        if not self.skip_build:
            self.run_command('build_config')

def main():

    setup(
        name='bigfloat',
        version='0.1.2',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Mark Dickinson',
        author_email='dickinsm@gmail.com',
        url='http://bitbucket.org/dickinsm/bigfloat',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: Academic Free License (AFL)',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Mathematics',
            ],
        platforms = [
            'Linux',
            'OS X',
            ],
        license = 'Academic Free License (AFL)',
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

        # Build info
        cmdclass = {
            'build':BigFloatBuild,
            'build_config':build_config,
            'install_lib':BigFloatInstallLib,
            },
        )

if __name__ == "__main__":
    main()


Prerequisites
-------------

This package requires Python 2.6 or later.  The `MPFR <mpfr library_>`_ and
`GMP <gmp library_>`_ libraries will need to be already installed on your
system, along with any necessary development headers for both of those
libraries.  On Linux, look for a package named something like ``libmpfr-dev``
or ``mpfr-devel``, along with similarly named packages for GMP.


Installation from a release tarball
-----------------------------------

The instructions cover installation from either a repository clone,
or a source distribution tarball.  After cloning the repository
or unpacking the tarball, you should have a top-level directory
named something like ``bigfloat-0.3.0``.

(1) Enter that top-level directory and execute the command::

        python setup.py install

    For a site-wide installation, you many need to be become superuser, or use
    the ``sudo`` command. You can also build and install in two separate
    steps::

        python setup.py build_ext
        sudo python setup.py install

    For this to work, the MPFR and GMP libraries must already be installed
    on your system, complete with any necessary header files.  If the libraries
    or include files are found in an unusual place, you many need to modify
    environment variables so that the setup command can find the necessary
    header files.

    An example: on OS X 10.9, using the system Python but with MPFR and GMP
    installed in /opt/local (e.g., by MacPorts), one can do::

        $ sudo LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py install

    Alternatively, the include and library directories can be supplied to the
    build_ext command::

        $ python setup.py build_ext -I /opt/local/include -L/opt/local/lib
        $ sudo python setup.py install

(2) (Optional) Test the installation by doing::

      $ python -m unittest discover bigfloat

    Note that test discovery requires Python >= 2.7.  If you're on Python 2.6,
    you can use the `unittest2`_ package instead.  For example::

      $ unit2-2.6 discover bigfloat

(3) To check that everything's working, compute the square root of 2 to 1000
    bits of precision::

        >>> from bigfloat import precision, sqrt
        >>> with precision(200):
        ...     print(sqrt(2))
        ...
        1.4142135623730950488016887242096980785696718753769480731766796

If installation was successful, the ``bigfloat-0.3.0`` directory that you
created can now be deleted.


.. _gmp library: http://gmplib.org
.. _mpfr library: http://www.mpfr.org
.. _unittest2: http://pypi.python.org/pypi/unittest2

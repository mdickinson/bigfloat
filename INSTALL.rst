Prerequisites
-------------

This package requires Python 2.6 or later.  The `MPFR <mpfr library_>`_ and
`GMP <gmp library_>`_ libraries will need to be already installed on your
system, along with any necessary development headers for both of those
libraries.  On Linux, look for a package named something like ``libmpfr-dev``
or ``mpfr-devel``, and corresponding packages for GMP.


Installation from a repository clone
------------------------------------

(1) Clone the GitHub repository with::

      $ git clone https://github.com/mdickinson/bigfloat.git

(2) Enter the top-level directory and use ``python setup.py install`` to
    install, adding paths to the GMP and MPFR include and library files if
    necessary.  Depending on your Python installation, you may need superuser
    privileges.  On my OS X setup, MPFR and GMP are installed in /opt/local
    (via MacPorts) and the following works::

      $ cd bigfloat
      $ sudo LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py install

(3) (Optional) Test the installation::

      $ python -m unittest discover bigfloat

    Note that test discovery requires Python >= 2.7.  If you're on Python 2.6,
    you can use the `unittest2`_ package instead.  For example::

      $ unit2-2.6 discover bigfloat

(4) To check that everything's working, compute the square root of 2 to 1000
    bits of precision::

        >>> from bigfloat import sqrt, precision
        >>> with precision(1000):
        ...     x = sqrt(2)
        ...
        >>> print(x)
        1.414213562373095048801688724209698078569...

To test without installing in Python's site-packages directory::

    $ LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py build_ext --inplace
    $ python -m unittest discover -v .



Installation from a distribution tarball
----------------------------------------

We'll assume that you've downloaded a tarball whose name is something like
``bigfloat-0.3.0a3.tar.gz``.  The exact version number may differ; just
substitute the real version number everywhere that ``0.3.0a3`` appears in what
follows.

(1) Unpack the tarball with something like::

        tar -zxvf bigfloat-0.3.0a3.tar.gz

    This should create a directory ``bigfloat-0.3.0a3`` containing a
    ``setup.py`` script and the rest of the bigfloat source.

(2) Enter the created directory, and execute the command::

        python setup.py install

    from the ``bigfloat-0.3.0a3`` directory.  For a site-wide installation, you
    may need to become superuser, or use the 'sudo' command.  You can also
    build and install in two separate steps::

        python setup.py build
        sudo python setup.py install

    For this to work, the MPFR and GMP libraries must already be installed on
    your system (complete with any necessary header files: on Linux, look for a
    packages called 'mpfr-devel' and 'gmp-devel').  If the libraries or include
    files are found in an unusual place, you may need to modify environment
    variables so that the setup command can find the necessary header files.

    An example: on Mac OS X, using the system Python, but with MPFR and GMP
    installed in /opt/local (e.g., by MacPorts), one can do::

        LIBRARY_PATH=/opt/local/lib CPATH=/opt/local/include python setup.py build

    Alternatively, the include and library directories can be supplied to the
    build_ext command::

        python setup.py build_ext -I /opt/local/include -L/opt/local/lib

(3) (Optional).  Test the installation by doing::

      python -m bigfloat.test.test_bigfloat

If installation was successful, the ``bigfloat-0.3.0a3`` directory that you
created can now be deleted.


.. _gmp library: http://gmplib.org
.. _mpfr library: http://www.mpfr.org
.. _unittest2: http://pypi.python.org/pypi/unittest2

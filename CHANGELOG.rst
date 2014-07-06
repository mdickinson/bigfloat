What's new in bigfloat 0.3.0?
=============================

Library
-------

- Fix string-returning functions and string constants in ``mpfr`` module to
  return something of type ``str`` both on Python 2 and Python 3.  In earlier
  0.3.0 pre-releases, objects of type ``unicode`` were being returned on
  Python 2.

- Declarations in ``cmpfr.pxd`` fixed to include ``const`` where necessary;
  this fixes some compiler warnings.

- Improved tests for hashing.


Miscellaneous
-------------

- Fix documentation link for PyPI upload.

- Docs updated to remove outdated instructions about use under Python 2.5 and
  outdated information (dating from the earlier ctypes version) about runtime
  location of the MPFR and GMP libraries.

- ``README``, ``setup.py`` updates: include the quick tour in the ``README``,
  make content match that of the ``setup.py`` long description.

- ``CHANGELOG``, ``README``, ``INSTALL`` files updated with various
  reStructuredText fixes; renamed to add ``.rst`` suffix so that they display
  nicely on GitHub.

- Update copyright notices.


What's new in bigfloat 0.3.0b1?
===============================

Library
-------

- Python 3.2 and later are now supported.  Python 2 support requires Python 2.6
  or later.

- Added support for the new 'divide-by-zero' flag (exposed as ``ZeroDivision``
  to bigfloat).

Miscellaneous
-------------

- Development moved from bitbucket (https://bitbucket.org/dickinsm/bigfloat)
  to GitHub (https://github.com/mdickinson/bigfloat), and repository
  converted from mercurial to Git.

- Travis CI and Read the Docs GitHub hooks added.


What's new in bigfloat 0.3.0a2?
===============================

- Minor documentation fixes.


What's new in bigfloat 0.3.0a1?
===============================


Prerequisites
-------------

- For now, Python 2.7 and MPFR version >= 3.0 are required.  Support for
  earlier versions of Python is planned.  Support for MPFR 2.x will probably
  not be added.


Library
-------

- Major rewrite and restructuring of the core code.  The core now uses Cython
  rather than ctypes.

- mpfr module now separately available as an extension type, with semantics
  very close to the Mpfr library.

- Added bigfloat support for new rounding mode MPFR_RNDA (round away from
  zero).

- Rounding modes are now represented as named integers (instances of
  RoundingMode, an int subclass), rather than strings.  This allows them to be
  passed directly to Mpfr functions.

- Fixed a bug that meant old context wasn't restored when changing exponents
  with one valid exponent and one invalid. (eminmax)

- Many more docstrings than originally; better function signatures.

- Restructured bigfloat package: mpfr wrapper module is now bigfloat.mpfr,
  context class and related functions are in bigfloat.context, rounding modes
  are defined in bigfloat.rounding_modes, and the main BigFloat type is defined
  in bigfloat.core.  Everything is importable directory from bigfloat, as
  before.


Documentation
-------------

- Most of the documentation is now generated automatically using Sphinx's
  autodoc extension.


What's new in bigfloat 0.2.1?
=============================

Library
-------

- Simplify weakref callback scheme used to ensure BigFloat instances
  are freed properly.

- Make sure all python files in distribution have the LGPL header.


What's new in bigfloat 0.2?
===========================

Library
-------

- The setup.py file no longer attempts to locate the MPFR library at
  install time.  The configuration file still exists, and can be edited
  to give a hard-coded location.  Alternatively, ctypes should find the
  library if it's within the usual library search paths.  (If not, it
  might be necessary to set LD_LIBRARY_PATH or DYLD_LIBRARY_PATH.)

- Use a weakref callback to ensure ``mpfr_clear`` gets called, instead of
  relying on ``__del__``.

- Make bigfloat compatible with versions of MPFR as far back as MPFR 2.3.0

- Relicense under LGPL, since this package might be considered a
  derived work of MPFR.


Tests
-----

- Skip the hashing consistency tests (those that test whether ``hash(n) ==
  hash(BigFloat(n))`` for integers ``n``) on Python 2.5.  In rare cases, this
  equality fails with Python 2.5, and this is awkward to fix.  If this affects
  you, upgrade to Python 2.6 or avoid mixing BigFloat instances with ints in
  sets or dictionary keys.


What's new in bigfloat 0.1.2?
=============================

Library
-------

- Make ``Context`` objects hashable.

Documentation
-------------

- Add 'where to get it' section to the documentation, pointing both
  to the PyPI page and the bitbucket source.

- Expand installation information in documentation.

Packaging/distribution
----------------------

- Include html documentation in distribution, in docs directory.

- Include INSTALL and CHANGELOG files in distribution.

- Make sure the bigfloat_config.py file ends up in the top-level
  package directory.

- Add /usr/lib{32,64} and /usr/local/lib{32,64} to default search
  paths in setup.py.

Preparing a release
===================

Notes on creating a release.  These notes apply my own system, currently OS X
10.9, with mpfr and gmp installed via MacPorts.

0. Make sure that you have a clean and up-to-date source tree.

1. Create a release branch::

      git checkout release/0.4.0

2. Update version numbers if necessary.  Places that need to be updated
   include::

      docs/conf.py ('version' and 'release' keys)
      setup.py ('version')

   You might also look at:

   * ``CHANGELOG.rst``
   * ``INSTALL.rst``
   * ``RELEASING.rst`` (this document).

3. Create a test release with ``python setup.py sdist``; copy the generated
   tarball and check that it's possible to install from it.  Run tests.

4. When satisfied, tag the release::

      git tag -a v0.4.0

5. Upload the release to PyPI.  Register first if necessary::

      python setup.py sdist upload

   If you don't have PyPI details registered in ~/.pypirc, this may fail; in
   that case you'll need to reissue the 'python setup.py sdist upload' command
   in the form::

      python setup.py sdist register upload

   Make sure you answer "y" to the "Save your login (y/N)" prompt!

6. Update tags on ReadTheDocs.

7. Building docs to upload to PyPI.  In the docs directory, do::

       make html
       cd build/html
       zip -r bigfloat_docs.zip *
       mv -i bigfloat_docs.zip ~/Desktop

   Now you can go to::

       http://pypi.python.org/pypi?%3Aaction=pkg_edit&name=bigfloat

   and upload the documentation from there.  The documentation is uploaded
   to http://pythonhosted.org/bigfloat.


Post-release
============

0. Merge the release branch back into master.

1. Bump version number again.

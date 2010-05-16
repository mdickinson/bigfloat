# Use Python 2.7 to build distribution, to take advantage of
# various distutils bugfixes.
PYTHON=python2.7
SPHINXBUILD=sphinx-build-2.6

DOCSRC=bigfloat/doc
DOCDIR=bigfloat/docs

.PHONY: build clean doc dist install

build: doc
	$(PYTHON) setup.py build

clean:
	-rm -fr $(DOCSRC)/_build/
	-rm -fr $(DOCDIR)
	-rm -fr build/
	-rm -fr dist/
	-rm -fr bigfloat/*.pyc
	-rm -fr bigfloat/examples/*.pyc
	-rm -fr bigfloat/test/*.pyc
	-rm MANIFEST
	find . -name \*~ -exec rm {} \;

doc: $(DOCDIR)

dist: doc
	$(PYTHON) setup.py sdist

install: build
	$(PYTHON) setup.py install

$(DOCDIR): $(DOCSRC)/index.rst
	cd $(DOCSRC) && $(MAKE) SPHINXBUILD=$(SPHINXBUILD) html
	-rm -fr $(DOCDIR)
	mv $(DOCSRC)/_build/html/ $(DOCDIR)

PYTHON=python2.7

.PHONY: build clean dist install test upload

build: doc
	$(PYTHON) setup.py build

clean:
	-rm -fr build/
	-rm -fr dist/
	-rm MANIFEST
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.orig -exec rm {} \;
	find -d . -type d -empty -exec rmdir {} \;

doc: $(DOCDIR)

dist: doc
	$(PYTHON) setup.py sdist

install: build
	$(PYTHON) setup.py install

upload: doc
	$(PYTHON) setup.py sdist upload

test: build
	$(PYTHON) runtests.py

$(DOCDIR): $(DOCSRC)/index.rst
	cd $(DOCSRC) && $(MAKE) SPHINXBUILD=$(SPHINXBUILD) html
	-rm -fr $(DOCDIR)
	mv $(DOCSRC)/_build/html/ $(DOCDIR)

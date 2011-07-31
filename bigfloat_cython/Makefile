PYTHON=python

.PHONY: build clean develop dist html install pdf test upload

src/mpfr.c: src/mpfr.pyx src/cgmp.pxd src/cmpfr.pxd
	cython -v $< -o $@

build: src/mpfr.c
	$(PYTHON) setup.py build

clean:
	-rm -r build/
	-rm -r dist/
	-rm -r docs/_build
	-rm MANIFEST
	-rm src/mpfr.c
	-rm bigfloat/mpfr.so
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.orig -exec rm {} \;
	find -d . -type d -empty -exec rmdir {} \;

# in-place build
develop: src/mpfr.c
	$(PYTHON) setup.py build_ext --inplace

dist: src/mpfr.c
	$(PYTHON) setup.py sdist

html:
	cd docs && $(MAKE) html


install: build
	$(PYTHON) setup.py install

pdf:
	cd docs && $(MAKE) latex
	cd docs/_build/latex && $(MAKE)

test: develop
	$(PYTHON) -m bigfloat.test.test_bigfloat
	$(PYTHON) -m bigfloat.test.test_context
	$(PYTHON) -m bigfloat.test.test_mpfr
	$(PYTHON) -m bigfloat.test.test_rounding_mode

upload: src/mpfr.c
	$(PYTHON) setup.py sdist upload

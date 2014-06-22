PYTHON=python3.4

.PHONY: build build_all clean develop dist html install pdf test upload

build: src/mpfr.c
	$(PYTHON) setup.py build

build_all: build html pdf
	mkdir -p bigfloat/docs
	cp -a docs/_build/html bigfloat/docs
	mkdir -p bigfloat/docs/pdf
	cp docs/_build/latex/BigFloat.pdf bigfloat/docs/pdf/

clean:
	-rm -r build/
	-rm -r dist/
	-rm -r docs/_build
	-rm -r bigfloat/docs
	-rm MANIFEST
	-rm src/mpfr.c
	-rm bigfloat/mpfr.so
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.orig -exec rm {} \;
	find -d . -type d -empty -exec rmdir {} \;

# in-place build
develop: src/mpfr.c
	$(PYTHON) setup.py build_ext --inplace

dist: build_all
	$(PYTHON) setup.py sdist

html: develop docs/_build/html/index.html

install: build_all
	$(PYTHON) setup.py install

pdf: develop docs/_build/latex/BigFloat.pdf

test: develop
	$(PYTHON) -m bigfloat.test.test___all__
	$(PYTHON) -m bigfloat.test.test_bigfloat
	$(PYTHON) -m bigfloat.test.test_context
	$(PYTHON) -m bigfloat.test.test_mpfr
	$(PYTHON) -m bigfloat.test.test_rounding_mode

upload: build_all
	$(PYTHON) setup.py sdist upload

src/mpfr.c: src/mpfr.pyx src/cgmp.pxd src/cmpfr.pxd
	cython -v $< -o $@

docs/_build/html/index.html: docs/index.rst
	cd docs && $(MAKE) html

docs/_build/latex/BigFloat.pdf: docs/index.rst
	cd docs && $(MAKE) latex
	cd docs/_build/latex && $(MAKE)

from fabric.api import local, lcd

# Default choice for Python executable
PYTHON = "python"
COVERAGE = "coverage"

# Unittest 2 runner for Python 2.6.
UNIT2 = "unit2-2.6"

# Paths for mpfr and gmp libraries and include files.
LIBRARY_PATH = "/opt/local/lib"
INCLUDE_PATH = "/opt/local/include"


def build(python=PYTHON):
    """Build the bigfloat library for in-place testing."""
    clean()
    local(
        "LIBRARY_PATH={library_path} CPATH={include_path} {python} "
        "setup.py build_ext --inplace".format(
            library_path=LIBRARY_PATH,
            include_path=INCLUDE_PATH,
            python=python,
        ))


def install(python=PYTHON):
    """Install into site-packages"""
    local(
        "LIBRARY_PATH={library_path} CPATH={include_path} {python} "
        "setup.py build".format(
            library_path=LIBRARY_PATH,
            include_path=INCLUDE_PATH,
            python=python,
        ))
    local("sudo {python} setup.py install".format(python=python))


def uninstall(python=PYTHON):
    """Uninstall from site-packages"""
    site_packages = local(
        "{python} -c 'from distutils.sysconfig import "
        "get_python_lib; print(get_python_lib())'".format(python=python),
        capture=True,
    )
    with lcd(site_packages):
        local("sudo rm mpfr.so")
        local("sudo rm -fr bigfloat")
        local("sudo rm bigfloat*.egg-info")


def clean():
    """Remove build artifacts."""
    local("git clean -fdX")


def run_tests(python=PYTHON):
    if python == "python2.6":
        unittest = UNIT2
    else:
        unittest = "{python} -m unittest".format(python=python)
    local("{unittest} discover -v .".format(unittest=unittest))


def test(python=PYTHON):
    """Run tests on a single version of Python."""
    build(python=python)
    run_tests(python=python)


def coverage(coverage=COVERAGE):
    local("{coverage} run -m unittest discover -v .".format(coverage=coverage))
    local("{coverage} html".format(coverage=coverage))


def html():
    """Build html documentation."""
    clean()
    with lcd("docs"):
        local("make html")


def pdf():
    """Build PDF documentation."""
    clean()
    with lcd("docs"):
        local("make latexpdf")


def docs(python=PYTHON):
    """Build PDF and html documentation."""
    html()
    pdf()


def test_all():
    """Run tests on Python versions 2.6 through 3.4."""
    test(python="python2.6")
    test(python="python2.7")
    test(python="python3.2")
    test(python="python3.3")
    test(python="python3.4")

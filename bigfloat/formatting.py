"""
Helper functions for formatting.

"""
import re


# Regular expression matching valid format specifiers.
_parse_format_specifier_regex = re.compile(r"""\A
(?P<sign>[-+ ])?
(?P<alternate>\#)?
(?P<zeropad>0)?
(?P<minimumwidth>[1-9][0-9]*)?
(?:(?P<dot>\.)(?P<precision>[0-9]*))?
(?P<type>[aAbfF])?
\Z""", re.VERBOSE)


def parse_format_specifier(specification):
    """
    Parse the given format specification and return a dictionary
    containing relevant values.

    """
    m = _parse_format_specifier_regex.match(specification)
    if m is None:
        raise ValueError("Invalid format specifier: {!r}".format(specification))
    return m.groupdict('')

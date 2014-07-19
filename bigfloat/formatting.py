"""
Helper functions for formatting.

"""
import re


# Regular expression matching valid format specifiers.
_parse_format_specifier_regex = re.compile(r"""\A
(?:
   (?P<fill>.)?
   (?P<align>[<>=^])
)?
(?P<sign>[-+ ])?
(?P<alternate>\#)?
(?P<zeropad>0)?
(?P<minimumwidth>[0-9]*)
(?:(?P<dot>\.)(?P<precision>[0-9]*))?
(?P<type>[aAbeEfFgG])?
\Z""", re.VERBOSE|re.DOTALL)


def parse_format_specifier(specification):
    """
    Parse the given format specification and return a dictionary
    containing relevant values.

    """
    m = _parse_format_specifier_regex.match(specification)
    if m is None:
        raise ValueError("Invalid format specifier: {!r}".format(specification))
    format_dict = m.groupdict('')

    # Convert zero-padding into fill and alignment.
    zeropad = format_dict.pop('zeropad')
    if zeropad:
        # If zero padding is requested, fill and align fields should be absent.
        if format_dict['align']:
            raise ValueError("Invalid format specifier: {!r}".format(specification))
        # Impossible to have 'fill' without 'align'.
        assert not format_dict['fill']
        format_dict['align'] = '='
        format_dict['fill'] = '0'

    # Default alignment is right-aligned.
    if not format_dict['align']:
        format_dict['align'] = '>'

    # Default fill character is space.
    if not format_dict['fill']:
        format_dict['fill'] = ' '

    # Default sign is '-'.
    if not format_dict['sign']:
        format_dict['sign'] = '-'

    # Convert minimum width to an int; default is zero.
    format_dict['minimumwidth'] = int(format_dict['minimumwidth'] or '0')

    return format_dict

# Copyright 2009--2019 Mark Dickinson.
#
# This file is part of the bigfloat package.
#
# The bigfloat package is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat package.  If not, see <http://www.gnu.org/licenses/>.
"""
Helper functions for formatting.

"""
import re

from bigfloat.rounding_mode import (
    ROUND_TIES_TO_EVEN,
    ROUND_TOWARD_ZERO,
    ROUND_TOWARD_POSITIVE,
    ROUND_TOWARD_NEGATIVE,
    ROUND_AWAY_FROM_ZERO,
)

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
(?P<precision>\.[0-9]+)?
(?P<rounding>[UDYZN])?
(?P<type>[aAbeEfFgG%])?
\Z""", re.VERBOSE | re.DOTALL)


rounding_mode_from_specifier = {
    'U': ROUND_TOWARD_POSITIVE,
    'D': ROUND_TOWARD_NEGATIVE,
    'Y': ROUND_AWAY_FROM_ZERO,
    'Z': ROUND_TOWARD_ZERO,
    'N': ROUND_TIES_TO_EVEN,
}


def parse_format_specifier(specification):
    """
    Parse the given format specification and return a dictionary
    containing relevant values.

    """
    m = _parse_format_specifier_regex.match(specification)
    if m is None:
        raise ValueError(
            "Invalid format specifier: {!r}".format(specification))
    format_dict = m.groupdict('')

    # Convert zero-padding into fill and alignment.
    zeropad = format_dict.pop('zeropad')
    if zeropad:
        # If zero padding is requested, fill and align fields should be absent.
        if format_dict['align']:
            raise ValueError(
                "Invalid format specifier: {!r}".format(specification))
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

    # Convert precision to an int, or `None` if no precision given.
    if format_dict['precision']:
        format_dict['precision'] = int(format_dict['precision'][1:])
    else:
        format_dict['precision'] = None

    # If no rounding mode is given, assume 'N'.
    if not format_dict['rounding']:
        format_dict['rounding'] = 'N'

    return format_dict


def format_align(sign, body, spec):
    """Given an unpadded, non-aligned numeric string 'body' and sign
    string 'sign', add padding and alignment conforming to the given
    format specifier dictionary 'spec' (as produced by
    parse_format_specifier).

    """
    padding = spec['fill'] * (spec['minimumwidth'] - len(sign) - len(body))
    align = spec['align']
    if align == '<':
        result = sign + body + padding
    elif align == '>':
        result = padding + sign + body
    elif align == '=':
        result = sign + padding + body
    elif align == '^':
        half = len(padding)//2
        result = padding[:half] + sign + body + padding[half:]
    else:
        raise ValueError("Unrecognised alignment field: {!r}".format(align))

    return result

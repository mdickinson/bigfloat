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

import unittest

from bigfloat import (
    BigFloat,
    double_precision,
    RoundTiesToEven,
    getcontext,
    setcontext,
)


DefaultTestContext = double_precision + RoundTiesToEven


class TestFormatting(unittest.TestCase):
    def setUp(self):
        self._original_context = getcontext()
        setcontext(DefaultTestContext)

    def tearDown(self):
        setcontext(self._original_context)
        del self._original_context

    def test_format(self):
        # Fixed precision formatting.
        test_triples = [
            (BigFloat(2), ".6f", "2.000000"),
            # 'F' behaves the same as 'f' except for infinities and nans.
            (BigFloat(2), ".6F", "2.000000"),
            # Extra zeros in the precision should be fine.
            (BigFloat(2), ".06f", "2.000000"),
            (BigFloat(2), ".5f", "2.00000"),
            # . only retained with 'alternate' formatting
            (BigFloat(2), ".0f", "2"),
            # Default precision is 6.
            (BigFloat(2), "f", "2.000000"),
            (BigFloat('nan'), "f", "nan"),
            (BigFloat('-nan'), "f", "nan"),
            (BigFloat('inf'), "f", "inf"),
            (BigFloat('-inf'), "f", "-inf"),
            (BigFloat('nan'), "F", "NAN"),
            (BigFloat('-nan'), "F", "NAN"),
            (BigFloat('inf'), "F", "INF"),
            (BigFloat('-inf'), "F", "-INF"),
            # Rounding behaviour.
            (BigFloat('3.1415926535'), ".6f", "3.141593"),
            (BigFloat('3.1415926535'), ".5f", "3.14159"),
            (BigFloat('3.1415926535'), ".4f", "3.1416"),
            (BigFloat('3.1415926535'), ".3f", "3.142"),
            (BigFloat('3.1415926535'), ".2f", "3.14"),
            (BigFloat('3.1415926535'), ".1f", "3.1"),
            (BigFloat('3.1415926535'), ".0f", "3"),
            # Sign specification.
            (BigFloat(+2), "+.3f", "+2.000"),
            (BigFloat(-2), "+.3f", "-2.000"),
            (BigFloat(+2), " .3f", " 2.000"),
            (BigFloat(-2), " .3f", "-2.000"),
            (BigFloat(+2), "-.3f", "2.000"),
            (BigFloat(-2), "-.3f", "-2.000"),
            (BigFloat(+2), ".3f", "2.000"),
            (BigFloat(-2), ".3f", "-2.000"),
            # With infinities and nans; note that MPFR doesn't include
            # these signs.
            (BigFloat('+inf'), "+.3f", "+inf"),
            (BigFloat('-inf'), "+.3f", "-inf"),
            (BigFloat('+nan'), "+.3f", "+nan"),
            (BigFloat('+inf'), "-.3f", "inf"),
            (BigFloat('-inf'), "-.3f", "-inf"),
            (BigFloat('+nan'), "-.3f", "nan"),
            (BigFloat('+inf'), " .3f", " inf"),
            (BigFloat('-inf'), " .3f", "-inf"),
            (BigFloat('+nan'), " .3f", " nan"),
            # Alternate formatting.
            (BigFloat(2), "#.0f", "2."),
            (BigFloat(2), "+#.0f", "+2."),
            # Minimum field width.
            (BigFloat(2), "10.3f", "     2.000"),
            (BigFloat(2), "6.3f", " 2.000"),
            (BigFloat(2), "5.3f", "2.000"),
            (BigFloat(2), "4.3f", "2.000"),
            (BigFloat(2), "1.3f", "2.000"),
            # Minimum field width in combination with sign.
            (BigFloat(2), "+10.3f", "    +2.000"),
            (BigFloat(-23), "+10.3f", "   -23.000"),
            # Zero padding.
            (BigFloat(2), "010.3f", "000002.000"),
            (BigFloat(2), "+010.3f", "+00002.000"),
            (BigFloat(2), " 010.3f", " 00002.000"),
            (BigFloat(2), "0010.3f", "000002.000"),
            # Alignment and filling.
            (BigFloat(2), "<10.3f", "2.000     "),
            (BigFloat(2), ">10.3f", "     2.000"),
            (BigFloat(2), "^10.3f", "  2.000   "),
            (BigFloat(2), "<10.2f", "2.00      "),
            (BigFloat(2), ">10.2f", "      2.00"),
            (BigFloat(2), "^10.2f", "   2.00   "),
            (BigFloat(2), "<4.2f", "2.00"),
            (BigFloat(2), ">4.2f", "2.00"),
            (BigFloat(2), "^4.2f", "2.00"),
            (BigFloat(2), "<3.2f", "2.00"),
            (BigFloat(2), ">3.2f", "2.00"),
            (BigFloat(2), "^3.2f", "2.00"),
            (BigFloat(2), "X<10.3f", "2.000XXXXX"),
            (BigFloat(2), "X>10.3f", "XXXXX2.000"),
            (BigFloat(2), "X^10.3f", "XX2.000XXX"),
            (BigFloat(2), "X<10.2f", "2.00XXXXXX"),
            (BigFloat(2), "X>10.2f", "XXXXXX2.00"),
            (BigFloat(2), "X^10.2f", "XXX2.00XXX"),
            (BigFloat(2), "X<4.2f", "2.00"),
            (BigFloat(2), "X>4.2f", "2.00"),
            (BigFloat(2), "X^4.2f", "2.00"),
            (BigFloat(2), "X<3.2f", "2.00"),
            (BigFloat(2), "X>3.2f", "2.00"),
            (BigFloat(2), "X^3.2f", "2.00"),
            (BigFloat(2), "X=+10.3f", "+XXXX2.000"),
            (BigFloat(2), " =+10.3f", "+    2.000"),
            (BigFloat(2), "0=+10.3f", "+00002.000"),
            (BigFloat(2), "\x00=+10.3f", "+\x00\x00\x00\x002.000"),
            (BigFloat(2), "\n=+10.3f", "+\n\n\n\n2.000"),

            # e-style formatting
            (BigFloat(2), ".6e", "2.000000e+00"),
            (BigFloat(3.141592653589793), ".6e", "3.141593e+00"),
            (BigFloat(3.141592653589793), ".6E", "3.141593E+00"),
            (BigFloat(314.1592653589793), ".6e", "3.141593e+02"),
            (BigFloat(314.1592653589793), ".6E", "3.141593E+02"),
            (BigFloat('nan'), "e", "nan"),
            (BigFloat('-nan'), "e", "nan"),
            (BigFloat('inf'), "e", "inf"),
            (BigFloat('-inf'), "e", "-inf"),
            (BigFloat('nan'), "E", "NAN"),
            (BigFloat('-nan'), "E", "NAN"),
            (BigFloat('inf'), "E", "INF"),
            (BigFloat('-inf'), "E", "-INF"),
            (BigFloat(314.1592653589793), ".0e", "3e+02"),
            (BigFloat(314.1592653589793), "#.0e", "3.e+02"),
            (BigFloat(314.1592653589793), "e", "3.1415926535897933e+02"),
            (BigFloat(314.1592653589793), "6e", "3.1415926535897933e+02"),

            # g-style formatting
            (BigFloat(3.141592653589793), ".7g", "3.141593"),
            (BigFloat(3.141592653589793), ".7G", "3.141593"),
            (BigFloat(314.1592653589793), ".7g", "314.1593"),
            (BigFloat(31415.92653589793), ".7g", "31415.93"),
            (BigFloat(3141592.653589793), ".7g", "3141593"),
            (BigFloat(3141592.653589793), ".7G", "3141593"),
            (BigFloat(31415926.53589793), ".7g", "3.141593e+07"),
            (BigFloat(31415926.53589793), ".7G", "3.141593E+07"),
            (BigFloat('nan'), "g", "nan"),
            (BigFloat('-nan'), "g", "nan"),
            (BigFloat('inf'), "g", "inf"),
            (BigFloat('-inf'), "g", "-inf"),
            (BigFloat('nan'), "G", "NAN"),
            (BigFloat('-nan'), "G", "NAN"),
            (BigFloat('inf'), "G", "INF"),
            (BigFloat('-inf'), "G", "-INF"),
            (BigFloat(314.1592653589793), ".0g", "3e+02"),
            (BigFloat(314.1592653589793), ".1g", "3e+02"),
            (BigFloat(314.1592653589793), "#.0g", "3.e+02"),
            (BigFloat(314.1592653589793), "#.1g", "3.e+02"),
            (BigFloat(314.1592653589793), "g", "314.159"),
            (BigFloat(314.1592653589793), "6g", "314.159"),
            # Trailing zeros are stripped, except in alternate style.
            (BigFloat(2), ".6g", "2"),
            (BigFloat(0.000023), ".6g", "2.3e-05"),
            (BigFloat(0.00023), ".6g", "0.00023"),
            (BigFloat(2.3), ".6g", "2.3"),
            (BigFloat(230), ".6g", "230"),
            (BigFloat(230000), ".6g", "230000"),
            (BigFloat(2300000), ".6g", "2.3e+06"),
            (BigFloat(2), "#.6g", "2.00000"),

            # %-formatting
            (BigFloat(3.141592653589793), ".2%", "314.16%"),
            (BigFloat(3.141592653589793), ".1%", "314.2%"),
            (BigFloat(3.141592653589793), ".0%", "314%"),
            (BigFloat(3.141592653589793), "%", "314.159265%"),
            (BigFloat(0.0234), ".3%", "2.340%"),
            (BigFloat(0.00234), ".3%", "0.234%"),
            (BigFloat(0.000234), ".3%", "0.023%"),
            (BigFloat(0.000234), ".3U%", "0.024%"),
            (BigFloat(0.0000234), ".3%", "0.002%"),
            (BigFloat(0.00000234), ".3%", "0.000%"),
            (BigFloat(0.00000234), ".3Y%", "0.001%"),
            (BigFloat(-3.141592653589793), ".2%", "-314.16%"),
            (BigFloat(-3.141592653589793), ".1%", "-314.2%"),
            (BigFloat(-3.141592653589793), ".0%", "-314%"),
            (BigFloat(-3.141592653589793), "%", "-314.159265%"),
            (BigFloat(-0.0234), ".3%", "-2.340%"),
            (BigFloat(-0.00234), ".3%", "-0.234%"),
            (BigFloat(-0.000234), ".3%", "-0.023%"),
            (BigFloat(-0.000234), ".3U%", "-0.023%"),
            (BigFloat(-0.0000234), ".3%", "-0.002%"),
            (BigFloat(-0.00000234), ".3%", "-0.000%"),
            (BigFloat(-0.00000234), ".3Y%", "-0.001%"),
            (BigFloat('0'), ".3%", "0.000%"),
            (BigFloat('-0'), ".3%", "-0.000%"),
            # We should see the '%' even on infinities and nans.
            (BigFloat('inf'), ".3%", "inf%"),
            (BigFloat('-inf'), ".3%", "-inf%"),
            (BigFloat('nan'), ".3%", "nan%"),
            (BigFloat('inf'), "+.3%", "+inf%"),
            (BigFloat('-inf'), "+.3%", "-inf%"),
            (BigFloat('nan'), "+.3%", "+nan%"),

            # Hexadecimal formatting.  It's not 100% clear how MPFR
            # chooses the exponent here.
            (BigFloat(1.5), ".6a", "0x1.800000p+0"),
            (BigFloat(1.5), ".5a", "0x1.80000p+0"),
            (BigFloat(1.5), ".1a", "0x1.8p+0"),
            (BigFloat(1.5), ".0a", "0xcp-3"),
            (BigFloat(1.5), ".6A", "0X1.800000P+0"),
            (BigFloat(3.0), ".6a", "0x3.000000p+0"),
            (BigFloat(3.141592653589793), ".6a", "0x3.243f6bp+0"),
            (BigFloat(3.141592653589793), ".5a", "0x3.243f7p+0"),
            (BigFloat(3.141592653589793), ".4a", "0x3.243fp+0"),
            (BigFloat(3.141592653589793), ".3a", "0x3.244p+0"),
            (BigFloat(3.141592653589793), ".2a", "0x3.24p+0"),
            (BigFloat(3.141592653589793), ".1a", "0x3.2p+0"),
            (BigFloat(3.141592653589793), ".0a", "0xdp-2"),
            # With no precision, outputs enough digits to give an
            # exact representation.
            (BigFloat(3.141592653589793), "a", "0x3.243f6a8885a3p+0"),
            (BigFloat(10.0), ".6a", "0xa.000000p+0"),
            (BigFloat(16.0), ".6a", "0x1.000000p+4"),
            (BigFloat('nan'), "a", "nan"),
            (BigFloat('-nan'), "a", "nan"),
            (BigFloat('inf'), "a", "inf"),
            (BigFloat('-inf'), "a", "-inf"),
            (BigFloat('nan'), "A", "NAN"),
            (BigFloat('-nan'), "A", "NAN"),
            (BigFloat('inf'), "A", "INF"),
            (BigFloat('-inf'), "A", "-INF"),

            # Binary formatting.
            (BigFloat('2.25'), "b", '1.001p+1'),
            (BigFloat('-2.25'), "b", '-1.001p+1'),
            (BigFloat('nan'), "b", 'nan'),
            (BigFloat('inf'), "b", "inf"),
            (BigFloat('-inf'), "b", "-inf"),

            # Rounding mode.

            # Round up.
            (BigFloat('-56.127'), ".2Uf", "-56.12"),
            (BigFloat('-56.125'), ".2Uf", "-56.12"),
            (BigFloat('-56.123'), ".2Uf", "-56.12"),
            (BigFloat('56.123'), ".2Uf", "56.13"),
            (BigFloat('56.125'), ".2Uf", "56.13"),
            (BigFloat('56.127'), ".2Uf", "56.13"),

            # Round down.
            (BigFloat('-56.127'), ".2Df", "-56.13"),
            (BigFloat('-56.125'), ".2Df", "-56.13"),
            (BigFloat('-56.123'), ".2Df", "-56.13"),
            (BigFloat('56.123'), ".2Df", "56.12"),
            (BigFloat('56.125'), ".2Df", "56.12"),
            (BigFloat('56.127'), ".2Df", "56.12"),

            # Round away from zero.
            (BigFloat('-56.127'), ".2Yf", "-56.13"),
            (BigFloat('-56.125'), ".2Yf", "-56.13"),
            (BigFloat('-56.123'), ".2Yf", "-56.13"),
            (BigFloat('56.123'), ".2Yf", "56.13"),
            (BigFloat('56.125'), ".2Yf", "56.13"),
            (BigFloat('56.127'), ".2Yf", "56.13"),

            # Round toward zero.
            (BigFloat('-56.127'), ".2Zf", "-56.12"),
            (BigFloat('-56.125'), ".2Zf", "-56.12"),
            (BigFloat('-56.123'), ".2Zf", "-56.12"),
            (BigFloat('56.123'), ".2Zf", "56.12"),
            (BigFloat('56.125'), ".2Zf", "56.12"),
            (BigFloat('56.127'), ".2Zf", "56.12"),

            # Round to nearest (ties to even).
            (BigFloat('-56.127'), ".2Nf", "-56.13"),
            (BigFloat('-56.125'), ".2Nf", "-56.12"),
            (BigFloat('-56.123'), ".2Nf", "-56.12"),
            (BigFloat('56.123'), ".2Nf", "56.12"),
            (BigFloat('56.125'), ".2Nf", "56.12"),
            (BigFloat('56.127'), ".2Nf", "56.13"),

            # Missing rounding mode implies round to nearest.
            (BigFloat('-56.127'), ".2f", "-56.13"),
            (BigFloat('-56.125'), ".2f", "-56.12"),
            (BigFloat('-56.123'), ".2f", "-56.12"),
            (BigFloat('56.123'), ".2f", "56.12"),
            (BigFloat('56.125'), ".2f", "56.12"),
            (BigFloat('56.127'), ".2f", "56.13"),

            # Missing type behaves like str formatting.
            (BigFloat('123'), ".0", "1e+02"),
            (BigFloat('123'), ".1", "1e+02"),
            (BigFloat('123'), ".2", "1.2e+02"),
            (BigFloat('123'), ".2U", "1.3e+02"),
            (BigFloat('123'), ".2D", "1.2e+02"),
            (BigFloat('123'), ".3", "123"),
            # 'alternate' flag is currently ignored.
            (BigFloat('123'), "#.3", "123"),
            (BigFloat('123'), ".4", "123.0"),
            (BigFloat('123'), "#.4", "123.0"),
            (BigFloat('123'), ".0", "1e+02"),
            (BigFloat('123'), "", "123.00000000000000"),
            (BigFloat('nan'), "", "nan"),
            (BigFloat('inf'), "", "inf"),
            (BigFloat('-inf'), "", "-inf"),
        ]
        for bf, fmt, expected_output in test_triples:
            result = format(bf, fmt)
            self.assertEqual(result, expected_output,
                             msg=(bf, fmt, expected_output))

    def test_empty_format_matches_str(self):
        test_values = [
            BigFloat('0.0'),
            BigFloat('-0.0'),
            BigFloat('1.0'),
            BigFloat('-2.3'),
            BigFloat('1e100'),
            BigFloat('1e-100'),
            BigFloat('nan'),
            BigFloat('inf'),
            BigFloat('-inf'),
        ]
        for value in test_values:
            self.assertEqual(str(value), format(value, ''))

    def test_invalid_formats(self):
        invalid_formats = [
            # Can't specify fill/align *and* zero padding at once ...
            "X<010.2f",
            ">010.2f",
            " ^010.2f",
            "=010.2f",
            # ... even if the fill/align matches the zero padding!
            "0=010.2f",
            # a . must be followed by a precision.
            ".f",
            "10.g",
        ]
        for fmt in invalid_formats:
            with self.assertRaises(ValueError):
                format(BigFloat(2), fmt)

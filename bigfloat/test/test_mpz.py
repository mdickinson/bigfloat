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

from mpfr import (
    Mpz_t,
    mpz_set_str,
    mpz_get_str,
)


class TestMpz(unittest.TestCase):
    def test_mpz_initial_value(self):
        z = Mpz_t()
        self.assertEqual(mpz_get_str(10, z), "0")

    def test_set_and_get_str(self):
        z = Mpz_t()
        mpz_set_str(z, "123", 10)
        self.assertEqual(mpz_get_str(10, z), "123")

    def test_set_str_base(self):
        z = Mpz_t()

        # Triples (str, base, value)
        test_values = [
            ("1001", 2, 9),
            ("1001", 3, 28),
            ("123", 10, 123),
            ("-123", 10, -123),
            ("abc", 16, 2748),
            ("ABC", 16, 2748),
            ("A", 37, 10),
            ("a", 37, 36),
            ("z", 62, 61),
            ("Z", 62, 35),
            ("11", 0, 11),
            ("011", 0, 9),
            ("0x12", 0, 18),
            ("-0x12", 0, -18),
            ("0X012", 0, 18),
            ("0B00101", 0, 5),
            ("-1 2 3 4 5 6", 0, -123456),
        ]

        for s, base, expected in test_values:
            mpz_set_str(z, s, base)
            actual = int(mpz_get_str(10, z))
            self.assertEqual(actual, expected)

        bad_bases = [-2, 1, 63]
        for base in bad_bases:
            with self.assertRaises(ValueError):
                mpz_set_str(z, "101", base)

    def test_set_str_return_value(self):
        z = Mpz_t()
        mpz_set_str(z, "13", 10)
        self.assertEqual(int(mpz_get_str(10, z)), 13)

        with self.assertRaises(ValueError):
            mpz_set_str(z, "123 abc", 10)
        self.assertEqual(int(mpz_get_str(10, z)), 13)

    def test_get_str(self):
        z = Mpz_t()

        # Triples (value, base, expected_output)
        test_values = [
            (456, 2, "111001000"),
            (456, 10, "456"),
            (456, 16, "1c8"),
            (456, 36, "co"),
            (456, 37, "CC"),
            (456, -2, "111001000"),
            (456, -16, "1C8"),
            (456, -36, "CO"),
        ]

        for value, base, expected in test_values:
            mpz_set_str(z, str(value), 10)
            actual = mpz_get_str(base, z)
            self.assertEqual(actual, expected)

        bad_bases = [-37, -1, 0, 1, 63]

        for base in bad_bases:
            with self.assertRaises(ValueError):
                mpz_get_str(base, z)

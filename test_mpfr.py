import unittest

from mpfr import Mpfr, mpfr_const_pi, mpfr_get_str


class TestMpfr(unittest.TestCase):
    def test_none_argument(self):
        with self.assertRaises(TypeError):
            mpfr_const_pi(None, 0)

    def test_const_pi(self):
        pi = Mpfr(10)
        mpfr_const_pi(pi, 0)
        self.assertEqual(
            mpfr_get_str(pi),
            ('31406', 1),
        )

if __name__ == '__main__':
    unittest.main()

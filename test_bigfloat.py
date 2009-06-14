import unittest
from bigfloat import *

class BigFloatTests(unittest.TestCase):
    def test_creation_from_integer(self):
        test_values = [-23, 0, 100, 7**100, -23L, 0L, 100L]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)

    def test_creation_from_float(self):
        test_values = [-12.3456, -0.0, 0.0, 5e-310, -1e308,
                        float('nan'), float('inf'), float('-inf')]
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)

    def test_creation_from_string(self):
        test_values = ['123.456',
                       '-1.23',
                       '1e456',
                       '+nan',
                       'inf',
                       '-inf',
                       u'-451.001']
        test_precisions = [2, 20, 53, 2000]
        for value in test_values:
            for p in test_precisions:
                with precision(p):
                    bf = BigFloat(value)
                    self.assertEqual(type(bf), BigFloat)
                    self.assertEqual(bf.precision, p)


    def test_subnormalization(self):
        # check that subnormalization doesn't result in
        # double rounding
        with double_precision:
            self.assertEqual(div(2**53+1, 2**1128), pow(2, -1074))

        # check that results are integer multiples of
        # 2**-1074
        with double_precision:
            self.assertEqual(BigFloat('3e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.4e-324'), pow(2, -1074))
            self.assertEqual(BigFloat('7.5e-324'), pow(2, -1073))

def test_main():
    unittest.main()

if __name__ == '__main__':
    test_main()

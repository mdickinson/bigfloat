import unittest

class TestAll(unittest.TestCase):
    def test_from_import_star_on_bigfloat_package(self):
        exec "from bigfloat import *"

if __name__ == '__main__':
    unittest.main()

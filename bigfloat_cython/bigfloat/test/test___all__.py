import collections
import unittest


class TestAll(unittest.TestCase):
    def test_from_import_star_on_bigfloat_package(self):
        exec "from bigfloat import *"

    def test_duplicates(self):
        # Check for duplicate entries in __all__.
        from bigfloat import __all__
        counts = collections.Counter(__all__)
        duplicates = sorted(k for k, v in counts.items() if v > 1)
        self.assertEqual(duplicates, [])


if __name__ == '__main__':
    unittest.main()

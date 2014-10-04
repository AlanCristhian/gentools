import gentools
import unittest


class TestDefine(unittest.TestCase):
    def test_where_method(self):
        a, b, c = 1, 2, 3
        expected = [(a, b, c) for _ in range(5)]
        gen = gentools.Define((x, y, z) for _ in range(5)).where(x=1, y=2, z=3)
        obtained = list(gen)
        self.assertEqual(expected, obtained)


if __name__ == '__main__':
    unittest.main()
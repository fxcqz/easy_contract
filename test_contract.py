import unittest
from easy_contract import contract


@contract
def foo(x, y):
    return x + y

@foo.pre
def foo_pre(x, y):
    assert any((
        (x % 2 == 0 and y % 2 == 0),
        (x % 2 != 0 and y % 2 != 0),
    ))

@foo.post
def foo_post(r, old):
    x, y = old['x'], old['y']
    assert r == x + y


class FunctionTestCase(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(foo(3, 3), 6)
        self.assertEqual(foo(2, 2), 4)
        self.assertRaises(AssertionError, foo, 2, 3)
        self.assertRaises(AssertionError, foo, 3, 2)


class Klass(object):
    @contract
    def bar(self, i, j, k):
        return i * j * k

    @bar.post
    def bar_post(self, r, old):
        i, j, k = old['i'], old['j'], old['k']
        assert r == i * j * k

    @bar.pre
    def bar_pre(self, i, j, k):
        assert all(isinstance(x, float) for x in (i, j, k))


class ClassTestCase(unittest.TestCase):
    def setUp(self):
        self.klass = Klass()

    def test_class(self):
        self.assertEqual(self.klass.bar(2.0, 3.0, 4.0), 24.0)
        self.assertRaises(AssertionError, self.klass.bar, 2, 3, 4)


if __name__ == '__main__':
    unittest.main()

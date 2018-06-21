import unittest
from easy_contract import contract, Invariant


# Test contract

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
    def test_function(self):
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


# Test Invariant

class StandardInvariant(metaclass=Invariant):
    def __init__(self):
        self.value = 2

    def __invariant__(self):
        assert self.value % 2 == 0, "Value must be divisible by two."


class IteratorInvariant(metaclass=Invariant):
    def __init__(self, correct):
        self.max = 10
        self.current = 0
        self.correct = correct

    def __invariant__(self):
        assert self.current % 2 == 0, \
            "An intermediate value is not divisible by two."

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max:
            raise StopIteration

        if self.correct:
            result = self.current
            self.current += 2
            return result
        else:
            result = self.current
            self.current += 1
            return result


class Base(object):
    def __init__(self):
        self.value = 2


class NoInitInvariant(Base, metaclass=Invariant):
    def __invariant__(self):
        assert self.value % 2 == 0, "Value must be divisible by two."


class CheckedInitInvariant(metaclass=Invariant, check_init=True):
    def __init__(self, n):
        self.n = n

    def __invariant__(self):
        assert getattr(self, 'n', 0) % 2 == 0, "N must be divisible by two."


class InvariantTestCase(unittest.TestCase):
    def test_standard_invariant(self):
        inv = StandardInvariant()
        try:
            # should not raise
            inv.value = 4
        except AssertionError:
            self.fail("Unexpectedly got AssertionError")

        with self.assertRaises(AssertionError):
            inv.value = 3

    def test_missing_invariant_function(self):
        with self.assertRaisesRegex(
            Exception,
            "Missing __invariant__ function for Invariant class Test"
        ):
            exec("class Test(metaclass=Invariant): pass")

    def test_iterator_invariant_correct(self):
        inv = IteratorInvariant(True)
        self.assertEqual([x for x in inv], [0, 2, 4, 6, 8, 10])

    def test_iterator_invariant_incorrect(self):
        inv = IteratorInvariant(False)
        with self.assertRaisesRegex(
            AssertionError,
            "An intermediate value is not divisible by two."
        ):
            xs = [x for x in inv]

    def test_no_init_invariant(self):
        inv = NoInitInvariant()
        try:
            # should not raise
            inv.value = 4
        except AssertionError:
            self.fail("Unexpectedly got AssertionError")

        with self.assertRaisesRegex(
            AssertionError,
            "Value must be divisible by two."
        ):
            inv.value = 3

    def test_checked_init_invariant(self):
        try:
            inv = CheckedInitInvariant(2)
        except AssertionError:
            self.fail("Unexpectedly got AssertionError")

        with self.assertRaisesRegex(AssertionError, "N must be divisible by two."):
            inv = CheckedInitInvariant(3)


if __name__ == '__main__':
    unittest.main()

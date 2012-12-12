from common import *

from uitools.qpath import qpath


class Object(list):

    def __init__(self, *args, **kwargs):
        super(Object, self).__init__(args)
        self._parent = None
        for x in args:
            x._parent = self
        for k, v in kwargs.iteritems():
            setattr(self, k, lambda: v)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(repr(x) for x in self))

    def parent(self):
        return self._parent

    def children(self):
        return list(self)

A = type('A', (Object, ), {})
B = type('B', (Object, ), {})
C = type('C', (Object, ), {})
X = type('X', (Object, ), {})
Y = type('Y', (Object, ), {})
Z = type('Z', (Object, ), {})
ABC = type('ABC', (A, B, C), {})
XYZ = type('XYZ', (X, Y, Z), {})


class TestQPath(TestCase):

    def test_linear_direct(self):

        tail = X()
        root = Object(A(B(tail)))

        self.assertEqual(qpath(root, 'A/B/X'), [tail])

        self.assertNotEqual(qpath(root, 'A/C/X'), [tail])

    def test_self(self):

        tail = X()
        root = Object(A(B(tail)))

        self.assertEqual(qpath(root, './A/B/X'), [tail])
        self.assertEqual(qpath(root, 'A/./B/X'), [tail])
        self.assertEqual(qpath(root, 'A/B/./X'), [tail])
        self.assertEqual(qpath(root, 'A/B/X/.'), [tail])

    def test_parent(self):

        tail = X()
        root = Object(A(B(tail)))

        self.assertEqual(qpath(root, 'A/../A/B/X'), [tail])
        self.assertEqual(qpath(root, 'A/B/../B/X'), [tail])
        self.assertNotEqual(qpath(root, 'A/B/X/..'), [tail])

    def test_ignore_leading_slash(self):

        tail = X()
        root = Object(A(B(tail)))

        self.assertEqual(qpath(root, '/A/B/X'), [tail])

    def test_linear_inheritance(self):

        tail = X()
        root = Object(A(ABC(X())))

        self.assertEqual(qpath(root, 'A/A/X'), [tail])
        self.assertEqual(qpath(root, 'A/B/X'), [tail])
        self.assertEqual(qpath(root, 'A/C/X'), [tail])
        self.assertEqual(qpath(root, 'A/Object/X'), [tail])
        self.assertEqual(qpath(root, 'A/object/X'), [tail])
        self.assertNotEqual(qpath(root, 'A/X/X'), [tail])

    def test_descendant_or_self(self):

        tail = X()
        root = Object(A(B(tail)))

        self.assertEqual(qpath(root, '//X'), [tail])
        self.assertEqual(qpath(root, 'A//X'), [tail])
        self.assertEqual(qpath(root, '//B/X'), [tail])






import sys
import unittest


class TestCase(unittest.TestCase):

    # Add some of the unittest methods that we love from 2.7.
    if sys.version_info < (2, 7):
    
        def assertIs(self, a, b, msg=None):
            if a is not b:
                self.fail(msg or '%r at 0x%x is not %r at 0x%x; %r is not %r' % (type(a), id(a), type(b), id(b), a, b))
    
        def assertIsNot(self, a, b, msg=None):
            if a is b:
                self.fail(msg or 'both are %r at 0x%x; %r' % (type(a), id(a), a))
        
        def assertIsNone(self, x, msg=None):
            if x is not None:
                self.fail(msg or 'is not None; %r' % x)
        
        def assertIsNotNone(self, x, msg=None):
            if x is None:
                self.fail(msg or 'is None; %r' % x)
        
        def assertIn(self, a, b, msg=None):
            if a not in b:
                self.fail(msg or '%r not in %r' % (a, b))
        
        def assertNotIn(self, a, b, msg=None):
            if a in b:
                self.fail(msg or '%r in %r' % (a, b))
        
        def assertIsInstance(self, instance, types, msg=None):
            if not isinstance(instance, types):
                self.fail(msg or 'not an instance of %r; %r' % (types, instance))
        
        def assertNotIsInstance(self, instance, types, msg=None):
            if isinstance(instance, types):
                self.fail(msg or 'is an instance of %r; %r' % (types, instance))



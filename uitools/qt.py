"""Wrapping the differences between PyQt4 and PySide."""

import sys

from .utils import ModuleProxy

__all__ = ['Qt', 'QtCore', 'QtGui']


try:
    import PyQt4
    from PyQt4 import QtCore, QtGui

except ImportError:

    # For our tests, so they don't suffer import errors.
    for name in __all__:
        globals().setdefault(name, None)


# For the convenience of our own tools.
Qt = QtCore.Qt if QtCore else None

Q = ModuleProxy(('', 'Q', 'Qt'), (Qt, QtCore, QtGui))

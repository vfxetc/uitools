"""Convenience to import Qt if it is availible, otherwise provide stubs.

Normally I wouldn't bother with something like this, but due to the
testing contexts that we often run we may import stuff from uitools that
does not have Qt avilaible.

"""

__all__ = ['Qt', 'QtCore', 'QtGui']

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    for name in __all__:
        globals().setdefault(name, None)
else:
    Qt = QtCore.Qt


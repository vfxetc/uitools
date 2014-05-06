"""Wrapping the differences between PyQt4 and PySide."""

import sys

__all__ = ['Qt', 'QtCore', 'QtGui']

try:
    import PySide
    from PySide import QtCore, QtGui
    sys.modules.setdefault('PyQt4', PySide)
except ImportError:
    try:
        import PyQt4
        from PyQt4 import QtCore, QtGui
        sys.modules.setdefault('PySide', PySide)
    except ImportError:
        for name in __all__:
            globals().setdefault(name, None)


Qt = QtCore.Qt if QtCore else None

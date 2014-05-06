"""Wrapping the differences between PyQt4 and PySide."""

import sys

__all__ = ['Qt', 'QtCore', 'QtGui']

try:

    import PySide
    from PySide import QtCore, QtGui
    sys.modules.setdefault('PyQt4', PySide)

    # Even out some of the API.
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot

except ImportError:
    try:

        import PyQt4
        from PyQt4 import QtCore, QtGui
        sys.modules.setdefault('PySide', PySide)
        
        # Even out some of the API.
        QtCore.Signal = QtCore.pyqtSignal
        QtCore.Slot = QtCore.pyqtSlot

    except ImportError:

        # For our tests, so they don't suffer import errors.
        for name in __all__:
            globals().setdefault(name, None)


# For the convenience of our own tools.
Qt = QtCore.Qt if QtCore else None

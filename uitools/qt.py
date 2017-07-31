"""Wrapping the differences between PyQt4 and PySide."""

import sys
import warnings

from .utils import ModuleProxy

__all__ = ['Qt', 'QtCore', 'QtGui']


provider = None


_qt2py_transforms = []
def qt2py(data):
    """Convert PyQt4 types to Python types."""

    # This will generally be a passthrough function, unless you override the
    # sip.setapi code in this module to force v1 of any of the APIs. Then
    # you should add functions to _qt2py_transforms. This exists mainly
    # as a reminder of what used to be, and the qt2py function as a signal
    # to myself when moving back into a PyQt4 environment (e.g. Western Post)
    # of what code will likely need to be changed.

    if not _qt2py_transforms:
        return data
    if isinstance(data, dict):
        return dict((k, qt2py(v)) for k, v in data.iteritems())
    if isinstance(data, (tuple, list)):
        return type(data)(qt2py(x) for x in data)
    for cls, func in _qt2py_transforms:
        if isinstance(data, cls):
            return func(data)
    return data



if 'maya' not in sys.executable.lower():
    sys.path[:] = [x for x in sys.path if 'maya' not in x.lower()]


# We prioritize PySide[2] because it is the one that tends to be bundled with
# applications, and so it is much more likely to be the one that works.

if not provider:
    try:
        import PySide2
    except ImportError:
        pass
    else:
        from PySide2 import QtCore, QtGui, QtWidgets
        provider = 'PySide2'
        __all__.append('QtWidgets')
        
        # Monkey-patch to match PyQt4
        QtCore.pyqtSignal = QtCore.Signal
        QtCore.pyqtSlot = QtCore.Slot


if not provider:
    try:
        import PySide
    except ImportError:
        pass
    else:
        from PySide import QtCore, QtGui

        provider = 'PySide'

        # Monkey-patch to match PyQt4
        QtCore.pyqtSignal = QtCore.Signal
        QtCore.pyqtSlot = QtCore.Slot


if not provider:

    try:
        import PyQt4
    except ImportError:
        pass
    else:

        # Force the newer API style.
        # If nessesary (which it won't be), pull from $UITOOLS_QT_LEGACY_{name}
        # to use the v1 sip API. Then
        import sip
        for cls_name in ('QDate', 'QDateTime', 'QString', 'QTextStream', 'QTime', 'QUrl', 'QVariant'):
            try:
                current = sip.getapi(cls_name)
            except ValueError:
                current = None
            if current is None:
                sip.setapi(cls_name, 2)
            if current and current == 1:
                warnings.warn('sip API for %s already set to version 1' % cls_name)

        from PyQt4 import QtCore, QtGui

        provider = 'PyQt4'

        # Monkey-patch to match PySide
        QtCore.Signal = QtCore.pyqtSignal
        QtCore.Slot = QtCore.pyqtSlot

        # Go looking for classes that we would want to transform.
        for cls_name, func in [
            ('QString', lambda x: unicode(x)),
            ('QVariant', lambda x: qt2py(x.toPyObject()) if x.isValid() else None)
        ]:
            if hasattr(QtCore, cls_name):
                _qt2py_transforms.append((getattr(QtCore, cls_name), func))


if provider:
    # For the convenience of our own tools.
    Qt = QtCore.Qt


else:
    # For our tests, so they don't suffer import errors.
    class UIToolsQtDummy(object):
        pass
    for name in __all__:
        globals().setdefault(name, UIToolsQtDummy)


Q = ModuleProxy(('', 'Q', 'Qt'), tuple(globals()[x] for x in __all__))









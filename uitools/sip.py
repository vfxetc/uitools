"""Wrapping the differences between PyQt4 and PySide."""

try:
    import shiboken
    sip = None
except ImportError:
    import sip
    shiboken = None

from .qt import QtGui, QtCore


def wrapinstance(ptr, base=None):
    """Convert a pointer to a Qt class instance.
 
    :param int ptr: Pointer to QObject in memory.
    :param class base: Base class to wrap with.
    :returns: QWidget or subclass instance

    """

    if ptr is None:
        return None
    ptr = long(ptr)

    if shiboken is not None:
        if base is None:

            # Do a generic wrap so that we can detect what type the object
            # actually is.
            q_obj = shiboken.wrapInstance(ptr, QtCore.QObject)
            meta_obj = q_obj.metaObject()
            class_name = meta_obj.className()
            super_name = meta_obj.superClass().className()

            base = (getattr(QtGui, class_name, None) or
                    getattr(QtGui, super_name, None) or
                    QtGui.QWidget)

        return shiboken.wrapInstance(ptr, base)

    elif sip is not None:
        return sip.wrapinstance(ptr, base or QtCore.QObject)
    
    else:
        return None



from .qt import QtCore, QtGui


class _ModuleProxy(object):
    
    def __init__(self, *modules):
        self._modules = modules
    
    def __getattr__(self, attr):
        for module, name_func in self._modules:
            for name in name_func(attr):
                try:
                    v = getattr(module, name)
                    setattr(self, attr, v)
                    return v
                except AttributeError:
                    pass
        raise AttributeError(attr)

Q = _ModuleProxy(
    (QtGui, lambda name: ('Q' + name, )),
    (QtCore, lambda name: ('Q' + name, )),
    (QtCore.Qt, lambda name: (name, 'Q' + name)),
)

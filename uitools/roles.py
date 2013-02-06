import itertools

from .qt import Qt


_role_counter = itertools.count(Qt.UserRole + 314159)
_name_to_role = {}


def get_role(name, create=True):
    try:
        return _name_to_role[name]
    except KeyError:
        if not create:
            raise
        if not isinstance(name, basestring):
            raise TypeError('role names must be strings; got %s %r' % (type(name).__name__, name))
        role = _name_to_role[name] = next(_role_counter)
        return role


_name_to_role['display'] = Qt.DisplayRole


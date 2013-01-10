"""XPath-like query system, designed for axising Qt but usable elsewhere.

Differences from XPath:

- Leading slash is ignored, since we are always passing in root objects.


Axis specifiers:

- attribute
    ``@abc`` -> ``self.abc``

- child
    ``xyz`` -> `child::xyz`

- self
    ``.`` -> `self`

- parent
    ``..`` -> `self.parent()`


"""

import re
import fnmatch


_query_re = re.compile(r'/?(/|[^/]*)')
_axis_re = re.compile(r'^\s*(.*?)\s*(?:\[(.+)\])?\s*$')


def qpath(root, query, globals=None):
    """Return a list of results by applying a query string to a context.

    :param object root: The object to start the search at.
    :param str query: The QPath query to process in the context of the
        given root.
    :return list: The results.

    """

    return list(qpath_iter([root], query, globals))


def qpath_iter(node_iter, query, globals=None):

    node_iter = list(node_iter)

    m = _query_re.match(query)
    if not m:
        if query.strip('/'):
            raise ValueError('could not parse query: %r' % query)
        return []

    axis = m.group(1)
    query = query[m.end(0):]

    m = _axis_re.match(axis)
    if m:
        axis, filter_expr = m.groups()
    else:
        filter_expr = None

    # Apply all transformations.
    if axis:
        node_iter = _apply_axis(node_iter, axis)
    if filter_expr:
        node_iter = _apply_filter(node_iter, filter_expr, globals)
    if query:
        node_iter = qpath_iter(node_iter, query, globals)
    
    return node_iter


def _apply_axis(node_iter, axis):

    # "self".
    if axis in ('.', '*'):
        return node_iter

    # "parent".
    if axis == '..':
        return (x.parent() for x in node_iter)

    # "descendant-or-self".
    if axis == '/':
        return _descendant_or_self(node_iter)

    # Simple class names -> pass through children which match.
    m = re.match(r'^((?:[a-zA-Z_*+][\w*+]*\.)*)([a-zA-Z_*+][\w*+]*)$', axis)
    if m:
        module_name, class_name = m.groups()
        return _test_class(_child_iter(node_iter), module_name, class_name)

    raise ValueError('did not understand axis: %r' % axis)


def _descendant_or_self(node_iter):
    for node in node_iter:
        yield node
        for x in _descendant_or_self(node.children()):
            yield x


def _child_iter(node_iter):
    for node in node_iter:
        for child in node.children():
            yield child


def _test_class(node_iter, module_name, class_name):

    class_re = re.compile(fnmatch.translate(class_name))

    module_name = module_name.rstrip('.')
    module_re = re.compile(fnmatch.translate(module_name)) if module_name else None

    for node in node_iter:
        for base in node.__class__.__mro__:
            if not class_re.match(base.__name__):
                continue
            if module_re and not module_re.match(base.__module__):
                continue
            yield node


class _FilterNamespace(dict):

    def __init__(_self, obj, **kwargs):
        _self.obj = obj
        super(_FilterNamespace, _self).__init__(**kwargs)

    def __getitem__(self, name):
        try:
            return super(_FilterNamespace, self).__getitem__(name)
        except KeyError:
            pass
        try:
            return getattr(self.obj, name)
        except AttributeError:
            raise KeyError(name)


class _NotSetType(object):

    def __repr__(self):
        return 'NotSet'

    def __nonzero__(self):
        return False

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        return ''


_NotSet = _NotSetType()

_search_re = re.compile(r'^(.+?)\s*~([i]*)\s*(.+?)$')


def _apply_filter(node_iter, filter_expr, globals_):

    # Convert attribute syntax.
    filter_expr = re.sub(r'@(\w+)', lambda m: r'getattr(self, %r, NotSet)' % m.group(1), filter_expr)

    # Convert match syntax.
    m = _search_re.match(filter_expr)
    if m:
        expr, flags, pattern = m.groups()
        filter_expr = 'match(%r, str(%s), %s)' % (fnmatch.translate(pattern), expr, '|'.join('re.%s' % x.upper() for x in flags))
        
    expr = compile(filter_expr, '<qpath:%r>' % filter_expr, 'eval')
    for node in node_iter:
        namespace = _FilterNamespace(node,
            self=node,
            NotSet=_NotSet,
            re=re,
            match=re.match,
            search=re.search,
        )
        res = eval(expr, globals_ or {}, namespace)
        if res:
            yield node





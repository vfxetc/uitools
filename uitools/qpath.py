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

import itertools
import re


_query_re = re.compile(r'/?(/|[^/]*)')
_axis_re = re.compile(r'^\s*(.*?)\s*(?:\[(.+)\])?\s*$')

def qpath(root, query):
    """Return a list of results by applying a query string to a context.

    :param object root: The object to start the search at.
    :param str query: The QPath query to process in the context of the
        given root.
    :return list: The results.

    """

    return list(_qpath_filter([root], query))


def _qpath_filter(node_iter, query):

    node_iter = list(node_iter)
    print '_qpath_filter(%r, %r)' % (node_iter, query)

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

    if axis:
        node_iter = _apply_axis(node_iter, axis)

    if query:
        return _qpath_filter(node_iter, query)
    else:
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
    m = re.match(r'^([a-zA-Z_]\w*)$', axis)
    if m:
        class_name = m.group(1)
        return _test_class(_child_iter(node_iter), class_name)

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


def _test_class(node_iter, class_name):
    for node in node_iter:
        print '_test_class(..., %r) on %r' % (class_name, node)
        if any(base.__name__ == class_name for base in node.__class__.__mro__):
            yield node


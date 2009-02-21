"""XPath Queries For DOM Trees

The :mod:`xpath` module is a pure Python implementation of XPath 1.0,
operating on DOM documents.

.. seealso::

   `XML Path Language (XPath) Version 1.0 <http://www.w3.org/TR/xpath>`_
      The W3C recommendation upon which the :mod:`xpath` API is based.

"""

from xpath.exceptions import *
import xpath.exceptions
import xpath.expr
import xpath.parser

__all__ = ['find', 'findnode', 'findvalue', 'XPathContext', 'XPath']
__all__.extend((x for x in dir(xpath.exceptions) if not x.startswith('_')))

def api(f):
    """Decorator for functions and methods that are part of the external
    module API and that can throw XPathError exceptions.

    The call stack for these exceptions can be very large, and not very
    interesting to the user.  This decorator rethrows XPathErrors to
    trim the stack.

    """
    def api_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except XPathError, e:
            raise e
    api_function.__name__ = f.__name__
    api_function.__doc__ = f.__doc__
    return api_function

class XPathContext(object):
    def __init__(self, document=None, **kwargs):
        self.default_namespace = None
        self.namespaces = {}
        self.variables = {}

        if document is not None:
            if document.nodeType != document.DOCUMENT_NODE:
                document = document.ownerDocument
            if document.documentElement is not None:
                attrs = document.documentElement.attributes
                for attr in (attrs.item(i) for i in xrange(attrs.length)):
                    if attr.name == 'xmlns':
                        self.default_namespace = attr.value
                    elif attr.name.startswith('xmlns:'):
                        self.namespaces[attr.name[6:]] = attr.value

        self.update(**kwargs)

    def clone(self):
        dup = XPathContext()
        dup.default_namespace = self.default_namespace
        dup.namespaces.update(self.namespaces)
        dup.variables.update(self.variables)
        return dup

    def update(self, default_namespace=None, namespaces=None,
                  variables=None, **kwargs):
        if default_namespace is not None:
            self.default_namespace = default_namespace
        if namespaces is not None:
            self.namespaces = namespaces
        if variables is not None:
            self.variables = variables
        self.variables.update(kwargs)

    def find(self, expr, node, **kwargs):
        return xpath.find(expr, node, context=self, **kwargs)

    def findnode(self, expr, node, **kwargs):
        return xpath.findnode(expr, node, context=self, **kwargs)

    def findvalue(self, expr, node, **kwargs):
        return xpath.findvalue(expr, node, context=self, **kwargs)

    def findvalues(self, expr, node, **kwargs):
        return xpath.findvalues(expr, node, context=self, **kwargs)

class XPath():
    """
    
    The :func:`find`, :func:`findnode`, and :func:`findvalue` functions
    cache the results of compiling an expression.

    """

    _max_cache = 100
    _cache = {}

    def __init__(self, expr):
        """Init docs.
        """
        self.expr = xpath.parser.parse('XPath', expr)
        if self.expr is None:
            raise XPathParseError()

    @classmethod
    def get(cls, s):
        if isinstance(s, cls):
            return s
        try:
            return cls._cache[s]
        except KeyError:
            if len(cls._cache) > cls._max_cache:
                cls._cache.clear()
            expr = cls(s)
            cls._cache[s] = expr
            return expr

    def find(self, node, context=None, **kwargs):
        """Evaluate the expression in the context of the given node.

        Returns an XPath value: a nodeset, string, boolean, or number.
        """
        if context is None:
            context = XPathContext(node, **kwargs)
        elif kwargs:
            context = context.clone()
            context.update(**kwargs)
        return self.expr.evaluate(node, 1, 1, context)

    def findnode(self, node, context=None, **kwargs):
        result = self.find(node, context, **kwargs)
        if not xpath.expr.nodesetp(result):
            raise XPathTypeError("expression is not a node-set")
        if len(result) == 0:
            return None
        return result[0]

    def findvalue(self, node, context=None, **kwargs):
        """Evaluate the expression in the context of the given node.

        If the result is a nodeset, it is coverted to a string (as if
        passed to the string() function).
        """
        result = self.find(node, context, **kwargs)
        if xpath.expr.nodesetp(result):
            if len(result) == 0:
                return None
            result = xpath.expr.string(result)
        return result

    def findvalues(self, node, context=None, **kwargs):
        """Evaluate the expression in the context of the given node.

        If the result is a nodeset, it is coverted to a string (as if
        passed to the string() function).
        """
        result = self.find(node, context, **kwargs)
        if not xpath.expr.nodesetp(result):
            raise XPathTypeError("expression is not a node-set")
        return [xpath.expr.string_value(x) for x in result]

    def __repr__(self):
        return '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              repr(str(self.expr)))

    def __str__(self):
        return str(self.expr)


@api
def find(expr, node, **kwargs):
    """Evaluate the XPath expression *expr* with *node* as the context node,
    and return the result.

    XPath expressions evaluate one of four basic types:

    * node-set, a list of :class:`xml.dom.Node`.
    * boolean, a :class:`bool`.
    * number, a :class:`float`.
    * string, a :class:`unicode`.

    """
    return XPath.get(expr).find(node, **kwargs)

@api
def findnode(expr, node, **kwargs):
    """Evaluate the XPath expression *expr* with *node* as the context node,
    and return a single :class:`xml.dom.Node`.

    If the result of evaluating *expr* is a node-set containing at least
    one node, the first node in the node-set is returned.

    If the result is an empty node-set, returns ``None``.

    If the result is not a node-set, raises :exc:`xpath.XPathTypeError`.

    """
    return XPath.get(expr).findnode(node, **kwargs)

@api
def findvalue(expr, node, **kwargs):
    """Evaluate the XPath expression *expr* with *node* as the context node,
    and return the result as cast to string.

    If the result of evaluating *expr* is an empty node-set, returns ``None``.

    Otherwise, returns the string-value of *expr*.

    """
    return XPath.get(expr).findvalue(node, **kwargs)

@api
def findvalues(expr, node, **kwargs):
    return XPath.get(expr).findvalues(node, **kwargs)

if __name__ == '__main__':
    import sys
    import xml.dom.minidom

    if len(sys.argv) != 3:
        print "Usage: python -m xpath <expression> <file>"
    else:
        dom = xml.dom.minidom.parse(sys.argv[2])
        try:
            result = find(sys.argv[1], dom)
            if isinstance(result, list):
                for node in result:
                    if node.nodeType == node.ATTRIBUTE_NODE:
                        print '%s=%s' % (node.name, node.value)
                    else:
                        print node.toxml()
            else:
                print result
        except XPathError, e:
            print "error"
            print e.__class__
            print e
            print e.message

import re
import weakref

import xpath
from xpath.exceptions import *
import xpath.parser

__all__ = ('Context',)

class Context(object):
    def __init__(self, default_namespace=None, namespaces=None, variables=None,
                 **kwargs):
        self.default_namespace = default_namespace
        self.namespaces = namespaces if namespaces is not None else {}
        self.variables = variables if variables is not None else {}
        self.variables.extend(kwargs)

    def find(self, expr, node):
        return xpath.find(expr, node, context=self)

    def findnode(self, expr, node):
        return xpath.findnode(expr, node, context=self)

    def findvalue(self, expr, node):
        return xpath.findnode(expr, node, context=self)

class XPath(Context):
    """XPath context object."""

    context_cache = weakref.WeakKeyDictionary()

    def __init__(self, document=None):
        Context.__init__(self)

        self.expr_cache = {}
        self.namespaces = {None: None}

        if document is not None:
            if document.nodeType != document.DOCUMENT_NODE:
                document = document.ownerDocument
            if document.documentElement is not None:
                attrs = document.documentElement.attributes
                for attr in (attrs.item(i) for i in xrange(attrs.length)):
                    if attr.name == 'xmlns':
                        self.namespaces[None] = attr.value
                    elif attr.name.startswith('xmlns:'):
                        self.namespaces[attr.name[6:]] = attr.value

    @classmethod
    def get(cls, document=None):
        if document is not None:
            if document.nodeType != document.DOCUMENT_NODE:
                document = document.ownerDocument

        if document not in cls.context_cache:
            cls.context_cache[document] = cls(document)
        return cls.context_cache[document]

    def local_context(self):
        return Context(self)

    def define_namespace(self, prefix, namespaceURI):
        self.namespaces[prefix] = namespaceURI

    def parse(self, s):
        """Parse an XPath expression and return a reuseable expression object.
        Parsed expressions are cached in the context.

        """
        expr = self.expr_cache.get(s)
        if expr is not None:
            return expr
        expr = xpath.parser.parse('Expr', s)
        if expr is None:
            raise XPathParseError()
        self.expr_cache[s] = expr
        return expr

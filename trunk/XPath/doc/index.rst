:mod:`xpath` --- XPath Queries For DOM Trees
============================================
The :mod:`xpath` module is a pure Python implementation of the XPath query
language, operating on DOM documents.  It supports most of XPath 1.0, with
the following exceptions:

* The namespace axis is not supported.
* The ``round()`` function rounds toward 0, not towards positive infinity.

The following XPath 2.0 features are supported:

* A default namespace may be supplied in the expression context.
* Node tests may have a wildcard namespace. (e.g., ``*:name``.)

This module provides the following functions for evaluating XPath expressions:

.. function:: find(expr, node, [\**kwargs])

   Evaluate the XPath expression *expr* with *node* as the context node,
   and return:

   * ``True`` or ``False``, when the expression has a boolean result.
   * A :class:`float`, when the expression has an numeric result.
   * A :class:`unicode`, when the expression has a string result.
   * A list of :class:`xml.dom.Node`, when the expression has a
     node-set result.

.. function:: findnode(expr, node, [\**kwargs])

   Evaluate the XPath expression *expr* with *node* as the context node,
   and return a single node.  If the result of the expression is a non-empty
   node-set, return the first node in the set.  If the result is an empty
   node-set, return ``None``.  If the result is not a node-set, raise
   :exc:`XPathTypeError`.

.. function:: findvalue(expr, node, [\**kwargs])

   Evaluate the XPath expression *expr* with *node* as the context node,
   and return the string-value of the result.  If the result is an empty
   node-set, return ``None`` instead.

.. function:: findvalues(expr, node, [\**kwargs])

   Evaluate the XPath expression *expr* with *node* as the context node,
   and return a list of the string-values of the resulting node-set.  If
   the result is not a node-set, raise :exc:`XPathTypeError`.

The above functions take take the following optional keyword arguments
defining the evaluation context:

*context*
  A :class:`XPathContext` object containing the evaluation context.  It
  is legal to supply both a context object and additional arguments
  extending its contents.

*default_namespace*
  The default namespace URI, which will be used for any unqualified name
  in the XPath expression.

*namespaces*
  A mapping of prefixes to namespace URIs.

*variables*
  A mapping of variable names to values.  To map a variable in a specific
  namespace, use a two element tuple of the (namespace URI, name) as the key.

Additional keyword arguments will be used as variable bindings.

Basic Queries
-------------
The examples in this section use this XML document: ::

   <doc>
     <item name="python" />
     <item name="parrot" />
   </doc>

Select the ``item`` element in a document: ::

   >>> xpath.find('//item', doc)
   [<DOM Element: item at 0x474468>, <DOM Element: item at 0x27d7d8>]

Select the ``name`` attribute of the first item element (note that this returns
a list of Attr nodes): ::

   >>> xpath.find('//item[1]/@name', doc)
   [<xml.dom.minidom.Attr instance at 0x474300>]

Select the string-value of the ``name`` attribute of the last item element: ::

   >>> xpath.findvalue('//item[last()]/@name', doc)
   u'parrot'

Select the first item element with a ``name`` attribute that starts with "p": ::

   >>> xpath.findnode('//item[starts-with(@name,"p")]', doc)
   <DOM Element: item at 0x474468>

Namespaces
----------
The examples in this section use this XML document: ::

   <doc xmlns="http://flying.example.org/"
        xmlns:circus="http://circus.example.org/">
     <item>python</item>
     <circus:item>parrot</circus:item>
   </doc>

The *namespaces* argument to the evaluation functions provides a dictionary
of prefixes to namespace URIs.  Prefixed QNames in expressions will be
expanded according to this mapping.

To select the string-values of the ``item`` elements in the
"\http://circus.example.org/" namespace: ::

   >>> xpath.findvalues('//prefix:item', doc,
   ...                  namespaces={'prefix':'http://circus.example.org/'})
   [u'parrot']

The *default_namespace* argument provides a namespace URI that will be
used for any unprefixed QName appearing in a position where an element
name is expected.  (Default namespaces are a feature of XPath 2.0.)

To select the string-values of the ``item`` elements in the
"\http://flying.example.org/" namespace: ::

   >>> xpath.findvalues('//item', doc,
   ...                  default_namespace='http://flying.example.org/')
   [u'python']

When a *default_namespaces* argument is not provided, the default namespace
is that of the document element.  When a *namespaces* argument is not
provided, the prefix declarations consist of all prefixes defined on the
document element.

To select the string values of all the ``item`` elements: ::

   >>> xpath.findvalues('//item | //circus:item', doc)
   [u'python', u'parrot']

The :mod:`xpath` module supports wildcard matches against both the prefix
and local name.  (XPath 1.0 only support wildcard matches against the local
name; XPath 2.0 adds support for wildcard matches against the prefix.)

To select all children of the document element, regardless of namespace: ::

   >>> xpath.find('/*:*/*:*', doc)
   [<DOM Element: item at 0x474d00>, <DOM Element: circus:item at 0x4743a0>]

Variables
---------
The examples in this section use this XML document: ::

   <doc>
     <item id="1">python</item>
     <item id="2">parrot</item>
   </doc>

XPath variables may be passed to the evaluation functions as keyword
arguments: ::

   >>> xpath.findvalue('//item[@id = $id]', doc, id=2)
   u'parrot'

It is also possible to pass a dictionary of variables to an evaluation
function with the *variables* keyword argument: ::

   >>> xpath.findvalue('//item[@id = $id]', doc, variables={'id':1})
   u'python'

To define a variable within a specific namespace, use a tuple of
``(namespace-URI, local-name)`` as the key in the variable dictionary: ::

   >>> variables = { ('http://python.example.org/', 'id') : 1 }
   >>> namespaces = { 'python' : 'http://python.example.org/' }
   >>> xpath.findvalue('//item[@id = $python:id]', doc,
   ...                 variables=variables, namespaces=namespaces)
   u'python'

Compiled Expression Objects
---------------------------
.. class:: XPath(expr)

   An expression object which contains a compiled form of the XPath
   expression *expr*.

   Under most circumstances, it is not necessary to directly use this class,
   since the :func:`find` et al. functions cache compiled expressions.

   .. method:: find(node, [\**kwargs])
               findnode(node, [\**kwargs])
               findvalue(node, [\**kwargs])
               findvalues(node, [\**kwargs])

      These methods are identical to the functions of the same name.

Create and use a compiled expression: ::

   >>> expr = xpath.XPath('//text()')
   >>> print expr
   /descendant-or-self::node()/child::text()
   >>> expr.find()
   [<DOM Text node "Monty">]

Expression Context Objects
--------------------------
.. class:: XPathContext([document,] [\**kwargs])

   The static context of an XPath expression.  Context objects may be
   created with the same keyword arguments accepted by the expression
   evaluation functions.

   The *document* argument may contain a DOM node.  If provided, the
   default namespace and namespace declarations will be initialized from
   the document element of this node.

   The context contains the following attributes and methods:

   .. attribute:: default_namespace
      
      The default namespace URI.

   .. attribute:: namespaces

      The mapping of prefixes to namespace URIs.

   .. attribute:: variables

      The mapping of variables to values.  The keys of this map may
      be either strings for variables with no namespace, or
      (namespaceURI, name) tuples for variables contained in a
      namespace.

   .. method:: find(expr, node, [\**kwargs])
               findnode(expr, node, [\**kwargs])
               findvalue(expr, node, [\**kwargs])
               findvalues(expr, node, [\**kwargs])

      Evaluate *expr* in the context with *node* as the context node.
      *expr* may be either a string or a :class:`XPath` object.

Create and use an evaluation context: ::

   >>> context = xpath.XPathContext()
   >>> context.namespaces['py'] = 'http://python.example.org/'
   >>> context.variables['min'] = 4
   >>> context.findvalues('//item[@id>=$min and @id<=$max]', doc, max=6)
   [u'4', u'5', u'6']

Exceptions
----------
This module defines the following exceptions:

.. exception:: XPathError

   Base exception class used for all XPath exceptions.

.. exception:: XPathNotImplementedError

   Raised when an XPath expression contains a feature of XPath which
   has not been implemented.

.. exception:: XPathParseError

   Raised when an XPath expression could not be parsed.

.. exception:: XPathTypeError

   Raised when an XPath expression is found to contain a type error.
   For example, the expression "string()/node()" contains a type error
   because the "string()" function does not return a node-set.

.. exception:: XPathUnknownFunctionError

   Raised when an XPath expression contains a function that has no
   binding in the expression context.

.. exception:: XPathUnknownPrefixError

   Raised when an XPath expression contains a QName with a namespace
   prefix that has no corresponding namespace declaration in the expression
   context.

.. exception:: XPathUnknownVariableError

   Raised when an XPath expression contains a variable that has no
   binding in the expression context.

References
----------
.. seealso::

   `XML Path Language (XPath) Version 1.0 <http://www.w3.org/TR/xpath>`_
      The W3C recommendation upon which this module is based.

   `XML Path Language (XPath) 2.0 <http://www.w3.org/TR/xpath20/>`_
      Second version of XPath, mostly unsupported by this module.

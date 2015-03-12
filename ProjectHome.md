`py-dom-xpath` is a pure Python implementation of XPath 1.0.  It supports almost all XPath 1.0, with the main exception being the namespace axis.  It operates on DOM 2.0 nodes, and works well with `xml.dom.minidom`.

`py-dom-xpath` requires Python 2.5 or greater.

Simple queries are easy:

```
>>> xpath.find('//item', doc)
[<DOM Element: item at 0x474468>, <DOM Element: item at 0x27d7d8>]
```

Namespaces are fully supported (although the namespace axis is not):

```
>>> context = xpath.XPathContext()
>>> context.namespaces['py'] = 'http://python.example.org/'
>>> context.findvalues('//py:skit/@name', doc)
[u'argument', u'lumberjack', u'parrot']
```

XPath variables are also supported:

```
>>> xpath.find('//chapter[@name = $name]', doc, name='Python')
[<DOM Element: chapter at 0x474468>]
```

`py-dom-xpath` uses the [Yapps 2](http://theory.stanford.edu/~amitp/yapps/) parser generator by Amit J. Patel.

`py-dom-xpath` was developed at [Nominum](http://www.nominum.com/).  Nominum has graciously permitted the author to release it under the MIT license.
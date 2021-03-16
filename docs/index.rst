.. Typeable documentation master file, created by

Typeable: Type Casting Simplified
=================================

Release v\ |version|. (:ref:`Installation <install>`)

**Typeable** is a concise yet expressive Python type casting library.

-------------------

::

   >>> data = {'a': ["0", True, 2, 3.14], 'b': range(4)}
   >>> DataType = dict[str,list[typing.Union[bool,float,int]]]
   >>> typeable.cast(DataType, data)
   {'a': [False, True, 2, 3.14], 'b': [0, 1, 2, 3]}

   >>> @typeable.cast.function
   ... def my_function(d: DataType):
   ...     return d
   >>> my_function(data)
   {'a': [False, True, 2, 3.14], 'b': [0, 1, 2, 3]}
   
   >>> with typeable.declare('Json') as _J:
   ...     Json = typing.Union[float, bool, int, str, None, dict[str, _J], list[_J]]
   >>> json.dumps(typeable.cast(Json, data))
   '{"a": ["0", true, 2, 3.14], "b": [0, 1, 2, 3]}'

   >>> class X(typeable.Object):
   ...     a: list[bool]
   ...     b: list[int]
   >>> ctx = typeable.Context()
   >>> with ctx.capture() as error:
   ...     x = X(data, ctx=ctx)
   Traceback (most recent call last):
       ...
   TypeError: No implementation found for 'bool' from float
   >>> error.location
   ('a', 3)

**Typeable** implements runtime type casting using Python's :term:`annotation` syntax.
Approaches from a practical point of view, and loves simplicity.

Quick Links
-----------

* `GitHub <https://github.com/flowdas/typeable>`_
* Documentations
   * `English <https://typeable.readthedocs.io/>`_
   * `Korean <https://typeable.flowdas.com/>`_

User's Guide
------------

.. toctree::
   :maxdepth: 2

   user/install

API Reference
-------------

.. toctree::
   :maxdepth: 3

   api/types
   api/typeable


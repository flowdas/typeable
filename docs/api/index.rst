Developer Interface
===================

.. py:currentmodule:: typeable

This package defines the following functions and decorators:

.. function:: cast(typ: typing.Type[_T], val: object, *, ctx: Context = None) -> _T

   Cast a value to a type.

   This returns the value converted to the designated type. *typ* can be 
   anything that can be used in type :term:`annotation`. 

   The conversion rules try to mimic the standard Python rules as much as 
   possible. But you can use *ctx* to change the rules.

   If the conversion rules do not allow conversion, various standard 
   exceptions such as :exc:`TypeError` and :exc:`ValueError` can be thrown. 
   If you wish, you can use *ctx* to locate the error position on *val*.

.. decorator:: cast.register

.. function:: declare(name: str)

.. function:: field(*, key=None, default=MISSING, default_factory=None, nullable=None, required=False)

.. function:: fields(class_or_instance)   
   
This module defines the following constant:

.. data:: MISSING

This package defines a couple of classes, which are detailed in the sections
below.

.. class:: Context(**policies)

   By passing the :class:`Context` object to the :func:`cast` you can change 
   the default conversion rules or find the location of the error that 
   occurred during conversion.

   Keyword-only parameters passed to *policies* are used to change conversion 
   rules. These parameters are provided as attributes of the :class:`Context` 
   instance. You can also subclass :class:`Context` to change the default 
   values of parameters, or add new parameters. The currently defined 
   parameters are:

   .. attribute:: accept_nan: bool = True

   .. attribute:: bool_is_int: bool = True

   .. attribute:: bool_strings: dict[str, bool] = {'0': False, '1': True, 'f': False, 'false': False, 'n': False, 'no': False, 'off': False, 'on': True, 't': True, 'true': True, 'y': True, 'yes': True,}

   .. attribute:: bytes_encoding: str = 'utf-8'

   .. attribute:: date_format: str = 'iso'

   .. attribute:: datetime_format: str = 'iso'

   .. attribute:: encoding_errors: str = 'strict'

   .. attribute:: lossy_conversion: bool = True

   .. attribute:: naive_timestamp: bool = False

   .. attribute:: strict_str: bool = True

   .. attribute:: time_format: str = 'iso'

   .. attribute:: union_prefers_same_type: bool = True

   .. attribute:: union_prefers_base_type: bool = True

   .. attribute:: union_prefers_super_type: bool = True
    
   .. attribute:: union_prefers_nearest_type: bool = True
    
   The location of the error that occurred during conversion can be found 
   using :meth:`capture`.

   :class:`Context` instances are neither thread-safe nor :term:`coroutine`-safe. 
   Make sure that an instance is not used by multiple threads or coroutines 
   simultaneously. But it's safe to use it repeatedly for successive 
   :func:`cast` calls.

   .. method:: capture()

      Tracks the location of errors that occur during conversion. Since it is 
      a :term:`context manager`, it must be used with the :keyword:`with` 
      statement. The error object is passed to the :keyword:`as` target of the 
      :keyword:`with` statement. This error object provides the ``location`` 
      attribute which is a :class:`tuple` when an error occurs, and is 
      :const:`None` if no error occurs. ``location`` is a tuple of keys or 
      indices needed to reach the error position. For example:

          >>> from typing import Dict, List
          >>> from typeable import *
          >>> ctx = Context()
          >>> with ctx.capture() as error:
          ...     data = cast(Dict[str,List[int]], {"a":[], "b":[0,"1",None,3]}, ctx=ctx)
          Traceback (most recent call last):
              ...
          TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
          >>> error.location
          ('b', 2)

    .. method:: traverse(key)

.. class:: Object(value = MISSING, *, ctx: Context = None)


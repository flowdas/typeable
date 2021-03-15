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

.. decorator:: typeable.cast.register

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

   .. attribute:: accept_nan 
      :type: bool 
      :value: True

   .. attribute:: bool_is_int
      :type: bool 
      :value: True

      If this attribute is :const:`False`, then :class:`bool` is not treated as :class:`int`.  

   .. attribute:: bool_strings
      :type: dict[str, bool]
      :value: {'0': False, '1': True, 'f': False, 'false': False, 'n': False, 'no': False, 'off': False, 'on': True, 't': True, 'true': True, 'y': True, 'yes': True}

      Defines strings that can be converted to :class:`bool` and the corresponding :class:`bool` value.
      All keys should be lowercase.
      When looking up a dictionary, the value converted to lowercase is used as a key.

   .. attribute:: bytes_encoding
      :type: str 
      :value: 'utf-8'

   .. attribute:: date_format
      :type: str 
      :value: 'iso'
      
   .. attribute:: datetime_format
      :type: str 
      :value: 'iso'

   .. attribute:: encoding_errors
      :type: str 
      :value: 'strict'

   .. attribute:: lossy_conversion
      :type: bool 
      :value: True

      If this attribute is :const:`False`, no conversion with information loss is performed.
      For example, ``cast(int, 1.2)`` is not allowed.

   .. attribute:: naive_timestamp
      :type: bool 
      :value: False

   .. attribute:: strict_str
      :type: bool 
      :value: True

   .. attribute:: time_format
      :type: str
      :value: 'iso'

   .. attribute:: union_prefers_same_type
      :type: bool 
      :value: True

   .. attribute:: union_prefers_base_type
      :type: bool 
      :value: True

   .. attribute:: union_prefers_super_type
      :type: bool 
      :value: True

   .. attribute:: union_prefers_nearest_type
      :type: bool 
      :value: True
    
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


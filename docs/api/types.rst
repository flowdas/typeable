Type Casting
============

.. py:currentmodule:: typeable

Here we describe the types that can be passed as the first argument to :func:`cast` and their conversion rules.
In principle, all types must accept values of the same type as themselves. Therefore, this is not described repeatedly.
In the description, ``val`` means the value passed as the second argument to :func:`cast`.

If a type that is not directly supported is passed as the first argument of :func:`cast`, the rules of the nearest base class are applied.
For example, a user-defined class that does not define a base class follows the rule of ``object``, and a class that inherits from :class:`int` follows the rule of ``int``.
So when we say we call ``int(val)`` in the description of ``int``, you should interpret ``int`` as being replaced by a user-defined type.
If the user-defined type does not follow the rules of the base class, it should be specialized with :func:`typeable.cast.register`.

The same rules apply to ``val``.
For example, when we say ``enum.IntEnum`` accepts :class:`int` in this description, it means accepts when ``isinstance(val, int)`` is true.
If the user-defined type instance passed to ``val`` doesn't follow this rule, it can also be specialized with :func:`typeable.cast.register`.

Builtin Types
-------------

:class:`bool`

:class:`bytearray`

:class:`bytes`

:class:`complex`

:class:`dict`

:class:`float`

:class:`frozenset`

:class:`int`

    Calls ``int(val)``. 
    This means that it accepts :class:`int`, :class:`float`, and :class:`str` as well as user-defined types that support the :class:`int` conversion.

    If :attr:`~typeable.Context.bool_is_int` is :const:`False` then :class:`bool` is not accepted.

    If :attr:`~typeable.Context.lossy_conversion` is :const:`False`, it does not accept :class:`float` which has non-zero fractional part.

:class:`list`

:data:`None`

:class:`object`
    
:class:`set`

:class:`str`

:class:`tuple`


Standard Types
--------------

:mod:`datetime`
~~~~~~~~~~~~~~~

:class:`datetime.date`

:class:`datetime.datetime`

:class:`datetime.time`

:class:`datetime.timedelta`

:mod:`enum`
~~~~~~~~~~~

:class:`enum.Enum`

    Converted to and from :class:`str` using **name**\ of enum member.

    Calls ``enum.Enum(val)`` for all other types, including :class:`enum.Enum`.
    Because of this, :class:`enum.Enum` that have ``None`` as their value will also accept ``None``.
    In this case, the reverse direction conversion is not provided.

:class:`enum.IntEnum`

    Converting to and from :class:`str` works like :class:`enum.Enum`.

    In addition to this, converting to and from :class:`int` is supported using **value**\ of enum member.

:mod:`typing`
~~~~~~~~~~~~~

:class:`typing.Dict`

:class:`typing.ForwardRef`

:class:`typing.FrozenSet`

:class:`typing.List`

:class:`typing.Optional`

:class:`typing.Set`

:class:`typing.Tuple`

:class:`typing.Union`


Typeable Types
--------------

:class:`Object`


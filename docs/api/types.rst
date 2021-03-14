Type Casting
============

.. py:currentmodule:: typeable

Here we describe the types that can be passed as the first argument to :func:`cast` and their conversion rules.
In principle, all types must accept values of the same type as themselves. Therefore, this is not described repeatedly.
In the description, ``val`` means the value passed as the second argument to :func:`cast`.

The description of each type only describes the rules for converting other types to the target type, not the rules for converting to other types.
For example, the ``cast(int, '123')`` conversion is described in ``int``, and the ``cast(str, 123)`` conversion is described in ``str``.

If a type that is not directly supported is passed as the first argument of :func:`cast`, the rules of the nearest base class are applied.
For example, a user-defined class that does not define a base class follows the rule of ``object``, and a class that inherits from :class:`int` follows the rule of ``int``.
So when we say we call ``int(val)`` in the description of ``int``, you should interpret ``int`` as being replaced by a user-defined type.
If the user-defined type does not follow the rules of the base class, it should be specialized with :func:`typeable.cast.register`.

The same rules apply to ``val``.
For example, when we say ``enum.IntEnum`` accepts :class:`int` in this description, it means accepts when ``isinstance(val, int)`` is true.
If the user-defined type instance passed to ``val`` doesn't follow this rule, it can also be specialized with :func:`typeable.cast.register`.

Standard Types
--------------

:class:`bool`

:class:`bytearray`

:class:`bytes`

:class:`complex`

:class:`datetime.date`

:class:`datetime.datetime`

:class:`dict`, :class:`typing.Dict`

:class:`float`

:class:`typing.ForwardRef`

:class:`frozenset`, :class:`typing.FrozenSet`

:class:`int`

    Calls ``int(val)``. 
    This means that it accepts :class:`int`, :class:`float`, and :class:`str` as well as user-defined types that support the :class:`int` conversion.

    If :attr:`~typeable.Context.bool_is_int` is :const:`False` then :class:`bool` is not accepted.

    If :attr:`~typeable.Context.lossy_conversion` is :const:`False`, it does not accept :class:`float` which has non-zero fractional part.

:class:`enum.IntEnum`

    Calls ``enum.IntEnum(val)``. 
    This means it accepts :class:`int`.
    However, actually it accepts any value that can be compared to be equal to an enum field. 
    Therefore, it also accepts the :class:`float` value which has zero fractional part.

:class:`list`, :class:`typing.List`

:data:`None`

:class:`object`

:class:`typing.Optional`

:class:`set`, :class:`typing.Set`

:class:`str`

:class:`datetime.time`

:class:`datetime.timedelta`

:class:`tuple`, :class:`typing.Tuple`

:class:`typing.Union`


Typeable Types
--------------

:class:`Object`


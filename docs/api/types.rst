Type Casting
============

.. py:currentmodule:: typeable

Here we describe the types that can be passed as the first argument to :func:`cast` and their conversion rules.
In principle, all types must accept values of the same type as themselves. Therefore, this is not described repeatedly.
In the description, ``val`` means the value passed as the second argument to :func:`cast`.

If a type that is not directly supported is passed as the first argument of :func:`cast`, the rules of the nearest base class are applied.
For example, a user-defined class that does not define a base class follows the rule of ``object``, and a class that inherits from :class:`int` follows the rule of ``int``.
So when we say we call ``int(val)`` in the description of ``int``, you should interpret ``int`` as being replaced by a user-defined type.
If the user-defined type does not follow the rules of the base class, it should be specialized with :func:`cast.register`.

The same rules apply to ``val``.
For example, when we say ``enum.IntEnum`` accepts :class:`int` in this description, it means accepts when ``isinstance(val, int)`` is true.
If the user-defined type instance passed to ``val`` doesn't follow this rule, it can also be specialized with :func:`cast.register`.

Builtin Types
-------------

:class:`bool`

    Converted to and from :class:`int` and :class:`str`.

    When :class:`bool` is converted to :class:`str`, it is converted to ``"True"`` or ``"False"``.
    When converting :class:`str` to :class:`bool`, convert it to lowercase first and then look up the :attr:`~typeable.Context.bool_strings` dictionary.
    It raises :exc:`TypeError` if this dictionary is empty, and :exc:`ValueError` if it is not empty but there is no key for that string.

    If :attr:`~typeable.Context.bool_is_int` is :const:`False`, conversion to and from :class:`int` is not allowed.

    If :attr:`~typeable.Context.lossy_conversion` is :const:`False`, :class:`int` other than 0 and 1 is not converted to :class:`bool`.

    One-way conversion from :class:`bool` to :class:`float` is allowed.
    If :attr:`~typeable.Context.lossy_conversion` is :const:`False`, values other than 0 and 1 are not converted.
    Even this is forbidden if :attr:`~typeable.Context.bool_is_int` is :const:`False`.

:class:`bytearray`

:class:`bytes`

:class:`complex`

:class:`dict`

:class:`float`

:class:`frozenset`

:class:`int`

    Converted to and from :class:`int`, :class:`bool`, :class:`float`, and :class:`str`.

    For other types, calls ``int(val)``.
    This means that it accepts all user-defined types that support the :class:`int` conversion.
    In this case, the conversion in the opposite direction is up to the implementation of the user-defined type.

    If :attr:`~typeable.Context.bool_is_int` is :const:`False` then :class:`bool` is not accepted.

    If :attr:`~typeable.Context.lossy_conversion` is :const:`False`, it does not accept :class:`float` which has non-zero fractional part, and integers other than 0 and 1 are not converted to :class:`bool`.

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

    Converted to and from :class:`str` using **name** of enum member.

    Calls ``enum.Enum(val)`` for all other types, including :class:`enum.Enum`.
    Because of this, :class:`enum.Enum` that have ``None`` as their value will also accept ``None``.
    In this case, the reverse direction conversion is not provided.

:class:`enum.Flag`
    
    Converted to and from :class:`int` using **value** of enum member.

    Unlike :class:`enum.Enum`, conversion to and from :class:`str` is not supported.

:class:`enum.IntEnum`

    Converting to and from :class:`str` works like :class:`enum.Enum`.

    In addition to this, converting to and from :class:`int` is supported using **value** of enum member.

:class:`enum.IntFlag`
    
    Converted to and from :class:`int` using **value** of enum member.

    Unlike :class:`enum.IntEnum`, conversion to and from :class:`str` is not supported.


:mod:`typing`
~~~~~~~~~~~~~

:data:`typing.Any`

    Pass ``val`` as it is without conversion or checking.

:class:`typing.Dict`

:class:`typing.ForwardRef`

    :class:`typing.ForwardRef` that appears in the type parameter of a generic type is automatically evaluated by Typeable.

    :class:`typing.ForwardRef` does not express a type by itself, it is just an intermediary passing a string forward reference to delay evaluation of a type.
    Usually (though not impossible) you don't create an instance of :class:`typing.ForwardRef` yourself, it is created automatically when you pass a string to the type parameter when using a generic type. The support provided by the :mod:`typing` module is limited to the :term:`annotation` area.

    Typeable provides a :func:`declare` context manager so that forward references can be used outside of the :term:`annotation`.

:class:`typing.FrozenSet`

:class:`typing.List`

:data:`typing.Literal`

    If there is a literal that matches ``val``, it returns the literal, otherwise :exc:`ValueError` is raised.

    Since :data:`typing.Literal` was added in Python 3.8, the :mod:`typeable.typing` module provides backport.

:data:`typing.Optional`

    :data:`typing.Optional` is automatically converted to :data:`typing.Union`.

:class:`typing.Set`

:data:`typing.Tuple`

:data:`typing.Union`


Typeable Types
--------------

:class:`JsonValue`

    The :data:`~typing.Union` of :class:`float`, :class:`bool`, :class:`int`, :class:`str`, :const:`None`, ``dict[str, JsonValue]``, ``list[JsonValue]`` and ``tuple[JsonValue, ...]``.

:class:`Object`

    Converted to and from :class:`dict`.

    When :class:`dict` is converted to :class:`Object`, undefined keys are ignored.
    It raises :exc:`TypeError` if a field with *required* specified as :const:`True` is missing.
    If the field specifying *default_factory* is missing, it creates a value and assigns it to the instance attribute.

    When :class:`Object` is converted to :class:`dict`, only :class:`Object` instance attributes are provided.
    Fields not assigned to instance attributes are not included.
    Although *default* is defined so the attribute can be read, it will not be included if it has not been assigned as an instance attribute.

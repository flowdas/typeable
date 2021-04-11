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

   .. decorator:: cast.function(user_function)
                  cast.function(*, ctx_name: str = 'ctx', cast_return: bool = False, keep_async: bool = True)

      A decorator that types-casts the arguments of a function.

      When a decorated function is called, the original function is called by type-casted values for the :term:`annotated <annotation>` arguments.
      Arguments without the :term:`annotation` are passed as it is.

      The default behavior is to not type-cast the return value even if there is a :term:`annotation` of the return value.
      If *cast_return* is true and there is a :term:`annotation` of the return value, the return value is also type casted.

      When tracking the error location with :func:`Context.capture`, the ``location`` attribute is given the name of the argument.
      If an error occurred in the return value, ``"return"`` is used.
      If :term:`annotation` is supplied to an argument of the form ``*args`` or ``**kwargs``, the name of the argument is supplied first, followed by the index or keyword name.

      The decorated function has an additional *ctx* argument that takes a :class:`Context` instance.
      It raises :exc:`TypeError`, if the original function already has an argument named *ctx*.
      To change this name, specify name with the *ctx_name* argument.
      If the original function wants to receive *ctx* arguments directly, it must provide :class:`Context` type :term:`annotation`.
      In this case, when :const:`None` is passed to *ctx*, a new instance is created and passed.

      This decorator can also be used for methods.
      When :func:`cast.function` is applied in combination with other method descriptors, it should be applied as the innermost decorator.

      This decorator can also be used with :term:`coroutine function`.
      In this case, the decorated function is also :term:`coroutine function`.
      However, if the *keep_async* parameter is :const:`False`, the decorated function becomes a synchronous function that immediately calls the original function and returns :term:`awaitable`.
      It is used for the purpose of generating an error due to type casting early.

   .. decorator:: typeable.cast.register(impl)

.. function:: declare(name: str)

   A :term:`context manager` that allows you to define recursive :term:`type aliases <type alias>` using forward references.

   Provides an instance of :class:`typing.ForwardRef` with the name provided as the *name* argument as the target of :keyword:`as` of the :keyword:`with` statement.
   If you use this value for a type parameter of a generic type, forward references are automatically evaluated when exiting the :keyword:`with` statement.
   
   It can be used for local aliases as well as global aliases.

.. function:: dump(obj: JsonValue, fp, *, ensure_ascii=False, separators=(',', ':'), **kw)

   A function that wraps the standard library :func:`json.dump` function so that *obj* arguments are automatically converted to :class:`JsonValue`.
   
   This function has changed the default values for the *ensure_ascii* and *separators* arguments.

.. function:: dumps(obj: JsonValue, *, ensure_ascii=False, separators=(',', ':'), **kw)

   A function that wraps the standard library :func:`json.dumps` function so that *obj* arguments are automatically converted to :class:`JsonValue`.
   
   This function has changed the default values for the *ensure_ascii* and *separators* arguments.

.. function:: field(*, key=None, default=dataclasses.MISSING, default_factory=None, nullable=None, required=False, kind=False)

.. function:: fields(class_or_instance)   

This package defines a number of classes, which are detailed in the sections below.

.. class:: AllOf(arg: Constraint, *args: Constraint)

   :Class:`Constraint` that must satisfy all constraints passed as arguments.

.. class:: AnyOf(arg: Constraint, *args: Constraint)

   :Class:`Constraint` that must satisfy at least one of the constraints passed as arguments.

.. class:: Constraint()

   Base class of constraints checked at runtime.

   Used as metadata provided to :data:`typing.Annotated`.

   Other than this purpose, the user does not have to deal with instances of :class:`Constraint` directly.
   The following interface is only needed if you want to define a new constraint by creating a subclass of :class:`Constraint`.

   .. method:: annotate(root: JsonSchema, schema: JsonSchema)

      Add the constraint to the JSON Schema passed as the *schema* argument.

      *root* is a JSON Schema instance of type defined as :data:`typing.Annotated`.

   .. method:: compile()

      Returns a callable that evaluates the constraint.

      The callable takes the value after casting by :func:`cast`.
      If the callable's return value evaluates to true, it is interpreted as satisfying the constraint.
      Returning false or raising an exception is interpreted as not satisfying the constraint.

   .. method:: emit()

      Returns a string expressing the constraint.

      The expression must assume that the argument to be tested is provided as a variable called ``x``.
      For example, ``"(x > 0)"``.

      If the expression refers to a module, :meth:`emit` can return a 2-tuple ``(expr, ns)``.
      ``expr`` is an expression, ``ns`` is a mapping where the key is the module name, and the value is the module instance.

.. class:: Context(**policies)

   By passing the :class:`Context` object to the :func:`cast` you can change 
   the default conversion rules or find the location of the error that 
   occurred during conversion.

   Keyword-only parameters passed to *policies* are used to change conversion 
   rules. These parameters are provided as attributes of the :class:`Context` 
   instance. You can also subclass :class:`Context` to change the default 
   values of parameters, or add new parameters. The currently defined 
   parameters are:

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

.. class:: IsFinite()

   :Class:`Constraint` which allows only finite numbers.

   Applies only to :class:`int`, :class:`float`, and :class:`complex` types, and does not allow NaN or infinity.

   Standard JSON does not allow NaN or infinite, so it is not reflected in JSON Schema.

.. class:: IsGreaterThan(exclusive_minimum)

   :class:`Constraint` that only allows values greater than *exclusive_minimum*.

   It is expressed as *exclusiveMinimum* in JSON Schema.

.. class:: IsGreaterThanOrEqual(minimum)

   :class:`Constraint` that only allows values greater than or equal to *minimum*.

   It is expressed as *minimum* in JSON Schema.

.. class:: IsLessThan(exclusive_maximum)

   :class:`Constraint` that only allows values less than *exclusive_maximum*.

   It is expressed as *exclusiveMaximum* in JSON Schema.

.. class:: IsLessThanOrEqual(maximum)

   :class:`Constraint` that only allows values less than or equal to *maximum*.

   It is expressed as *maximum* in JSON Schema.

.. class:: IsLongerThanOrEqual(minimum)

   :class:`Constraint` that only allows values longer than or equal to *minimum*.

    In JSON Schema, it is expressed as *minLength*, *minProperties*, *minItems* depending on the type.

.. class:: IsMultipleOf(value)

   :class:`Constraint` that allows only numbers that are integer multiples of *value*.

   Raises :exc:`ValueError` if *value* is not positive.

   It is expressed as *multipleOf* in JSON Schema.

.. class:: IsShorterThanOrEqual(maximum)

   :class:`Constraint` that only allows values shorter than or equal to *maximum*.

    In JSON Schema, it is expressed as *maxLength*, *maxProperties*, *maxItems* depending on the type.

.. class:: JsonSchema(value_or_type = dataclasses.MISSING, *, ctx: Context = None)

   A subclass of :class:`Object` representing `JSON Schema <https://json-schema.org/>`_.

   The constructor takes a JSON Schema representation or type as the *value_or_type* parameter.
   Passing a type gives you a JSON Schema representation of that type.

   .. classmethod:: register(type)

.. class:: JsonValue

   This is a type that represents a JSON value recursively.

   You cannot create an instance, you can only type cast with :func:`cast`.

   Values converted to this type can be passed directly to :func:`json.dumps` and :func:`json.dump` in the standard library. 

.. class:: NoneOf(arg: Constraint, *args: Constraint)

   :Class:`Constraint` which must not satisfy any of the constraints passed as arguments.

.. class:: Object(value = dataclasses.MISSING, /, *, ctx: Context = None, **kwargs)

   Represents an object model with typed fields.

   When a value is passed as *value*, ``Object(value, ctx=ctx)`` is equivalent to ``cast(Object, value, ctx=ctx)``.
   
   If no value is passed as *value*, no type checking is performed, and only fields with *default_factory* are created as instance attributes.

   By design, it mimics :func:`dataclasses.dataclass`.
   However, there are several differences:
   
   - Unlike :func:`dataclasses.dataclass`, it must inherit :class:`Object`.
   - The signature of the constructor is different.
   - Unlike :func:`dataclasses.dataclass`, there is a concept of missing fields. So you may get :exc:`AttributeError` when trying to read an instance attribute.
   - :func:`field` supports different feature sets.


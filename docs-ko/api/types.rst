타입 캐스팅
================

.. py:currentmodule:: typeable

여기에서는 :func:`cast` 의 첫번째 인자로 전달될 수 있는 형들과, 그들의 변환 규칙을 설명합니다.
원칙적으로 모든 형은 자신과 같은 형을 갖는 값을 받아들여야 합니다. 때문에 이는 따로 설명하지 않습니다.
설명에서 ``val`` 은 :func:`cast` 에서 두 번째 인자로 전달된 값을 뜻합니다.

각 형의 설명은 다른 형이 대상 형으로 변환되는 규칙만 설명할 뿐, 다른 형으로 변환되는 규칙을 설명하지는 않습니다.
예를 들어, ``cast(int, '123')`` 변환은 ``int`` 에서 설명하고, ``cast(str, 123)`` 변환은 ``str`` 에서 설명합니다.

직접 지원되지 않는 형이 :func:`cast` 의 첫번째 인자로 전달되면, 가장 가까운 베이스 클래스의 규칙이 적용됩니다.
예를 들어, 베이스 클래스를 정의하지 않은 사용자 정의 클래스는 ``object`` 의 규칙을 따르고, :class:`int` 를 계승하는 클래스는 ``int`` 의 규칙을 따릅니다.
따라서 ``int`` 의 설명에서 ``int(val)`` 을 호출한다고 할 때 ``int`` 는 사용자 정의 형으로 대체된다고 해석해야 합니다.
사용자 정의 형이 베이스 클래스의 규칙을 따르지 않는다면, :func:`typeable.cast.register` 로 특수화(specialization)해야 합니다.

``val`` 에도 같은 규칙이 적용됩니다. 
예를 들어, ``enum.IntEnum`` 이 설명에서 :class:`int` 를 받아들인다고 할 때는 ``isinstance(val, int)`` 가 참인 것을 받아들인다는 뜻입니다. 
``val`` 로 전달되는 사용자 정의 형 인스턴스가 이 규칙을 따르지 않는다면, 역시 :func:`typeable.cast.register` 로 특수화할 수 있습니다.

표준 형
----------

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

    ``int(val)`` 를 실행합니다. 이는 :class:`int`, :class:`float`, :class:`str` 뿐만 아니라 :class:`int` 변환을 지원하는 사용자 정의형도 받아들인다는 뜻입니다.

    :attr:`~typeable.Context.bool_is_int` 가 :const:`False` 이면 :class:`bool` 을 받아들이지 않습니다.

    :attr:`~typeable.Context.lossy_conversion` 이 :const:`False` 이면 소부수가 있는 :class:`float` 를 받아들이지 않습니다.

:class:`enum.IntEnum`
    
    ``enum.IntEnum(val)`` 을 실행합니다. 이는 :class:`int` 를 받아들인다는 뜻입니다.
    하지만 정확히는 열거형 필드와 같다고 비교될 수 있는 값은 모두 받아들입니다. 따라서 소수부가 없는 
    :class:`float` 값도 허용할 수 있습니다. 

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


Typeable 형
------------

:class:`Object`


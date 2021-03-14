타입 캐스팅
================

.. py:currentmodule:: typeable

여기에서는 :func:`cast` 의 첫번째 인자로 전달될 수 있는 형들과, 그들의 변환 규칙을 설명합니다.
원칙적으로 모든 형은 자신과 같은 형을 갖는 값을 받아들여야 합니다. 때문에 이는 따로 설명하지 않습니다.
설명에서 ``val`` 은 :func:`cast` 에서 두 번째 인자로 전달된 값을 뜻합니다.

직접 지원되지 않는 형이 :func:`cast` 의 첫번째 인자로 전달되면, 가장 가까운 베이스 클래스의 규칙이 적용됩니다.
예를 들어, 베이스 클래스를 정의하지 않은 사용자 정의 클래스는 ``object`` 의 규칙을 따르고, :class:`int` 를 계승하는 클래스는 ``int`` 의 규칙을 따릅니다.
따라서 ``int`` 의 설명에서 ``int(val)`` 을 호출한다고 할 때 ``int`` 는 사용자 정의 형으로 대체된다고 해석해야 합니다.
사용자 정의 형이 베이스 클래스의 규칙을 따르지 않는다면, :func:`typeable.cast.register` 로 특수화(specialization)해야 합니다.

``val`` 에도 같은 규칙이 적용됩니다. 
예를 들어, ``enum.IntEnum`` 이 설명에서 :class:`int` 를 받아들인다고 할 때는 ``isinstance(val, int)`` 가 참인 것을 받아들인다는 뜻입니다. 
``val`` 로 전달되는 사용자 정의 형 인스턴스가 이 규칙을 따르지 않는다면, 역시 :func:`typeable.cast.register` 로 특수화할 수 있습니다.

빌트인 형
-------------

:class:`bool`

:class:`bytearray`

:class:`bytes`

:class:`complex`

:class:`dict`

:class:`float`

:class:`frozenset`

:class:`int`

    :class:`int`, :class:`bool`, :class:`float`, :class:`str` 과 양방향 변환됩니다.

    그 외의 형에 대해서는 ``int(val)`` 를 실행합니다. 
    이는 :class:`int` 변환을 지원하는 사용자 정의형을 모두 받아들인다는 뜻입니다.
    이 경우 반대 방향의 변환은 사용자 정의형의 구현에 달렸습니다.

    :attr:`~typeable.Context.bool_is_int` 가 :const:`False` 이면 :class:`bool` 을 받아들이지 않습니다.

    :attr:`~typeable.Context.lossy_conversion` 이 :const:`False` 이면 소수부가 있는 :class:`float` 를 받아들이지 않고, 0 과 1 이외의 정수가 :class:`bool` 로 변환되지도 않습니다.

:class:`list`

:data:`None`

:class:`object`
    
:class:`set`

:class:`str`

:class:`tuple`

    
표준 라이브러리 형
--------------------------

:mod:`datetime`
~~~~~~~~~~~~~~~

:class:`datetime.date`

:class:`datetime.datetime`

:class:`datetime.time`

:class:`datetime.timedelta`

:mod:`enum`
~~~~~~~~~~~

:class:`enum.Enum`

    열거형 멤버의 **이름**\ 으로 :class:`str` 과 양방향 변환됩니다.

    :class:`enum.Enum` 을 포함한 그 외의 모든 형에 대해서는 ``enum.Enum(val)`` 을 실행합니다.
    이 때문에 ``None`` 을 값으로 갖는 :class:`enum.Enum` 은 ``None`` 도 받아들이게 됩니다.
    이 경우는 반대 방향의 변환이 제공되지 않습니다.

:class:`enum.IntEnum`
    
    :class:`str` 과의 상호 변환은 :class:`enum.Enum` 처럼 동작합니다.

    여기에 더해, 열거형 멤버의 **값**\ 으로 :class:`int` 와 양방향 변환됩니다.

:class:`enum.IntFlag`
    
    열거형 멤버의 **값**\ 으로 :class:`int` 와 양방향 변환됩니다.

    :class:`enum.IntEnum` 과는 달리 :class:`str` 과의 상호 변환은 지원되지 않습니다.

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


Typeable 형
------------

:class:`Object`


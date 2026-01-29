타입 캐스팅
================

.. py:currentmodule:: typeable

여기에서는 :func:`deepcast` 의 첫번째 인자로 전달될 수 있는 형들과, 그들의 변환 규칙을 설명합니다.
원칙적으로 모든 형은 자신과 같은 형을 갖는 값을 받아들여야 합니다. 때문에 이는 따로 설명하지 않습니다.
설명에서 ``val`` 은 :func:`deepcast` 에서 두 번째 인자로 전달된 값을 뜻합니다.

직접 지원되지 않는 형이 :func:`deepcast` 의 첫번째 인자로 전달되면, 가장 가까운 베이스 클래스의 규칙이 적용됩니다.
예를 들어, 베이스 클래스를 정의하지 않은 사용자 정의 클래스는 ``object`` 의 규칙을 따르고, :class:`int` 를 계승하는 클래스는 ``int`` 의 규칙을 따릅니다.
따라서 ``int`` 의 설명에서 ``int(val)`` 을 호출한다고 할 때 ``int`` 는 사용자 정의 형으로 대체된다고 해석해야 합니다.
사용자 정의 형이 베이스 클래스의 규칙을 따르지 않는다면, :func:`deepcast.register` 로 특수화(specialization)해야 합니다.

``val`` 에도 같은 규칙이 적용됩니다. 
예를 들어, ``enum.IntEnum`` 이 설명에서 :class:`int` 를 받아들인다고 할 때는 ``isinstance(val, int)`` 가 참인 것을 받아들인다는 뜻입니다. 
``val`` 로 전달되는 사용자 정의 형 인스턴스가 이 규칙을 따르지 않는다면, 역시 :func:`deepcast.register` 로 특수화할 수 있습니다.

빌트인 형
-------------

:class:`bool`

    :class:`int`, :class:`str` 과 양방향 변환됩니다.

    :class:`bool` 이 :class:`str` 로 변환될 때는 ``"True"`` 나 ``"False"`` 로 변환됩니다.
    :class:`str` 을 :class:`bool` 로 변환할 때는 먼저 소문자로 변환한 후 :attr:`~typeable.Context.bool_strings` 딕셔너리에서 찾습니다. 
    이 딕셔너리가 비어있으면 :exc:`TypeError` 를, 비어있지 않지만 해당 문자열의 키가 없다면 :exc:`ValueError` 를 발생시킵니다.

    :attr:`~typeable.Context.bool_is_int` 가 :const:`False` 이면, :class:`int` 와의 변환이 금지됩니다.

    :attr:`~typeable.Context.lossy_conversion` 이 :const:`False` 이면, 0 과 1 이외의 :class:`int` 가 :class:`bool` 로 변환되지 않습니다.

    :class:`bool` 에서 :class:`float` 로의 단방향 변환이 지원됩니다. 
    :attr:`~typeable.Context.lossy_conversion` 이 :const:`False` 이면, 0 과 1 이외의 값은 변환되지 않습니다.
    이마저도 :attr:`~typeable.Context.bool_is_int` 가 :const:`False` 이면 금지됩니다.

:class:`bytearray`

:class:`bytes`

:class:`complex`

    ``tuple[float,float]``, :class:`str` 과 양방향 변환됩니다.

    :class:`int`, :class:`float` 에서 :class:`complex` 로의 단방향 변환이 지원됩니다.

    :attr:`~typeable.Context.accept_nan` 이 :const:`False` 이면 :func:`cmath.isfinite` 가 참을 반환하는 값만 받아들입니다.

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

:class:`type`

    :class:`str` 과 양방향 변환됩니다.

    형 객체를 :class:`str` 로 변환할 때 :term:`완전히 정규화된 이름 <qualified name>` 으로 변환됩니다.
    내장형은 :mod:`builtins` 모듈이 모듈 이름으로 사용됩니다.

    :class:`str` 에서 형 객체로 변환할 때 :term:`완전히 정규화된 이름 <qualified name>` 을 받아들입니다.
    다만 내장형은 :mod:`builtins` 를 생략할 수 있습니다.

    *val* 이 형이면 형 검사만 수행한 후 *val* 을 그대로 반환합니다.

    제네릭 형 매개 변수가 주어지면 공변적(covariant)으로 해석합니다.
    즉 형 매개 변수의 서브 클래스를 모두 받아들입니다.

    :exc:`TypeError` 뿐만 아니라, :exc:`ImportError` 나 :exc:`AttributeError` 도 발생할 수 있습니다.

표준 라이브러리 형
--------------------------

:mod:`dataclasses`
~~~~~~~~~~~~~~~~~~

@dataclass 로 데코레이트한 모든 클래스들은 :class:`dict` 와 양방향 변환됩니다.

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

:class:`enum.Flag`
    
    열거형 멤버의 **값**\ 으로 :class:`int` 와 양방향 변환됩니다.

    :class:`enum.Enum` 과는 달리 :class:`str` 과의 상호 변환은 지원되지 않습니다.

:class:`enum.IntEnum`
    
    :class:`str` 과의 상호 변환은 :class:`enum.Enum` 처럼 동작합니다.

    여기에 더해, 열거형 멤버의 **값**\ 으로 :class:`int` 와 양방향 변환됩니다.

:class:`enum.IntFlag`
    
    열거형 멤버의 **값**\ 으로 :class:`int` 와 양방향 변환됩니다.

    :class:`enum.IntEnum` 과는 달리 :class:`str` 과의 상호 변환은 지원되지 않습니다.

:mod:`typing`
~~~~~~~~~~~~~

:data:`typing.Annotated`

    형 ``T`` 는 형 힌트 ``Annotated[T, x]`` 를 통해 메타 데이터 ``x`` 로 어노테이트될 수 있습니다.

    ``x`` 가 :class:`Constraint` 의 인스턴스면, :func:`deepcast` 는 형 변환 후의 값이 ``x`` 가 정의하는 제약 조건을 만족하는지 검사합니다.
    또한, 이 제약 조건은 :class:`JsonSchema` 에도 반영됩니다.

    메타 데이터가 여러개가 제공되면 모든 제약 조건을 만족해야 합니다.

    ``x`` 가 :class:`Constraint` 의 인스턴스가 아니면 무시합니다.

    :data:`typing.Annotated` 는 파이썬 3.9에 추가되었기 때문에, :mod:`typeable.typing` 모듈에서 역이식을 제공합니다.

    현재 Typeable 은 다음과 같은 :class:`Constraint` 서브 클래스를 제공합니다:

    :class:`AllOf`, :class:`AnyOf`, :class:`NoneOf`, :class:`IsFinite`, :class:`IsGreaterThan`,
    :class:`IsGreaterThanOrEqual`, :class:`IsLessThan`, :class:`IsLessThanOrEqual`, :class:`IsLongerThanOrEqual`,
    :class:`IsMatched`, :class:`IsMultipleOf`, :class:`IsShorterThanOrEqual`.

:data:`typing.Any`

    ``val`` 을 변환이나 검사 없이 그대로 통과시킵니다.

:class:`typing.Dict`

:class:`typing.ForwardRef`

    제네릭 형의 형 매개 변수에 등장하는 :class:`typing.ForwardRef` 는 Typeable 이 자동 평가합니다.

    :class:`typing.ForwardRef` 는 그 스스로 어떤 형을 표현하는 것이 아니라, 어떤 형에 대한 평가를 지연시키기 위한 문자열 전방 참조를 전달하는 매개체일 뿐입니다.
    (불가능하지는 않지만) 보통 사용자가 직접 :class:`typing.ForwardRef` 의 인스턴스를 만들지는 않고, 제네릭 형을 사용할 때 형 매개 변수에 문자열을 전달하면 자동으로 만들어집니다. :mod:`typing` 모듈에서 제공되는 지원은 :term:`어노테이션 <annotation>` 영역으로 제한됩니다. 

    Typeable 은 :term:`어노테이션 <annotation>` 이외의 영역에서 전방 참조를 사용할 수 있도록 :func:`declare` 컨택스트 관리자를 제공합니다.

:class:`typing.FrozenSet`

:class:`typing.List`

:data:`typing.Literal`

    ``val`` 과 일치하는 리터럴이 있으면 리터럴을 반환하고, 그렇지 않으면 :exc:`ValueError` 를 발생시킵니다.

    :data:`typing.Literal` 은 파이썬 3.8에 추가되었기 때문에, :mod:`typeable.typing` 모듈에서 역이식을 제공합니다.

:data:`typing.Optional`

    :data:`typing.Optional` 은 :data:`typing.Union` 으로 자동 변환됩니다.

:class:`typing.Set`

:data:`typing.Tuple`

:class:`typing.Type`

    :class:`type` 의 변환 규칙과 같습니다.

:data:`typing.Union`


Typeable 형
------------

:class:`JsonSchema`

    `JSON Schema <https://json-schema.org/>`_ 를 표현하는 :class:`Object` 의 서브 클래스.

:class:`JsonValue`

    JSON 값을 재귀적으로 표현하는 형입니다.

    값을 :class:`float`, :class:`bool`, :class:`int`, :class:`str`, :const:`None`, ``dict[str, JsonValue]``, ``list[JsonValue]``, ``tuple[JsonValue, ...]`` 중 하나로 변환합니다.

:class:`Object`

    :class:`dict` 와 양방향 변환됩니다.

    :class:`dict` 가 :class:`Object` 로 변환될 때 정의되지 않은 키는 무시됩니다. 
    *required* 가 :const:`True` 로 지정된 필드가 빠졌으면, :exc:`TypeError` 를 발생시킵니다.
    *default_factory* 를 지정하는 필드가 빠졌으면, 값을 만들어 인스턴스 어트리뷰트에 대입합니다. 

    :class:`Object` 가 :class:`dict` 로 변환될 때 :class:`Object` 인스턴스 어트리뷰트만 제공됩니다. 
    인스턴스 어트리뷰트로 대입되지 않은 필드들은 포함되지 않습니다.
    *default* 가 정의되어서 어트리뷰트을 읽을 수 있어도, 인스턴스 어트리뷰트로 대입되지 않았다면 포함되지 않습니다.

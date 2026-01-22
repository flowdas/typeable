개발자 인터페이스
=========================

.. py:currentmodule:: typeable

이 패키지는 다음과 같은 함수와 데코레이터를 정의합니다:

.. function:: deepcast(typ: typing.Type[_T], val: object, *, ctx: Context = None) -> _T

   값을 형으로 캐스트합니다.

   지정한 형으로 변환한 값을 반환합니다. :term:`어노테이션 <annotation>` 에 사용될 수 있는 것은 모두
   *typ* 으로 사용할 수 있습니다. 

   변환 규칙은 가능한한 표준 파이썬 규칙을 따르려고 시도합니다. 하지만 *ctx* 를 사용하여 규칙을 변경할 수 
   있습니다.

   변환 규칙이 변환을 허락하지 않으면, :exc:`TypeError` 나 :exc:`ValueError` 와 같은 다양한 표준 
   예외가 발생할 수 있습니다. 원한다면, *ctx* 를 사용하여 에러가 발생한 *val* 에서의 위치를 얻을 수 
   있습니다. 

   .. decorator:: deepcast.function(user_function)
                  deepcast.function(*, ctx_name: str = 'ctx', cast_return: bool = False, keep_async: bool = True)

      함수의 인자를 타입 캐스팅하는 데코레이터.

      데코레이트된 함수를 호출하면 :term:`어노테이션 <annotation>` 이 있는 인자들을 타입 캐스팅해서 원래 함수를 호출합니다.
      :term:`어노테이션 <annotation>` 이 없는 인자들은 그대로 전달합니다.

      반환값의 :term:`어노테이션 <annotation>` 이 있어도 반환값은 타입 캐스팅하지 않는 것이 기본 동작입니다.
      *cast_return* 이 참이고 반환값의 :term:`어노테이션 <annotation>` 이 있으면 반환값도 타입 캐스팅합니다.
      
      :func:`Context.capture` 로 에러 위치를 추적할 때 ``location`` 어트리뷰트에는 인자의 이름이 제공됩니다.
      반환값에서 에러가 발생했으면 ``"return"`` 이 사용됩니다.
      ``*args`` 나 ``**kwargs`` 와 같은 형태의 인자에 :term:`어노테이션 <annotation>` 이 제공되면, 먼저 인자의 이름이 제공된 후 인덱스나 키워드 이름이 추가됩니다.

      데코레이트된 함수는 :class:`Context` 인스턴스를 받는 *ctx* 인자를 추가로 얻습니다.
      원래 함수에 이미 *ctx* 라는 이름의 인자가 있으면 :exc:`TypeError` 를 발생시킵니다.
      이 이름을 변경하려면 *ctx_name* 인자로 이름을 지정합니다.
      원래 함수가 *ctx* 인자를 직접 받고자 한다면 :class:`Context` 형으로 :term:`어노테이션 <annotation>` 을 제공해야 합니다.
      이 경우 *ctx* 에 :const:`None` 이 전달되면 새 인스턴스를 만들어 전달합니다.

      메서드에도 사용될 수 있습니다.
      :func:`deepcast.function` 이 다른 메서드 디스크립터와 함께 적용될 때, 가장 안쪽의 데코레이터로 적용되어야 합니다.

      :term:`코루틴 함수 <coroutine function>` 에도 사용될 수 있습니다.
      이 경우 데코레이트된 함수도 :term:`코루틴 함수 <coroutine function>` 입니다.
      하지만 *keep_async* 매개 변수가 :const:`False` 이면, 데코레이트된 함수는 원래 함수를 즉시 호출하여 :term:`어웨이터블 <awaitable>` 을 반환하는 동기 함수가 됩니다.
      타입 캐스팅으로 인한 에러를 일찍 발생시키려는 목적으로 사용합니다.

   .. decorator:: deepcast.register(impl)

.. function:: declare(name: str)

   전방 참조를 사용하여 재귀적 :term:`형 애일리어스 <type alias>` 를 정의할 수 있도록 지원하는 :term:`컨택스트 관리자 <context manager>`.

   *name* 인자로 제공된 이름의 :class:`typing.ForwardRef` 인스턴스를 :keyword:`with` 문의 :keyword:`as` 대상으로 제공합니다.
   이 값을 제네릭 형의 형 매개 변수에 사용하면 :keyword:`with` 문을 빠져나갈 때 전방 참조가 자동 평가됩니다.
   
   전역 애일리어스뿐만 아니라 지역 애일리어스에도 사용할 수 있습니다.

.. function:: dump(obj: JsonValue, fp, *, ensure_ascii=False, separators=(',', ':'), **kw)

   표준 라이브러리 :func:`json.dump` 함수의 *obj* 인자를 :class:`JsonValue` 로 자동 변환하는 버전.
   
   *ensure_ascii* 와 *separators* 의 기본값을 변경했습니다.

.. function:: dumps(obj: JsonValue, *, ensure_ascii=False, separators=(',', ':'), **kw)

   표준 라이브러리 :func:`json.dumps` 함수의 *obj* 인자를 :class:`JsonValue` 로 자동 변환하는 버전.
   
   *ensure_ascii* 와 *separators* 의 기본값을 변경했습니다.

.. function:: field(*, key=None, default=dataclasses.MISSING, default_factory=None, nullable=None, required=False, kind=False)

.. function:: fields(class_or_instance)

이 패키지는 여러 클래스를 정의합니다. 아래에 나오는 절에서 자세히 설명합니다.

.. class:: AllOf(arg: Constraint, *args: Constraint)

   인자로 전달된 모든 제약 조건들을 모두 만족해야하는 :class:`Constraint`.

.. class:: AnyOf(arg: Constraint, *args: Constraint)

   인자로 전달된 제약 조건 중 하나 이상을 만족해야하는 :class:`Constraint`.

.. class:: Constraint()

   실행 시간에 검사되는 제약 조건들의 베이스 클래스.

   :data:`typing.Annotated` 에 제공되는 메타 데이터로 사용됩니다.

   이 용도 외에 사용자가 :class:`Constraint` 의 인스턴스를 직접 다룰 일은 없습니다.
   다음 인터페이스는 :class:`Constraint` 의 서브 클래스를 만들어 새로운 제약 조건을 정의하고자 할 때만 필요합니다.

   .. method:: annotate(root: JsonSchema, schema: JsonSchema)

      제약 조건을 *schema* 인자로 전달된 JSON Schema 에 추가합니다.

      *root* 는 :data:`typing.Annotated` 로 정의된 형의 JSON Schema 인스턴스 입니다.

   .. method:: compile()

      제약 조건을 평가하는 콜러블을 반환합니다.

      콜러블은 :func:`deepcast` 가 캐스팅한 후의 값을 인자로 취합니다.
      콜러블의 반환값이 참으로 평가되면 제약 조건을 만족하는 것으로 해석합니다.
      거짓을 반환하거나 예외를 발생시키면 제약 조건을 만족하지 않는 것으로 해석합니다.

   .. method:: emit()

      제약 조건을 표현하는 문자열을 반환합니다.

      표현식은 검사하고자 하는 인자가 ``x`` 라는 변수로 제공된다고 가정해야 합니다.
      예를 들어, ``"(x > 0)"``.

      표현식이 모듈을 참조한다면, :meth:`emit` 는 ``(expr, ns)`` 2-튜플을 반환할 수 있습니다.
      ``expr`` 은 표현식이고, ``ns`` 는 키가 모듈 이름이고, 값이 모듈 인스턴스인 매핑 입니다.

.. class:: Context(**policies)

   :class:`Context` 객체를 :func:`deepcast` 에 전달하여 기본 변환 규칙을 변경하거나 변환 중에 발생한
   에러의 위치를 찾을 수 있습니다. 

   *policies* 에 전달된 키워드 전용 파라미터는 변환 규칙을 변경하는데 사용됩니다. 이 파라미터는 
   :class:`Context` 인스턴스의 어트리뷰트로 제공됩니다. :class:`Context` 를 서브클래싱해서
   파라미터의 기본값을 변경하거나, 새 파라미터를 추가할 수 있습니다. 현제 정의된 파라미터는 다음과 같습니다:

   .. attribute:: bool_is_int
      :type: bool 
      :value: True

      이 어트리뷰트가 :const:`False` 면, :class:`bool` 을 :class:`int` 로 취급하지 않습니다. 

   .. attribute:: bool_strings
      :type: dict[str, bool]
      :value: {'0': False, '1': True, 'f': False, 'false': False, 'n': False, 'no': False, 'off': False, 'on': True, 't': True, 'true': True, 'y': True, 'yes': True}

      :class:`bool` 로 변환될 수 있는 문자열들과 해당 :class:`bool` 값을 정의합니다.
      키는 모두 소문자여야 합니다. 
      딕셔너리를 조회할 때는 소문자로 변환한 값을 키로 사용합니다.

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

      이 어트리뷰트가 :const:`False` 면, 정보 손실을 수반하는 변환을 수행하지 않습니다. 
      예를 들어, ``deepcast(int, 1.2)`` 를 허락하지 않습니다.

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

   변환 중에 발생한 에러의 위치는 :meth:`capture` 로 찾을 수 있습니다.

   :class:`Context` 인스턴스는 스레드 안전하지도 :term:`코루틴 <coroutine>` 안전하지도 않습니다.
   같은 인스턴스를 여러 스레드나 코루틴에서 동시에 사용하지 않도록 주의하십시오. 하지만 순차적인 :func:`deepcast`
   호출에서 반복적으로 사용하는 것은 안전합니다.

   .. method:: capture()

      변환 중에 발생한 에러의 위치를 추적합니다. :term:`컨텍스트 관리자 <context manager>` 이기
      때문에, :keyword:`with` 문과 함께 사용해야 합니다. 에러 객체가 :keyword:`with` 문의 
      :keyword:`as` 대상으로 전달됩니다. 에러 객체는 ``location`` 어트리뷰트를 제공하는데, 에러가 
      발생했으면 :class:`tuple` 이고, 발생하지 않았으면 :const:`None` 입니다. ``location`` 은
      에러 위치에 도달하는데 필요한 인덱스나 키의 튜플입니다. 예를 들어:

          >>> from typing import Dict, List
          >>> from typeable import *
          >>> ctx = Context()
          >>> with ctx.capture() as error:
          ...     data = deepcast(Dict[str,List[int]], {"a":[], "b":[0,"1",None,3]}, ctx=ctx)
          Traceback (most recent call last):
              ...
          TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
          >>> error.location
          ('b', 2)

   .. method:: traverse(key)

.. class:: IsFinite()

   유한한 숫자만을 허락하는 :class:`Constraint`.

   :class:`int`, :class:`float`, :class:`complex` 형에만 적용되고, NaN 이나 무한을 허락하지 않습니다.

   표준 JSON 은 NaN 이나 무한을 허락하지 않기 때문에, JSON Schema 에는 반영되지 않습니다.

.. class:: IsGreaterThan(exclusive_minimum)

   *exclusive_minimum* 보다 큰 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 *exclusiveMinimum* 으로 표현됩니다.

.. class:: IsGreaterThanOrEqual(minimum)

   *minimum* 보다 크거나 같은 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 *minimum* 으로 표현됩니다.

.. class:: IsLessThan(exclusive_maximum)

   *exclusive_maximum* 보다 작은 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 *exclusiveMaximum* 으로 표현됩니다.

.. class:: IsLessThanOrEqual(maximum)

   *maximum* 보다 작거나 같은 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 *maximum* 으로 표현됩니다.

.. class:: IsLongerThanOrEqual(minimum)

   *minimum* 보다 길거나 같은 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 형에 따라 *minLength*, *minProperties*, *minItems* 로 표현됩니다.

.. class:: IsMatched(pattern)

   정규식 *pattern* 과 일치하는 문자열만 허락하는 :class:`Constraint`.

   정규식은 묵시적으로 앵커링되지 않습니다. 즉, :func:`re.search` 로 일치를 검사합니다.

   JSON Schema 에는 *pattern* 으로 표현됩니다.

.. class:: IsMultipleOf(value)

   *value* 의 정수배인 숫자만 허락하는 :class:`Constraint`.

   *value* 가 양수가 아니면 :exc:`ValueError` 를 발생시킵니다.

   JSON Schema 에는 *multipleOf* 로 표현됩니다.

.. class:: IsShorterThanOrEqual(maximum)

   *maximum* 보다 짧거나 같은 값만 허락하는 :class:`Constraint`.

   JSON Schema 에는 형에 따라 *maxLength*, *maxProperties*, *maxItems* 로 표현됩니다.

.. class:: JsonSchema(value_or_type = dataclasses.MISSING, *, ctx: Context = None)

   `JSON Schema <https://json-schema.org/>`_ 를 표현하는 :class:`Object` 의 서브 클래스.

   생성자는 *value_or_type* 매개 변수로 JSON Schema 표현이나 형을 취합니다. 
   형을 전달하면 해당 형의 JSON Schema 표현을 얻게됩니다.

   .. classmethod:: register(type)

.. class:: JsonValue

   JSON 값을 재귀적으로 표현하는 형입니다.

   인스턴스를 만들 수는 없고 :func:`deepcast` 로 타입 캐스팅할 수만 있습니다.

   이 형으로 변환된 값은 표준 라이브러리의 :func:`json.dumps` 와 :func:`json.dump` 로 직접 전달할 수 있습니다. 

.. class:: NoneOf(arg: Constraint, *args: Constraint)

   인자로 전달된 제약 조건 중 어느 것도 만족하지 않아야 하는 :class:`Constraint`.

.. class:: Object(value = dataclasses.MISSING, /, *, ctx: Context = None, **kwargs)

   형이 지정된 필드를 갖는 객체 모델을 표현합니다.

   *value* 로 값이 전달되면, ``Object(value, ctx=ctx)`` 는 ``deepcast(Object, value, ctx=ctx)`` 와 동등합니다.
   
   *value* 로 값이 전달되지 않으면 형 검사를 수행하지 않고, *default_factory* 가 지정된 필드만 인스턴스 어트리뷰트로 만들어집니다.

   의도적으로 :func:`dataclasses.dataclass` 를 모방합니다.
   하지만 여러가지 차이점이 있습니다:
   
   - :func:`dataclasses.dataclass` 와는 달리 :class:`Object` 를 계승해야 합니다.
   - 생성자의 서명이 다릅니다.
   - :func:`dataclasses.dataclass` 와는 달리 빠진 필드라는 개념이 있습니다. 따라서 인스턴스 어트리뷰트를 읽으려고 할 때 :exc:`AttributeError` 가 발생할 수 있습니다.
   - :func:`field` 가 지원하는 기능 집합이 다릅니다.


   
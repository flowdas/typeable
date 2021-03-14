개발자 인터페이스
=========================

.. py:currentmodule:: typeable

이 패키지는 다음과 같은 함수와 데코레이터를 정의합니다:

.. function:: cast(typ: typing.Type[_T], val: object, *, ctx: Context = None) -> _T

   값을 형으로 캐스트합니다.

   지정한 형으로 변환한 값을 반환합니다. :term:`어노테이션 <annotation>` 에 사용될 수 있는 것은 모두
   *typ* 으로 사용할 수 있습니다. 

   변환 규칙은 가능한한 표준 파이썬 규칙을 따르려고 시도합니다. 하지만 *ctx* 를 사용하여 규칙을 변경할 수 
   있습니다.

   변환 규칙이 변환을 허락하지 않으면, :exc:`TypeError` 나 :exc:`ValueError` 와 같은 다양한 표준 
   예외가 발생할 수 있습니다. 원한다면, *ctx* 를 사용하여 에러가 발생한 *val* 에서의 위치를 얻을 수 
   있습니다. 

.. decorator:: typeable.cast.register

.. function:: declare(name: str)

.. function:: field(*, key=None, default=MISSING, default_factory=None, nullable=None, required=False)

.. function:: fields(class_or_instance)

이 패키지는 다음과 같은 상수를 정의합니다.

.. data:: MISSING


이 패키지는 몇 가지 클래스를 정의합니다. 아래에 나오는 절에서 자세히 설명합니다.

.. class:: Context(**policies)

   :class:`Context` 객체를 :func:`cast` 에 전달하여 기본 변환 규칙을 변경하거나 변환 중에 발생한
   에러의 위치를 찾을 수 있습니다. 

   *policies* 에 전달된 키워드 전용 파라미터는 변환 규칙을 변경하는데 사용됩니다. 이 파라미터는 
   :class:`Context` 인스턴스의 어트리뷰트로 제공됩니다. :class:`Context` 를 서브클래싱해서
   파라미터의 기본값을 변경하거나, 새 파라미터를 추가할 수 있습니다. 현제 정의된 파라미터는 다음과 같습니다:

   .. attribute:: accept_nan 
      :type: bool 
      :value: True

   .. attribute:: bool_is_int
      :type: bool 
      :value: True

      이 어트리뷰트가 :const:`False` 면, :class:`bool` 을 :class:`int` 로 취급하지 않습니다.  

   .. attribute:: bool_strings
      :type: dict[str, bool]
      :value: {'0': False, '1': True, 'f': False, 'false': False, 'n': False, 'no': False, 'off': False, 'on': True, 't': True, 'true': True, 'y': True, 'yes': True}

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
      예를 들어, ``cast(int, 1.2)`` 를 허락하지 않습니다.

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
   같은 인스턴스를 여러 스레드나 코루틴에서 동시에 사용하지 않도록 주의하십시오. 하지만 순차적인 :func:`cast`
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
          ...     data = cast(Dict[str,List[int]], {"a":[], "b":[0,"1",None,3]}, ctx=ctx)
          Traceback (most recent call last):
              ...
          TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
          >>> error.location
          ('b', 2)

   .. method:: traverse(key)

.. class:: Object(value = MISSING, *, ctx: Context = None)


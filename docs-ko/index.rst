.. Typeable documentation master file, created by

Typeable: Type Casting Simplified
=================================

Release v\ |version|. (:ref:`설치 <install>`)

**Typeable** 은 간결하면서도 풍부한 표현을 제공하는 파이썬 타입 캐스팅 라이브러리입니다.

-------------------

::

   >>> data = {'a': ["0", True, 2, 3.14], 'b': range(4)}
   >>> DataType = dict[str,list[typing.Union[bool,float,int]]]
   >>> typeable.cast(DataType, data)
   {'a': [False, True, 2, 3.14], 'b': [0, 1, 2, 3]}

   >>> with typeable.declare('Json') as _J:
   ...     Json = typing.Union[float, bool, int, str, None, dict[str, _J], list[_J]]
   >>> json.dumps(typeable.cast(Json, data))
   '{"a": ["0", true, 2, 3.14], "b": [0, 1, 2, 3]}'

   >>> class X(typeable.Object):
   ...     a: list[bool]
   ...     b: list[int]
   >>> ctx = typeable.Context()
   >>> with ctx.capture() as error:
   ...     x = X(data, ctx=ctx)
   Traceback (most recent call last):
       ...
   TypeError: No implementation found for 'bool' from float
   >>> error.location
   ('a', 3)

**Typeable** 은 파이썬의 :term:`어노테이션 <annotation>` 문법을 사용하여 실행 시간 타입 캐스팅을 구현합니다.
실용적인 관점으로 접근하고, 단순함을 사랑합니다.

사용자 설명서
-------------------

.. toctree::
   :maxdepth: 2

   user/install

API 레퍼런스
----------------

.. toctree::
   :maxdepth: 2

   api/index


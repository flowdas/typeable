from collections.abc import Iterable, Mapping

from .._typecast import DeepCast, JsonValue, deepcast, traverse


@deepcast.register
def JsonValue_from_Mapping(
    deepcast: DeepCast, cls: type[JsonValue], val: Mapping
) -> JsonValue:
    return deepcast(dict[str, JsonValue], val)  # type: ignore


@deepcast.register
def JsonValue_from_Iterable(
    deepcast: DeepCast, cls: type[JsonValue], val: Iterable
) -> JsonValue:
    patch = {}
    for i, v in enumerate(val):
        with traverse(i):
            cv = deepcast(JsonValue, v)
            if cv is not v:
                patch[i] = cv
    if patch:
        val = list(patch.get(i, v) for i, v in enumerate(val))
    if not isinstance(val, (list, tuple)):
        val = list(val)
    return val  # type: ignore


@deepcast.register
def JsonValue_from_object(
    deepcast: DeepCast, cls: type[JsonValue], val: object
) -> JsonValue:
    return deepcast(dict[str, JsonValue], val)  # type: ignore

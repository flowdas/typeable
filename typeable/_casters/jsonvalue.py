from collections.abc import Iterable, Mapping

from .._typecast import JsonValue, Typecast, traverse, typecast


@typecast.register
def JsonValue_from_Mapping(
    deepcast: Typecast, cls: type[JsonValue], val: Mapping
) -> JsonValue:
    return deepcast(dict[str, JsonValue], val)  # type: ignore


@typecast.register
def JsonValue_from_Iterable(
    deepcast: Typecast, cls: type[JsonValue], val: Iterable
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


@typecast.register
def JsonValue_from_object(
    deepcast: Typecast, cls: type[JsonValue], val: object
) -> JsonValue:
    return deepcast(dict[str, JsonValue], val)  # type: ignore

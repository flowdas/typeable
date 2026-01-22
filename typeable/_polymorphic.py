from collections.abc import Callable, Mapping
from dataclasses import (
    dataclass,
    field as _field,
    fields,
    Field,
    MISSING,
    _FIELDS,  # type: ignore
)
from typing import (
    Any,
    Literal,
    Optional,
    TypeVar,
    get_origin,
    get_args,
    get_type_hints,
    overload,
)

_T = TypeVar("_T", bound=type)

# avoid name mangling
_POLYMORPHIC = "__polymorphic"


@overload
def polymorphic(cls: _T, /) -> _T: ...


@overload
def polymorphic(cls: None = None, /, *, on: str) -> Callable[[_T], _T]: ...


def polymorphic(_=None, /, *, on: str | None = None):
    def deco(cls: _T) -> _T:
        discriminator: str

        if _FIELDS not in cls.__dict__:
            cls = dataclass(cls)
        annotations: dict[str, Any] = cls.__annotations__
        if not annotations:
            raise TypeError(
                "@polymorphic requires a discriminator field, but nothing was found."
            )
        if on is None:
            names = annotations.keys() - set(_get_discriminator_names(cls))
            if len(names) > 1:
                raise TypeError(
                    "There is ambiguity in selecting the discriminator field. Please specify one using the ‘on’."
                )
            discriminator = list(names)[0]
        else:
            if on not in annotations:
                raise TypeError(f"discriminator field '{on}' not found.")
            if on in _get_discriminator_names(cls):
                raise TypeError(f"discriminator field '{on}' is already used.")
            discriminator = on
        field = None
        for f in fields(cls):
            if f.name == discriminator:
                field = f
                break
        assert field is not None
        if field.default is not MISSING or field.default_factory is not MISSING:
            raise TypeError("the discriminator field cannot have a default value.")
        next: _Polymorphic | None = getattr(cls, _POLYMORPHIC, None)
        if next and next.cls is cls:
            raise TypeError("duplicated @polymorphic")

        setattr(cls, _POLYMORPHIC, _Polymorphic(cls, field, next))
        setattr(cls, "__init_subclass__", classmethod(_init_subclass_))
        return cls

    if _ is None:
        return deco
    return deco(_)


def _init_subclass_(cls: type):
    mark: _Polymorphic = getattr(cls, _POLYMORPHIC)
    annotations: dict[str, Any] = cls.__annotations__
    if not annotations or mark.field.name not in annotations:
        raise TypeError(
            f"cannot find discriminator field '{cls.__name__}.{mark.field.name}'."
        )
    tp = get_type_hints(cls)[mark.field.name]
    if get_origin(tp) is not Literal:
        raise TypeError(
            f"non-Literal discriminator field '{cls.__name__}.{mark.field.name}'."
        )
    values = get_args(tp)
    for val in values:
        if not isinstance(val, mark.field.type):
            raise TypeError(f"{mark.field.type!r} required, but {val!r} is given")
        if val in mark.classes:
            raise TypeError(
                f"{cls.__qualname__}.{mark.field.name}'s descriptor value '{val}' is already defined by class {mark.classes[val].__qualname__}: {cls.__dict__.get('__polymorphic')}"
            )
    for val in values:
        mark.classes[val] = cls


@dataclass(slots=True)
class _Polymorphic:
    cls: type
    field: Field
    next: Optional["_Polymorphic"]
    classes: dict = _field(default_factory=dict)


def _get_discriminator_names(cls: type):
    names = []
    mark: _Polymorphic | None = getattr(cls, _POLYMORPHIC, None)
    while mark is not None:
        names.append(mark.field.name)
        mark = mark.next
    return names


def is_polymorphic(cls: type) -> bool:
    return _POLYMORPHIC in cls.__dict__


def _resolve_polymorphic(cls: _T, val: Mapping, ctx) -> _T:
    klass = cls
    while True:
        mark: _Polymorphic | None = getattr(klass, _POLYMORPHIC, None)
        if not mark or mark.cls is not klass:
            break
        value = val.get(mark.field.name, MISSING)
        if value is MISSING:
            with ctx.traverse(mark.field.name):
                raise TypeError(
                    f"discriminator '{klass.__qualname__}.{mark.field.name}' is missing"
                )
        if value not in mark.classes:
            with ctx.traverse(mark.field.name):
                raise TypeError(f"unknown discriminator value '{value}'")
        klass = mark.classes[value]
    return klass

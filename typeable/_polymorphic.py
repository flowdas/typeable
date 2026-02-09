from collections.abc import Callable, Mapping
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from inspect import Parameter, signature
from typing import TypeVar, overload

from ._error import traverse

_T = TypeVar("_T", bound=type)


def polymorphic(
    *, on: str, key: Callable[[str], str] | None = None
) -> Callable[[_T], _T]:
    def deco(cls: _T) -> _T:
        Polymorphic.install(cls, on=on, key=key)
        return cls

    return deco


def identity(id: str, /) -> Callable[[_T], _T]:
    def deco(cls: _T) -> _T:
        Polymorphic.register(cls, id)
        return cls

    return deco


_PM = "__polymorphic__"
_ID = "__identity__"


@dataclass
class Identity:
    pm: "Polymorphic"
    ids: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Polymorphic:
    cls: type
    name: str
    alias: str
    key: Callable[[str], str] | None
    default: str | None
    mapping: dict[str, type] = field(default_factory=dict)

    @staticmethod
    def install(cls: type, *, on: str, key: Callable[[str], str] | None):
        pms: list[Polymorphic] = [
            getattr(base, _PM) for base in cls.__mro__ if _PM in base.__dict__
        ]
        if pms and pms[0].cls is cls:
            raise TypeError(f"duplicated @polymorphic: {pms[0].name}")
        name_to_pm = {}
        alias_to_pm = {}
        ids = getattr(cls, _ID, {})
        for pm in pms:
            if pm.name in name_to_pm:
                raise TypeError(
                    f"discriminator field '{pm.name}' conflict: {pm.cls.__qualname__}, {name_to_pm[pm.name].cls.__qualname__}."
                )
            name_to_pm[pm.name] = pm.cls
            if pm.alias in alias_to_pm:
                raise TypeError(
                    f"discriminator field alias '{pm.alias}' conflict: {pm.cls.__qualname__}, {alias_to_pm[pm.alias].cls.__qualname__}."
                )
            alias_to_pm[pm.alias] = pm.cls
            if pm.alias not in ids:
                raise TypeError(f"unresolved @polymorphic: {pm.name}.")

        sig = signature(cls)

        if on in name_to_pm:
            raise TypeError(
                f"discriminator field '{on}' conflict: {cls.__qualname__}, {name_to_pm[on].cls.__qualname__}."
            )
        if on not in sig.parameters:
            raise TypeError(f"discriminator field '{on}' not found.")
        if sig.parameters[on].annotation is not str:
            raise TypeError(f"discriminator field '{on}' should be annotated as str.")

        name = alias = on
        default = sig.parameters[on].default
        if default == Parameter.empty:
            default = None
        if is_dataclass(cls):
            for f in fields(cls):
                if f.name == on:
                    if f.default_factory != MISSING:
                        default = f.default_factory()
                    if f.metadata:
                        alias = f.metadata.get("alias", on)
                    break
        if default is not None and not isinstance(default, str):
            raise TypeError(
                f"discriminator default should be a str: but {type(default).__qualname__} given."
            )
        pm = Polymorphic(cls=cls, name=name, alias=alias, key=key, default=default)
        setattr(cls, _PM, pm)

    @staticmethod
    def register(cls: type, id: str):
        if not isinstance(id, str):
            raise TypeError(
                f"discriminator value should be a str: but {type(id).__qualname__} given."
            )

        pm = getattr(cls, _PM, None)
        if pm is None:
            raise TypeError("@polymorphic base class not found")
        if id in pm.mapping:
            raise TypeError(
                f"{cls.__qualname__}.{pm.name}'s discriminator value '{id}' is already defined by class {pm.mapping[id].__qualname__}."
            )
        ids: dict[str, Identity] = cls.__dict__.get(_ID, {})
        if pm.alias not in ids:
            ids[pm.alias] = Identity(pm=pm)
        ids[pm.alias].ids.add(id)
        for base in cls.__mro__[1:]:
            bids = base.__dict__.get(_ID)
            if not bids:
                continue
            for key, val in bids.items():
                ids.setdefault(key, val)
        setattr(cls, _ID, ids)
        pm.mapping[id] = cls

    @staticmethod
    def resolve(cls: _T, val: Mapping) -> _T:
        pm = getattr(cls, _PM, None)
        if pm is None:
            return cls

        ids: dict[str, Identity] = getattr(cls, _ID, {})
        for k, v in ids.items():
            with traverse(v.pm.name):
                id = val.get(k)
                if id is None:
                    if v.pm.default is None:
                        raise TypeError(f"discriminator '{v.pm.name}' is missing")
                    id = v.pm.default
                if id not in v.ids:
                    raise TypeError(
                        f"discriminator value '{id}' is not allowed for {cls.__qualname__}."
                    )

        if pm.cls is not cls:
            return cls

        klass = cls
        while True:
            id = val.get(pm.alias)
            if id is None:
                id = pm.default
            elif pm.key:
                id = pm.key(id)
                if not isinstance(id, str):
                    raise TypeError(
                        f"key function should return str, but {type(id).__qualname__} returned."
                    )
            if id is None:
                with traverse(pm.name):
                    raise TypeError(
                        f"discriminator '{klass.__qualname__}.{pm.name}' is missing"
                    )
            if id not in pm.mapping:
                with traverse(pm.name):
                    raise TypeError(f"unknown discriminator value '{id}'")
            klass = pm.mapping[id]
            pm = getattr(klass, _PM)
            if pm.cls is not klass:
                break
        return klass

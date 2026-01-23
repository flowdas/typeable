import typing


_GenericBases = []
for _name in (
    "GenericAlias",
    "_GenericAlias",
    "_SpecialForm",
):
    if hasattr(typing, _name):  # pragma: no cover
        _GenericBases.append(getattr(typing, _name))
if hasattr(typing.Union, "__mro__"):
    _GenericBases.append(typing.Union)
_GenericBases = tuple(_GenericBases)

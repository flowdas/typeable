# Typeable: A Python type casting at runtime

Cast a value to a type.

`typeable.deepcast` provides an extensible runtime implementation of `typing.cast`. 
**`deepcast(T, v)`** returns the value obtained by recursively converting `v` to type `T`.
This process performs validation and conversion. 
The principle is to support standard library and user-defined types as-is.
It does not force the use of a specific base class.
In other words, it adheres to the principle of **non-interference**.

This can also be applied to function calls. 
**`deepcast.apply(f, v)`** performs a function call roughly equivalent to `f(**v)`. 
It performs validation and conversion on all annotated arguments before the call.

Too simple? 
Yes, that's my goal.

The code is currently at the alpha stage. 
Although `typeable.deepcast` understands and casts generic types, it is still lacking in consistency and completeness.

Typeable requires Python 3.10+.

Installation:

```
pip install typeable
```

## Supported Types

The list below summarizes the `T` types supported by `deepcast(T, v)`.
Generic types are denoted by `[]`.
`@` denotes types with the specified decoration applied.
This list is non-exhaustive.

- `dict`
- `dict[]`
- `float`
- `int`
- `object`
- `str`
- `collections.Counter`
- `collections.Counter[]`
- `collections.defaultdict`
- `collections.defaultdict[]`
- `collections.OrderedDict`
- `collections.OrderedDict[]`
- `@dataclasses.dataclass`
- `types.NoneType`
- `typing.Counter`
- `typing.Counter[]`
- `typing.DefaultDict`
- `typing.DefaultDict[]`
- `typing.Dict`
- `typing.Dict[]`
- `typing.OrderedDict`
- `typing.OrderedDict[]`
- `typing.TypedDict`

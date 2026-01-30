# Typeable: A Python type casting at runtime

Cast a value to a type.

`typeable.deepcast` provides an extensible runtime implementation of `typing.cast`. 
Calling `deepcast(T, v)` returns the value of `v` converted to type `T`. 
This process performs validation and conversion. 
This can also be applied to function calls. 
`deepcast.apply(f, v)` performs a function call roughly equivalent to `f(**v)`. 
It performs validation and conversion on all arguments before the call.

The code is currently at the alpha stage. 
Although `typeable.deepcast` understands and casts generic types, it is still lacking in consistency and completeness.

Typeable requires Python 3.10+.

Documentations:

* Korean - https://typeable.flowdas.com/

## Supported Type Conversions

The tables below summarize the pairs of `T` and `type(v)` supported by `deepcast(T, v)`.
They are grouped into three categories based on `T`.
All subtypes of the type shown in the `type(v)` column are also supported.
If a conversion is conditionally supported depending on the context, it is indicated in the “if” column.

### Built-in Types

| `T` | `type(v)` | if | Note |
| :--- | :--- | :--- | :--- |
| `None` | `NoneType` | | |
| `object` | `collections.abc.Mapping` | | |
| | `object` | | |

### Standard Library Types

| `T` | `type(v)` | if | Note |
| :--- | :--- | :--- | :--- |
| `types.NoneType` | `NoneType` | | |

### Typeable Types


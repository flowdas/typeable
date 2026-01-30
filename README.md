# Typeable: A Python type casting at runtime

Cast a value to a type.

`typeable.deepcast` provides an extensible runtime implementation of `typing.cast`. 
In addition, we plan to provide various features and extensions based on this.
For example, input validation, data conversion, serialization, schematic 
assertion and structural transformation can all be viewed as type casting.

The code is currently at the alpha stage. Although `typeable.deepcast` 
understands and casts generic types, it is still lacking in consistency and 
completeness.

Your criticism and participation are always welcome.

Typeable requires Python 3.10+.

Documentations:

* Korean - https://typeable.flowdas.com/

## Supported Type Conversions

The tables below summarize the pairs of `T` and `type(v)` supported by `deepcast(T, v)`.
They are grouped into three categories based on `T`.
All subtypes of the type shown in the `type(v)` column are also supported.
If a conversion is conditionally supported depending on the context, it is indicated in the “If” column.

### Built-in Types

| `T` | `type(v)` | If | Note |
| :--- | :--- | :--- | :--- |
| `None` | `NoneType` | | `None` is replaced with `types.NoneType`. |
| `object` | `collections.abc.Mapping` | | |
| | `object` | | |

### Standard Library Types

### Typeable Types


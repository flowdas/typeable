Typeable: A Python type casting at runtime
==========================================

Cast a value to a type.

Typeable provides an extensible runtime implementation of ``typing.cast``. 
In addition, we plan to provide various features and extensions based on this.
For example, input validation, data conversion, serialization, schematic 
assertion and structural transformation can all be viewed as type casting.

The code is currently at the proof-of-concept stage. Although ``typeable.cast`` 
understands and casts generic types, it is still lacking in consistency and 
completeness. The documentation is also being prepared. The Long and Winding 
Road.

Your criticism and participation are always welcome.

Typeable requires Python 3.6+. And it doesn't require any other dependencies.

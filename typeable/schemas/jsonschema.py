from dataclasses import dataclass, field
import sys
from typing import Annotated, ForwardRef, Literal

from typeable import JsonValue, Metadata, Missing, MissingType, V

Anchor = Annotated[str, V.pattern("^[A-Za-z_][-A-Za-z0-9._]*$")]
NonNegativeInteger = Annotated[int, V >= 0]
SimpleTypes = Literal[
    "array", "boolean", "integer", "null", "number", "object", "string"
]
StringArray = Annotated[list[str], V.unique()]
Regex = Annotated[str, V.format("regex")]
Uri = Annotated[str, V.format("uri")]
UriReference = Annotated[str, V.format("uri-reference")]

JsonSchema = ForwardRef("JsonSchema")  # type: ignore
if sys.version_info >= (3, 11):
    FullJsonSchema = JsonSchema | bool
else:
    from typing import Union

    FullJsonSchema = Union[JsonSchema, bool]
SchemaArray = Annotated[list[FullJsonSchema], V.length > 0]


@dataclass
class JsonSchema:
    _anchor: Anchor | None = field(default=None, metadata=Metadata(alias="$anchor"))
    _comment: str | None = field(default=None, metadata=Metadata(alias="$comment"))
    _defs: dict[str, FullJsonSchema] | None = field(
        default=None, metadata=Metadata(alias="$defs")
    )
    _dynamicAnchor: Anchor | None = field(
        default=None, metadata=Metadata(alias="$dynamicAnchor")
    )
    _dynamicRef: UriReference | None = field(
        default=None, metadata=Metadata(alias="$dynamicRef")
    )
    _id: Annotated[UriReference, V.pattern("^[^#]*#?$")] | None = field(
        default=None, metadata=Metadata(alias="$id")
    )
    _ref: UriReference | None = field(default=None, metadata=Metadata(alias="$ref"))
    _schema: Uri | None = field(default=None, metadata=Metadata(alias="$schema"))
    _vocabulary: dict[Uri, bool] | None = field(
        default=None, metadata=Metadata(alias="$vocabulary")
    )
    additionalProperties: FullJsonSchema | None = None
    allOf: SchemaArray | None = None
    anyOf: SchemaArray | None = None
    const: JsonValue | MissingType = Missing
    contains: FullJsonSchema | None = None
    dependentRequired: dict[str, StringArray] | None = None
    dependentSchemas: dict[str, FullJsonSchema] = field(default_factory=dict)
    else_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="else"))
    enum: list[JsonValue] | None = None
    exclusiveMaximum: int | float | None = None
    exclusiveMinimum: int | float | None = None
    if_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="if"))
    items: FullJsonSchema | None = None
    maxContains: NonNegativeInteger | None = None
    maximum: int | float | None = None
    maxItems: NonNegativeInteger | None = None
    maxLength: NonNegativeInteger | None = None
    maxProperties: NonNegativeInteger | None = None
    minContains: NonNegativeInteger = 1
    minimum: int | float | None = None
    minItems: NonNegativeInteger = 0
    minLength: NonNegativeInteger = 0
    minProperties: NonNegativeInteger = 0
    multipleOf: Annotated[int | float, V > 0] | None = None
    not_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="not"))
    oneOf: SchemaArray | None = None
    pattern: Regex | None = None
    patternProperties: dict[Regex, FullJsonSchema] = field(default_factory=dict)
    prefixItems: SchemaArray | None = None
    properties: dict[str, FullJsonSchema] = field(default_factory=dict)
    propertyNames: FullJsonSchema | None = None
    required: StringArray = field(default_factory=list)
    then: FullJsonSchema | None = None
    type: (
        SimpleTypes | Annotated[list[SimpleTypes], V.length > 0, V.unique()] | None
    ) = None
    unevaluatedItems: FullJsonSchema | None = None
    unevaluatedProperties: FullJsonSchema | None = None
    uniqueItems: bool = False

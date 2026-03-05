from dataclasses import dataclass, field
import sys
from typing import Annotated, ForwardRef

from typeable import Metadata, V

Anchor = Annotated[str, V.pattern("^[A-Za-z_][-A-Za-z0-9._]*$")]
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
    additionalProperties: FullJsonSchema | None = field(default=None)
    allOf: SchemaArray | None = field(default=None)
    anyOf: SchemaArray | None = field(default=None)
    contains: FullJsonSchema | None = field(default=None)
    dependentSchemas: dict[str, FullJsonSchema] = field(default_factory=dict)
    else_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="else"))
    if_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="if"))
    items: FullJsonSchema | None = field(default=None)
    not_: FullJsonSchema | None = field(default=None, metadata=Metadata(alias="not"))
    oneOf: SchemaArray | None = field(default=None)
    patternProperties: dict[Regex, FullJsonSchema] = field(default_factory=dict)
    prefixItems: SchemaArray | None = field(default=None)
    properties: dict[str, FullJsonSchema] = field(default_factory=dict)
    propertyNames: FullJsonSchema | None = field(default=None)
    then: FullJsonSchema | None = field(default=None)
    unevaluatedItems: FullJsonSchema | None = field(default=None)
    unevaluatedProperties: FullJsonSchema | None = field(default=None)

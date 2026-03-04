from dataclasses import dataclass, field
import sys
from typing import Annotated, ForwardRef

from typeable import Metadata, V

Anchor = Annotated[str, V.pattern("^[A-Za-z_][-A-Za-z0-9._]*$")]
Uri = Annotated[str, V.format("uri")]
UriReference = Annotated[str, V.format("uri-reference")]

JsonSchema = ForwardRef("JsonSchema")  # type: ignore
if sys.version_info >= (3, 11):
    FullJsonSchema = JsonSchema | bool
else:
    from typing import Union

    FullJsonSchema = Union[JsonSchema, bool]


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

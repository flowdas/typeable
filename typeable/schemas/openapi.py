"""OpenAPI 3.2 Schema"""

from dataclasses import dataclass, field
import sys
from typing import Annotated, Any, ForwardRef, Literal

from typeable import Metadata, Missing, V, enforce_constraints, identity, polymorphic
from typeable.schemas.jsonschema import (
    ExtensionMixIn,
    ExternalDocs,
    JsonSchema,
    UriReference,
)

MediaRange = Annotated[str, V.format("media-range")]


def _explode_for_form(self):
    if self.explode is None:
        self.explode = True if self.style == "form" else False


@dataclass
class Reference:
    _ref: UriReference | None = None
    summary: str | None = None
    description: str | None = None


@dataclass
class ExampleReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class HeaderReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class MediaTypeReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class ParameterReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class RequestBodyReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class CallbacksReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class ResponseReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class LinkReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


@dataclass
class SecuritySchemeReference(Reference):
    def __post_init__(self):
        enforce_constraints(self, V.hasAny("_ref"))


MediaType = ForwardRef("MediaType")  # type: ignore
if sys.version_info >= (3, 11):
    MediaTypeOrReference = MediaTypeReference | MediaType
else:
    from typing import Union

    MediaTypeOrReference = Union[MediaTypeReference, MediaType]

Content = dict[MediaRange, MediaTypeOrReference]
SingleContent = Annotated[Content, V.minProperties(1), V.maxProperties(1)]


@dataclass
class Example(ExtensionMixIn):
    summary: str | None = None
    description: str | None = None
    dataValue: Any = Missing
    serializedValue: str | None = None
    value: Any = Missing
    externalValue: UriReference | None = None

    def __post_init__(self):
        enforce_constraints(
            self,
            V.hasNotAll("value", "externalValue"),
            V.hasNotAll("value", "dataValue"),
            V.hasNotAll("value", "serializedValue"),
            V.hasNotAll("serializedValue", "externalValue"),
        )


@dataclass(kw_only=True)
class ExamplesMixIn:
    example: Any = Missing
    examples: dict[str, ExampleReference | Example] | None = None


ExamplesMixInConstraint = V.hasNotAll("example", "examples")


@dataclass
class Contact(ExtensionMixIn):
    name: str | None = None
    url: UriReference | None = None
    email: Annotated[str, V.format("email")] | None = None


@dataclass
class License(ExtensionMixIn):
    name: str
    identifier: str | None = None
    url: UriReference | None = None


@dataclass
class Info(ExtensionMixIn):
    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    termsOfService: str | None = None
    contact: Contact | None = None
    license: License | None = None


@dataclass
class ServerVariable(ExtensionMixIn):
    default: str
    description: str | None = None
    enum: Annotated[list[str], V.minItems(1)] | None = None


@dataclass
class Server(ExtensionMixIn):
    url: str
    description: str | None = None
    name: str | None = None
    variables: dict[str, ServerVariable] | None = None


_default_server = Server(url="/")


@dataclass
class Header(ExtensionMixIn, ExamplesMixIn):
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    schema: JsonSchema | None = None
    style: Literal["simple"] = "simple"
    explode: bool = False
    content: SingleContent | None = None

    def __post_init__(self):
        enforce_constraints(
            self, ExamplesMixInConstraint, V.hasOne("schema", "content")
        )


Encoding = ForwardRef("Encoding")  # type: ignore
if sys.version_info >= (3, 11):
    OptionalEncoding = Encoding | None
else:
    from typing import Optional

    OptionalEncoding = Optional[Encoding]


@dataclass
class Encoding(ExtensionMixIn):
    contentType: MediaRange | None = None
    headers: dict[str, HeaderReference | Header] | None = None
    style: Literal["form", "spaceDelimited", "pipeDelimited", "deepObject"] | None = (
        None
    )
    explode: bool | None = None
    allowReserved: bool | None = None
    encoding: dict[str, Encoding] | None = None
    prefixEncoding: list[Encoding] | None = None
    itemEncoding: OptionalEncoding = None

    def __post_init__(self):
        if enforce_constraints(
            self,
            V.hasNotAll("encoding", "prefixEncoding"),
            V.hasNotAll("encoding", "itemEncoding"),
            V.hasNotAll("style", "allowReserved"),
        ):
            has_style = self.style is not None
            has_explode = self.explode is not None
            has_allowReserved = self.allowReserved is not None
            if has_style:
                _explode_for_form(self)
            if has_explode:
                if self.style is None:
                    self.style = "form"
                if self.allowReserved is None:
                    self.allowReserved = False
            if has_allowReserved:
                if self.style is None:
                    self.style = "form"
                _explode_for_form(self)


@dataclass
class MediaType(ExtensionMixIn, ExamplesMixIn):
    description: str | None = None
    schema: JsonSchema | None = None
    itemSchema: JsonSchema | None = None
    encoding: dict[str, Encoding] | None = None
    prefixEncoding: list[Encoding] | None = None
    itemEncoding: Encoding | None = None

    def __post_init__(self):
        enforce_constraints(
            self,
            ExamplesMixInConstraint,
            V.hasNotAll("encoding", "prefixEncoding"),
            V.hasNotAll("encoding", "itemEncoding"),
        )


@polymorphic(on="in_")
@dataclass(kw_only=True)
class Parameter(ExtensionMixIn, ExamplesMixIn):
    name: str
    in_: str = field(metadata=Metadata(alias="in"))
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    schema: JsonSchema | None = None
    style: str | None = None
    explode: bool | None = None
    content: SingleContent | None = None

    def __post_init__(self):
        enforce_constraints(
            self, ExamplesMixInConstraint, V.hasOne("schema", "content")
        )


@identity("query")
@dataclass
class QueryParameter(Parameter):
    style: Literal["form", "spaceDelimited", "pipeDelimited", "deepObject"] = (
        "form"  # override
    )
    allowEmptyValue: bool = False
    allowReserved: bool = False

    def __post_init__(self):
        super().__post_init__()
        if enforce_constraints(self):
            _explode_for_form(self)


@identity("querystring")
@dataclass
class QueryStringParameter(Parameter):
    def __post_init__(self):
        super().__post_init__()
        enforce_constraints(self, V.hasAny("content"))


@identity("header")
@dataclass
class HeaderParameter(Parameter):
    style: Literal["simple"] = "simple"  # override
    explode: bool = False  # override


@identity("path")
@dataclass
class PathParameter(Parameter):
    name: Annotated[str, V.pattern("^[^{}]+$")]  # override
    style: Literal["matrix", "label", "simple"] = "simple"  # override
    explode: bool = False  # override
    allowReserved: bool = False

    def __post_init__(self):
        super().__post_init__()
        enforce_constraints(
            self, V.hasOne("schema", "content"), V.hasConst("required", True)
        )


@identity("cookie")
@dataclass
class CookieParameter(Parameter):
    style: Literal["form", "cookie"] = "form"  # override
    explode: bool = False  # override
    allowReserved: bool | None = None

    def __post_init__(self):
        super().__post_init__()
        if enforce_constraints(self):
            if self.allowReserved is None and self.style == "form":
                self.allowReserved = False


@dataclass
class RequestBody(ExtensionMixIn):
    content: Content
    description: str | None = None
    required: bool = False


@dataclass
class Link(ExtensionMixIn):
    operationRef: UriReference | None = None
    operationId: str | None = None
    parameters: dict[str, str] | None = None
    requestBody: Any = Missing
    description: str | None = None
    server: Server | None = None

    def __post_init__(self):
        enforce_constraints(self, V.hasOne("operationRef", "operationId"))


@dataclass
class Response(ExtensionMixIn):
    summary: str | None = None
    description: str | None = None
    headers: dict[str, HeaderReference | Header] | None = None
    content: Content | None = None
    links: dict[str, LinkReference | Link] | None = None


@dataclass
class Responses(ExtensionMixIn):
    default: ResponseReference | Response | None = None
    responses: dict[str, ResponseReference | Response] | None = field(
        default=None, metadata=Metadata(extra="^[1-5](?:[0-9]{2}|XX)$")
    )

    def __post_init__(self):
        enforce_constraints(
            self,
            V.minProperties(1),
            V.hasOne("default", "responses"),
        )


PathItem = ForwardRef("PathItem")  # type: ignore


@dataclass
class Callbacks(ExtensionMixIn):
    callbacks: dict[str, PathItem] = field(
        default_factory=dict, metadata=Metadata(extra=True)
    )


SecurityRequirement = dict[str, list[str]]


@dataclass
class Operation(ExtensionMixIn):
    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    externalDocs: ExternalDocs | None = None
    operationId: str | None = None
    parameters: list[ParameterReference | Parameter] | None = None
    requestBody: RequestBodyReference | RequestBody | None = None
    responses: Responses | None = None
    callbacks: dict[str, CallbacksReference | Callbacks] | None = None
    deprecated: bool = False
    security: list[SecurityRequirement] | None = None
    servers: list[Server] | None = None


@dataclass
class PathItem(ExtensionMixIn):
    _ref: UriReference | None = field(default=None, metadata=Metadata(alias="$ref"))
    summary: str | None = None
    description: str | None = None
    servers: list[Server] | None = None
    parameters: list[ParameterReference | Parameter] | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    options: Operation | None = None
    head: Operation | None = None
    patch: Operation | None = None
    trace: Operation | None = None
    query: Operation | None = None
    additionalOperations: (
        dict[Annotated[str, V.pattern("^[a-zA-Z0-9!#$%&'*+.^_`|~-]+$")], Operation]
        | None
    ) = None


@dataclass
class Paths(ExtensionMixIn):
    paths: dict[str, PathItem] = field(
        default_factory=dict, metadata=Metadata(extra="^/")
    )


@dataclass
class Tag(ExtensionMixIn):
    name: str
    summary: str | None = None
    description: str | None = None
    externalDocs: ExternalDocs | None = None
    parent: str | None = None
    kind: str | None = None


@polymorphic(on="type")
@dataclass(kw_only=True)
class SecurityScheme(ExtensionMixIn):
    type: str
    description: str | None = None
    deprecated: bool = False


@identity("apiKey")
@dataclass
class ApiKeySecurityScheme(SecurityScheme):
    name: str
    in_: Literal["query", "header", "cookie"] = field(metadata=Metadata(alias="in"))


@identity("http")
@dataclass
class HttpSecurityScheme(SecurityScheme):
    scheme: str
    bearerFormat: str | None = None


@identity("mutualTLS")
@dataclass
class MutualTLSSecurityScheme(SecurityScheme):
    pass


@dataclass
class ImplicitOAuthFlow(ExtensionMixIn):
    authorizationUrl: UriReference
    scopes: dict[str, str]
    refreshUrl: UriReference | None = None


@dataclass
class PasswordOAuthFlow(ExtensionMixIn):
    tokenUrl: UriReference
    scopes: dict[str, str]
    refreshUrl: UriReference | None = None


@dataclass
class ClientCredentialsOAuthFlow(ExtensionMixIn):
    tokenUrl: UriReference
    scopes: dict[str, str]
    refreshUrl: UriReference | None = None


@dataclass
class AuthorizationCodeOAuthFlow(ExtensionMixIn):
    authorizationUrl: UriReference
    tokenUrl: UriReference
    scopes: dict[str, str]
    refreshUrl: UriReference | None = None


@dataclass
class DeviceAuthorizationOAuthFlow(ExtensionMixIn):
    deviceAuthorizationUrl: UriReference
    tokenUrl: UriReference
    scopes: dict[str, str]
    refreshUrl: UriReference | None = None


@dataclass
class OAuthFlows(ExtensionMixIn):
    implicit: ImplicitOAuthFlow | None = None
    password: PasswordOAuthFlow | None = None
    clientCredentials: ClientCredentialsOAuthFlow | None = None
    authorizationCode: AuthorizationCodeOAuthFlow | None = None
    deviceAuthorization: DeviceAuthorizationOAuthFlow | None = None


@identity("oauth2")
@dataclass
class OAuth2SecurityScheme(SecurityScheme):
    flows: OAuthFlows
    oauth2MetadataUrl: UriReference | None = None


@identity("openIdConnect")
@dataclass
class OpenIdConnectSecurityScheme(SecurityScheme):
    openIdConnectUrl: UriReference


@dataclass
class Components(ExtensionMixIn):
    schemas: dict[str, JsonSchema] | None = None
    responses: dict[str, ResponseReference | Response] | None = None
    parameters: dict[str, ParameterReference | Parameter] | None = None
    examples: dict[str, ExampleReference | Example] | None = None
    requestBodies: dict[str, RequestBodyReference | RequestBody] | None = None
    headers: dict[str, HeaderReference | Header] | None = None
    securitySchemes: dict[str, SecuritySchemeReference | SecurityScheme] | None = None
    links: dict[str, LinkReference | Link] | None = None
    callbacks: dict[str, CallbacksReference | Callbacks] | None = None
    pathItems: dict[str, PathItem] | None = None
    mediaTypes: dict[str, MediaTypeReference | MediaType] | None = None
    components: dict | None = field(
        default=None, metadata=Metadata(extra="^[a-zA-Z0-9._-]+$")
    )


def ignore_patch(version):
    try:
        return ".".join(version.split(".")[:2])
    except Exception:
        return version


@polymorphic(on="openapi", key=ignore_patch)
@dataclass
class OpenAPI:
    openapi: str


@identity("3.2")
@dataclass
class OpenAPI32(OpenAPI, ExtensionMixIn):
    info: Info
    _self: Annotated[str, V.format("uri-reference"), V.pattern("^[^#]*$")] | None = (
        field(default=None, metadata=Metadata(alias="$self"))
    )
    jsonSchemaDialect: UriReference = (
        "https://spec.openapis.org/oas/3.2/dialect/2025-09-17"
    )
    servers: list[Server] = field(default_factory=lambda: [_default_server])
    paths: Paths | None = None
    webhooks: dict[str, PathItem] | None = None
    components: Components | None = None
    security: list[SecurityRequirement] | None = None
    tags: list[Tag] | None = None
    externalDocs: ExternalDocs | None = None

    def __post_init__(self):
        if enforce_constraints(self, V.hasAny("paths", "components", "webhooks")):
            if not self.servers:
                self.servers = [_default_server]
            # TODO: resolve references
            # TODO: parameters validation under paths

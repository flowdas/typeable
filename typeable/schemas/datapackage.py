"""Data Package Schema"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Any, Literal

from typeable import Metadata, Missing, V, identity, polymorphic
from typeable.schemas.jsonschema import JsonSchema, Uri

PATH1_PATTERN = "^(?=^[^./~])(^((?!\\.{2}).)*$).*$"
PATH2_PATTERN = "^((?=[^./~])(?!file:)((?!\\/\\.\\.\\/)(?!\\\\)(?!:\\/\\/).)*|(http|ftp)s?:\\/\\/.*)$"
Path1 = Annotated[str, V.pattern(PATH1_PATTERN)]
Path2 = Annotated[str, V.pattern(PATH2_PATTERN)]


@dataclass(kw_only=True)
class Contributor:
    email: Annotated[str, V.format("email")] | None = None
    organization: str | None = None


@dataclass
class Contributor1(Contributor):
    title: str
    path: Path1 | None = None
    role: str = "contributor"


@dataclass
class Contributor2(Contributor):
    title: str | None = None
    path: Path2 | None = None
    givenName: str | None = None
    familyName: str | None = None
    roles: Annotated[list[str], V.minItems(1)] | None = None


@dataclass
class License:
    name: Annotated[str, V.pattern("^([-a-zA-Z0-9._])+$")] | None = None
    title: str | None = None


@dataclass
class License1(License):
    path: Path1 | None = None

    def __post_init__(self):
        if self.name is None and self.path is None:
            raise TypeError(
                "The License object MUST contain a name property and/or a path property."
            )


@dataclass
class License2(License):
    path: Path2 | None = None

    def __post_init__(self):
        if self.name is None and self.path is None:
            raise TypeError(
                "The License object MUST contain a name property and/or a path property."
            )


@dataclass(kw_only=True)
class Source:
    email: Annotated[str, V.format("email")] | None = None


@dataclass
class Source1(Source):
    title: str
    path: Path1 | None = None


@dataclass
class Source2(Source):
    title: str | None = None
    path: Path2 | None = None
    version: str | None = None


@polymorphic(on="_schema")
@dataclass
class TableDialect:
    _schema: str = field(
        default="https://datapackage.org/profiles/1.0/tabledialect.json",
        metadata=Metadata(alias="$schema"),
    )
    commentChar: str | None = None
    delimiter: str = ","
    doubleQuote: bool = True
    escapeChar: str | None = None
    header: bool = True
    lineTerminator: str = "\r\n"
    nullSequence: str | None = None
    quoteChar: str = '"'
    skipInitialSpace: bool = False


@identity("https://datapackage.org/profiles/1.0/tabledialect.json")
@dataclass
class TableDialect1(TableDialect):
    caseSensitiveHeader: bool = False
    csvddfVersion: float = 1.2


@identity("https://datapackage.org/profiles/2.0/tabledialect.json")
@dataclass
class TableDialect2(TableDialect):
    commentRows: list[Annotated[int, V >= 1]] = field(default_factory=lambda: [1])
    headerJoin: str = " "
    headerRows: list[Annotated[int, V >= 1]] = field(default_factory=lambda: [1])
    itemKeys: list[str] | None = None
    itemType: Literal["array", "object"] | None = None
    property: str | None = None
    sheetName: str | None = None
    sheetNumber: Annotated[int, V >= 1] | None = None
    table: str | None = None


@dataclass
class MissingValue:
    value: str
    label: str | None = None


@dataclass
class StringCategory:
    value: str
    label: str | None = None


@dataclass
class IntegerCategory:
    value: int
    label: str | None = None


@dataclass
class StringConstraints:
    required: bool | None = None
    unique: bool | None = None
    pattern: str | None = None
    enum: Annotated[list[str], V.minItems(1), V.uniqueItems()] | None = None
    minLength: int | None = None
    maxLength: int | None = None


@dataclass
class NumberConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: (
        Annotated[list[str] | list[int | float], V.minItems(1), V.uniqueItems()] | None
    ) = None
    minimum: int | float | str | None = None
    maximum: int | float | str | None = None


@dataclass
class NumberConstraints1(NumberConstraints):
    pass


@dataclass
class NumberConstraints2(NumberConstraints):
    exclusiveMinimum: int | float | str | None = None
    exclusiveMaximum: int | float | str | None = None


@dataclass
class IntegerConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: Annotated[list[str] | list[int], V.minItems(1), V.uniqueItems()] | None = None
    minimum: int | str | None = None
    maximum: int | str | None = None


@dataclass
class IntegerConstraints1(IntegerConstraints):
    pass


@dataclass
class IntegerConstraints2(IntegerConstraints):
    exclusiveMinimum: int | str | None = None
    exclusiveMaximum: int | str | None = None


@dataclass
class DateTimeConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: Annotated[list[str], V.minItems(1), V.uniqueItems()] | None = None
    minimum: str | None = None
    maximum: str | None = None


@dataclass
class DateTimeConstraints1(DateTimeConstraints):
    pass


@dataclass
class DateTimeConstraints2(DateTimeConstraints):
    exclusiveMinimum: str | None = None
    exclusiveMaximum: str | None = None


@dataclass
class BooleanConstraints:
    required: bool | None = None
    enum: Annotated[list[bool], V.minItems(1), V.uniqueItems()] | None = None


@dataclass
class ObjectConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: (
        Annotated[list[str] | list[dict[str, Any]], V.minItems(1), V.uniqueItems()]
        | None
    ) = None
    minLength: int | None = None
    maxLength: int | None = None


@dataclass
class ObjectConstraints1(ObjectConstraints):
    pass


@dataclass
class ObjectConstraints2(ObjectConstraints):
    jsonSchema: JsonSchema | None = None


@dataclass
class GeoPointConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: (
        Annotated[
            list[str] | list[list] | list[dict[str, Any]],
            V.minItems(1),
            V.uniqueItems(),
        ]
        | None
    ) = None


@dataclass
class GeoJsonConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: (
        Annotated[list[str] | list[dict[str, Any]], V.minItems(1), V.uniqueItems()]
        | None
    ) = None
    minLength: int | None = None
    maxLength: int | None = None


@dataclass
class ArrayConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: Annotated[list[str] | list[list], V.minItems(1), V.uniqueItems()] | None = (
        None
    )
    minLength: int | None = None
    maxLength: int | None = None


@dataclass
class ArrayConstraints1(ArrayConstraints):
    pass


@dataclass
class ArrayConstraints2(ArrayConstraints):
    jsonSchema: JsonSchema | None = None


@dataclass
class ListConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: Annotated[list[str] | list[list], V.minItems(1), V.uniqueItems()] | None = (
        None
    )
    minLength: int | None = None
    maxLength: int | None = None


@dataclass
class AnyConstraints:
    required: bool | None = None
    unique: bool | None = None
    enum: Annotated[list, V.minItems(1), V.uniqueItems()] | None = None


@dataclass(kw_only=True)
class Field:
    name: str
    title: str | None = None
    description: str | None = None
    example: str | None = None
    rdfType: str | None = None


@polymorphic(on="type")
@dataclass
class Field1(Field):
    type: str = "string"


@polymorphic(on="type")
@dataclass
class Field2(Field):
    type: str = "string"
    missingValues: list[str] | list[MissingValue] = field(default_factory=lambda: [""])


@dataclass
class StringMixIn:
    format: Literal["default", "email", "uri", "binary", "uuid"] = "default"
    constraints: StringConstraints | None = None


@identity("string")
@dataclass
class StringField1(Field1, StringMixIn):
    pass


@identity("string")
@dataclass
class StringField2(Field2, StringMixIn):
    categories: list[str] | list[StringCategory] | None = None
    categoriesOrdered: bool | None = None


@dataclass
class NumberMixIn:
    format: Literal["default"] = "default"
    bareNumber: bool = True
    groupChar: str | None = None
    decimalChar: str = "."  # Note(flowdas): The profile does not define default values.


@identity("number")
@dataclass
class NumberField1(Field1, NumberMixIn):
    constraints: NumberConstraints1 | None = None


@identity("number")
@dataclass
class NumberField2(Field2, NumberMixIn):
    constraints: NumberConstraints2 | None = None


@dataclass
class IntegerMixIn:
    format: Literal["default"] = "default"
    bareNumber: bool = True


@identity("integer")
@dataclass
class IntegerField1(Field1, IntegerMixIn):
    constraints: IntegerConstraints1 | None = None


@identity("integer")
@dataclass
class IntegerField2(Field2, IntegerMixIn):
    categories: list[int] | list[IntegerCategory] | None = None
    categoriesOrdered: bool | None = None
    groupChar: str | None = None
    constraints: IntegerConstraints2 | None = None


@dataclass
class DateTimeMixIn:
    format: Literal["default"] = "default"


@identity("date")
@dataclass
class DateField1(Field1, DateTimeMixIn):
    constraints: DateTimeConstraints1 | None = None


@identity("date")
@dataclass
class DateField2(Field2, DateTimeMixIn):
    constraints: DateTimeConstraints2 | None = None


@identity("time")
@dataclass
class TimeField1(Field1, DateTimeMixIn):
    constraints: DateTimeConstraints1 | None = None


@identity("time")
@dataclass
class TimeField2(Field2, DateTimeMixIn):
    constraints: DateTimeConstraints2 | None = None


@identity("datetime")
@dataclass
class DateTimeField1(Field1, DateTimeMixIn):
    constraints: DateTimeConstraints1 | None = None


@identity("datetime")
@dataclass
class DateTimeField2(Field2, DateTimeMixIn):
    constraints: DateTimeConstraints2 | None = None


@identity("year")
@dataclass
class YearField1(Field1, DateTimeMixIn):
    constraints: IntegerConstraints1 | None = None


@identity("year")
@dataclass
class YearField2(Field2, DateTimeMixIn):
    constraints: IntegerConstraints2 | None = None


@identity("yearmonth")
@dataclass
class YearMonthField1(Field1, DateTimeMixIn):
    constraints: DateTimeConstraints1 | None = None


@identity("yearmonth")
@dataclass
class YearMonthField2(Field2, DateTimeMixIn):
    constraints: DateTimeConstraints2 | None = None


@dataclass
class BooleanMixIn:
    format: Literal["default"] = "default"
    trueValues: Annotated[list[str], V.minItems(1)] = field(
        default_factory=lambda: ["true", "True", "TRUE", "1"]
    )
    falseValues: Annotated[list[str], V.minItems(1)] = field(
        default_factory=lambda: ["false", "False", "FALSE", "0"]
    )
    constraints: BooleanConstraints | None = None


@identity("boolean")
@dataclass
class BooleanField1(Field1, BooleanMixIn):
    pass


@identity("boolean")
@dataclass
class BooleanField2(Field2, BooleanMixIn):
    pass


@dataclass
class ObjectMixIn:
    format: Literal["default"] = "default"


@identity("object")
@dataclass
class ObjectField1(Field1, ObjectMixIn):
    constraints: ObjectConstraints1 | None = None


@identity("object")
@dataclass
class ObjectField2(Field2, ObjectMixIn):
    constraints: ObjectConstraints2 | None = None


@dataclass
class GeoPointMixIn:
    format: Literal["default", "array", "object"] = "default"
    constraints: GeoPointConstraints | None = None


@identity("geopoint")
@dataclass
class GeoPointField1(Field1, GeoPointMixIn):
    pass


@identity("geopoint")
@dataclass
class GeoPointField2(Field2, GeoPointMixIn):
    pass


@dataclass
class GeoJsonMixIn:
    format: Literal["default", "topojson"] = "default"
    constraints: GeoJsonConstraints | None = None


@identity("geojson")
@dataclass
class GeoJsonField1(Field1, GeoJsonMixIn):
    pass


@identity("geojson")
@dataclass
class GeoJsonField2(Field2, GeoJsonMixIn):
    pass


@dataclass
class ArrayMixIn:
    format: Literal["default"] = "default"


@identity("array")
@dataclass
class ArrayField1(Field1, ArrayMixIn):
    constraints: ArrayConstraints1 | None = None


@identity("array")
@dataclass
class ArrayField2(Field2, ArrayMixIn):
    constraints: ArrayConstraints2 | None = None


@identity("list")
@dataclass
class ListField(Field2):
    format: Literal["default"] = "default"
    delimiter: str = ","
    itemType: Literal[
        "string", "integer", "boolean", "number", "datetime", "date", "time"
    ] = "string"
    constraints: ListConstraints | None = None


@identity("duration")
@dataclass
class DurationField1(Field1, DateTimeMixIn):
    constraints: DateTimeConstraints1 | None = None


@identity("duration")
@dataclass
class DurationField2(Field2, DateTimeMixIn):
    constraints: DateTimeConstraints2 | None = None


@dataclass
class AnyMixIn:
    constraints: AnyConstraints | None = None


@identity("any")
@dataclass
class AnyField1(Field1, AnyMixIn):
    pass


@identity("any")
@dataclass
class AnyField2(Field2, AnyMixIn):
    pass


@dataclass
class SimpleReference:
    fields: str
    resource: str | None = None


@dataclass
class SimpleForeignKey:
    fields: str
    reference: SimpleReference


@dataclass
class CompositeReference1:
    fields: Annotated[list[str], V.minItems(1), V.uniqueItems()]
    resource: str = ""


@dataclass
class CompositeForeignKey1:
    fields: Annotated[list[str], V.minItems(1), V.uniqueItems()]
    reference: CompositeReference1


@dataclass
class CompositeReference2:
    fields: Annotated[list[str], V.minItems(1), V.uniqueItems()]
    resource: str | None = None


@dataclass
class CompositeForeignKey2:
    fields: Annotated[list[str], V.minItems(1), V.uniqueItems()]
    reference: CompositeReference2


@polymorphic(on="_schema")
@dataclass(kw_only=True)
class TableSchema:
    _schema: str = field(
        default="https://datapackage.org/profiles/1.0/tableschema.json",
        metadata=Metadata(alias="$schema"),
    )
    primaryKey: str | Annotated[list[str], V.minItems(1), V.uniqueItems()] | None = None


@identity("https://datapackage.org/profiles/1.0/tableschema.json")
@dataclass
class TableSchema1(TableSchema):
    fields: Annotated[list[Field1], V.minItems(1)]
    foreignKeys: (
        Annotated[list[SimpleForeignKey | CompositeForeignKey1], V.minItems(1)] | None
    ) = None
    missingValues: list[str] = field(default_factory=lambda: [""])


@identity("https://datapackage.org/profiles/2.0/tableschema.json")
@dataclass
class TableSchema2(TableSchema):
    fields: Annotated[list[Field2], V.minItems(1)]
    fieldsMatch: (
        list[Literal["exact", "equal", "subset", "superset", "partial"]] | None
    ) = None
    uniqueKeys: (
        Annotated[
            list[Annotated[list[str], V.minItems(1), V.uniqueItems()]],
            V.minItems(1),
            V.uniqueItems(),
        ]
        | None
    ) = None
    foreignKeys: (
        Annotated[list[SimpleForeignKey | CompositeForeignKey2], V.minItems(1)] | None
    ) = None
    missingValues: list[str] | list[MissingValue] = field(default_factory=lambda: [""])


@polymorphic(on="_schema")
@dataclass(kw_only=True)
class DataResource:
    _schema: str = field(
        default="https://datapackage.org/profiles/1.0/dataresource.json",
        metadata=Metadata(alias="$schema"),
    )
    bytes: int | None = None
    data: Any = Missing
    description: str | None = None
    encoding: str = "utf-8"
    format: str | None = None
    hash: (
        Annotated[str, V.pattern("^([^:]+:[a-fA-F0-9]+|[a-fA-F0-9]{32}|)$")] | None
    ) = None
    homepage: Uri | None = None
    mediatype: Annotated[str, V.pattern("^(.+)/(.+)$")] | None = None
    title: str | None = None


@identity("https://datapackage.org/profiles/1.0/dataresource.json")
@dataclass
class DataResource1(DataResource):
    name: Annotated[str, V.pattern("^([-a-z0-9._/])+$")]
    dialect: str | TableDialect1 | None = None
    licenses: Annotated[list[License1], V.minItems(1)] | None = None
    path: Path1 | Annotated[list[Path1], V.minItems(1)] | None = None
    profile: str | None = None
    schema: str | TableSchema1 | None = None
    sources: list[Annotated[Source1, V.minProperties(1)]] | None = None

    def __post_init__(self):
        if self.path is None and self.data is Missing:
            raise TypeError(
                "The DataResource object MUST contain one (and only one) of path or data properties."
            )


@identity("https://datapackage.org/profiles/2.0/dataresource.json")
@dataclass
class DataResource2(DataResource):
    name: str
    dialect: str | TableDialect | None = None
    licenses: Annotated[list[License2], V.minItems(1)] | None = None
    path: Path2 | Annotated[list[Path2], V.minItems(1)] | None = None
    schema: str | TableSchema | None = None
    sources: list[Annotated[Source2, V.minProperties(1)]] | None = None
    type: Literal["table"] | None = None

    def __post_init__(self):
        if self.path is None and self.data is Missing:
            raise TypeError(
                "The DataResource object MUST contain one (and only one) of path or data properties."
            )


@polymorphic(on="_schema")
@dataclass(kw_only=True)
class DataPackage:
    _schema: str = field(
        default="https://datapackage.org/profiles/1.0/datapackage.json",
        metadata=Metadata(alias="$schema"),
    )
    created: Annotated[datetime, V.zonedTime()] | None = None
    description: str | None = None
    homepage: Uri | None = None
    id: str | None = None
    image: str | None = None
    keywords: Annotated[list[str], V.minItems(1)] | None = None
    title: str | None = None


@identity("https://datapackage.org/profiles/1.0/datapackage.json")
@dataclass
class DataPackage1(DataPackage):
    resources: Annotated[list[DataResource1], V.minItems(1)]
    contributors: Annotated[list[Contributor1], V.minItems(1)] | None = None
    licenses: Annotated[list[License1], V.minItems(1)] | None = None
    name: Annotated[str, V.pattern("^([-a-z0-9._/])+$")] | None = None
    profile: str | None = None
    sources: list[Annotated[Source1, V.minProperties(1)]] | None = None


@identity("https://datapackage.org/profiles/2.0/datapackage.json")
@dataclass
class DataPackage2(DataPackage):
    resources: Annotated[list[DataResource], V.minItems(1)]
    contributors: (
        Annotated[list[Annotated[Contributor2, V.minProperties(1)]], V.minItems(1)]
        | None
    ) = None
    licenses: Annotated[list[License2], V.minItems(1)] | None = None
    name: str | None = None
    sources: list[Annotated[Source2, V.minProperties(1)]] | None = None
    version: str | None = None

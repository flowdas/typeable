import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, is_dataclass
from datetime import datetime, time
from importlib import import_module
from inspect import signature
from typing import Any, Literal, get_args, get_origin


@dataclass(frozen=True, kw_only=True)
class Constraint:
    quiet: bool = False

    def evaluate(self, val, before) -> bool | None:
        raise NotImplementedError

    def __call__(self, val, before) -> bool:
        ret = self.evaluate(val, before)
        if ret is None:
            if self.quiet:
                return True
            raise TypeError(
                f"'{self!r}' is not applicable to {val.__class__.__qualname__}."
            )
        return ret

    def __bool__(self):
        raise RuntimeError(
            "Use bitwise operators instead of logical operators in V-expression. Note that chained comparisons implicitly introduce logical operators."
        )

    def __and__(self, other):
        if isinstance(other, AllOf):
            return AllOf((self,) + other.args)
        elif isinstance(other, Constraint):
            return AllOf((self, other))
        return NotImplemented

    def __or__(self, other):
        if isinstance(other, AnyOf):
            return AnyOf((self,) + other.args)
        elif isinstance(other, Constraint):
            return AnyOf((self, other))
        return NotImplemented


@dataclass(frozen=True)
class Combined(Constraint):
    args: tuple[Constraint, ...]


@dataclass(frozen=True)
class AllOf(Combined):
    def evaluate(self, val, before) -> bool | None:
        return all(arg(val, before) for arg in self.args)

    def __repr__(self) -> str:
        return " & ".join(f"({arg!r})" for arg in self.args)

    def __and__(self, other):
        if isinstance(other, AllOf):
            return AllOf(self.args + other.args)
        elif isinstance(other, Constraint):
            return AllOf(self.args + (other,))
        return NotImplemented


@dataclass(frozen=True)
class AnyOf(Combined):
    def evaluate(self, val, before) -> bool | None:
        return any(arg(val, before) for arg in self.args)

    def __repr__(self) -> str:
        return " | ".join(f"({arg!r})" for arg in self.args)

    def __or__(self, other):
        if isinstance(other, AnyOf):
            return AnyOf(self.args + other.args)
        elif isinstance(other, Constraint):
            return AnyOf(self.args + (other,))
        return NotImplemented


@dataclass(frozen=True)
class Not(Constraint):
    arg: Constraint

    def evaluate(self, val, before) -> bool | None:
        if isinstance(self.arg, Constraint):
            return not self.arg(val, before)

    def __repr__(self) -> str:
        return f"~({self.arg!r})"


@dataclass(frozen=True)
class ExclusiveMinimum(Constraint):
    exclusiveMinimum: int | float

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (int, float)):
            return val > self.exclusiveMinimum

    def __repr__(self) -> str:
        return f"Value > {self.exclusiveMinimum}"


@dataclass(frozen=True)
class Minimum(Constraint):
    minimum: int | float

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (int, float)):
            return val >= self.minimum

    def __repr__(self) -> str:
        return f"Value >= {self.minimum}"


@dataclass(frozen=True)
class ExclusiveMaximum(Constraint):
    exclusiveMaximum: int | float

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (int, float)):
            return val < self.exclusiveMaximum

    def __repr__(self) -> str:
        return f"Value < {self.exclusiveMaximum}"


@dataclass(frozen=True)
class Maximum(Constraint):
    maximum: int | float

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (int, float)):
            return val <= self.maximum

    def __repr__(self) -> str:
        return f"Value <= {self.maximum}"


@dataclass(frozen=True)
class MaxLength(Constraint):
    maxLength: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (str, bytes, bytearray, memoryview)):
            return len(val) <= self.maxLength

    def __repr__(self) -> str:
        return f"Value.maxLength({self.maxLength})"


@dataclass(frozen=True)
class MinLength(Constraint):
    minLength: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (str, bytes, bytearray, memoryview)):
            return len(val) >= self.minLength

    def __repr__(self) -> str:
        return f"Value.minLength({self.minLength})"


@dataclass(frozen=True)
class MaxItems(Constraint):
    maxItems: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, Sequence) and not isinstance(
            val, (str, bytes, bytearray, memoryview)
        ):
            return len(val) <= self.maxItems

    def __repr__(self) -> str:
        return f"Value.maxItems({self.maxItems})"


@dataclass(frozen=True)
class MinItems(Constraint):
    minItems: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, Sequence) and not isinstance(
            val, (str, bytes, bytearray, memoryview)
        ):
            return len(val) >= self.minItems

    def __repr__(self) -> str:
        return f"Value.minItems({self.minItems})"


@dataclass(frozen=True)
class MaxProperties(Constraint):
    maxProperties: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, Mapping):
            return len(val) <= self.maxProperties
        elif is_dataclass(val) and isinstance(before, Mapping):
            return len(before) <= self.maxProperties

    def __repr__(self) -> str:
        return f"Value.maxProperties({self.maxProperties})"


@dataclass(frozen=True)
class MinProperties(Constraint):
    minProperties: int

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, Mapping):
            return len(val) >= self.minProperties
        elif is_dataclass(val) and isinstance(before, Mapping):
            return len(before) >= self.minProperties

    def __repr__(self) -> str:
        return f"Value.minProperties({self.minProperties})"


@dataclass(frozen=True)
class MultipleOf(Constraint):
    multipleOf: int | float

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (int, float)):
            return val % self.multipleOf == 0

    def __repr__(self) -> str:
        return f"Value.multipleOf({self.multipleOf})"


@dataclass(frozen=True)
class Pattern(Constraint):
    pattern: str

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, str):
            return re.search(self.pattern, val) is not None

    def __repr__(self) -> str:
        return f"Value.pattern({self.pattern!r})"


@dataclass(frozen=True)
class UniqueItems(Constraint):
    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (list, tuple)):
            last = object()
            for v in sorted(val):
                if last == v:
                    return False
                last = v
            return True

    def __repr__(self) -> str:
        return "Value.uniqueItems()"


@dataclass(frozen=True)
class LocalTime(Constraint):
    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (datetime, time)):
            return val.tzinfo is None

    def __repr__(self) -> str:
        return "Value.localTime()"


@dataclass(frozen=True)
class ZonedTime(Constraint):
    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, (datetime, time)):
            return val.tzinfo is not None

    def __repr__(self) -> str:
        return "Value.zonedTime()"


@dataclass(frozen=True)
class Validator(Constraint):
    callable: Callable[[Any, Any], bool | None]

    def evaluate(self, val, before) -> bool | None:
        return self.callable(val, before)

    def __repr__(self) -> str:
        return f"Value.validate({self.callable!r})"


def _import_fqn(val: str) -> Any:
    spec = val.rsplit(".", maxsplit=1)
    if len(spec) == 1:
        modname = "builtins"
        parts = spec
    else:
        modname = spec[0]
        parts = [spec[1]]
    if not (modname and parts[0]):
        raise TypeError
    while True:
        try:
            mod = import_module(modname)
            break
        except ModuleNotFoundError:
            spec = modname.rsplit(".", maxsplit=1)
            if len(spec) <= 1:
                raise
            modname = spec[0]
            parts.append(spec[1])
            continue
    cls = mod
    for part in reversed(parts):
        cls = getattr(cls, part)
    return cls


def _type_from_str(val: str, T=None):
    cls = _import_fqn(val)
    if not isinstance(cls, type):
        raise TypeError
    if T and T is not Any and not issubclass(cls, T):
        raise TypeError
    return cls


def _Callable_from_object(val: object, PT=None, RT=None):
    if not callable(val):
        raise TypeError
    if isinstance(PT, list):
        # check only structural compatibility of arguments
        sig = signature(val)
        args = [None] * len(PT)
        sig.bind(*args)  # may raise TypeError
    return val


def _Callable_from_str(val: str, PT=None, RT=None):
    f = _import_fqn(val)
    return _Callable_from_object(f, PT, RT)


@dataclass(frozen=True)
class ImportPath(Constraint):
    spec: type | None = None

    def __post_init__(self):
        if self.spec:
            origin = get_origin(self.spec) or self.spec
            if origin not in {type, Callable}:
                raise TypeError(
                    f"Value.importPath() support only type or Callable, but {self.spec!r} given."
                )

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, str):
            if self.spec:
                origin = get_origin(self.spec) or self.spec
                if origin is type:
                    try:
                        _type_from_str(val, *get_args(self.spec))
                    except Exception:
                        return False
                else:
                    try:
                        _Callable_from_str(val, *get_args(self.spec))
                    except Exception:
                        return False
            else:
                try:
                    _import_fqn(val)
                except Exception:
                    return False
            return True

    def __repr__(self) -> str:
        return f"Value.importPath({self.spec})"


FormatLiteral = Literal["email", "regex", "uri", "uri-reference"]

# https://jmrware.com/articles/2009/uri_regexp/URI_regex.html
re_python_rfc3986_URI = re.compile(
    r""" ^
    # RFC-3986 URI component:  URI
    [A-Za-z][A-Za-z0-9+\-.]* :                                      # scheme ":"
    (?: //                                                          # hier-part
      (?: (?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})* @)?
      (?:
        \[
        (?:
          (?:
            (?:                                                    (?:[0-9A-Fa-f]{1,4}:){6}
            |                                                   :: (?:[0-9A-Fa-f]{1,4}:){5}
            | (?:                            [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){4}
            | (?: (?:[0-9A-Fa-f]{1,4}:){0,1} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){3}
            | (?: (?:[0-9A-Fa-f]{1,4}:){0,2} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){2}
            | (?: (?:[0-9A-Fa-f]{1,4}:){0,3} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}:
            | (?: (?:[0-9A-Fa-f]{1,4}:){0,4} [0-9A-Fa-f]{1,4})? ::
            ) (?:
                [0-9A-Fa-f]{1,4} : [0-9A-Fa-f]{1,4}
              | (?: (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) \.){3}
                    (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
              )
          |   (?: (?:[0-9A-Fa-f]{1,4}:){0,5} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}
          |   (?: (?:[0-9A-Fa-f]{1,4}:){0,6} [0-9A-Fa-f]{1,4})? ::
          )
        | [Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+
        )
        \]
      | (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
           (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
      | (?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*
      )
      (?: : [0-9]* )?
      (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
    | /
      (?:    (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+
        (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
      )?
    |        (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+
        (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
    |
    )
    (?:\? (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?   # [ "?" query ]
    (?:\# (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?   # [ "#" fragment ]
    $ """,
    re.VERBOSE,
)
re_python_rfc3986_URI_reference = re.compile(
    r""" ^
    # RFC-3986 URI component: URI-reference
    (?:                                                               # (
      [A-Za-z][A-Za-z0-9+\-.]* :                                      # URI
      (?: //
        (?: (?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})* @)?
        (?:
          \[
          (?:
            (?:
              (?:                                                    (?:[0-9A-Fa-f]{1,4}:){6}
              |                                                   :: (?:[0-9A-Fa-f]{1,4}:){5}
              | (?:                            [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){4}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,1} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){3}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,2} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){2}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,3} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}:
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,4} [0-9A-Fa-f]{1,4})? ::
              ) (?:
                  [0-9A-Fa-f]{1,4} : [0-9A-Fa-f]{1,4}
                | (?: (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) \.){3}
                      (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
                )
            |   (?: (?:[0-9A-Fa-f]{1,4}:){0,5} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}
            |   (?: (?:[0-9A-Fa-f]{1,4}:){0,6} [0-9A-Fa-f]{1,4})? ::
            )
          | [Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+
          )
          \]
        | (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
             (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
        | (?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*
        )
        (?: : [0-9]* )?
        (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
      | /
        (?:    (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+
          (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
        )?
      |        (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+
          (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
      |
      )
      (?:\? (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?
      (?:\# (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?
    | (?: //                                                          # / relative-ref
        (?: (?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})* @)?
        (?:
          \[
          (?:
            (?:
              (?:                                                    (?:[0-9A-Fa-f]{1,4}:){6}
              |                                                   :: (?:[0-9A-Fa-f]{1,4}:){5}
              | (?:                            [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){4}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,1} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){3}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,2} [0-9A-Fa-f]{1,4})? :: (?:[0-9A-Fa-f]{1,4}:){2}
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,3} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}:
              | (?: (?:[0-9A-Fa-f]{1,4}:){0,4} [0-9A-Fa-f]{1,4})? ::
              ) (?:
                  [0-9A-Fa-f]{1,4} : [0-9A-Fa-f]{1,4}
                | (?: (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) \.){3}
                      (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
                )
            |   (?: (?:[0-9A-Fa-f]{1,4}:){0,5} [0-9A-Fa-f]{1,4})? ::    [0-9A-Fa-f]{1,4}
            |   (?: (?:[0-9A-Fa-f]{1,4}:){0,6} [0-9A-Fa-f]{1,4})? ::
            )
          | [Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+
          )
          \]
        | (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
             (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
        | (?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*
        )
        (?: : [0-9]* )?
        (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
      | /
        (?:    (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+
          (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
        )?
      |        (?:[A-Za-z0-9\-._~!$&'()*+,;=@] |%[0-9A-Fa-f]{2})+
          (?:/ (?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})* )*
      |
      )
      (?:\? (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?
      (?:\# (?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})* )?
    )                                                                       # )
    $ """,
    re.VERBOSE,
)

re_python_rfc5322_email_simplified = re.compile(
    r""" ^
    [a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@
    (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
    $ """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class Format(Constraint):
    format: FormatLiteral

    def evaluate(self, val, before) -> bool | None:
        if isinstance(val, str):
            match self.format:
                case "email":
                    return re_python_rfc5322_email_simplified.match(val) is not None
                case "regex":
                    try:
                        re.compile(val)
                        return True
                    except Exception:
                        return False
                case "uri":
                    return re_python_rfc3986_URI.match(val) is not None
                case "uri-reference":
                    return re_python_rfc3986_URI_reference.match(val) is not None
            return False


class _ValueType:
    def __gt__(self, other: int | float) -> Constraint:
        if isinstance(other, (int, float)):
            return ExclusiveMinimum(other)
        return NotImplemented

    def __ge__(self, other: int | float) -> Constraint:
        if isinstance(other, (int, float)):
            return Minimum(other)
        return NotImplemented

    def __lt__(self, other: int | float) -> Constraint:
        if isinstance(other, (int, float)):
            return ExclusiveMaximum(other)
        return NotImplemented

    def __le__(self, other: int | float) -> Constraint:
        if isinstance(other, (int, float)):
            return Maximum(other)
        return NotImplemented

    def exclusiveMaximum(
        self, exclusiveMaximum: int | float, *, quiet: bool = False
    ) -> Constraint:
        return ExclusiveMaximum(exclusiveMaximum, quiet=quiet)

    def exclusiveMinimum(
        self, exclusiveMinimum: int | float, *, quiet: bool = False
    ) -> Constraint:
        return ExclusiveMinimum(exclusiveMinimum, quiet=quiet)

    def format(self, format: FormatLiteral, *, quiet: bool = False) -> Constraint:
        return Format(format, quiet=quiet)

    def importPath(self, spec=None, *, quiet: bool = False) -> Constraint:
        return ImportPath(spec, quiet=quiet)

    def localTime(self, *, quiet: bool = False) -> Constraint:
        return LocalTime(quiet=quiet)

    def maximum(self, maximum: int | float, *, quiet: bool = False) -> Constraint:
        return Maximum(maximum, quiet=quiet)

    def maxItems(self, maxItems: int, *, quiet: bool = False) -> Constraint:
        return MaxItems(maxItems, quiet=quiet)

    def maxLength(self, maxLength: int, *, quiet: bool = False) -> Constraint:
        return MaxLength(maxLength, quiet=quiet)

    def maxProperties(self, maxProperties: int, *, quiet: bool = False) -> Constraint:
        return MaxProperties(maxProperties, quiet=quiet)

    def minimum(self, minimum: int | float, *, quiet: bool = False) -> Constraint:
        return Minimum(minimum, quiet=quiet)

    def minItems(self, minItems: int, *, quiet: bool = False) -> Constraint:
        return MinItems(minItems, quiet=quiet)

    def minLength(self, minLength: int, *, quiet: bool = False) -> Constraint:
        return MinLength(minLength, quiet=quiet)

    def minProperties(self, minProperties: int, *, quiet: bool = False) -> Constraint:
        return MinProperties(minProperties, quiet=quiet)

    def multipleOf(self, multipleOf: int | float, *, quiet: bool = False) -> Constraint:
        return MultipleOf(multipleOf, quiet=quiet)

    def pattern(self, pattern: str, *, quiet: bool = False) -> Constraint:
        return Pattern(pattern, quiet=quiet)

    def uniqueItems(self, *, quiet: bool = False) -> Constraint:
        return UniqueItems(quiet=quiet)

    def validate(
        self, callable: Callable[[Any, Any], bool | None], *, quiet: bool = False
    ) -> Constraint:
        return Validator(callable, quiet=quiet)

    def zonedTime(self, *, quiet: bool = False) -> Constraint:
        return ZonedTime(quiet=quiet)


V = _ValueType()

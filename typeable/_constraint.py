from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from inspect import signature
import re
from typing import Any, Literal, get_args, get_origin


@dataclass(frozen=True)
class Constraint:
    def __call__(self, val) -> bool:
        raise NotImplementedError

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
    def __call__(self, val) -> bool:
        return all(arg(val) for arg in self.args)

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
    def __call__(self, val) -> bool:
        return any(arg(val) for arg in self.args)

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

    def __call__(self, val) -> bool:
        return not self.arg(val)

    def __repr__(self) -> str:
        return f"~({self.arg!r})"


@dataclass(frozen=True)
class ExclusiveMinimum(Constraint):
    exclusiveMinimum: int | float

    def __call__(self, val: int | float) -> bool:
        return val > self.exclusiveMinimum

    def __repr__(self) -> str:
        return f"Value > {self.exclusiveMinimum}"


@dataclass(frozen=True)
class Minimum(Constraint):
    minimum: int | float

    def __call__(self, val: int | float) -> bool:
        return val >= self.minimum

    def __repr__(self) -> str:
        return f"Value >= {self.minimum}"


@dataclass(frozen=True)
class ExclusiveMaximum(Constraint):
    exclusiveMaximum: int | float

    def __call__(self, val: int | float) -> bool:
        return val < self.exclusiveMaximum

    def __repr__(self) -> str:
        return f"Value < {self.exclusiveMaximum}"


@dataclass(frozen=True)
class Maximum(Constraint):
    maximum: int | float

    def __call__(self, val: int | float) -> bool:
        return val <= self.maximum

    def __repr__(self) -> str:
        return f"Value <= {self.maximum}"


@dataclass(frozen=True)
class MinLength(Constraint):
    minLength: int

    def __call__(self, val: str | dict | list | tuple) -> bool:
        return len(val) >= self.minLength

    def __repr__(self) -> str:
        return f"Value.length >= {self.minLength}"


@dataclass(frozen=True)
class MaxLength(Constraint):
    maxLength: int

    def __call__(self, val: str | dict | list | tuple) -> bool:
        return len(val) <= self.maxLength

    def __repr__(self) -> str:
        return f"Value.length <= {self.maxLength}"


@dataclass(frozen=True)
class MultipleOf(Constraint):
    multipleOf: int | float

    def __call__(self, val: int | float) -> bool:
        return val % self.multipleOf == 0

    def __repr__(self) -> str:
        return f"Value.multipleOf({self.multipleOf})"


@dataclass(frozen=True)
class Pattern(Constraint):
    pattern: str

    def __call__(self, val: str) -> bool:
        return re.search(self.pattern, val) is not None

    def __repr__(self) -> str:
        return f"Value.pattern({self.pattern!r})"


@dataclass(frozen=True)
class Unique(Constraint):
    def __call__(self, val: list | tuple) -> bool:
        last = object()
        for v in sorted(val):
            if last == v:
                return False
            last = v
        return True

    def __repr__(self) -> str:
        return "Value.unique()"


@dataclass(frozen=True)
class Validator(Constraint):
    callable: Callable[[Any], bool]

    def __call__(self, val) -> bool:
        return self.callable(val)

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

    def __call__(self, val: str) -> bool:
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

    def __call__(self, val: str) -> bool:
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


class _LengthType:
    def __gt__(self, other: int) -> Constraint:
        if isinstance(other, int):
            return MinLength(other + 1)
        return NotImplemented

    def __ge__(self, other: int) -> Constraint:
        if isinstance(other, int):
            return MinLength(other)
        return NotImplemented

    def __lt__(self, other: int) -> Constraint:
        if isinstance(other, int):
            return MaxLength(other - 1)
        return NotImplemented

    def __le__(self, other: int) -> Constraint:
        if isinstance(other, int):
            return MaxLength(other)
        return NotImplemented

    def __eq__(self, other: int) -> Constraint:
        if isinstance(other, int):
            return MinLength(other) & MaxLength(other)
        return NotImplemented


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

    @property
    def length(self):
        return _LengthType()

    def format(self, format: FormatLiteral):
        return Format(format)

    def importPath(self, spec=None):
        return ImportPath(spec)

    def multipleOf(self, multipleOf: int | float) -> Constraint:
        return MultipleOf(multipleOf)

    def pattern(self, pattern: str) -> Constraint:
        return Pattern(pattern)

    def unique(self) -> Constraint:
        return Unique()

    def validate(self, callable: Callable[[Any], bool]) -> Constraint:
        return Validator(callable)


V = _ValueType()

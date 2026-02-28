from dataclasses import dataclass
from re import search
from typing import Any, Callable


@dataclass(slots=True)
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


@dataclass(slots=True)
class Combined(Constraint):
    args: tuple[Constraint, ...]


@dataclass(slots=True)
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


@dataclass(slots=True)
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


@dataclass(slots=True)
class Not(Constraint):
    arg: Constraint

    def __call__(self, val) -> bool:
        return not self.arg(val)

    def __repr__(self) -> str:
        return f"~({self.arg!r})"


@dataclass(slots=True)
class ExclusiveMinimum(Constraint):
    exclusiveMinimum: int | float

    def __call__(self, val: int | float) -> bool:
        return val > self.exclusiveMinimum

    def __repr__(self) -> str:
        return f"Value > {self.exclusiveMinimum}"


@dataclass(slots=True)
class Minimum(Constraint):
    minimum: int | float

    def __call__(self, val: int | float) -> bool:
        return val >= self.minimum

    def __repr__(self) -> str:
        return f"Value >= {self.minimum}"


@dataclass(slots=True)
class ExclusiveMaximum(Constraint):
    exclusiveMaximum: int | float

    def __call__(self, val: int | float) -> bool:
        return val < self.exclusiveMaximum

    def __repr__(self) -> str:
        return f"Value < {self.exclusiveMaximum}"


@dataclass(slots=True)
class Maximum(Constraint):
    maximum: int | float

    def __call__(self, val: int | float) -> bool:
        return val <= self.maximum

    def __repr__(self) -> str:
        return f"Value <= {self.maximum}"


@dataclass(slots=True)
class MinLength(Constraint):
    minLength: int

    def __call__(self, val: str | dict | list | tuple) -> bool:
        return len(val) >= self.minLength

    def __repr__(self) -> str:
        return f"Value.length >= {self.minLength}"


@dataclass(slots=True)
class MaxLength(Constraint):
    maxLength: int

    def __call__(self, val: str | dict | list | tuple) -> bool:
        return len(val) <= self.maxLength

    def __repr__(self) -> str:
        return f"Value.length <= {self.maxLength}"


@dataclass(slots=True)
class MultipleOf(Constraint):
    multipleOf: int | float

    def __call__(self, val: int | float) -> bool:
        return val % self.multipleOf == 0

    def __repr__(self) -> str:
        return f"Value.multipleOf({self.multipleOf})"


@dataclass(slots=True)
class Pattern(Constraint):
    pattern: str

    def __call__(self, val: str) -> bool:
        return search(self.pattern, val) is not None

    def __repr__(self) -> str:
        return f"Value.pattern({self.pattern!r})"


@dataclass(slots=True)
class Validator(Constraint):
    callable: Callable[[Any], bool]

    def __call__(self, val) -> bool:
        return self.callable(val)

    def __repr__(self) -> str:
        return f"Value.validate({self.callable!r})"


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

    def multipleOf(self, multipleOf: int | float) -> Constraint:
        return MultipleOf(multipleOf)

    def pattern(self, pattern: str) -> Constraint:
        return Pattern(pattern)

    def validate(self, callable: Callable[[Any], bool]) -> Constraint:
        return Validator(callable)


V = _ValueType()

from collections.abc import Callable
from dataclasses import dataclass, field
import sys
from typing import Annotated, Any, Literal

from typeable import Metadata, V

Level = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
Class = Annotated[str, V.importPath(type)]


@dataclass
class Factory:
    factory: Annotated[str, V.importPath(Callable)] = field(
        metadata=Metadata(alias="()")
    )
    dot: dict[str, Any] | None = field(default=None, metadata=Metadata(alias="."))
    kwargs: dict[str, Any] = field(default_factory=dict, metadata=Metadata(extra=True))


@dataclass
class Formatter:
    class_: Class | None = field(default=None, metadata=Metadata(alias="class"))
    format: str | None = None
    datefmt: str | None = None
    style: str = "%"
    validate: bool = True
    if sys.version_info >= (3, 12):
        defaults: dict[str, Any] | None = None


@dataclass
class Filter:
    name: str = ""


@dataclass
class Handler:
    class_: Class = field(metadata=Metadata(alias="class"))
    level: Level | None = None
    formatter: str | None = None
    filters: list[str] | None = None
    kwargs: dict[str, Any] = field(default_factory=dict, metadata=Metadata(extra=True))


@dataclass
class Logger:
    level: Level | None = None
    propagate: bool = True
    filters: list[str] | None = None
    handlers: list[str] | None = None


@dataclass
class LoggingConfig:
    version: Literal[1]
    formatters: dict[str, Factory | Formatter] | None = None
    filters: dict[str, Factory | Filter] | None = None
    handlers: dict[str, Factory | Handler] | None = None
    loggers: dict[str, Logger] | None = None
    root: Logger | None = None
    incremental: bool = False
    disable_existing_loggers: bool = True

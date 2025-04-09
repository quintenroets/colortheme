import typing
from typing import TypeVar

import superpathlib
from simple_classproperty import classproperty
from typing_extensions import Self

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @classmethod
    @classproperty
    def source_root(cls) -> Self:
        return cls(__file__).parent.parent

    @classmethod
    @classproperty
    def script_templates(cls: type[T]) -> T:
        path = cls.source_root / "assets" / "script_templates"
        return typing.cast(T, path)

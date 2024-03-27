from typing import Any

from fastapi import File, Path, Query


__all__ = ("F", "Q", "P")


def Q(title: str, default_value: Any = ..., *, description="") -> Query:  # noqa N802
    return Query(
        default_value,
        title=title,
        description=description,
    )


def P(title: str, default_value: Any = ..., *, description="") -> Path:  # noqa N802
    return Path(
        default_value,
        title=title,
        description=description,
    )


def F(title: str, default_value: Any = ..., *, description="") -> File:  # noqa N802
    return File(
        default_value,
        title=title,
        description=description,
    )

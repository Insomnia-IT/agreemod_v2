import uuid

from typing import Any

from pydantic import BaseModel, ValidationError


class _Source(BaseModel):
    pointer: str | None = None
    parameter: str | None = None
    header: str | None = None


class ErrorSource:
    pointer: str | None = None
    parameter: str | None = None
    header: str | None = None

    def __init__(
        self, pointer: Any = None, parameter: str = None, header: str | dict = None
    ) -> None:
        if pointer:
            self.pointer = self._format_pointer(pointer)
        if self.pointer and self.pointer[0] != "/":
            self.pointer = "/" + self.pointer
        if parameter:
            self.parameter = parameter
        if header:
            self.header = str(header)

    def _format_pointer(self, pointer, parent: str = None) -> str:
        if isinstance(pointer, (tuple, list)):
            return "/".join(map(str, pointer))
        if isinstance(pointer, dict) and len(pointer) == 1:
            for k, v in pointer.items():
                if isinstance(v, (tuple, list)):
                    return "/".join(map(str, v))
                elif isinstance(v, (int, str)):
                    return (
                        "/".join(map(str, [parent, k, v]))
                        if parent
                        else "/".join(map(str, [k, v]))
                    )
                elif isinstance(v, dict):
                    self._format_pointer(v, parent=f"{parent}/{k}" if parent else k)
        return str(pointer)

    def dict(self) -> dict:
        result = {}
        if self.pointer:
            result["pointer"] = self.pointer
        if self.header:
            result["header"] = self.header
        if self.parameter:
            result["parameter"] = self.parameter
        return result


class Error(BaseModel):
    error_id: str

    title: str | None = None
    detail: str | None = None
    code: str | None = None
    status_code: int | None = None
    source: _Source | None = None
    meta: dict | None = None


class Errors(BaseModel):
    errors: list[Error]


class RepresentativeError(Exception):
    status_code: int = 422
    code: str | None = None
    detail: str | None = None
    title: str | None = None

    pointer: str | None = None
    source: ErrorSource | dict | None = None
    meta: dict | None = None

    def __init__(
        self,
        title: str = None,
        detail: str = None,
        code: str = None,
        status_code: int = None,
        source: ErrorSource | dict | None = None,
        meta: dict | None = None,
        pointer: str = None,
    ) -> None:
        self.title = title or self.title
        self.detail = detail or self.detail
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.source = source or self.source
        self.meta = meta or self.meta
        self.pointer = pointer or self.pointer

    def __str__(self):
        return f"{self.code}: {self.detail}"

    def dict(self):
        if not isinstance(self.source, ErrorSource):
            if isinstance(self.source, dict):
                self.source = ErrorSource(**self.source)
            elif self.pointer:
                self.source = ErrorSource(pointer=self.pointer)

        _error = Error(
            status_code=self.status_code,
            source=_Source(**self.source.dict()) if self.source else None,
            code=self.code,
            detail=self.detail,
            title=self.title,
            error_id=str(uuid.uuid4()),
            meta=self.meta,
        )

        return Errors(errors=[_error]).model_dump(exclude_none=True)


class IntakeValidationError:
    code: str = "bad_intake"

    def __init__(self, error, **kwargs):
        self.error_id: uuid.UUID = uuid.uuid4()
        if kwargs.get("source"):
            self.source = kwargs["source"]
        else:
            pointer = list(error.get("loc", ("body",)))
            if pointer[0] == "body":
                pointer[0] = ""
            self.source = ErrorSource(pointer=pointer)
        self.detail = kwargs["detail"] if kwargs.get("detail") else error.get("msg", "")
        self.title = kwargs["title"] if kwargs.get("title") else error.get("type", "")
        ctx = error.get("ctx", None)
        if isinstance(ctx, dict):
            for k, v in ctx.items():
                if not isinstance(v, (bool, int, float, str)):
                    ctx[k] = str(v)
        self.meta = kwargs["meta"] if kwargs.get("meta") else ctx

    def dict(self):
        return {
            "id": str(self.error_id),
            "code": self.code,
            "title": self.title,
            "detail": self.detail,
            "source": self.source.dict(),
            "meta": self.meta,
        }


def intake_validation_error_handler(exc: ValidationError):
    errors = []
    for error in exc.errors():
        errors.append(IntakeValidationError(error).dict())
    return {"errors": errors}

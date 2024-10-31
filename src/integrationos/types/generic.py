from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar('T')

class APIError(Exception):
    def __init__(self, error_response: ResponseError):
        self.error = error_response
        super().__init__(f"{error_response.type}: {error_response.message}")

class UnifiedOptions(BaseModel):
    response_passthrough: Optional[bool] = None
    passthrough_headers: Optional[Dict[str, str]] = None
    passthrough_query: Optional[Dict[str, str]] = None

class ListFilter(BaseModel):
    createdAfter: Optional[str] = None
    createdBefore: Optional[str] = None
    updatedAfter: Optional[str] = None
    updatedBefore: Optional[str] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None

class Pagination(BaseModel):
    limit: Optional[int] = None
    pageSize: int
    nextCursor: Optional[str] = None
    previousCursor: Optional[str] = None

class DeleteOptions(BaseModel):
    modifyToken: Optional[str] = None

class Count(BaseModel):
    count: int

class ListResponse(BaseModel, Generic[T]):
    unified: List[T]
    passthrough: Optional[Any] = None
    pagination: Pagination
    meta: Dict[str, Any]
    headers: Dict[str, str]
    statusCode: int

class Response(BaseModel, Generic[T]):
    unified: Optional[T] = None
    passthrough: Optional[Any] = None
    meta: Dict[str, Any] | None = None
    headers: Dict[str, str]
    statusCode: int

class ResponseError(BaseModel):
    type: Optional[str] = None
    code: Optional[int] = None
    status: Optional[int] = None
    key: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class HttpStatusCode(Enum):
    # 1xx Informational
    Continue = 100
    SwitchingProtocols = 101
    Processing = 102

    # 2xx Success
    OK = 200
    Created = 201
    Accepted = 202
    NonAuthoritativeInformation = 203
    NoContent = 204
    ResetContent = 205
    PartialContent = 206

    # 3xx Redirection
    MultipleChoices = 300
    MovedPermanently = 301
    Found = 302
    SeeOther = 303
    NotModified = 304
    UseProxy = 305
    TemporaryRedirect = 307

    # 4xx Client Error
    BadRequest = 400
    Unauthorized = 401
    PaymentRequired = 402
    Forbidden = 403
    NotFound = 404
    MethodNotAllowed = 405
    NotAcceptable = 406
    ProxyAuthenticationRequired = 407
    RequestTimeout = 408
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    PayloadTooLarge = 413
    URITooLong = 414
    UnsupportedMediaType = 415
    RangeNotSatisfiable = 416
    ExpectationFailed = 417
    ImATeapot = 418
    UnprocessableEntity = 422
    TooManyRequests = 429

    # 5xx Server Error
    InternalServerError = 500
    NotImplemented = 501
    BadGateway = 502
    ServiceUnavailable = 503
    GatewayTimeout = 504
    HTTPVersionNotSupported = 505

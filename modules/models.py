from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TelemetryToken(BaseModel):
    token: str


class EMQXAuthRequest(BaseModel):
    token: str
    sub: Optional[str]


class EMQXAuthResponse(BaseModel):
    class ClientAttribute(BaseModel):
        role: str
        sn: str

    class Result(Enum):
        ALLOW = "allow"
        DENY = "deny"

    class Permission(Enum):
        ALLOW = "allow"
        DENY = "deny"

    class Action(Enum):
        SUBSCRIBE = "subscribe"
        PUBLISH = "publish"
        ALL = "all"

    class AclItem(BaseModel):
        permission: str
        action: str
        topic: str
        qos: Optional[list[int]]

    result: Result
    is_superuser: bool
    client_attrs: ClientAttribute
    acl: list[AclItem]

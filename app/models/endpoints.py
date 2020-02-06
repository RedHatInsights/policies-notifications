# Standard library
from typing import List, Union
from enum import Enum, IntEnum
from datetime import datetime
from uuid import UUID

# Third-party
from pydantic import BaseModel, HttpUrl


class EndpointType(IntEnum):
    Webhook = 1
    Email = 2


class HttpType(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class Attributes(BaseModel):
    pass


class WebhookAttributes(Attributes):
    url: HttpUrl
    method: HttpType = HttpType.GET
    # timeout? SSL?
    # Request headers


class EmailAttributes(Attributes):
    to: str


# Base endpoint definition
class Endpoint(BaseModel):
    endpoint_type: EndpointType
    name: str = None
    description: str = None
    enabled: bool = False
    properties: Union[WebhookAttributes, EmailAttributes] = None
    # For response model, do we need a "status / state" properties etc?


class EndpointOut(Endpoint):
    id: UUID
    endpoint_type: int

    class Config:
        orm_mode = True


class EndpointDB(Endpoint):
    id: UUID
    accountID: str  # This is DB only - not response / request model
    created: datetime
    modified: datetime
    # These we might need in the UI?
    last_delivery_status: datetime
    last_delivery_time: datetime
    last_failure_time: datetime
    # auto_disabled etc? Tai vastavaa infoa.

    class Config:
        orm_mode = True

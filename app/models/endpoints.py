# Standard library
from typing import Union
from enum import Enum, IntEnum
from uuid import UUID

# Third-party
from pydantic import BaseModel, HttpUrl, Field


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
    disable_ssl_verification: bool
    secret_token: str
    payload_transformer: str
    # timeout? SSL?
    # Request headers


class WebhookOut(WebhookAttributes):
    class Config:
        orm_mode = True


class EmailAttributes(Attributes):
    to: str


# Base endpoint definition
class Endpoint(BaseModel):
    # endpoint_type: EndpointType
    name: str = None
    description: str = None
    enabled: bool = False
    properties: Union[WebhookAttributes, EmailAttributes] = None
    # For response model, do we need a "status / state" properties etc?


class EndpointOut(Endpoint):
    id: UUID
    # endpoint_type: int # This has to be converted back to string..

    properties: WebhookOut

    class Config:
        orm_mode = True


class EndpointResponse(Endpoint):
    # id: UUID
    # accountID: str  # This is DB only - not response / request model
    # created: datetime
    # modified: datetime
    # These we might need in the UI?
    # last_delivery_status: datetime
    # last_delivery_time: datetime
    # last_failure_time: datetime
    # auto_disabled etc? Tai vastavaa infoa.

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Settings(BaseModel):
    policies_daily_mail: bool = Field(None, alias='policies-daily-mail')
    policies_instant_mail: bool = Field(None, alias='policies-instant-mail')

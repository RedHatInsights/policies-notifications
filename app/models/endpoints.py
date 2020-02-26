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
    # payload_transformer: str
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
    # endpoint_type: int = 1
    properties: Union[WebhookAttributes, EmailAttributes] = None
    # For response model, do we need a "status / state" properties etc?

    # class Config:
    #     orm_mode = True


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

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Settings(BaseModel):
    policies_daily_mail: bool = Field(None, alias='policies-daily-mail')
    policies_instant_mail: bool = Field(None, alias='policies-instant-mail')


class StatusReply(BaseModel):
    status: str


class NotificationHistory(BaseModel):
    account_id: str
    endpoint_id: str
    invocation_time: int = 0
    invocation_result: bool = False
    details: dict = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class NotificationHistoryOut(NotificationHistory):
    id: str

    class Config:
        orm_mode = True


class NotificationDetails(BaseModel):
    code: int

    class Config:
        orm_mode = True

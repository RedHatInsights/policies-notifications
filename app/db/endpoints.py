from typing import List

from ..models.endpoints import Endpoint as EndpointCreate, EndpointType, WebhookAttributes
from .schemas import Endpoint


# from .conn import db

async def get_endpoints(account_id: str):
    Endpoint.query.where(Endpoint.account_id == account_id).gino.all()
    endpoints: List[Endpoint] = await Endpoint.query.gino.all()
    return endpoints


async def create_endpoint(account_id: str, endpoint: EndpointCreate):
    # Here we need to parse the attributestype also.. is it webhook or email?
    endpoint_dict = endpoint.dict()
    endpoint_dict.pop('properties', None)
    endpoint_row = Endpoint(**endpoint_dict)
    endpoint_row.account_id = account_id
    await endpoint_row.create()


async def get_endpoint(account_id: str, id: str):
    return await Endpoint.get(id)


async def delete_endpoint(account_id: str, id: str):
    pass


async def update_endpoint(account_id: str, id: str, endpoint: EndpointCreate):
    pass

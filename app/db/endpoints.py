from typing import List

from ..models.endpoints import Endpoint as EndpointCreate, EndpointResponse, WebhookAttributes
from .schemas import Endpoint, WebhookEndpoint


async def get_endpoints(account_id: str):
    # SELECT e. *, w. * FROM public.endpoints AS e
    # LEFT OUTER JOIN public.endpoint_webhooks AS w ON(w.endpoint_id = e.id AND e.endpoint_type = 1)

    q = Endpoint.query.where((Endpoint.account_id == account_id) & (Endpoint.endpoint_type == 1)).alias()\
        .join(WebhookEndpoint).select()
    endpoints: List[Endpoint] = await q.gino.load(
        Endpoint.load(properties=WebhookEndpoint, id=WebhookEndpoint.endpoint_id)).all()
    return endpoints


async def create_endpoint(account_id: str, endpoint: EndpointCreate):
    # Here we need to parse the attributestype also.. is it webhook or email?
    endpoint_dict = endpoint.dict()
    endpoint_dict.pop('properties', None)
    endpoint_row = Endpoint(**endpoint_dict)
    endpoint_row.account_id = account_id
    endpoint_row = await endpoint_row.create()

    if isinstance(endpoint.properties, WebhookAttributes):
        attributes: WebhookAttributes = endpoint.properties
        webhook: WebhookEndpoint = WebhookEndpoint(**attributes.dict())
        webhook.endpoint_id = endpoint_row.id
        await webhook.create()


async def get_endpoint(account_id: str, id: str):
    # TODO Missing account_id filtering
    endpoint = await Endpoint.get(id)
    if endpoint.endpoint_type == 1:
        webhook: WebhookEndpoint = await WebhookEndpoint.query.where(WebhookEndpoint.endpoint_id == endpoint.id)\
            .gino.one()
        print('Received: ', endpoint.__dict__)
        print('Received 2: ', webhook.__dict__)
        # ep: EndpointResponse = EndpointResponse(**endpoint.__dict__)
        ep = EndpointResponse.from_orm(endpoint)
        ep.properties = webhook
        return ep

    return endpoint


async def delete_endpoint(account_id: str, id: str):
    pass


async def update_endpoint(account_id: str, id: str, endpoint: EndpointCreate):
    pass

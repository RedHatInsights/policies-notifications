from typing import List

from ..models.endpoints import Endpoint as EndpointCreate, EndpointResponse, WebhookAttributes, NotificationHistory as NotificationHistoryCreate
from .schemas import Endpoint, WebhookEndpoint, NotificationHistory


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
    print('Name: {}'.format(endpoint.name))
    endpoint_dict = endpoint.dict()
    endpoint_dict.pop('properties', None)
    endpoint_row = Endpoint(**endpoint_dict)
    endpoint_row.account_id = account_id

    if isinstance(endpoint.properties, WebhookAttributes):
        endpoint_row.endpoint_type = 1

    endpoint_row = await endpoint_row.create()

    if isinstance(endpoint.properties, WebhookAttributes):
        attributes: WebhookAttributes = endpoint.properties
        webhook: WebhookEndpoint = WebhookEndpoint(**attributes.dict())
        webhook.endpoint_id = endpoint_row.id
        await webhook.create()


async def get_endpoint(account_id: str, id: str):
    print('get_endpoint')
    # TODO This could return 0 hits also.. stop processing in that case.
    endpoint = await Endpoint.query.where((Endpoint.account_id == account_id) & (Endpoint.id == id)).gino.one()
    if endpoint.endpoint_type == 1:
        # TODO This could be a JOIN query also, but works fine this way as well (see get_endpoints)
        webhook: WebhookEndpoint = await WebhookEndpoint.query.where(WebhookEndpoint.endpoint_id == endpoint.id)\
            .gino.one()
        # ep: EndpointResponse = EndpointResponse(**endpoint.__dict__)
        ep = EndpointResponse.from_orm(endpoint)
        ep.properties = webhook
        return ep

    return endpoint


async def delete_endpoint(account_id: str, id: str):
    endpoint = await Endpoint.query.where((Endpoint.account_id == account_id) & (Endpoint.id == id)).gino.status()
    if endpoint.endpoint_type == 1:
        # Delete WebhookEndpoint first, then the Endpoint
        # TODO Or add CASCADE to DB definition to simplify deletes?
        pass


async def update_endpoint(account_id: str, id: str, endpoint: EndpointCreate):
    pass


async def create_history_event(notif_history: NotificationHistoryCreate):
    notif_history_row: NotificationHistory = NotificationHistory(**notif_history.dict())
    await notif_history_row.create()


async def get_endpoint_history(account_id: str, endpoint_id: str):
    notif_history = await NotificationHistory.query.where((NotificationHistory.account_id == account_id) &
                                                          (NotificationHistory.endpoint_id == endpoint_id))\
        .gino.all()
    return notif_history

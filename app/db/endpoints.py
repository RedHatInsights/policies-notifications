from typing import List

from asyncpg.exceptions import DataError

from ..db.conn import db
from ..core.errors import InvalidInputException
from ..models.endpoints import Endpoint as EndpointCreate, EndpointResponse, WebhookAttributes, \
    NotificationHistory as NotificationHistoryCreate
from .schemas import Endpoint, WebhookEndpoint, NotificationHistory


async def get_endpoints(account_id: str):
    q = Endpoint.query.where((Endpoint.account_id == account_id) & (Endpoint.endpoint_type == 1)).alias() \
        .join(WebhookEndpoint).select()
    endpoints: List[Endpoint] = await q.gino.load(
        Endpoint.load(properties=WebhookEndpoint, id=WebhookEndpoint.endpoint_id)).all()

    return endpoints


async def create_endpoint(account_id: str, endpoint: EndpointCreate) -> EndpointResponse:
    # Here we need to parse the attributestype also.. is it webhook or email?
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
        properties = await webhook.create()

    response: EndpointResponse = EndpointResponse.from_orm(endpoint_row)
    response.properties = properties
    return response


async def get_endpoint(account_id: str, id: str):
    try:
        endpoint = await Endpoint.query.where((Endpoint.account_id == account_id) & (Endpoint.id == id)).gino.first()
    except DataError as e:
        raise InvalidInputException(e)

    if endpoint is None:
        return None

    if endpoint.endpoint_type == 1:
        webhook: WebhookEndpoint = await WebhookEndpoint.query.where(WebhookEndpoint.endpoint_id == endpoint.id) \
            .gino.one()
        ep = EndpointResponse.from_orm(endpoint)
        ep.properties = webhook
        return ep

    return endpoint


async def delete_endpoint(account_id: str, id: str) -> bool:
    await Endpoint.delete.where((Endpoint.account_id == account_id) & (Endpoint.id == id)).gino.status()


async def update_endpoint(account_id: str, id: str, endpoint: EndpointCreate):
    pass


async def create_history_event(notif_history: NotificationHistoryCreate):
    notif_history_row: NotificationHistory = NotificationHistory(**notif_history.dict())
    # TODO Return the history?
    await notif_history_row.create()


async def get_endpoint_history(account_id: str, endpoint_id: str):
    notif_history = await db.select(
        [NotificationHistory.id, NotificationHistory.invocation_result, NotificationHistory.invocation_time,
         NotificationHistory.created]) \
        .where((NotificationHistory.account_id == account_id) & (NotificationHistory.endpoint_id == endpoint_id)) \
        .order_by(NotificationHistory.id.desc()) \
        .gino.model(NotificationHistory).all()

    return notif_history


async def get_endpoint_history_details(account_id: str, endpoint_id: str, history_id: int):
    details = await db.select([NotificationHistory.details])\
        .where((NotificationHistory.account_id == account_id) & (NotificationHistory.endpoint_id == endpoint_id) &
               (NotificationHistory.id == history_id)).gino.load(NotificationHistory.details).first()
    return details

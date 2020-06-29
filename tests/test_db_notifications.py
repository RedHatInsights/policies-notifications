import pytest

from app.db import endpoints as endpoints_db
from app.models.endpoints import Endpoint as EndpointCreate, WebhookAttributes, NotificationHistory


@pytest.mark.asyncio
async def test_notifications_history(client):
    webhook = WebhookAttributes(url='http://localhost.com/test', method='POST')
    endpoint = EndpointCreate(name='test', description='test endpoint', enabled=True, properties=webhook)
    endpoint_created = await endpoints_db.create_endpoint('test_account', endpoint)
    assert endpoint_created.id is not None

    endpoint_id = str(endpoint_created.id)

    # Positive
    await endpoints_db.create_history_event(NotificationHistory(account_id='test_account',
                                                                endpoint_id=endpoint_id, invocation_time=1,
                                                                invocation_result=True))
    # Negative
    await endpoints_db.create_history_event(NotificationHistory(account_id='test_account',
                                                                endpoint_id=endpoint_id, invocation_time=100,
                                                                invocation_result=False, details={'code': 500}))

    history = await endpoints_db.get_endpoint_history('test_account', endpoint_id)
    assert len(history) == 2
    # DESC order
    assert history[0].invocation_result is False
    assert history[1].invocation_result is True
    assert history[0].details is None

    details = await endpoints_db.get_endpoint_history_details('test_account', endpoint_id, history[0].id)
    assert details is not None
    assert details['code'] == 500

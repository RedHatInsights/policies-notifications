import pytest

from app.db import endpoints as endpoints_db
from app.models.endpoints import Endpoint as EndpointCreate, WebhookAttributes, NotificationHistory


@pytest.mark.asyncio
async def test_endpoints_cascade(client):
    webhook = WebhookAttributes(url='http://localhost.com/test', method='POST')
    endpoint = EndpointCreate(name='test', description='test endpoint', enabled=True, properties=webhook)
    endpoint_created = await endpoints_db.create_endpoint('test_account', endpoint)
    assert endpoint_created.id is not None

    endpoint_fetched = await endpoints_db.get_endpoint('test_account', str(endpoint_created.id))
    assert endpoint_fetched.created == endpoint_created.created
    assert endpoint_fetched.id == endpoint_created.id
    assert endpoint_fetched.properties.url == webhook.url

    # Add data to history
    endpoint_id = str(endpoint_created.id)

    await endpoints_db.create_history_event(NotificationHistory(account_id='test_account',
                                                                endpoint_id=endpoint_id, invocation_time=1,
                                                                invocation_result=True))

    history = await endpoints_db.get_endpoint_history('test_account', endpoint_id)
    assert len(history) == 1

    # Now delete the endpoint and verify that webhook properties as well as history is gone also
    await endpoints_db.delete_endpoint('test_account', endpoint_id)

    fetched_endpoint = await endpoints_db.get_endpoint('test_account', endpoint_id)
    assert fetched_endpoint is None

    history = await endpoints_db.get_endpoint_history('test_account', endpoint_id)
    assert len(history) == 0

from typing import Set, List
import json
from datetime import date, timedelta, datetime

import pytest
from aiohttp import web

from app.db import email as email_store
from app.db import subscriptions as sub_store
from app.db.schemas import EmailAggregation
from app.email import process
from app.email.process import EmailProcessor, BopSender, instant_mail_topic, _get_subscribers
from app.events.models import Notification
from app.models.auth import Credentials
from app.integ import rbac


@pytest.mark.asyncio
async def test_process_topic(monkeypatch, client):
    async def mock_send_to_subscribers(self, account_id: str, template_type: str, topic: str, data: dict):
        assert topic.endswith('2 policies triggered on localhost')

    monkeypatch.setattr(EmailProcessor, "_send_to_subscribers", mock_send_to_subscribers)
    email_process: EmailProcessor = EmailProcessor()
    notif = Notification(tenantId='a', insightId='b', tags={'display_name': 'localhost'},
                         triggerNames=['trigger1', 'trigger2'])
    await email_process.process(notif)


@pytest.mark.asyncio
async def disable_test_invalid_recipients(monkeypatch, aiohttp_raw_server, aiohttp_unused_port):
    port = aiohttp_unused_port()

    async def handler(request):
        json_payload = json.loads(await request.text())
        receivers: Set = set(json_payload['emails'][0]['bccList'])
        if 'invalid1' in receivers and 'invalid2' in receivers:
            return web.Response(status=400, content_type='application/json',
                                text=str(json.dumps({'message': 'Invalid recipient(s): invalid1,invalid2'})))
        elif len(receivers) == 1 and 'correct1' in receivers:
            return web.Response(status=200, content_type='application/json',
                                text=str(json.dumps({'message': 'success'})))
        else:
            return web.Response(status=500, content_type='application/json',
                                text=str(json.dumps({'message': 'Nearly impossible error'})))

    async def _get_subscribers(account_id: str, template_type: str):
        return {'invalid1', 'invalid2', 'correct1'}

    def get_url(self):
        return 'http://localhost:{}/v1/sendEmails'.format(port)

    await aiohttp_raw_server(handler, port=port)

    monkeypatch.setattr(BopSender, "get_url", get_url)
    monkeypatch.setattr(process, "_get_subscribers", _get_subscribers)

    email_process: EmailProcessor = EmailProcessor()
    notif = Notification(tenantId='a', insightId='b', tags={'display_name': 'localhost'},
                         triggerNames=['trigger1', 'trigger2'])

    # If no status 200 is returned, then this will throw an exception
    await email_process._send_to_subscribers('account_id', EmailProcessor.INSTANT_TEMPLATE_KEY,
                                             instant_mail_topic(notif), notif.dict())


@pytest.mark.asyncio
async def test_email_aggregation(client):
    await email_store.insert_email('test_account', 'insight_id_1', {'time': 'now'})

    # Fetching for future
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    tomorrow = today + timedelta(days=1)

    fetched_mails: List[EmailAggregation] = await email_store.fetch_emails(today, tomorrow)
    current_length = len(fetched_mails)

    first_mail: EmailAggregation = fetched_mails.pop(1)  # pop(0) is one of the previous tests

    assert 'insight_id_1' == first_mail.insight_id
    assert 'test_account' == first_mail.account_id

    await email_store.remove_aggregations(today, tomorrow, 'test_account')

    # Aggregations should have been deleted.. lets check
    fetched_mails: List[EmailAggregation] = await email_store.fetch_emails(today, tomorrow)
    assert len(fetched_mails) == current_length - 1
    for mail in fetched_mails:
        if mail.account_id == 'test_account' and mail.insight_id == 'insight_id_1':
            assert False


@pytest.mark.asyncio
async def test_rbac_recipients(monkeypatch, client):
    async def get_rbac_permissions_for_identity(identity: Credentials):
        if identity.username == 'user1' and identity.account_number == 'test_account':
            return json.loads(
                json.dumps({'data': [{'permission': 'policies:*:*', 'resourceDefinitions': []}]}))['data']
        elif identity.username == 'user2' and identity.account_number == 'test_account':
            return json.loads(
                json.dumps({'data': [{'permission': 'vulnerabilities:*:*', 'resourceDefinitions': []}]}))['data']
        else:
            return json.loads(
                json.dumps({'data': []}))['data']

    monkeypatch.setattr(rbac, "get_rbac_permissions_for_identity", get_rbac_permissions_for_identity)

    # Create our subscriptions
    await sub_store.add_email_subscription('test_account', 'user1', 'policies-daily-mail')
    await sub_store.add_email_subscription('test_account', 'user2', 'policies-daily-mail')
    await sub_store.add_email_subscription('test_account', 'user3', 'policies-daily-mail')

    # Fetch and verify RBAC filtering
    subscribers = await _get_subscribers('test_account', 'policies-daily-mail')
    assert len(subscribers) == 1
    assert 'user1' in subscribers

from typing import Set
import json

import pytest
from aiohttp import web

from app.email import process
from app.email.process import EmailProcessor, BopSender, instant_mail_topic
from app.events.models import Notification


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

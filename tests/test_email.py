import pytest

from app.email.process import EmailProcessor
from app.events.models import Notification
from app.db import conn


@pytest.mark.asyncio
async def test_process(monkeypatch):
    await conn.setup()

    async def mock_send_to_subscribers(self, account_id: str, template_type: str, topic: str, data: dict):
        assert topic.endswith('2 policies triggered on localhost')

    monkeypatch.setattr(EmailProcessor, "_send_to_subscribers", mock_send_to_subscribers)
    process: EmailProcessor = EmailProcessor()
    notif = Notification(tenantId='a', insightId='b', tags={'display_name': 'localhost'},
                         triggerNames=['trigger1', 'trigger2'])
    await process.process(notif)

import logging
from typing import List
import json
import sched
import time

from ..events.models import Notification
from .template import TemplateEngine
from .bop_service import BopSender
from ..db import email as email_store, subscriptions
from ..db.schemas import EmailAggregation

logger = logging.getLogger(__name__)


async def _get_subscribers(account_id: str, template_type: str):
    subscribers = await subscriptions.get_subscribers(account_id, template_type)
    receivers = []
    for s in subscribers:
        receivers.append(s.user_id)

    return receivers


class EmailProcessor:
    INSTANT_TEMPLATE_KEY = 'custom-policies-instant-mail'
    DAILY_TEMPLATE_KEY = 'custom-policies-daily-mail'

    def __init__(self) -> None:
        self.rendering = TemplateEngine()
        self.sender = BopSender()

    async def _send_to_subscribers(self, account_id: str, template_type: str, data: dict):
        email = await self.rendering.render(template_type, data)
        receivers = await _get_subscribers(account_id, template_type)

        # TODO What if BOP is down? Should we discard the message?
        #      Also, if we process duplicate email to aggregation, we will have issues..
        await self.sender.send_email(email, receivers)

    async def process(self, notification: Notification):
        account_id: str = notification.tenantId

        data: dict = notification.dict()
        await email_store.insert_email(account_id, data)
        await self._send_to_subscribers(account_id, self.INSTANT_TEMPLATE_KEY, data)

    async def process_aggregated(self):
        # Should the scheduler give this one a timestamp?
        # Load all stored emails (not processed previously) for the past defined time, group by account_id
        emails: List[EmailAggregation] = await email_store.fetch_emails()

        prev_account_id = None
        aggregated = {}
        for e in emails:
            if prev_account_id != e.account_id:
                # Add new processed item..
                prev_account_id = e.account_id
                aggregated[e.account_id] = {}

            payload = json.loads(e.payload)
            for trigger in payload['triggerNames']:
                if trigger in aggregated[e.account_id]:
                    count = aggregated[e.account_id][trigger]
                    aggregated[e.account_id][trigger] = count + 1
                else:
                    aggregated[e.account_id][trigger] = 1

        for account_aggregate in aggregated.items():
            account_id = account_aggregate[0]
            policies = account_aggregate[1]
            await self._send_to_subscribers(account_id, self.DAILY_TEMPLATE_KEY, policies)

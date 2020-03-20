import logging
from typing import List
import json
from datetime import date, timedelta, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
        self.scheduler = AsyncIOScheduler()
        cron_trigger = CronTrigger(hour=1)
        self.scheduler.add_job(self.daily_mail, cron_trigger)
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=False)

    async def _send_to_subscribers(self, account_id: str, template_type: str, data: dict):
        email = await self.rendering.render(template_type, data)
        receivers = await _get_subscribers(account_id, template_type)

        # TODO What if BOP is down? Should we discard the message?
        #      Also, if we process duplicate email to aggregation, we will have issues..
        await self.sender.send_email(email, receivers)

    async def process(self, notification: Notification):
        account_id: str = notification.tenantId

        data: dict = notification.dict()
        await self._send_to_subscribers(account_id, self.INSTANT_TEMPLATE_KEY, data)
        await email_store.insert_email(account_id, data)

    async def daily_mail(self):
        today = date.today()
        today = datetime(today.year, today.month, today.day)
        yesterday = today - timedelta(days=1)
        await self.process_aggregated(yesterday, today)

    async def process_aggregated(self, start_time: datetime, end_time: datetime):
        emails: List[EmailAggregation] = await email_store.fetch_emails(start_time, end_time)

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
            data: dict = {"trigger_stats": policies}
            await self._send_to_subscribers(account_id, self.DAILY_TEMPLATE_KEY, data)

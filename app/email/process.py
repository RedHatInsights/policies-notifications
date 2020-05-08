import logging
from typing import List, Dict, Any, Set, Tuple
import json
from datetime import date, timedelta, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from asyncpg.exceptions import PostgresError
from prometheus_client import Counter

from ..core.errors import BOPInvalidRecipientException
from ..events.models import Notification
from .template import TemplateEngine, dateformat, datetimeformat, set_from_sets
from .bop_service import BopSender
from ..db import email as email_store, subscriptions
from ..db.conn import db
from ..db.schemas import EmailAggregation

logger = logging.getLogger(__name__)


async def _get_subscribers(account_id: str, template_type: str) -> Set[str]:
    subscribers = await subscriptions.get_subscribers(account_id, template_type)
    receivers = set()
    for s in subscribers:
        receivers.add(s.user_id)

    return receivers


def aggregate(emails: List[EmailAggregation]) -> Dict[Any, dict]:
    aggregated = {}
    for e in emails:
        if e.account_id not in aggregated:
            aggregated[e.account_id] = {}

        payload: Notification = Notification(**json.loads(e.payload))
        for trigger in payload.triggerNames:
            if trigger not in aggregated[e.account_id]:
                aggregated[e.account_id][trigger] = set()

            aggregated[e.account_id][trigger].add(payload.insightId)

    return aggregated


def policies_systems(policies_count, systems_count) -> Tuple[str, str]:
    policies_str = "policies" if policies_count > 1 else "policy"
    systems_str = "systems" if systems_count > 1 else "system"

    return policies_str, systems_str


def daily_mail_topic(data: dict) -> str:
    policies: dict = data['trigger_stats']
    policies_count = len(policies.keys())
    systems_count = len(set_from_sets(policies.values()))

    policies_str, systems_str = policies_systems(policies_count, systems_count)
    topic = "{} - {} {}} triggered on {} {}}".format(dateformat(data['start_time']), policies_str, policies_count,
                                                     systems_count, systems_str)

    return topic


def instant_mail_topic(data: Notification) -> str:
    policies_count = len(data.triggerNames)
    policies_str, _ = policies_systems(policies_count, 0)

    topic = '{} - {} {} triggered on {}'.format(datetimeformat(datetime.now()), policies_count, policies_str,
                                                data.tags['display_name'])
    return topic


class EmailProcessor:
    postgres_errors = Counter('postgres_insert_errors', 'Unrecoverable errors when inserting to Postgres')
    INSTANT_TEMPLATE_KEY = 'policies-instant-mail'
    DAILY_TEMPLATE_KEY = 'policies-daily-mail'

    def __init__(self) -> None:
        self.rendering = TemplateEngine()
        self.sender = BopSender()
        self.scheduler = AsyncIOScheduler()
        cron_trigger = CronTrigger(hour=1)
        self.scheduler.add_job(self.daily_mail, cron_trigger)
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=False)

    async def _send_to_subscribers(self, account_id: str, template_type: str, topic: str, data: dict):
        email = await self.rendering.render(template_type, data)
        receivers = await _get_subscribers(account_id, template_type)

        try:
            await self.sender.send_email(topic, email, receivers)
        except BOPInvalidRecipientException as e:
            # This shouldn't cause deeper recursion if the BOP service's behavior isn't changed, the first call
            # should return all the failed matches
            logger.error(
                'Invalid recipients {} for account {}'.format(e.invalid_recipients, account_id))
            receivers = receivers.difference(e.invalid_recipients)
            if len(receivers) > 0:
                await self.sender.send_email(topic, email, receivers)

    async def process(self, notification: Notification):
        account_id: str = notification.tenantId
        insight_id: str = notification.insightId

        data: dict = notification.dict()
        # Use a transaction to Postgres. First write, then send.. if write and send succeed - commit
        try:
            async with db.transaction() as tx:
                await email_store.insert_email(account_id, insight_id, data)
                await self._send_to_subscribers(account_id, self.INSTANT_TEMPLATE_KEY, instant_mail_topic(notification),
                                                data)
                tx.raise_commit()
        except PostgresError as e:
            logger.error('Failed to insert to database, fatal error - will not try again: {}'.format(e))
            self.postgres_errors.inc()

    async def daily_mail(self):
        today = date.today()
        today = datetime(today.year, today.month, today.day)
        yesterday = today - timedelta(days=1)
        await self.process_aggregated(yesterday, today)

    async def process_aggregated(self, start_time: datetime, end_time: datetime):
        emails: List[EmailAggregation] = await email_store.fetch_emails(start_time, end_time)

        aggregated_emails = aggregate(emails)

        for account_aggregate in aggregated_emails.items():
            account_id = account_aggregate[0]
            policies = account_aggregate[1]

            data: dict = {"trigger_stats": policies, 'start_time': start_time, 'end_time': end_time}

            await self._send_to_subscribers(account_id, self.DAILY_TEMPLATE_KEY, daily_mail_topic(data), data)
            await email_store.remove_aggregations(start_time, end_time, account_id)

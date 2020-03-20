import json
import logging
from typing import List
from datetime import datetime

from .schemas import EmailAggregation

logger = logging.getLogger(__name__)


async def insert_email(account_id: str, email_params: dict):
    email: EmailAggregation = EmailAggregation(account_id=account_id,
                                               payload=json.dumps(email_params))
    await email.create()


async def fetch_emails(start_time: datetime, end_time: datetime):
    emails: List[EmailAggregation] = await EmailAggregation.query\
        .where((EmailAggregation.created >= start_time) & (EmailAggregation.created < end_time))\
        .order_by(EmailAggregation.account_id).gino.all()
    return emails


async def remove_aggregations(start_time: datetime, end_time: datetime, account_id: str):
    await EmailAggregation.delete\
        .where((EmailAggregation.created >= start_time)
               & (EmailAggregation.created < end_time)
               & (EmailAggregation.account_id == account_id))\
        .gino.status()

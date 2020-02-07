import json
import logging

from .schemas import EmailAggregation


logger = logging.getLogger(__name__)


async def insert_email(account_id: str, email_params: dict):
    email: EmailAggregation = EmailAggregation(account_id=account_id,
                                               payload=json.dumps(email_params))

    logger.info('email.account_id: %s', email.account_id)

    await email.create()

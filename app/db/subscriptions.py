from typing import List

from asyncpg.exceptions import UniqueViolationError

from .schemas import EmailSubscription


async def add_email_subscription(account_id: str, user_id: str, event_type: str):
    subscription: EmailSubscription = EmailSubscription()
    subscription.account_id = account_id
    subscription.user_id = user_id
    subscription.event_type = event_type
    try:
        await subscription.create()
    except UniqueViolationError as e:
        # This is acceptable, the subscription already exists
        pass


async def remove_email_subscription(account_id: str, user_id: str, event_type: str):
    await EmailSubscription.delete\
        .where((EmailSubscription.account_id == account_id) & (EmailSubscription.user_id == user_id) &
               (EmailSubscription.event_type == event_type)).gino.status()


async def get_subscribers(account_id: str, event_type: str):
    emails: List[EmailSubscription] = await EmailSubscription.query.where((account_id == account_id) &
                                                                          (event_type == event_type)).gino.all()
    return emails

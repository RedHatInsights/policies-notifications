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
    except UniqueViolationError:
        # This is acceptable, the subscription already exists
        pass


async def remove_email_subscription(account_id: str, user_id: str, event_type: str):
    await EmailSubscription.delete \
        .where((EmailSubscription.account_id == account_id) & (EmailSubscription.user_id == user_id) &
               (EmailSubscription.event_type == event_type)).gino.status()


async def get_email_subscription_status(account_id: str, user_id: str, event_type: str):
    subscription = await EmailSubscription.query.where((EmailSubscription.account_id == account_id) &
                                                       (EmailSubscription.event_type == event_type) &
                                                       (EmailSubscription.user_id == user_id)).gino.first()
    return subscription


async def get_subscribers(account_id: str, event_type: str):
    emails: List[EmailSubscription] = await EmailSubscription.query.where((EmailSubscription.account_id == account_id) &
                                                                          (EmailSubscription.event_type == event_type)) \
        .gino.all()
    return emails


async def get_all_subscribers():
    emails: List[EmailSubscription] = await EmailSubscription.query.gino.all()
    return emails

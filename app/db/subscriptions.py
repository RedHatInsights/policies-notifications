from typing import List

from .schemas import EmailSubscription


async def add_email_subscription(account_id: str, user_id: str, event_type: str):
    subscription: EmailSubscription = EmailSubscription()
    subscription.account_id = account_id
    subscription.user_id = user_id
    subscription.event_type = event_type
    await subscription.create()


async def remove_email_subscription(account_id: str, user_id: str, event_type: str):
    pass


async def get_subscribers(account_id: str, event_type: str):
    emails: List[EmailSubscription] = await EmailSubscription.query.where((account_id == account_id) &
                                                                          (event_type == event_type)).gino.all()
    return emails

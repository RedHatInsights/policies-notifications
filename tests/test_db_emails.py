from typing import List
from datetime import date, timedelta, datetime

import pytest

import app.db.email as email_store
from app.db.schemas import EmailAggregation


@pytest.mark.asyncio
async def test_email_aggregation(client):
    await email_store.insert_email('test_account', 'insight_id_1', {'time': 'now'})

    # Fetching for future
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    tomorrow = today + timedelta(days=1)

    fetched_mails: List[EmailAggregation] = await email_store.fetch_emails(today, tomorrow)

    assert len(fetched_mails) == 1

    first_mail: EmailAggregation = fetched_mails.pop(0)

    assert 'insight_id_1' == first_mail.insight_id
    assert 'test_account' == first_mail.account_id

    await email_store.remove_aggregations(tomorrow, today, 'test_account')

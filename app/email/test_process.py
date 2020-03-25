import json

from .process import aggregate
from ..db.schemas import EmailAggregation
from ..events.models import Notification


def test_aggregate_duplicate():
    notif = Notification(tenantId='a', insightId='b', tags={}, triggerNames=['trigger1', 'trigger2'])
    # Assume trigger1 was fixed in the next report
    notif2 = Notification(tenantId='a', insightId='b', tags={}, triggerNames=['trigger2'])

    e = EmailAggregation()
    e.account_id = 'a'
    e.payload = json.dumps(notif.dict())

    e2 = EmailAggregation()
    e2.account_id = 'a'
    e2.payload = json.dumps(notif2.dict())

    aggregated_emails = aggregate([e, e2])
    assert len(aggregated_emails) == 1
    assert 'a' in aggregated_emails
    assert len(aggregated_emails['a']) == 2
    assert aggregated_emails['a']['trigger1'] == 1
    assert aggregated_emails['a']['trigger2'] == 1


def test_aggregate_per_account():
    notif = Notification(tenantId='a', insightId='b', tags={}, triggerNames=['trigger1', 'trigger2'])
    # Assume trigger1 was fixed in the next report
    notif2 = Notification(tenantId='b', insightId='b', tags={}, triggerNames=['trigger2'])

    e = EmailAggregation()
    e.account_id = 'a'
    e.payload = json.dumps(notif.dict())

    e2 = EmailAggregation()
    e2.account_id = 'b'
    e2.payload = json.dumps(notif2.dict())

    aggregated_emails = aggregate([e, e2])
    assert len(aggregated_emails) == 2
    assert 'a' in aggregated_emails and 'b' in aggregated_emails
    assert len(aggregated_emails['a']) == 2
    assert aggregated_emails['a']['trigger1'] == 1
    assert aggregated_emails['a']['trigger2'] == 1
    assert aggregated_emails['b']['trigger2'] == 1

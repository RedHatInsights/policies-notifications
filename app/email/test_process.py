import json

from .process import aggregate
from ..db.schemas import EmailAggregation
from ..events.models import Notification


def test_aggregate_duplicate():
    notif = Notification(tenantId='a', insightId='b', tags={}, triggers={'1': 'trigger1', '2': 'trigger2'})
    # Assume trigger1 was fixed in the next report
    notif2 = Notification(tenantId='a', insightId='b', tags={}, triggers={'2': 'trigger2'})

    e = EmailAggregation()
    e.account_id = 'a'
    e.payload = json.dumps(notif.dict())

    e2 = EmailAggregation()
    e2.account_id = 'a'
    e2.payload = json.dumps(notif2.dict())

    aggregated_emails, names = aggregate([e, e2])
    assert len(aggregated_emails) == 1
    assert 'a' in aggregated_emails
    assert len(aggregated_emails['a']) == 2
    assert len(aggregated_emails['a']['1']) == 1
    assert len(aggregated_emails['a']['2']) == 1
    assert names['1'] == 'trigger1'
    assert names['2'] == 'trigger2'


def test_aggregate_per_account():
    notif = Notification(tenantId='a', insightId='b', tags={}, triggers={'1': 'trigger1', '2': 'trigger2'})
    notif2 = Notification(tenantId='b', insightId='b', tags={}, triggers={'2': 'trigger2'})

    e = EmailAggregation()
    e.account_id = 'a'
    e.payload = json.dumps(notif.dict())

    e2 = EmailAggregation()
    e2.account_id = 'b'
    e2.payload = json.dumps(notif2.dict())

    aggregated_emails, _ = aggregate([e, e2])
    assert len(aggregated_emails) == 2
    assert 'a' in aggregated_emails and 'b' in aggregated_emails
    assert len(aggregated_emails['a']) == 2
    assert len(aggregated_emails['a']['1']) == 1
    assert len(aggregated_emails['a']['2']) == 1
    assert len(aggregated_emails['b']['2']) == 1


def test_aggregate_per_system_count():
    notif = Notification(tenantId='a', insightId='b', tags={}, triggers={'1': 'trigger1', '2': 'trigger2'})
    notif2 = Notification(tenantId='a', insightId='b', tags={}, triggers={'2': 'trigger2'})
    notif3 = Notification(tenantId='a', insightId='b', tags={}, triggers={'3': 'trigger3'})
    notif4 = Notification(tenantId='a', insightId='b', tags={}, triggers={'4': 'trigger4'})
    notif5 = Notification(tenantId='a', insightId='c', tags={}, triggers={'2': 'trigger2'})
    notif6 = Notification(tenantId='a', insightId='c', tags={}, triggers={'3': 'trigger3', '2': 'trigger2'})

    notifs = [notif, notif2, notif3, notif4, notif5, notif6]

    email_aggregations = []
    for n in notifs:
        e = EmailAggregation()
        e.account_id = n.tenantId
        e.payload = json.dumps(n.dict())
        email_aggregations.append(e)

    aggregated_emails, _ = aggregate(email_aggregations)

    assert len(aggregated_emails) == 1  # Account level
    assert len(aggregated_emails['a']) == 4  # 4 different triggers
    # These should probably be sets instead of lists..
    assert len(aggregated_emails['a']['1']) == 1
    assert len(aggregated_emails['a']['2']) == 2
    assert len(aggregated_emails['a']['3']) == 2
    assert aggregated_emails['a']['1'] == {'b'}
    assert aggregated_emails['a']['2'] == {'b', 'c'}
    assert aggregated_emails['a']['3'] == {'b', 'c'}
    assert aggregated_emails['a']['4'] == {'b'}

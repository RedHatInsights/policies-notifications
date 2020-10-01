from datetime import datetime, date, timedelta

import pytest

from ..events.models import Notification
from .template import TemplateEngine
from .bop_service import BopSender
from .process import instant_mail_topic, daily_mail_topic


@pytest.mark.asyncio
async def disable_test_mailing_with_japanese_characters():
    engine: TemplateEngine = TemplateEngine()
    tags = {'display_name': 'localhost'}
    trigger_names = {'12345': 'name Node 世丕且且世两上与丑万丣丕且丗丕 with no äöäöäöäöäÅå'}
    msg = {'tenantId': 'test', 'insightId': '1', 'tags': tags, 'triggers': trigger_names}
    notification: Notification = Notification(**msg)
    # notification: Notification = Notification(tenantId='test', insightId='1', tags=tags, triggerNames=trigger_names)
    notif_dict = notification.dict()

    notif_dict['now'] = datetime.now()
    rendered = await engine.render('policies-instant-mail', notif_dict)
    bop: BopSender = BopSender()
    await bop.send_email(instant_mail_topic(notification), rendered, {'miburman@redhat.com'})


@pytest.mark.asyncio
async def disable_test_japanese_with_aggregated_params():
    engine: TemplateEngine = TemplateEngine()
    policies = {'name Node 世丕且且世两上与丑万丣丕且丗丕 with no äöäöäöäöäÅå': {'a'}, 'こんいちわ': {'a', 'b'}}
    now = datetime.now()
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    yesterday = today - timedelta(days=1)
    params: dict = {"trigger_stats": policies, 'start_time': yesterday, 'end_time': today, 'now': now}
    rendered = await engine.render('policies-daily-mail', params)
    bop: BopSender = BopSender()
    await bop.send_email(daily_mail_topic(params), rendered, {'miburman@redhat.com'})


@pytest.mark.asyncio
async def disable_test_japanese_with_new_aggregated_params():
    engine: TemplateEngine = TemplateEngine()
    policies = {'12345': {'a'}, '67890': {'a', 'b'}}
    triggerNames = {'12345': 'name Node 世丕且且世两上与丑万丣丕且丗丕 with no äöäöäöäöäÅå', '67890': 'こんいちわ'}
    now = datetime.now()
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    yesterday = today - timedelta(days=1)
    params: dict = {"trigger_stats": policies, 'start_time': yesterday, 'end_time': today, 'now': now,
                    'triggerNames': triggerNames}
    rendered = await engine.render('policies-daily-mail', params)
    bop: BopSender = BopSender()
    await bop.send_email(daily_mail_topic(params), rendered, {'miburman@redhat.com'})

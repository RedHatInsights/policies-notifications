from datetime import date, timedelta, datetime

import pytest
from jinja2 import UndefinedError

from ..core.errors import NoTemplateFoundException
from ..events.models import Notification
from .template import TemplateEngine, set_from_sets
from .process import daily_mail_topic


@pytest.mark.asyncio
async def test_template_render_missing_params():
    with pytest.raises(UndefinedError):
        engine: TemplateEngine = TemplateEngine()
        policies = {}
        params: dict = {"trigger_stats": policies}
        await engine.render('policies-daily-mail', params)


@pytest.mark.asyncio
async def test_no_template_exception():
    with pytest.raises(NoTemplateFoundException):
        engine: TemplateEngine = TemplateEngine()
        params: dict = {"trigger_stats": {}}
        await engine.render('policies-not-found-typo', params)


@pytest.mark.asyncio
async def test_with_aggregated_params():
    engine: TemplateEngine = TemplateEngine()
    policies = {'Strict policy': {'a'}, 'Relaxed one': {'a', 'b'}}
    now = datetime.now()
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    yesterday = today - timedelta(days=1)
    params: dict = {"trigger_stats": policies, 'start_time': yesterday, 'end_time': today, 'now': now}
    await engine.render('policies-daily-mail', params)


@pytest.mark.asyncio
async def test_with_instant_params():
    engine: TemplateEngine = TemplateEngine()
    tags = {'display_name': 'localhost'}
    trigger_names = ['First policy', 'Second policy']
    notification: Notification = Notification(tenantId='test', insightId='1', tags=tags, triggerNames=trigger_names)
    notif_dict = notification.dict()
    notif_dict['now'] = datetime.now()
    await engine.render('policies-instant-mail', notif_dict)


def test_set_of_sets():
    list_of_sets = [{'a', 'b', 'c'}, {'a'}, {'b', 'c'}]
    clear_set = set_from_sets(list_of_sets)
    assert clear_set == {'a', 'b', 'c'}


def test_daily_mail_topic():
    policies = {'name': {'a'}, 'name2': {'a', 'b'}}
    now = datetime.now()
    today = date.today()
    today = datetime(today.year, today.month, today.day)
    yesterday = today - timedelta(days=1)
    params: dict = {"trigger_stats": policies, 'start_time': yesterday, 'end_time': today, 'now': now}
    topic = daily_mail_topic(params)
    assert topic.endswith('2 policies triggered on 2 systems')

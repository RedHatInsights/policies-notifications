import json

from ..events.models import Action


def transform(target: str, action: Action):
    if target is None:
        payload = json.dumps(action.__dict__)
    elif target == 'slack':
        payload = to_slack(action)
    else:
        payload = json.dumps(action.__dict__)


# TODO Slack probably needs OAuth authentication to add as app also.. a common way for all insights apps
#  to contribute to Slack?
def to_slack(action: Action):
    return '{ \"text\": \"A super static transformer\"}'

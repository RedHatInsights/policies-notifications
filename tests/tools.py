import json
from base64 import b64encode


def create_identity_header(account_number: str, username: str):
    identity = {'identity': {'user': {'username': username}, 'account_number': account_number}}
    json_identity = json.dumps(identity).encode('utf-8')
    return b64encode(json_identity)


def create_broken_identity_header():
    identity = {'user': {'username': 'first'}, 'account_number': 'one'}
    json_identity = json.dumps(identity).encode('utf-8')
    return b64encode(json_identity)

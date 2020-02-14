import base64
import json

from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import APIKeyHeader

X_RH_IDENTITY = APIKeyHeader(name='x-rh-identity')


class Credentials(BaseModel):
    account_number: str
    username: str


def decode_identity_header(x_rh_identity: str = Depends(X_RH_IDENTITY)):
    rh_identity = base64.standard_b64decode(x_rh_identity)
    json_identity = json.load(rh_identity)
    return Credentials(
        account_number=json_identity['identity']['account_number'],
        username=json_identity['identity']['user']['username'])

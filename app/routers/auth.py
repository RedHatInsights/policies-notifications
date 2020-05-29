import base64
import json

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from ..models.auth import Credentials
from ..core.config import X_RH_IDENTITY_HEADER_NAME

X_RH_IDENTITY = APIKeyHeader(name=X_RH_IDENTITY_HEADER_NAME)


def decode_identity_header(x_rh_identity: str = Depends(X_RH_IDENTITY)):
    try:
        rh_identity = base64.standard_b64decode(x_rh_identity)
        json_identity = json.loads(rh_identity.decode("utf-8"))
        return Credentials(
            account_number=json_identity['identity']['account_number'],
            username=json_identity['identity']['user']['username'])
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials from x-rh-identity")

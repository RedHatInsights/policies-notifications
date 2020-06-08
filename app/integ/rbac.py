import logging
import json

import aiohttp

from ..core.config import RBAC_ENDPOINT_URL
from ..core.errors import RbacException
from ..routers.auth import X_RH_IDENTITY_HEADER_NAME
from ..models.auth import Credentials

logger = logging.getLogger(__name__)

"""
TODO Add short TTL caching for these RBAC requests (otherwise emails might spam it..)
"""


async def get_rbac_permissions_for_identity(identity: Credentials):
    headers = {X_RH_IDENTITY_HEADER_NAME: identity.get_rh_identity()}

    try:
        async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(RBAC_ENDPOINT_URL) as resp:
                if resp.status == 200:
                    # Auth succeeded, return payload
                    json_payload = await resp.json()
                    return json_payload['data']

    except Exception as e:
        logger.error('Calling Rbac threw an exception, ', e)
        pass

    # For any other situation than resp.status == 200
    error_msg = 'Could not validate user, rbac responded with code {}'.format(resp.status)
    raise RbacException(error_msg)


async def verify_access(identity: Credentials, app_permission: str) -> bool:
    rbac_response = await get_rbac_permissions_for_identity(identity)
    # TODO We could need higher granularity here as well (other than * resources * rights)
    auth_property = '{}:*:*'.format(app_permission)
    if auth_property not in [x['permission'] for x in rbac_response]:
        return False

    return True

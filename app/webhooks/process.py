import logging

import aiohttp

from ..events.models import Action
from ..db import endpoints
from ..models.endpoints import Endpoint, WebhookAttributes

logger = logging.getLogger(__name__)


class WebhookProcessor:

    def __init__(self) -> None:
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

    async def _call_webhook(self, endpoint: WebhookAttributes):
        logger.info('Webhook call to: %s', endpoint.__dict__)
        async with self.session.request(endpoint.method, endpoint.url) as resp:
            # TODO Process reply, write statistics to db / handle errors etc
            logger.info('Got reply with: %s', resp.status)
            pass

    async def process(self, action: Action):
        account_id: str = action.tenantId
        endpoint_id: str = action.properties['endpoint_id']
        endpoint: Endpoint = await endpoints.get_endpoint(account_id, endpoint_id)
        print(endpoint.__dict__)
        if endpoint.enabled:
            await self._call_webhook(endpoint.properties)
            # TODO If we fail - disable?
        else:
            return

from typing import List
import logging

import aiohttp
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ..core.config import BOP_URL, BOP_APITOKEN, BOP_CLIENT_ID, BOP_ENV
from ..core.errors import BOPException

logger = logging.getLogger(__name__)


class BopSender:

    def __init__(self) -> None:
        self.headers = {"x-rh-apitoken": BOP_APITOKEN, "x-rh-clientid": BOP_CLIENT_ID, "x-rh-insights-env": BOP_ENV}

    async def send_email(self, topic, payload, receivers):
        email_set: List[Email] = []
        if len(receivers) > 0:
            email: Email = Email(
                subject=topic,
                bodyType='html',
                recipients=receivers,
                body=payload)
            email_set.append(email)
        else:
            return

        emails: Emails = Emails(emails=email_set)

        json_payload = jsonable_encoder(emails)

        async with aiohttp.ClientSession(headers=self.headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(BOP_URL, json=json_payload) as resp:
                try:
                    if resp.status == 200:
                        json = await resp.json()
                        if json['message'] != 'success':
                            raise BOPException('Received error message from BOP: %s', json['message'])
                    else:
                        text = await resp.text()
                        # logger.error('Error code: %s, Received error from BOP: %s, RESP: %s', resp.status, text, resp)
                        raise BOPException('Error code: {}, error message: {}'.format(resp.status, text))
                except Exception as e:
                    # logger.error(e)
                    raise BOPException(e)

    async def shutdown(self):
        await self.session.close()


class Email(BaseModel):
    subject: str
    body: str
    recipients: List[str]
    bodyType: str


class Emails(BaseModel):
    emails: List[Email]

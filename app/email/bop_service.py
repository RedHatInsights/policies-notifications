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
        headers = {"x-rh-apitoken": BOP_APITOKEN, "x-rh-clientid": BOP_CLIENT_ID, "x-rh-insights-env": BOP_ENV}
        self.session = aiohttp.ClientSession(headers=headers,
                                             connector=aiohttp.TCPConnector(verify_ssl=False))

    async def send_email(self, payload, receivers):
        email_set: List[Email] = []
        for r in receivers:
            email: Email = Email(
                subject='Custom Policy Notification',
                bodyType='html',
                recipients=receivers,
                body=payload)
            email_set.append(email)

        if len(email_set) < 1:
            return

        emails: Emails = Emails(emails=email_set)

        json_payload = jsonable_encoder(emails)

        async with self.session.post(BOP_URL, json=json_payload) as resp:
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

from typing import List, Set
import logging

import aiohttp
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ..core.config import BOP_URL, BOP_APITOKEN, BOP_CLIENT_ID, BOP_ENV
from ..core.errors import BOPException, BOPInvalidRecipientException

logger = logging.getLogger(__name__)


class BopSender:

    def __init__(self) -> None:
        self._url = BOP_URL
        self.headers = {"x-rh-apitoken": BOP_APITOKEN, "x-rh-clientid": BOP_CLIENT_ID, "x-rh-insights-env": BOP_ENV}

    def get_url(self):
        return self._url

    async def send_email(self, topic, payload, receivers: Set[str]):
        email_set: List[Email] = []
        if len(receivers) > 0:
            email: Email = Email(
                subject=topic,
                bodyType='html',
                recipients=['no-reply@redhat.com'],
                bccList=receivers,
                ccList=[],
                body=payload)
            email_set.append(email)
        else:
            return

        emails: Emails = Emails(emails=email_set)

        json_payload = jsonable_encoder(emails)

        async with aiohttp.ClientSession(headers=self.headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(self.get_url(), json=json_payload) as resp:
                if resp.status == 200:
                    return
                elif resp.status == 400:
                    json = await resp.json()
                    err_msg: str = json['message']
                    if err_msg.startswith('Invalid recipient(s):'):
                        invalid_users = err_msg[21:]
                        invalid_users = [user.strip() for user in invalid_users.split(',')]
                        raise BOPInvalidRecipientException(set(invalid_users))
                else:
                    text = await resp.text()
                    raise BOPException('Error code: {}, error message: {}'.format(resp.status, text))

    async def shutdown(self):
        await self.session.close()


class Email(BaseModel):
    subject: str
    body: str
    recipients: List[str]
    ccList: List[str]
    bccList: List[str]
    bodyType: str


class Emails(BaseModel):
    emails: List[Email]

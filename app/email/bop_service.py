from typing import List, Set
import logging

import aiohttp
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BopSender:

    def __init__(self) -> None:
        self.url = ''
        apitoken = ''
        headers = {"x-rh-apitoken": apitoken}
        self.session = aiohttp.ClientSession(headers=headers)

    async def send_email(self, payload, *receivers):
        email_set: List[Email] = []
        for r in receivers:
            email: Email = Email(
                subject='Custom Policy Notification',
                bodyType='html',
                recipients={r},
                body=payload)
            email_set.append(email)

        emails: Emails = Emails(emails=email_set)

        json_payload = jsonable_encoder(emails)

        logger.info('Request: %s', json_payload)
        # await self.session.post(self.url, json=json_payload)

    async def shutdown(self):
        await self.session.close()


class Email(BaseModel):
    subject: str
    body: str
    recipients: Set[str]
    bodyType: str


class Emails(BaseModel):
    emails: List[Email]

from typing import Optional

import json
from base64 import b64encode

from pydantic import BaseModel


class Credentials(BaseModel):
    account_number: str
    username: str
    orig_header: Optional[str]

    def get_rh_identity(self) -> str:
        if self.orig_header is not None:
            return self.orig_header
        identity = {'identity': {'user': {'username': self.username}, 'account_number': self.account_number}}
        json_identity = json.dumps(identity).encode('utf-8')
        return b64encode(json_identity)

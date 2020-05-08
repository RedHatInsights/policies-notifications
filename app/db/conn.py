import logging

from gino.ext.starlette import Gino

from ..core.config import DB_DSN

logging.getLogger('gino.engine').setLevel(logging.ERROR)

db = Gino(dsn=DB_DSN, echo=False)

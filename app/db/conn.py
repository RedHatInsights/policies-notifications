import logging

from gino import Gino

from ..core.config import DATABASE_URL

logging.getLogger('gino.engine').setLevel(logging.ERROR)

db = Gino()


async def setup():
    await db.set_bind(str(DATABASE_URL), echo=False)


async def shutdown():
    await db.pop_bind().close()

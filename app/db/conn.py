from gino import Gino

from ..core.config import DATABASE_URL

db = Gino()


async def setup():
    await db.set_bind(str(DATABASE_URL))


async def shutdown():
    await db.pop_bind().close()

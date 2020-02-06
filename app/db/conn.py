from gino import Gino

db = Gino()


async def setup():
    await db.set_bind('postgres://hook:addme@192.168.1.139/hook')


async def shutdown():
    await db.pop_bind().close()

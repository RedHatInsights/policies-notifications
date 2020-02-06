from typing import List

from ..models.apps import App
from .schemas import Application


# TODO Might require further filtering.. but for now, not.
async def get_applications():
    apps: List[Application] = await Application.query.gino.all()
    return apps


async def get_application(id: str):
    app: Application = await Application.get(id)
    return app


async def create_application(app: App):
    await Application(**app.dict()).create()


async def delete_application(id: str):
    pass


async def update_application(id: str, app: App):
    pass
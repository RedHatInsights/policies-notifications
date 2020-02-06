from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException

from ..models.apps import App, AppOut
from ..db import apps as apps_db

apps = FastAPI()

"""
TODO:
    - Don't allow writes with x-rh-identity added (external apps)
"""


@apps.get("/apps", response_model=List[AppOut])
async def get_applications():
    apps = await apps_db.get_applications()
    return apps


@apps.post("/apps")
async def create_application(app: App):
    return await apps_db.create_application(app=app)


@apps.get("/apps/{id}", response_model=AppOut)
async def get_application(id: UUID):
    app = await apps_db.get_application(id=id)
    if app is None:
        raise HTTPException(status_code=404, detail="No application found for id: {}".format(id))

    return app


@apps.delete("/apps/{id}")
async def delete_application(id: UUID):
    pass


@apps.put("/apps/{id}")
async def update_application(id: UUID, app: App):
    await apps_db.update_application(id, app)
    # Find the existing one first, reject if not found (don't allow user generated UUIDs)

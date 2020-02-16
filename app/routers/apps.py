from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from ..models.apps import App, AppOut
from ..db import apps as apps_db
# from .auth import Credentials, decode_identity_header

apps = FastAPI()

"""
TODO:
    - Don't allow writes with x-rh-identity added (external apps)
"""


@apps.get("/apps", response_model=List[AppOut])
async def get_applications():
    # TODO Don't allow access when x-rh-identity is set - or should we for GET?
    return await apps_db.get_applications()


@apps.post("/apps")
async def create_application(app: App, status_code=204):
    # TODO Don't allow access when x-rh-identity is set
    await apps_db.create_application(app=app)


@apps.get("/apps/{id}", response_model=AppOut)
async def get_application(id: UUID):
    # TODO Don't allow access when x-rh-identity is set - or should we for GET?
    app = await apps_db.get_application(id=id)
    if app is None:
        raise HTTPException(status_code=404, detail="No application found for id: {}".format(id))

    return app


@apps.delete("/apps/{id}")
async def delete_application(id: UUID):
    # TODO Don't allow access when x-rh-identity is set
    pass


@apps.put("/apps/{id}")
async def update_application(id: UUID, app: App):
    # TODO Don't allow access when x-rh-identity is set
    await apps_db.update_application(id, app)
    # Find the existing one first, reject if not found (don't allow user generated UUIDs)

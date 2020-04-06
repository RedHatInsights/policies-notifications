# Standard library
import logging

# Third-party
from fastapi import FastAPI

# Local
from .routers import apps, endpoints
from .db import conn
from .events import consume, email
from .core.config import TESTING

consumer = consume.EventConsumer()
email_consumer = email.EmailSubscriptionConsumer()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


notif_app: FastAPI = FastAPI(title='Notifications backend', openapi_url='/api/v1/openapi.json', redoc_url=None)

# The main application (register additional routers here)


@notif_app.on_event("startup")
async def startup_event():
    await conn.setup()
    if not TESTING:
        await consumer.start()
        await email_consumer.start()
    logger.info('Notifications backend started')


@notif_app.on_event("shutdown")
async def shutdown_event():
    await conn.shutdown()
    if not TESTING:
        await consumer.shutdown()
        await email_consumer.shutdown()


notif_app.include_router(apps.apps, tags=['Apps'])
notif_app.include_router(endpoints.endpoints, tags=['Endpoints'])

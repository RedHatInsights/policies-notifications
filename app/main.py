# Standard library
import logging

# Third-party
from fastapi import FastAPI

# Local
from .routers import apps, endpoints
from .db import conn
from .events import consume, email

"""
What's needed..

#1 URL to call
#2 ID to use in the ActionDefinition
#3 AccountID linking to URLs
#4 Dynamic URLs with data inserted to them
#5 Dynamic payload / template? Field selection?
#6 Active / not active
#7 Status (previous attempt, previous status etc)
#8 custom-policies-api integration (directly read from the Kafka)
#9 Some other more generic Kafka queue for applications that do not use engine
#10 HTTP call type (POST/GET/etc)
#11 HTTPS certificate installing..?
--#12 Actions require tenantId information there to separate the IDs
#13 Request headers must be settable
#14 JSON payload or something else like Form encoded?

#15 Migrate email to the same service?

#16 Allow override from the Action messages. Such as using the properties to, from etc (plugin: email)
#   or using this one's internal DB with: endpoint_id = xxxx in the Action

# HTTP services should probably have something like: /service/{serviceName}/... format. Like /service/email/.. /service/webhook/..

# Use aiohttp for HTTP client
# Use FastAPI for HTTP server
# Use aiokafka for Kafka?
# Use asyncpg for Postgres

# Pydantic for Models
# <?> for DB? Or nothing?

# Pytests, REST tests

# Where to store the template matching (for email) ?

# Allow user_id to subscribe for certain event_types? (event_type coming from the Action message?) At least as a first step 

"""

notif_app: FastAPI = FastAPI(title='Notifications backend', openapi_url='/api/v1/openapi.json', redoc_url=None)
notif_app.include_router(apps.apps, tags=['Apps'])
notif_app.include_router(endpoints.endpoints, tags=['Endpoints'])

consumer = consume.EventConsumer()
email_consumer = email.EmailSubscriptionConsumer()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# The main application (register additional routers here)

@notif_app.on_event("startup")
async def startup_event():
    await conn.setup()
    await consumer.start()
    await email_consumer.start()
    logger.info('Notifications backend started')


@notif_app.on_event("shutdown")
async def shutdown_event():
    await conn.shutdown()
    await consumer.shutdown()
    await email_consumer.shutdown()

# db: MetaData = Gino(app, dsn=DATABASE_CONFIG.url)

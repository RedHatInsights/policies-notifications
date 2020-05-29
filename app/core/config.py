from sqlalchemy.engine.url import URL, make_url
from starlette.config import Config
from starlette.datastructures import Secret

config = Config()
TESTING = config('TESTING', cast=bool, default=False)  # Set in conftest.py

DATABASE_HOST = config('DATABASE_HOST', default='')
DATABASE_PORT = config('DATABASE_PORT', cast=int, default='')
DATABASE_USER = config('DATABASE_USER', default='')
DATABASE_PASSWORD = config('DATABASE_PASSWORD', cast=Secret, default='')
DATABASE_NAME = config('DATABASE_NAME', default='policies_notifications')

if TESTING:
    DATABASE_NAME = DATABASE_NAME + '-test'

DB_DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername='postgresql',
        username=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
    ),
)

KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_QUEUE_HOOK = config('KAFKA_QUEUE_HOOK')
KAFKA_QUEUE_EMAIL = config('KAFKA_QUEUE_EMAIL')
BOP_URL = config.get('BOP_URL')
BOP_APITOKEN = config('BOP_APITOKEN')
BOP_CLIENT_ID = config('BOP_CLIENT_ID')
BOP_ENV = config('BOP_ENV')
RBAC_URL = config('RBAC_URL')
RBAC_APP_NAME = config('RBAC_APP_NAME')
RBAC_ENDPOINT_URL = '{}/api/rbac/v1/access/?application={}'.format(RBAC_URL, RBAC_APP_NAME)
X_RH_IDENTITY_HEADER_NAME = 'x-rh-identity'

from starlette.config import Config
from starlette.datastructures import URL, Secret

# Parse configuration file here, make some methods to return certain info..

config = Config('.env')
TESTING = config('TESTING', cast=bool, default=False)  # Set in conftest.py


def create_db_url():
    return 'postgresql://{}:{}@{}:{}/{}' \
        .format(DATABASE_USER, str(DATABASE_PASSWORD), DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)


DATABASE_HOST = config('DATABASE_HOST', default='')
DATABASE_PORT = config('DATABASE_PORT', default='')
DATABASE_USER = config('DATABASE_USER', default='')
DATABASE_PASSWORD = config('DATABASE_PASSWORD', cast=Secret, default='')
DATABASE_NAME = config('DATABASE_NAME', default='policies_notifications')

if TESTING:
    DATABASE_NAME = DATABASE_NAME + '-test'
    DATABASE_URL = config('TEST_DATABASE_URL', cast=URL, default=create_db_url())
else:
    DATABASE_URL = config('DATABASE_URL', cast=URL, default=create_db_url())

KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_QUEUE_HOOK = config('KAFKA_QUEUE_HOOK')
KAFKA_QUEUE_EMAIL = config('KAFKA_QUEUE_EMAIL')
BOP_URL = config('BOP_URL')
BOP_APITOKEN = config('BOP_APITOKEN')
BOP_CLIENT_ID = config('BOP_CLIENT_ID')
BOP_ENV = config('BOP_ENV')

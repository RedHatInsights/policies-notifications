from starlette.config import Config
from starlette.datastructures import URL

# Parse configuration file here, make some methods to return certain info..

config = Config('.env')

DATABASE_URL = config('DATABASE_URL', cast=URL)
KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_QUEUE_HOOK = config('KAFKA_QUEUE_HOOK')
KAFKA_QUEUE_EMAIL = config('KAFKA_QUEUE_EMAIL')
BOP_URL = config('BOP_URL')
BOP_APITOKEN = config('BOP_APITOKEN')
BOP_CLIENT_ID = config('BOP_CLIENT_ID')
